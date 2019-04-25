import os
import requests
import numpy as np
import pandas
import time
import math
from statsmodels.tsa.arima_model import ARIMA
from prometheus_client import Gauge, start_http_server

webapp_url = os.getenv("ONLAB_WEBAPP_URL", "http://webapp:8080/time")
time_before_pred_start = int(os.getenv("TIME_BEFORE_PRED_START", 10))
prediction_interval = int(os.getenv("PREDICTION_INTERVAL", 30))

arima_resource_gauge = Gauge('ARIMA_predicted_active_worker_threads',
                             'Predicted values by ARIMA model based on used resources')
ma_resource_gauge = Gauge('MA_predicted_active_worker_threads',
                          'Predicted values by MA model based on used resources')
ema_resource_gauge = Gauge('EMA_predicted_active_worker_threads',
                           'Predicted values by EMA model based on used resources')

arima_resource_avg_smape_gauge = Gauge('ARIMA_resource_avg_smape',
                                       'average SMAPE value for the ARIMA prediction based on used resources')
ma_resource_avg_smape_gauge = Gauge('MA_resource_avg_smape',
                                    'average SMAPE value for the MA prediction based on used resources')
ema_resource_avg_smape_gauge = Gauge('EMA_resource_avg_smape',
                                     'average SMAPE value for the EMA prediction based on used resources')


class Controller(object):

    predicted_values_by_pred_model = dict()
    previous_pred_vals_by_pred_model = dict()

    average_smapes_by_pred_model = dict()
    average_smape = 0
    smape_samples_num = 0

    def __init__(self, predict_model):
        self.predict_model = predict_model
        self.prediction_models = {
            "arima": ARIMAPredict(ar=4, ir=0, ma=2),
            "ma": MAPredict(window=prediction_interval),
            "ema": EMAPredict(window=prediction_interval)
        }

        for model in self.prediction_models:
            self.average_smapes_by_pred_model[model] = 0
        for model in self.prediction_models:
            self.predicted_values_by_pred_model[model] = []

    def calculate_avg_smape(self, new_smape, model):
        if not math.isnan(new_smape):
            new_avg_smape = (self.average_smapes_by_pred_model.get(model) * self.smape_samples_num + new_smape) / (self.smape_samples_num + 1)
            self.smape_samples_num += 1
            self.average_smapes_by_pred_model[model]= new_avg_smape

            self.set_avg_smape_gauge(new_avg_smape, model)

    def set_avg_smape_gauge(self, value,  model):
        if model == 'arima':
            arima_resource_avg_smape_gauge.set(value)
        elif model == 'ma':
            ma_resource_avg_smape_gauge.set(value)
        elif model == 'ema':
            ema_resource_avg_smape_gauge.set(value)
        else:
            raise KeyError('No model with this name')

    def start(self):
        print("START")
        time.sleep(time_before_pred_start)
        print("SLEEP_END")
        while True:
            print("IN LOOP")
            predict_start = time.time()

            print("PREDICT START: {}".format(time.ctime()))

            # TODO this in VARIABLE (prometheus address)
            metrics = requests.get(
                "http://prometheus:9090/api/v1/query?query=active_worker_threads[{}s]".format(time_before_pred_start))
            metric_values = [int(record[1]) for record in metrics.json().get('data').get('result')[0].get('values')]
            print("Metric values: {} at {}".format(metric_values, time.ctime()))

            for model in self.prediction_models:
                if len(self.predicted_values_by_pred_model.get(model)) != 0:
                    self.previous_pred_vals_by_pred_model[model] = self.predicted_values_by_pred_model.get(model)
                    actual_values = metric_values[-len(self.previous_pred_vals_by_pred_model.get(model)):]

                    print("PREV_PREDICTED: " + str(self.previous_pred_vals_by_pred_model.get(model)))
                    print("ACTUAL: " + str(actual_values))
                    smape_val = smape(self.previous_pred_vals_by_pred_model.get(model), actual_values)

                    self.calculate_avg_smape(smape_val, model)

            try:
                self.predict(metric_values)
            except Exception as e:
                print(e)

            predict_end = time.time()
            time_delta = predict_end - predict_start
            print("TIME_DELTA " + str(time_delta))
            if time_delta < prediction_interval:
                time.sleep(prediction_interval - time_delta)

    def predict(self, metric_values):
        for model in self.prediction_models:
            self.predicted_values_by_pred_model[model] = self.prediction_models.get(model).forecast(
                metric_values, prediction_interval)


def smape(predicted_list, actual_list):
    assert len(predicted_list) == len(actual_list)
    sum_val = 0
    for i in range(len(predicted_list)):
        nominator = math.fabs(predicted_list[i] - actual_list[i])
        denominator = (math.fabs(actual_list[i]) + math.fabs(predicted_list[i])) / 2
        sum_val += nominator / denominator

    return sum_val / len(predicted_list)


class ARIMAPredict(object):
    # input_values = list()

    def __init__(self, ar, ir, ma):
        self.ar = ar
        self.ir = ir
        self.ma = ma

    def forecast(self, input_values, predict_num):
        model = ARIMA(np.asarray(input_values), order=(self.ar, self.ir, self.ma))
        model_fit = model.fit(disp=0)

        # round the predicted values to integers
        predicted_values = [round(pv) for pv in model_fit.forecast(predict_num)[0]]

        # get the max, and set it to be the predicted value
        max_pred_value = max(predicted_values)

        predicted_values = [max_pred_value for i in range(predict_num)]

        arima_resource_gauge.set(max_pred_value)
        return predicted_values


class MAPredict(object):
    def __init__(self, window):
        self.window = window

    def forecast(self, input_values, predict_num):

        if len(input_values) < self.window:
            self.window = len(input_values)

        input_series = pandas.Series(data=input_values)
        ma = input_series.iloc[-self.window:].mean()

        predicted_values = [ma for i in range(predict_num)]

        ma_resource_gauge.set(ma)

        return predicted_values


class EMAPredict(object):
    def __init__(self, window):
        self.window = window

    def forecast(self, input_values, predict_num):
        if len(input_values) < self.window:
            self.window = len(input_values)

        input_series = pandas.Series(data=input_values)
        ema = input_series.ewm(span=10, min_periods=self.window).mean().to_list()
        predicted_value = ema[len(ema) - 1]

        ema_resource_gauge.set(predicted_value)

        return [predicted_value for i in range(predict_num)]


if __name__ == '__main__':
    start_http_server(8000)
    arima_resource_gauge.set(0)
    ma_resource_gauge.set(0)
    ema_resource_gauge.set(0)
    arima_resource_avg_smape_gauge.set(0)
    ma_resource_avg_smape_gauge.set(0)
    ema_resource_avg_smape_gauge.set(0)
    Controller(predict_model=ARIMAPredict(ar=4, ir=0, ma=2)).start()

