# -*- coding: utf-8 -*-
import json
import time
import threading
from utils import logger

class watcher(object):
    def __init__(self, config_path):
        self._config_path = config_path
        self._bid = 0.0
        self._ask = 0.0
        self._last_price = 0.0

    def start(self):
        self._parse_config()
        self._update_worker = threading.Thread(target=self._update_config)
        self._send_worker = threading.Thread(target=self._send_msg)
        self._update_worker.daemon = True
        self._send_worker.daemon = True
        self._send_worker.start()
        self._logger.info('watcher for {symbol} worker start...'.format(self.symbol))
        self._update_worker.start()
        self._logger.info('watcher for {symbol} config update worker start...'.format(self.symbol))


    def fetch_market_price(self):
        pass

    def _parse_config(self):
        with open(self._config_path) as conf:
            config = json.load(conf)
            self.symbol = config['symbol']
            self.url = config['url']
            self._monitor_value = config['monitor_value']
            self._time_limit = config['time_limit']
            self._logger = logger(config['log_path'])

    def _send_msg(self):
        while True:
            try:
                self.fetch_market_price()
                lastest_price = (self._bids + self._asks) / 2.0
                if self._last_price != 0.0:
                    move_precent = round(((lastest_price - self._last_price) / lastest_price)*100, 3)
                    self._last_price = lastest_price
                    if move_precent > self._monitor_value:
                        msg = "{symbol}\n最新价格: {price}\n{period}秒价格上涨{precent}".format(symbol=str(symbol),
                                                                                             price=str(lastest_price),
                                                                                             period=str(self._time_limit),
                                                                                             precent=str(move_precent))
                        self._send_func(msg)
                    elif move_precent < -self._monitor_value:
                        msg = "{symbol}\n最新价格: {price}\n{period}秒价格下跌{precent}".format(symbol=str(symbol),
                                                                                             price=str(lastest_price),
                                                                                             period=str(self._time_limit),
                                                                                             precent=str(move_precent))
                        self._send_func(msg)
                else:
                    self._last_price = lastest_price
                time.sleep(self._time_limit)
            except Exception as e:
                self._logger.error(e)
                time.sleep(self._time_limit)

    def _update_config(self):
        while True:
            try:
                last_nonce = 0
                with open(self._config_path) as conf:
                    config = json.load(conf)
                    nonce = config['nonce']
                    if last_nonce != nonce:
                        self._monitor_value = config['monitor_value']
                        self._time_limit = config['time_limit']
                time.sleep(10)
            except Exception as e:
                self._logger.error(e)
                time.sleep(10)
