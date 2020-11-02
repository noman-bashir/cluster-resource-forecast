# Copyright 2020 Google LLC.

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#    http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from simulator.predictor import StatefulPredictor
from collections import deque
import numpy as np


class _State:
    def __init__(self, num_history_samples):
        self.num_history_samples = num_history_samples
        self.usage = deque(maxlen=self.num_history_samples)
        self.limit = deque(maxlen=self.num_history_samples)


class PerVMPercentilePredictor(StatefulPredictor):
    def __init__(self, config):
        super().__init__(config)
        self.num_history_samples = config.num_history_samples
        self.percentile = min(config.percentile, 100)
        self.cap_to_limit = config.cap_to_limit

    def CreateState(self, vm_info):
        return _State(self.num_history_samples)

    def UpdateState(self, vm_measure, vm_state):
        limit = vm_measure["sample"]["abstract_metrics"]["limit"]
        usage = vm_measure["sample"]["abstract_metrics"]["usage"]
        if self.cap_to_limit == True:
            usage = min(usage, limit)
        vm_state.usage.append(usage)
        vm_state.limit.append(limit)

    def Predict(self, vm_states_and_num_samples):

        vms_percentiles = []
        for vm_state_and_num_sample in vm_states_and_num_samples:
            normalized_usage = [
                usage / limit
                for usage, limit in zip(
                    list(vm_state_and_num_sample.vm_state.usage),
                    list(vm_state_and_num_sample.vm_state.limit),
                )
            ]

            vms_percentiles.append(
                np.percentile(np.array(normalized_usage), self.percentile)
                * vm_state_and_num_sample.vm_state.limit[-1]
            )

        predicted_peak = np.sum(vms_percentiles)

        return predicted_peak
