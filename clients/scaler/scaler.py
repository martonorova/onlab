import requests
import os

prometheus_url = "http://localhost:9090/api/v1/query?query="

wait_time_before_start = 10

def start():
    os.system('cd ..; cd ..; pwd')
    # os.system('cd ..')
    # os.system('pwd')
    # os.system('docker-compose images')



def get_metrics():
    arima_prediction = requests.get(
        prometheus_url + "ARIMA_predicted_active_worker_threads")
    arima_prediction = int(arima_prediction.json().get('data').get('result')[0].get('value')[1])

    metrics_dict = dict()
    metrics_dict['arima'] = arima_prediction

    return metrics_dict



if __name__ == '__main__':
    start()