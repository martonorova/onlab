import os
import requests
from pandas import read_csv
import time


webapp_url = os.getenv("ONLAB_WEBAPP_URL", "http://localhost:8080/time")


def load_input_data_series(pattern_row):
    data_frame = read_csv('data/train_1_row_1.csv', header=0, index_col=0)
    return data_frame.iloc[pattern_row]


def start():
    pattern_row = 0
    series = load_input_data_series(pattern_row)

    # generate load
    print("START")
    interval = 10  # 10 seconds

    for i in range(series.size):
        start_time = time.time()
        request_num = int(series.iloc[i])
        time_to_wait = interval / request_num
        print("TIME TO WAIT " + str(time_to_wait))

        for j in range(request_num):
            requests.get(webapp_url)
            time.sleep(time_to_wait)

        end_time = time.time()
        time_delta = end_time - start_time
        print("TIME_DELTA " + str(time_delta))
        if time_delta < interval:
            time.sleep(interval - time_delta)


if __name__ == '__main__':
    start()
