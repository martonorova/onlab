import requests
import os
import time
import operator
import math

prometheus_url = "http://localhost:9090/api/v1/query?query="
scaling_url = "http://localhost:8080/setPoolSize?poolSize="

wait_time_before_start = 10
scaling_interval = os.getenv("SCALING_INTERVAL", 10)


def start():
    time.sleep(scaling_interval)
    while True:
        metrics_dict = get_metrics()
        print(metrics_dict)
        decisive_pred_value = metrics_dict.get('decisive_predict')
        if decisive_pred_value > 0:

            requests.get(scaling_url + str(int(math.ceil(decisive_pred_value * 1.05))))
        else:
            max_value = float(max(metrics_dict.items(), key=operator.itemgetter(1))[0])
            requests.get(scaling_url + str(int(math.ceil(max_value * 1.05))))

        time.sleep(scaling_interval)


def get_metrics():
    arima_prediction = requests.get(
        prometheus_url + "ARIMA_predicted_active_worker_threads")
    print(arima_prediction.json())
    arima_prediction = int(math.ceil(float(arima_prediction.json().get('data').get('result')[0].get('value')[1])))

    ma_prediction = requests.get(
        prometheus_url + "MA_predicted_active_worker_threads"
    )
    ma_prediction = int(math.ceil(float(ma_prediction.json().get('data').get('result')[0].get('value')[1])))

    ema_prediction = requests.get(
        prometheus_url + "EMA_predicted_active_worker_threads"
    )
    ema_prediction = int(math.ceil(float(ema_prediction.json().get('data').get('result')[0].get('value')[1])))

    decisive_prediction = requests.get(
        prometheus_url + "prediction_decisive"
    )
    decisive_prediction = int(math.ceil(float(decisive_prediction.json().get('data').get('result')[0].get('value')[1])))

    metrics_dict = dict()
    metrics_dict['arima_predict'] = arima_prediction
    metrics_dict['ma_predict'] = ma_prediction
    metrics_dict['ema_predict'] = ema_prediction
    metrics_dict['decisive_predict'] = decisive_prediction

    return metrics_dict


if __name__ == '__main__':
    start()
