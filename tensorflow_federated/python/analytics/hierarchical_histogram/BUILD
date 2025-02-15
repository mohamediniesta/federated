load("@rules_python//python:defs.bzl", "py_library", "py_test")

package(default_visibility = [
    ":hierarchical_histogram_packages",
    "//tensorflow_federated/python/analytics:analytics_users",

    # Python package namespace
    "//tensorflow_federated/python/analytics:__pkg__",
])

package_group(
    name = "hierarchical_histogram_packages",
    packages = ["//tensorflow_federated/python/analytics/hierarchical_histogram/..."],
)

licenses(["notice"])

py_library(
    name = "hierarchical_histogram",
    srcs = ["__init__.py"],
    srcs_version = "PY3",
    visibility = ["//tensorflow_federated/tools/python_package:python_package_tool"],
)

py_library(
    name = "hierarchical_histogram_factory",
    srcs = ["hierarchical_histogram_factory.py"],
    srcs_version = "PY3",
    deps = [
        ":clipping_factory",
        "//tensorflow_federated/python/aggregators:differential_privacy",
        "//tensorflow_federated/python/aggregators:secure",
        "//tensorflow_federated/python/aggregators:sum_factory",
    ],
)

py_test(
    name = "hierarchical_histogram_factory_test",
    timeout = "long",
    srcs = ["hierarchical_histogram_factory_test.py"],
    python_version = "PY3",
    shard_count = 4,
    srcs_version = "PY3",
    deps = [
        ":build_tree_from_leaf",
        ":hierarchical_histogram_factory",
        "//tensorflow_federated/python/aggregators:differential_privacy",
        "//tensorflow_federated/python/aggregators:factory",
        "//tensorflow_federated/python/core/backends/test:execution_contexts",
        "//tensorflow_federated/python/core/impl/types:computation_types",
        "//tensorflow_federated/python/core/impl/types:type_conversions",
        "//tensorflow_federated/python/core/templates:aggregation_process",
        "//tensorflow_federated/python/core/templates:measured_process",
    ],
)

py_library(
    name = "hierarchical_histogram_lib",
    srcs = ["hierarchical_histogram_lib.py"],
    srcs_version = "PY3",
    deps = [
        ":clipping_factory",
        ":hierarchical_histogram_factory",
        "//tensorflow_federated/python/core/impl/federated_context:federated_computation",
        "//tensorflow_federated/python/core/impl/federated_context:intrinsics",
        "//tensorflow_federated/python/core/impl/tensorflow_context:tensorflow_computation",
        "//tensorflow_federated/python/core/impl/types:computation_types",
        "//tensorflow_federated/python/core/impl/types:placements",
        "//tensorflow_federated/python/core/templates:iterative_process",
    ],
)

py_test(
    name = "hierarchical_histogram_lib_test",
    srcs = ["hierarchical_histogram_lib_test.py"],
    python_version = "PY3",
    shard_count = 6,
    srcs_version = "PY3",
    deps = [
        ":hierarchical_histogram_lib",
        "//tensorflow_federated/python/core/backends/test:execution_contexts",
        "//tensorflow_federated/python/core/test:static_assert",
    ],
)

py_library(
    name = "hierarchical_histogram_decoder",
    srcs = ["hierarchical_histogram_decoder.py"],
    srcs_version = "PY3",
    deps = [":build_tree_from_leaf"],
)

py_test(
    name = "hierarchical_histogram_decoder_test",
    srcs = ["hierarchical_histogram_decoder_test.py"],
    python_version = "PY3",
    srcs_version = "PY3",
    deps = [
        ":build_tree_from_leaf",
        ":hierarchical_histogram_decoder",
    ],
)

py_library(
    name = "build_tree_from_leaf",
    srcs = ["build_tree_from_leaf.py"],
    srcs_version = "PY3",
)

py_test(
    name = "build_tree_from_leaf_test",
    srcs = ["build_tree_from_leaf_test.py"],
    python_version = "PY3",
    srcs_version = "PY3",
    deps = [":build_tree_from_leaf"],
)

py_library(
    name = "clipping_factory",
    srcs = ["clipping_factory.py"],
    srcs_version = "PY3",
    deps = [
        "//tensorflow_federated/python/aggregators:factory",
        "//tensorflow_federated/python/aggregators:sum_factory",
        "//tensorflow_federated/python/core/impl/federated_context:federated_computation",
        "//tensorflow_federated/python/core/impl/federated_context:intrinsics",
        "//tensorflow_federated/python/core/impl/tensorflow_context:tensorflow_computation",
        "//tensorflow_federated/python/core/impl/types:computation_types",
        "//tensorflow_federated/python/core/impl/types:placements",
        "//tensorflow_federated/python/core/impl/types:type_analysis",
        "//tensorflow_federated/python/core/templates:aggregation_process",
    ],
)

py_test(
    name = "clipping_factory_test",
    srcs = ["clipping_factory_test.py"],
    python_version = "PY3",
    srcs_version = "PY3",
    deps = [
        ":clipping_factory",
        "//tensorflow_federated/python/aggregators:factory",
        "//tensorflow_federated/python/core/backends/test:execution_contexts",
        "//tensorflow_federated/python/core/impl/types:computation_types",
        "//tensorflow_federated/python/core/impl/types:placements",
        "//tensorflow_federated/python/core/templates:aggregation_process",
        "//tensorflow_federated/python/core/templates:measured_process",
    ],
)
