from simulator.predictor import StatefulPredictor


class _State:
    def __init__(self):
        self.limit = 0


class LimitPredictor(StatefulPredictor):
    def __init__(self, config, decorated_predictors=None):
        super().__init__(config, decorated_predictors)
        self.decorated_predictors = decorated_predictors

    def CreateState(self, vm_info):
        return _State()

    def UpdateState(self, vm_measure, vm_state):
        vm_state.limit = vm_measure["sample"]["abstract_metrics"]["limit"]

    def Predict(self, vm_states_and_num_samples):

        vms_limits = []
        for vm_state_and_num_sample in vm_states_and_num_samples:
            vms_limits.append(vm_state_and_num_sample.vm_state.limit)

        predicted_peak = sum(vms_limits)

        return predicted_peak
