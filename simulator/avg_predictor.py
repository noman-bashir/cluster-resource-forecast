from predictor import StatefulPredictor


class _State:
    def __init__(self):
        self.total_usage = 0


class AvgPredictor(StatefulPredictor):
    def __init__(self, config, decorated_predictors=None):
        super().__init__(config, decorated_predictors)
        self.decorated_predictors = decorated_predictors

    def CreateState(self, vm_info):
        return _State()

    def UpdateState(self, vm_measure, vm_state):
        vm_state.total_usage += vm_measure["sample"]["abstract_metrics"]["usage"]

    def Predict(self, vm_states_and_num_samples):

        vms_avgs = []
        for vm_state_and_num_sample in vm_states_and_num_samples:
            vms_avgs.append(
                vm_state_and_num_sample.vm_state.total_usage
                / vm_state_and_num_sample.vm_num_samples
            )

        predicted_peak = sum(vms_avgs)

        return predicted_peak
