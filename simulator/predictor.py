class _StateAndNumSamples:
    def __init__(self, vm_state, vm_num_samples):
        self.vm_state = vm_state
        self.vm_num_samples = vm_num_samples


class _Predictor:
    def __init__(self, config, decorated_predictors=None):
        pass

    def _UpdateMeasures(self, snapshot):
        pass


class StatefulPredictor(_Predictor):
    def __init__(self, config, decorated_predictors=None):
        super().__init__(config, decorated_predictors)
        self.warm_vms = {}
        self.cold_vms = {}
        self.vm_limits = {}
        self.min_num_samples = config.min_num_samples

    def _CreateState(self, vminfo):
        raise NotImplementedError

    def _UpdateState(self, vmmeasure, vmstate):
        raise NotImplementedError

    def _Predict(self, vmstates):
        raise NotImplementedError

    def UpdateMeasures(self, snapshot):
        vm_measures = [item for item in vars(snapshot)["measures"]]
        current_vm_keys = []

        for vm_measure in vm_measures:
            vm_unique_id = vm_measure["sample"]["info"]["unique_id"]
            if vm_unique_id in self.warm_vms:
                self.UpdateState(vm_measure, self.warm_vms[vm_unique_id].vm_state)
                self.warm_vms[vm_unique_id].vm_num_samples += 1
                self.vm_limits[vm_unique_id] = vm_measure["sample"]["abstract_metrics"][
                    "limit"
                ]

            elif vm_unique_id in self.cold_vms:
                self.UpdateState(vm_measure, self.cold_vms[vm_unique_id].vm_state)
                self.cold_vms[vm_unique_id].vm_num_samples += 1
                self.vm_limits[vm_unique_id] = vm_measure["sample"]["abstract_metrics"][
                    "limit"
                ]
                if self.cold_vms[vm_unique_id].vm_num_samples >= self.min_num_samples:
                    self.warm_vms[vm_unique_id] = self.cold_vms.pop(vm_unique_id)
            else:
                vm_state = self.CreateState(vm_measure["sample"]["info"])
                self.cold_vms[vm_unique_id] = _StateAndNumSamples(vm_state, 1)
                self.vm_limits[vm_unique_id] = vm_measure["sample"]["abstract_metrics"][
                    "limit"
                ]
                self.UpdateState(vm_measure, self.cold_vms[vm_unique_id].vm_state)

            current_vm_keys.append(vm_unique_id)

        self.warm_vms = dict(
            (key, self.warm_vms[key]) for key in current_vm_keys if key in self.warm_vms
        )

        self.cold_vms = dict(
            (key, self.cold_vms[key]) for key in current_vm_keys if key in self.cold_vms
        )

        self.vm_limits = dict(
            (key, self.vm_limits[key])
            for key in current_vm_keys
            if key in self.vm_limits
        )

        predicted_peak = self.Predict(list(self.warm_vms.values()))
        total_limit_for_cold_vms = sum(
            self.vm_limits[vm_unique_id] for vm_unique_id in self.cold_vms
        )
        total_limit_for_warm_vms = sum(
            self.vm_limits[vm_unique_id] for vm_unique_id in self.warm_vms
        )
        total_peak = predicted_peak + total_limit_for_cold_vms
        limit = total_limit_for_cold_vms + total_limit_for_warm_vms

        return (total_peak, limit)