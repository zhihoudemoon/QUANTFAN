# -*- coding: utf-8 -*-

import os
import time
import math
from binance.client import Client
import pandas as pd


def stamp2strtime(timestamp):
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))


class fetchKline(object):
    """
    fetch kline by biance
    resize kline to generate new one
    """
    BINANCE_APIKEY = "vmPUZE6mv9SD5VNHk4HlWFsOr6aKE2zvsw0MuIgwCIPy6utIco14y7Ju91duEh8A"
    BINANCE_SECRETSKEY = "NhqPtmdSJYdKjVHjA7PZj4Mge3R5YNiP1e3UZjInClVN65XAbvqqM6A7H5fATj0j"

    def __init__(self, symbol, resize_params, days=1, period=None, freq=None, begin_start=False, file_dir="hq", show=False):
        self.symbol = symbol
        self._cahe = {}
        self._begin_start = begin_start
        self._file_dir = file_dir
        self._show = show
        self.result = None
        if period is not None:
            self._cahe['start'] = period[0]
            self._cahe['end'] = period[-1]
        else:
            self._cahe['days'] = days
        self._resize_start, self._resize_max, self._resize_min = resize_params
        if freq == "5min":
            self.freq = Client.KLINE_INTERVAL_5MINUTE
        elif freq == "1hour":
            self.freq = Client.KLINE_INTERVAL_1HOUR
        else:
            self.freq = Client.KLINE_INTERVAL_1MINUTE

    @property
    def plot(self):
        if self.result is None:
            print("non data to plot!")
            return None
        self.result['price'].plot()
        return None

    def save(self):
        if self.result is None:
            print("non data to save!")
            return None
        file_name = 'reszie_' + str(int(time.time())) + '.csv'
        self.result.to_csv(os.path.join(self._file_dir, file_name),index=None)
        return None

    def resize(self, symbol=None, period=None, resizes=None):
        self.result = self._resize_kline(self._fetch_kline(symbol, period), resizes)
        return None

    def fetch_kline(self, symbol="", period="", save=False):
        df = self._fetch_kline(symbol, period)
        if save:
            file_name = 'hq_' + str(int(time.time())) + '.csv'
            df.to_csv(os.path.join(self._file_dir, file_name),index=None)
            return None
        else:
            return df

    def _fetch_kline(self, symbol=None, period=None):
        _client = Client(self.BINANCE_APIKEY, self.BINANCE_SECRETSKEY)
        if symbol is None:
            _symbol = self.symbol
        else:
            _symbol = symbol

        if period is None:
            if self._cahe.get('days', ''):
                dayStr = "{} day ago UTC".format(self._cahe['days'])
                klines = _client.get_historical_klines(_symbol, self.freq, dayStr)
            else:
                klines = _client.get_historical_klines(_symbol, self.freq, self._cahe['start'], self._cahe['end'])
        else:
            klines = _client.get_historical_klines(_symbol, self.freq, period[0], period[-1])

        klineDf = pd.DataFrame(klines, columns=None)
        klineDf = klineDf[[0,1,2,3,4,5]]
        klineDf.columns = ['timestamp', 'Open', 'High', 'Low', 'Close', 'Volume']
        klineDf['timestamp'] = klineDf['timestamp'] / 1000
        klineDf['Date Time'] = klineDf['timestamp'].apply(stamp2strtime)
        klineDf = klineDf[['Date Time', 'Open', 'High', 'Low', 'Close', 'Volume']]
        return klineDf

    def _resize_kline(self, df, resizes=None):
        column_len = len(df.columns)
        if column_len == 1:
            df_ts = df
        else:
            df.columns = ['time', 'open', 'high', 'low', 'close', 'volume']
            df_ts = df[['time', 'close']]
            df_ts.columns = ['time', 'price']
            df_ts['price'] = df_ts['price'].apply(float)
            df_start = df_ts['price'][0]
            df_max = max(df_ts['price'])
            df_min = min(df_ts['price'])
            if resizes is not None:
                target_start, target_max, target_min = resizes
            else:
                target_start, target_max, target_min = self._resize_start, self._resize_max, self._resize_min
            bs = (target_max - target_min) / (df_max - df_min)
            if self._begin_start:
                diff = target_max - df_start * bs
                df_ts['price'] = df_ts['price'] * bs + diff
            else:
                diff = target_min - df_min * bs
                df_ts['price'] = df_ts['price'] * bs + diff
        return df_ts


if __name__ == '__main__':
    resizes = (0.0001512, 0.00015999, 0.00015000)
    binance_kline = fetchKline(symbol="ZILETH",
                               period=('17 Oct, 2018','25 Oct, 2018'),
                               resize_params=resizes)
    binance_kline.resize()
    binance_kline.save()
