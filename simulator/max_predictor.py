from predictor import StatefulPredictor


class _State:
    def __init__(self):
        self.usage = 0


class MaxPredictor(StatefulPredictor):
    def __init__(self, config, decorated_predictors=None):
        super().__init__(config, decorated_predictors)
        self.decorated_predictors = decorated_predictors
        self.cap_to_limit = config.cap_to_limit

    def CreateState(self, vm_info):
        return _State()

    def UpdateState(self, vm_measure, vm_state):
        vm_state.usage = max(
            vm_measure["sample"]["abstract_metrics"]["usage"], vm_state.usage
        )

    def Predict(self, vm_states_and_num_samples):

        vms_peaks = []
        for vm_state_and_num_sample in vm_states_and_num_samples:
            vms_avgs.append(vm_state_and_num_sample.vm_state.usage)

        predicted_peak = sum(vms_peaks)

        return predicted_peak