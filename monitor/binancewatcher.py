# -*- coding: utf-8 -*-
import os
import requests
from basewatcher import watcher

class BinanceWathcher(watcher):
    def __init__(self, config_path):
        super(BinanceWathcher, self).__init__(config_path)
        self.exchange = 'biance'

    def __repr__(self):
        return "watcher: {exchange}".format(self.exchange)

    def fetch_market_price(self):
        resp = requests.get(self.url)
        data = resp.json()
        self._bid = float(data["bids"][0][0])
        self._ask = float(data["asks"][0][0])


if __name__ == '__main__':
    config_path = os.path.join('config', 'binance.config')
    binance_watcher = BinanceWathcher(config_path)
    binance_watcher.start()
