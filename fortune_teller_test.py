import unittest
import apache_beam as beam
import simulator.config_pb2 as config_pb2
from apache_beam.testing.util import assert_that
from apache_beam.testing.util import equal_to
from apache_beam.runners.direct import direct_runner
from apache_beam.testing.test_pipeline import TestPipeline

from simulator.fortune_teller import CallFortuneTellerRunner
from simulator.fortune_teller_factory import FortuneTellerFactory
from simulator.fortune_teller_factory import PredictorFactory
from simulator.avg_predictor import AvgPredictor
from simulator.per_vm_percentile_predictor import PerVMPercentilePredictor
from simulator.n_sigma_predictor import NSigmaPredictor


class CallFortuneTellerRunnerTest(unittest.TestCase):
    def setUp(self):
        self.config = config_pb2.SimulationConfig()

        self.samples = [
            {
                "simulated_time": 300_000_000,
                "simulated_machine": 1,
                "sample": {
                    "time": 1,
                    "info": {"unique_id": "1-2",},
                    "metrics": {"avg_cpu_usage": 0.1,},
                    "abstract_metrics": {"usage": 0.1, "limit": 0.3,},
                },
            },
            # {
            #     "simulated_time": 1_800_000_000,
            #     "simulated_machine": 2,
            #     "sample": {
            #         "time": 1,
            #         "info": {"unique_id": "1-3",},
            #         "metrics": {"avg_cpu_usage": 0.2,},
            #         "abstract_metrics": {"usage": 0.2, "limit": 0.3,},
            #     },
            # },
            {
                "simulated_time": 900_000_000,
                "simulated_machine": 1,
                "sample": {
                    "time": 1,
                    "info": {"unique_id": "1-2",},
                    "metrics": {"avg_cpu_usage": 0.3,},
                    "abstract_metrics": {"usage": 0.3, "limit": 0.3,},
                },
            },
            {
                "simulated_time": 1200_000_000,
                "simulated_machine": 1,
                "sample": {
                    "time": 1,
                    "info": {"unique_id": "1-2",},
                    "metrics": {"avg_cpu_usage": 0.4,},
                    "abstract_metrics": {"usage": 0.4, "limit": 0.3,},
                },
            },
            {
                "simulated_time": 300_000_000,
                "simulated_machine": 1,
                "sample": {
                    "time": 1,
                    "info": {"unique_id": "1-3",},
                    "metrics": {"avg_cpu_usage": 0.1,},
                    "abstract_metrics": {"usage": 0.1, "limit": 0.3,},
                },
            },
            {
                "simulated_time": 600_000_000,
                "simulated_machine": 1,
                "sample": {
                    "time": 1,
                    "info": {"unique_id": "1-3",},
                    "metrics": {"avg_cpu_usage": 0.2,},
                    "abstract_metrics": {"usage": 0.2, "limit": 0.3,},
                },
            },
            {
                "simulated_time": 900_000_000,
                "simulated_machine": 1,
                "sample": {
                    "time": 1,
                    "info": {"unique_id": "1-3",},
                    "metrics": {"avg_cpu_usage": 0.3,},
                    "abstract_metrics": {"usage": 0.3, "limit": 0.3,},
                },
            },
            {
                "simulated_time": 900_000_000,
                "simulated_machine": 1,
                "sample": {
                    "time": 1,
                    "info": {"unique_id": "1-4",},
                    "metrics": {"avg_cpu_usage": 0.3,},
                    "abstract_metrics": {"usage": 0.3, "limit": 0.3,},
                },
            },
            {
                "simulated_time": 1200_000_000,
                "simulated_machine": 1,
                "sample": {
                    "time": 1,
                    "info": {"unique_id": "1-4",},
                    "metrics": {"avg_cpu_usage": 0.4,},
                    "abstract_metrics": {"usage": 0.4, "limit": 0.3,},
                },
            },
        ]

    def do_not_test_oracle(self):
        fortune_teller_one = self.config.fortune_teller.add()
        fortune_teller_one.oracle.cap_to_limit = False
        fortune_teller_one.oracle.percentile = 90
        fortune_teller_one.oracle.horizon_in_seconds = 600
        fortune_teller_one.save_samples = True
        fortune_teller_one.name = "oracle0.9"

        correct_output = [
            {
                "fortune_teller_name": "oracle0.9",
                "simulated_time": 300000000,
                'simulated_machine': 1,
                "samples": [
                    {
                        "simulated_time": 300000000,
                        "simulated_machine": 1,
                        "sample": {
                            "time": 1,
                            "info": {"unique_id": "1-2"},
                            "metrics": {"avg_cpu_usage": 0.1},
                            "abstract_metrics": {"usage": 0.1, "limit": 0.3},
                        },
                    },
                    {
                        "simulated_time": 300000000,
                        "simulated_machine": 1,
                        "sample": {
                            "time": 1,
                            "info": {"unique_id": "1-3"},
                            "metrics": {"avg_cpu_usage": 0.1},
                            "abstract_metrics": {"usage": 0.1, "limit": 0.3},
                        },
                    },
                ],
                "predicted_peak": 0.5800000000000001,
                "total_usage": 0.2,
                "limit": 0.6,
            },
            {
                "fortune_teller_name": "oracle0.9",
                "simulated_time": 600000000,
                'simulated_machine': 1,
                "samples": [
                    {
                        "simulated_time": 600000000,
                        "simulated_machine": 1,
                        "sample": {
                            "time": 1,
                            "info": {"unique_id": "1-2"},
                            "metrics": {"avg_cpu_usage": 0.2},
                            "abstract_metrics": {"usage": 0.2, "limit": 0.3},
                        },
                    },
                    {
                        "simulated_time": 600000000,
                        "simulated_machine": 1,
                        "sample": {
                            "time": 1,
                            "info": {"unique_id": "1-3"},
                            "metrics": {"avg_cpu_usage": 0.2},
                            "abstract_metrics": {"usage": 0.2, "limit": 0.3},
                        },
                    },
                ],
                "predicted_peak": 0.5800000000000001,
                "total_usage": 0.4,
                "limit": 0.6,
            },
        ]

        with TestPipeline(runner=direct_runner.BundleBasedDirectRunner()) as p:
            input_vmsamples = p | "Create time test input" >> beam.Create(
                self.samples
            )
            output = CallFortuneTellerRunner(
                input_vmsamples, self.config
            )

            assert_that(output, equal_to(correct_output))

    def test_avg_predictor(self):
        fortune_teller_three = self.config.fortune_teller.add()
        # fortune_teller_one.save_samples = False
        # fortune_teller_one.name = "avg_predictor_max_cpu_3600"
        # fortune_teller_one.predictor.avg_predictor.cap_to_limit = True
        # fortune_teller_one.predictor.avg_predictor.min_num_samples = 3
        # fortune_teller_three.save_samples = False
        # fortune_teller_three.name = "per_vm_percentile_max_cpu_3600"
        # fortune_teller_three.predictor.per_vm_percentile_predictor.cap_to_limit = True
        # fortune_teller_three.predictor.per_vm_percentile_predictor.min_num_samples = 1
        # fortune_teller_three.predictor.per_vm_percentile_predictor.num_history_samples = 1
        # fortune_teller_three.predictor.per_vm_percentile_predictor.percentile = 90
        fortune_teller_three.save_samples = False
        fortune_teller_three.name = "test"
        fortune_teller_three.predictor.n_sigma_predictor.cap_to_limit = True
        fortune_teller_three.predictor.n_sigma_predictor.min_num_samples = 2
        fortune_teller_three.predictor.n_sigma_predictor.num_history_samples = 2
        fortune_teller_three.predictor.n_sigma_predictor.n = 2

        self.config.simulation_result.dataset = "test"

        correct_output = [
            {
                "fortune_teller_name": "oracle0.9",
                "simulated_time": 300000000,
                'simulated_machine': 1,
                "predicted_peak": 0.5800000000000001,
                "total_usage": 0.2,
                "limit": 0.6,
            },
            {
                "fortune_teller_name": "oracle0.9",
                "simulated_time": 600000000,
                'simulated_machine': 1,
                "predicted_peak": 0.5800000000000001,
                "total_usage": 0.4,
                "limit": 0.6,
            },
        ]

        with TestPipeline(runner=direct_runner.BundleBasedDirectRunner()) as p:
            input_vmsamples = p | "Create time test input" >> beam.Create(
                self.samples
            )
            output = CallFortuneTellerRunner(
                input_vmsamples, self.config
            )

            # output | beam.Map(print)

            # assert_that(output, equal_to(correct_output))

if __name__ == "__main__":
    # PredictorFactory().RegisterPredictor("avg_predictor", lambda config: AvgPredictor(config))  
    PredictorFactory().RegisterPredictor("per_vm_percentile_predictor", lambda config: PerVMPercentilePredictor(config))  
    PredictorFactory().RegisterPredictor("n_sigma_predictor", lambda config: NSigmaPredictor(config))  
    # print(PredictorFactory().concrete_predictor_factories)
    unittest.main()
