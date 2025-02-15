# Copyright 2019, The TensorFlow Federated Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import asyncio
import collections
import time

from absl.testing import absltest
import tensorflow as tf

from tensorflow_federated.python.core.impl.executors import eager_tf_executor
from tensorflow_federated.python.core.impl.executors import executor_base
from tensorflow_federated.python.core.impl.executors import thread_delegating_executor
from tensorflow_federated.python.core.impl.tensorflow_context import tensorflow_computation


def _invoke(ex, comp, arg=None):
  v1 = asyncio.run(ex.create_value(comp))
  if arg is not None:
    type_spec = v1.type_signature.parameter
    v2 = asyncio.run(ex.create_value(arg, type_spec))
  else:
    v2 = None
  v3 = asyncio.run(ex.create_call(v1, v2))
  return asyncio.run(v3.compute())


def _threaded_eager_executor() -> executor_base.Executor:
  return thread_delegating_executor.ThreadDelegatingExecutor(
      eager_tf_executor.EagerTFExecutor())


class ThreadDelegatingExecutorTest(absltest.TestCase):

  def _threaded_eager_value_to_numpy(self, value):
    self.assertIsInstance(
        value, thread_delegating_executor.ThreadDelegatingExecutorValue)
    self.assertIsInstance(value.internal_representation,
                          eager_tf_executor.EagerValue)
    return value.internal_representation.internal_representation.numpy()

  def test_nondeterminism_with_fake_executor_that_synchronously_sleeps(self):

    class FakeExecutor(executor_base.Executor):

      def __init__(self):
        self._values = []

      @property
      def output(self):
        return ''.join([str(x) for x in self._values])

      async def create_value(self, value, type_spec=None):
        del type_spec
        for _ in range(3):
          time.sleep(1)
          self._values.append(value)
        return value

      async def create_call(self, comp, arg=None):
        raise NotImplementedError

      async def create_struct(self, elements):
        raise NotImplementedError

      async def create_selection(self, source, index):
        raise NotImplementedError

      def close(self):
        pass

    def make_output():
      test_ex = FakeExecutor()
      executors = [
          thread_delegating_executor.ThreadDelegatingExecutor(test_ex)
          for _ in range(10)
      ]
      vals = [ex.create_value(idx) for idx, ex in enumerate(executors)]

      async def gather_coro(vals):
        return await asyncio.gather(*vals)

      results = asyncio.run(gather_coro(vals))
      results = [
          thread_value.internal_representation for thread_value in results
      ]
      self.assertCountEqual(results, list(range(10)))
      del executors
      return test_ex.output

    o1 = make_output()
    for _ in range(1000):
      o2 = make_output()
      if o2 != o1:
        break
    self.assertNotEqual(o1, o2)

  def test_with_eager_tf_executor(self):

    @tensorflow_computation.tf_computation(tf.int32)
    def add_one(x):
      return tf.add(x, 1)

    ex = _threaded_eager_executor()

    async def compute():
      return await ex.create_selection(
          await ex.create_struct(
              collections.OrderedDict([
                  ('a', await
                   ex.create_call(await ex.create_value(add_one), await
                                  ex.create_value(10, tf.int32)))
              ])), 0)

    result = asyncio.run(compute())
    self.assertEqual(self._threaded_eager_value_to_numpy(result), 11)

  def use_executor(self, ex):

    @tensorflow_computation.tf_computation(tf.int32)
    def add_one(x):
      return tf.add(x, 1)

    async def compute():
      return await ex.create_selection(
          await ex.create_struct(
              collections.OrderedDict([
                  ('a', await
                   ex.create_call(await ex.create_value(add_one), await
                                  ex.create_value(10, tf.int32)))
              ])), 0)

    return asyncio.run(compute())

  def test_close_then_use_executor(self):
    ex = _threaded_eager_executor()
    ex.close()
    result = self.use_executor(ex)
    self.assertEqual(self._threaded_eager_value_to_numpy(result), 11)

  def test_multiple_computations_with_same_executor(self):

    @tensorflow_computation.tf_computation(tf.int32)
    def add_one(x):
      return tf.add(x, 1)

    ex = _threaded_eager_executor()

    async def compute():
      return await ex.create_selection(
          await ex.create_struct(
              collections.OrderedDict([
                  ('a', await
                   ex.create_call(await ex.create_value(add_one), await
                                  ex.create_value(10, tf.int32)))
              ])), 0)

    result = asyncio.run(compute())
    self.assertEqual(self._threaded_eager_value_to_numpy(result), 11)

    # After this call, the ThreadDelegatingExecutor has been closed, and needs
    # to be re-initialized.
    ex.close()

    result = asyncio.run(compute())
    self.assertEqual(self._threaded_eager_value_to_numpy(result), 11)

  def test_end_to_end(self):

    @tensorflow_computation.tf_computation(tf.int32)
    def add_one(x):
      return tf.add(x, 1)

    executor = _threaded_eager_executor()

    result = _invoke(executor, add_one, 7)
    self.assertEqual(result, 8)

    # After this invocation, the ThreadDelegatingExecutor has been closed,
    # and needs to be re-initialized.

    result = _invoke(executor, add_one, 8)
    self.assertEqual(result, 9)


if __name__ == '__main__':
  absltest.main()
