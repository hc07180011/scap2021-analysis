import time
import json
import requests
import numpy as np
import matplotlib.pyplot as plt


market_name = "BTC-PERP"
base_url = "https://ftx.com/api/markets/{}/candles".format(market_name)

req_args = {
    "resolution": "300",
    "start_time": time.mktime(time.strptime('2021-01-01 00:00:00', '%Y-%m-%d %H:%M:%S')),
    "end_time": time.mktime(time.strptime('2021-07-01 23:59:59', '%Y-%m-%d %H:%M:%S'))
}

respond = requests.get(base_url, params=req_args)
history_data = json.loads(respond.text)["result"]
history_price = list([x["close"] for x in history_data])


def moving_average(a, n):
    ret = np.cumsum(a, dtype=float)
    ret[n:] = ret[n:] - ret[:-n]
    return ret[n - 1:] / n


def plot_history(price):
    plt.figure(figsize=(16, 4), dpi=200)
    plt.plot(price)
    plt.plot(moving_average(price, 12)) # 1 hour
    plt.plot(moving_average(price, 60)) # 5 hour
    plt.legend(["Price", "MA12", "MA60"])
    plt.savefig("history.png")


plot_history(history_price)

sma_len = 12
lma_len = 60
short_ma = moving_average(history_price, sma_len)
long_ma = moving_average(history_price, lma_len)

asset = 10000.0
stock = 0.0
fee = 0.0145 * 0.01

for i, j in zip(range(lma_len, len(history_price) - 1), range(len(history_price) - lma_len - 1)):
    if short_ma[j] < long_ma[j] and short_ma[j + 1] > long_ma[j + 1]: # golden
        if asset:
            stock = (asset / history_price[i]) * (1 - fee)
            asset = 0.0
    if short_ma[j] > long_ma[j] and short_ma[j + 1] < long_ma[j + 1]: # death
        if stock:
            asset = (stock * history_price[i]) * (1 - fee)
            stock = 0.0

print("Final asset: {}".format(asset + stock * history_price[-1] * (1 - fee)))
