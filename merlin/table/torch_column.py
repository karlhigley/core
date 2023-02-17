#
# Copyright (c) 2023, NVIDIA CORPORATION.
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
from merlin.core.compat import torch as th
from merlin.table.tensor_column import Device, TensorColumn


class TorchColumn(TensorColumn):
    def __init__(self, values: th.Tensor, offsets: th.Tensor = None, dtype=None, _ref=None):
        values_device = self._th_device(values)
        offsets_device = self._th_device(offsets)
        if values_device != offsets_device:
            raise ValueError(
                f"Values and offsets were detected on different devices: "
                f"values ({values_device}) and offsets ({offsets_device})."
            )
        super().__init__(values, offsets, dtype, _ref=_ref)

    @property
    def device(self) -> Device:
        return Device.GPU if self.values.is_cuda else Device.CPU

    def _th_device(self, tensor):
        return Device.GPU if self.values.is_cuda else Device.CPU
