#
# Copyright (c) 2022, NVIDIA CORPORATION.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from functools import singledispatch
from typing import Any, Union

import merlin.dtypes as md
from merlin.core.compat import cupy as cp
from merlin.core.compat import numpy as np
from merlin.core.compat import tensorflow as tf
from merlin.core.compat import tf_ops
from merlin.core.compat import torch as th
from merlin.dag.table.tensor_column import Device, TensorColumn


class TensorflowColumn(TensorColumn):
    @classmethod
    def cast(cls, other):
        column = cls(to_tf(other.values), to_tf(other.offsets))
        column._ref = (other.values, other.offsets)
        return column

    def __init__(self, values: tf.Tensor, offsets: tf.Tensor = None, dtype=None):
        super().__init__(values, offsets, dtype)

    @property
    def device(self) -> Device:
        return Device.GPU if "GPU" in self.values.device else Device.CPU


def to_tf(tensor):
    return _to_tf(tensor)


@singledispatch
def _to_tf(tensor):
    raise NotImplementedError


if cp:

    @_to_tf.register
    def cupy_to_tf(tensor: cp.ndarray):
        # TODO: Use CUDA array interface or DLpack
        return tf.convert_to_tensor(cp.asnumpy(tensor))


if np:

    @_to_tf.register
    def numpy_to_tf(tensor: np.ndarray):
        with tf.device("CPU"):
            return tf.convert_to_tensor(tensor)


if th:

    @_to_tf.register
    def torch_to_tf(tensor: th.Tensor):
        # TODO: Use CUDA array interface or DLpack
        is_gpu = tensor.is_cuda
        device_num = th.cuda.current_device() if is_gpu else ""
        device = "GPU" if is_gpu else "CPU"
        with tf.device(f"{device}{device_num}"):
            return tf.convert_to_tensor(tensor.numpy())


if tf:

    @_to_tf.register(tf.Tensor)
    @_to_tf.register(tf_ops.EagerTensor)
    def tf_to_tf(tensor: Union[tf.Tensor, tf_ops.EagerTensor]):
        return tensor
