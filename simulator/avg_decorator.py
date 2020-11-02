from simulator.predictor import Predictor
import numpy as np


class AvgDecorator(Predictor):
    def __init__(self, config=None, decorated_predictors=None):
        self.decorated_predictors = decorated_predictors


    def UpdateMeasures(self, snapshot):
        predictions = []
        for predictor in self.decorated_predictors:
            predictions.append(predictor.UpdateMeasures(snapshot))

        return self._Predict(predictions)

    def Predict(self, predictions):

        limits = []
        predicted_peaks = []
        for prediction_limit in predictions:
            limits.append(prediction_limit[0])
            predicted_peaks.append(prediction_limit[1])

        return (np.mean(limits), np.mean(predicted_peaks))
