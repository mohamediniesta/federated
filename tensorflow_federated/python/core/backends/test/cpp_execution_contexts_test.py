# Copyright 2021, The TensorFlow Federated Authors.
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

from absl.testing import absltest
from absl.testing import parameterized
import numpy as np
import tensorflow as tf

from tensorflow_federated.python.core.backends.test import cpp_execution_contexts
from tensorflow_federated.python.core.impl.context_stack import context_base
from tensorflow_federated.python.core.impl.federated_context import federated_computation
from tensorflow_federated.python.core.impl.federated_context import intrinsics
from tensorflow_federated.python.core.impl.types import computation_types


class CreateTestExecutionTest(tf.test.TestCase):

  def test_returns_cpp_context(self):
    context = cpp_execution_contexts.create_test_cpp_execution_context()
    self.assertIsInstance(context, context_base.SyncContext)


class SecureModularSumTest(parameterized.TestCase, tf.test.TestCase):

  # pyformat: disable
  @parameterized.named_parameters(
      ('one_client_not_divisible', [1], 1,
       computation_types.at_clients(tf.int32)),
      ('two_clients_none_divisible', [1, 2], 3,
       computation_types.at_clients(tf.int32)),
      ('three_clients_one_divisible', [1, 2, 10], 3,
       computation_types.at_clients(tf.int32)),
      ('all_clients_divisible_by_modulus', [x * 5 for x in range(5)], 0,
       computation_types.at_clients(tf.int32)),
      ('nonscalar_struct_arg', [([1, 2], 3), ([4, 5], 6)],
       (np.array([0, 2], dtype=np.int32), 4),
       computation_types.at_clients(((tf.int32, [2]), tf.int32))),
  )
  # pyformat: enable
  def test_executes_computation_with_modular_secure_sum_integer_modulus(
      self, arg, expected_result, tff_type):

    cpp_execution_contexts.set_test_cpp_execution_context()

    modulus = 5

    @federated_computation.federated_computation(tff_type)
    def modular_sum_by_five(arg):
      return intrinsics.federated_secure_modular_sum(arg, modulus)

    # assertAllEqual doesnt handle nested structures well, so we use
    # assertAllClose with no tolerance here.
    self.assertAllClose(
        expected_result, modular_sum_by_five(arg), atol=0.0, rtol=0.0)

  @parameterized.named_parameters(
      ('one_client_not_divisible', [[1, 2]], [1, 2],
       computation_types.at_clients([tf.int32, tf.int32])),
      ('two_clients_none_divisible', [[1, 2], [3, 4]], [4, 6],
       computation_types.at_clients([tf.int32, tf.int32])),
      ('three_clients_one_divisible', [[1, 2], [3, 4], [10, 14]], [4, 6],
       computation_types.at_clients([tf.int32, tf.int32])),
      ('two_clients_one_partially_divisible', [[1, 2], [3, 4], [10, 15]],
       [4, 0], computation_types.at_clients([tf.int32, tf.int32])),
  )
  def test_executes_computation_with_modular_secure_sum_struct_modulus(
      self, arg, expected_result, tff_type):

    cpp_execution_contexts.set_test_cpp_execution_context()
    modulus = [5, 7]

    @federated_computation.federated_computation(tff_type)
    def modular_sum_by_five(arg):
      return intrinsics.federated_secure_modular_sum(arg, modulus)

    self.assertEqual(expected_result, modular_sum_by_five(arg))


class SecureSumBitwidthTest(tf.test.TestCase, parameterized.TestCase):

  @parameterized.named_parameters(
      ('one_client', [1]),
      ('three_clients', [1, 2, 10]),
      ('five_clients', [x * 5 for x in range(5)]),
  )
  def test_executes_computation_with_bitwidth_secure_sum_large_bitwidth(
      self, arg):
    cpp_execution_contexts.set_test_cpp_execution_context()
    bitwidth = 32
    expected_result = sum(arg)

    @federated_computation.federated_computation(
        computation_types.at_clients(tf.int32))
    def sum_with_bitwidth(arg):
      return intrinsics.federated_secure_sum_bitwidth(arg, bitwidth)

    self.assertEqual(expected_result, sum_with_bitwidth(arg))

  # pyformat: disable
  @parameterized.named_parameters(
      ('two_clients_scalar_tensors', [[1, 2], [3, 4]], [4, 6],
       computation_types.at_clients([tf.int32, tf.int32])),
      ('two_clients_nonscalar_tensors',
       [[tf.ones(shape=[10], dtype=tf.int32), 2],
        [tf.ones(shape=[10], dtype=tf.int32), 4]],
       [2 * tf.ones(shape=[10], dtype=tf.int32).numpy(), 6],
       computation_types.at_clients([
           computation_types.TensorType(dtype=tf.int32, shape=[10]), tf.int32]),
      ),
  )
  # pyformat: enable
  def test_executes_computation_with_argument_structure(self, arg,
                                                        expected_result,
                                                        tff_type):
    cpp_execution_contexts.set_test_cpp_execution_context()

    bitwidth = 32

    @federated_computation.federated_computation(tff_type)
    def sum_with_bitwidth(arg):
      return intrinsics.federated_secure_sum_bitwidth(arg, bitwidth)

    self.assertAllClose(expected_result, sum_with_bitwidth(arg))


class SecureSumMaxValueTest(tf.test.TestCase, parameterized.TestCase):

  def test_raises_with_arguments_over_max_value(self):
    cpp_execution_contexts.set_test_cpp_execution_context()

    max_value = 1

    @federated_computation.federated_computation(
        computation_types.at_clients(tf.int32))
    def secure_sum(arg):
      return intrinsics.federated_secure_sum(arg, max_value)

    with self.assertRaisesRegex(
        Exception, 'client value larger than maximum specified for secure sum'):
      secure_sum([2, 4])

  @parameterized.named_parameters(
      ('one_client', [1]),
      ('three_clients', [1, 2, 10]),
      ('five_clients', [x * 5 for x in range(5)]),
  )
  def test_executes_computation_with_secure_sum_under_max_values(self, arg):
    cpp_execution_contexts.set_test_cpp_execution_context()

    max_value = 30

    expected_result = sum(arg)

    @federated_computation.federated_computation(
        computation_types.at_clients(tf.int32))
    def secure_sum(arg):
      return intrinsics.federated_secure_sum(arg, max_value)

    self.assertEqual(expected_result, secure_sum(arg))

  # pyformat: disable
  @parameterized.named_parameters(
      ('two_clients_scalar_tensors', [[1, 2], [3, 4]], [4, 6],
       computation_types.at_clients([tf.int32, tf.int32])),
      ('two_clients_nonscalar_tensors',
       [[tf.ones(shape=[10], dtype=tf.int32), 2],
        [tf.ones(shape=[10], dtype=tf.int32), 4]],
       [2 * tf.ones(shape=[10], dtype=tf.int32).numpy(), 6],
       computation_types.at_clients([
           computation_types.TensorType(
               dtype=tf.int32, shape=[10]), tf.int32])),
  )
  # pyformat: enable
  def test_executes_computation_with_argument_structure(self, arg,
                                                        expected_result,
                                                        tff_type):
    cpp_execution_contexts.set_test_cpp_execution_context()

    max_value = 100

    @federated_computation.federated_computation(tff_type)
    def secure_sum(arg):
      return intrinsics.federated_secure_sum(arg, max_value)

    self.assertAllClose(expected_result, secure_sum(arg))


if __name__ == '__main__':
  absltest.main()
