import os
import requests
import numpy as np
import pandas
import time
import math
from statsmodels.tsa.arima_model import ARIMA
# import matplotlib.pyplot as plt
# import matplotlib as mpl
from prometheus_client import Gauge, start_http_server

webapp_url = os.getenv("ONLAB_WEBAPP_URL", "http://webapp:8080/time")
time_before_pred_start = int(os.getenv("TIME_BEFORE_PRED_START", 10))
prediction_interval = int(os.getenv("PREDICTION_INTERVAL", 30))

arima_gauge = Gauge('ARIMA_predicted_active_worker_threads', 'Predicted values by ARIMA modell')


class Controller(object):

    predicted_values = list()  # holds the predicted values for the next iteration to calculate error
    predictions_num = 0  # how many times did the prediction has run so far
    average_smape = 0
    smape_samples_num = 0

    predicted_values_to_plot = list()
    actual_values_to_plot = list()
    should_draw_plot = False

    def __init__(self, predict_model, should_draw_plot):
        self.predict_model = predict_model
        self.should_draw_plot = should_draw_plot

    def calculate_avg_smape(self, new_smape):
        if not math.isnan(new_smape):
            new_avg_smape = (self.average_smape * self.smape_samples_num + new_smape) / (self.smape_samples_num + 1)
            self.smape_samples_num += 1
            self.average_smape = new_avg_smape

    def save_values_to_plot(self, predicted_list, actual_list):
        assert len(predicted_list) == len(actual_list)
        length = len(predicted_list)

        for i in range(length):
            # next_pred_value = predicted_list[i]
            # if math.isnan(next_pred_value):
            #     self.predicted_values_to_plot.append()
            self.predicted_values_to_plot.append(predicted_list[i])
            self.actual_values_to_plot.append(actual_list[i])

    def draw_plot(self):
        pass
        # mpl.rcParams['lines.linewidth'] = 7
        # font = {
        #     'family': 'normal',
        #     'weight': 'bold',
        #     'size': 30,
        # }
        # mpl.rc('font', **font)
        #
        # predicted_series = pandas.Series(data=self.predicted_values_to_plot)
        # actual_series = pandas.Series(data=self.actual_values_to_plot)
        #
        # predicted_series.plot(legend=True, label='Predicted')
        # actual_series.plot(legend=True, label='Actual')
        #
        # plt.xlabel('time (s)')
        # plt.ylabel('active threads')
        #
        # if type(self.predict_model) is ARIMAPredict:
        #     title = 'ARIMA'
        # elif type(self.predict_model) is MAPredict:
        #     title = 'MA'
        # elif type(self.predict_model) is EMAPredict:
        #     title = 'EMA'
        #
        # plt.title(title)
        #
        # plt.draw()
        # plt.pause(1)
        # plt.clf()

    def start(self):
        print("START")
        time.sleep(time_before_pred_start)
        print("SLEEP_END")
        while True:
            print("IN LOOP")
            predict_start = time.time()

            print("PREDICT START: {}".format(time.ctime()))

            # TODO this in VARIABLE (prmetheus address)
            metrics = requests.get(
                "http://prometheus:9090/api/v1/query?query=active_worker_threads[{}s]".format(time_before_pred_start))
            metric_values = [int(record[1]) for record in metrics.json().get('data').get('result')[0].get('values')]
            print("Metric values: {} at {}".format(metric_values, time.ctime()))

            # check error of last prediction
            if len(self.predicted_values) != 0:
                previous_predicted_values = self.predicted_values
                actual_values = metric_values[-len(previous_predicted_values):]

                assert len(previous_predicted_values) == len(actual_values)

                smape_val = smape(previous_predicted_values, actual_values)

                self.save_values_to_plot(previous_predicted_values, actual_values)

                if self.should_draw_plot:
                    self.draw_plot()

                self.calculate_avg_smape(smape_val)

                print("Prev predicted: {}, Actual: {} || SMAPE: {}, AVG_SMAPE: {}".format(
                    previous_predicted_values,
                    actual_values,
                    smape_val,
                    self.average_smape
                ))

            try:
                self.predicted_values = self.predict_model.forecast(metric_values, prediction_interval)
            except Exception as e:
                print(e)

            predict_end = time.time()
            time_delta = predict_end - predict_start
            print("TIME_DELTA " + str(time_delta))
            if time_delta < prediction_interval:
                time.sleep(prediction_interval - time_delta)


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
        max_pred_value = -1
        for val in predicted_values:
            if val > max_pred_value:
                max_pred_value = val

        predicted_values = [max_pred_value for i in range(predict_num)]

        arima_gauge.set(max_pred_value)
        return predicted_values


class MAPredict(object):
    def __init__(self, window):
        self.window = window

    def forecast(self, input_values, predict_num):

        if len(input_values) < self.window:
            self.window = len(input_values)

        input_series = pandas.Series(data=input_values)
        ma = input_series.iloc[-self.window:].mean()

        return [ma for i in range(predict_num)]


class EMAPredict(object):
    def __init__(self, window):
        self.window = window

    def forecast(self, input_values, predict_num):
        if len(input_values) < self.window:
            self.window = len(input_values)

        input_series = pandas.Series(data=input_values)
        ema = input_series.ewm(span=10, min_periods=self.window).mean().to_list()
        predicted_value = ema[len(ema) - 1]
        return [predicted_value for i in range(predict_num)]


class MovingAveragePredict(object):
    input_values = list()
    # window

    def forecast(self, input_values, predict_num):
        input_series = pandas.Series(data=input_values)

        moving_avg = input_series.rolling(window=10).mean()

        predicted_values = [moving_avg for i in range(predict_num)]

        return predicted_values


if __name__ == '__main__':
    start_http_server(8000)
    Controller(predict_model=ARIMAPredict(ar=4, ir=0, ma=2),
               should_draw_plot=True).start()

