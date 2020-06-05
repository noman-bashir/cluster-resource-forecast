from predictor import StatefulPredictor
from collections import deque
import numpy as np
import statistics


class _State:
    def __init__(self):
        self.usage = deque(maxlen=self.num_history_samples)
        self.limit = deque(maxlen=self.num_history_samples)


class NSigmaPredictor(StatefulPredictor):
    def __init__(self, config, decorated_predictors=None):
        super().__init__(config, decorated_predictors)
        self.decorated_predictors = decorated_predictors
        self.num_history_samples = config.num_history_samples
        self.percentile = min(config.percentile, 100)
        self.cap_to_limit = config.cap_to_limit
        self.n = config.n

    def CreateState(self, vm_info):
        return _State()

    def UpdateState(self, vm_measure, vm_state):
        limit = vm_measure["sample"]["abstract_metrics"]["limit"]
        usage = vm_measure["sample"]["abstract_metrics"]["usage"]
        if self.cap_to_limit == True:
            usage = min(usage, limit)
        vm_state.usage.append(usage)
        vm_state.limit.append(limit)

    def Predict(self, vm_states_and_num_samples):

        vms_normalized_usages = []
        for vm_state_and_num_sample in vm_states_and_num_samples:
            normalized_usage = list(vm_state_and_num_sample.vm_state.usage) / list(
                vm_state_and_num_sample.vm_state.limit
            )
            vms_percentiles.append(normalized_usage)

        total_normalized_usage = np.sum(vms_normalized_usages, axis=0)
        mean = np.mean(total_normalized_usage)
        standard_deviation = statistics.stdev(total_normalized_usage)
        predicted_peak = mean + self.n * standard_deviation

        return predicted_peak
