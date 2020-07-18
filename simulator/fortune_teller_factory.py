from simulator.oracle import Oracle


def FortuneTellerFactory(config):
    oracle_or_predictor = config.WhichOneof("teller")
    if oracle_or_predictor == "oracle":
        return Oracle(config)

    if oracle_or_predictor == "predictor":
        return PredictorFactory().CreatePredictor(config.predictor)


class PredictorFactory(object):
    __instance = None

    def __new__(cls):
        if PredictorFactory.__instance is None:
            PredictorFactory.__instance = object.__new__(cls)
            PredictorFactory.__instance.decorator_factories = {}
            PredictorFactory.__instance.concrete_predictor_factories = {}
        return PredictorFactory.__instance

    def RegisterDecorator(self, name, factory_func):
        self.decorator_factories[name] = factory_func

    def RegisterPredictor(self, name, factory_func):
        self.concrete_predictor_factories[name] = factory_func

    def CreatePredictor(self, config):
        name = config.WhichOneof("predictor")

        if name in self.concrete_predictor_factories:
            return self.concrete_predictor_factories[name](getattr(config, name))

        elif name in self.decorator_factories:
            decorated_predictors = []
            for decorated_predictor_config in config.decorated_predictors:
                predictor = self.CreatePredictor(decorated_predictor_config)
                decorated_predictors.append(predictor)
            return self.decorator_factories[name](
                getattr(config, name), decorated_predictors
            )

        else:
            assert False, "Requested predictor or decorator not registered. "
