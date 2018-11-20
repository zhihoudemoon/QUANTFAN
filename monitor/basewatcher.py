# -*- coding: utf-8 -*-
import json
import time
import threading
from utils import logger

class watcher(object):
    def __init__(self, config_path):
        self._config_path = config_path
        self._last_nonce = 0


    def start(self):
        self._parse_config()
        self._send_msg()
        self._update_worker = threading.Thread(target=self._update_config)
        self._update_worker.daemon = True
        self._update_worker.start()
        self._logger.info('watcher for {symbol} config update worker start...'.format(self.symbol))


    def fetch_market_price(self, symbol):
        return (0.0, 0.0)


    def _send_msg(self):
        symbol_threads = []
        for symbol in self.symbols:
            t = threading.Thread(target=_generate_msg, args=(symbol))
            t.daemon = True
            t.start()
            self._logger.info('watcher for {symbol} worker start...'.format(symbol))


    def _parse_config(self):
        with open(self._config_path) as conf:
            config = json.load(conf)
            self.symbols = config['symbols']
            self.url = config['url']
            self._monitor_value = config['monitor_value']
            self._time_limit = config['time_limit']
            self._logger = logger(config['log_path'])


    def _generate_msg(self, symbol):
        last_price = 0.0
        while True:
            try:
                bid, ask = self.fetch_market_price(symbol)
                lastest_price = (bid + ask) / 2.0
                if last_price != 0.0:
                    move_precent = round(((lastest_price - last_price) / lastest_price)*100, 3)
                    last_price = lastest_price
                    if move_precent > self._monitor_value:
                        msg = "{symbol}\n最新价格: {price}\n{period}秒价格上涨{precent}".format(symbol=str(symbol),
                                                                                             price=str(lastest_price),
                                                                                             period=str(self._time_limit),
                                                                                             precent=str(move_precent))
                        #self._send_func(msg)
                        self._logger.info(msg)
                    elif move_precent < -self._monitor_value:
                        msg = "{symbol}\n最新价格: {price}\n{period}秒价格下跌{precent}".format(symbol=str(symbol),
                                                                                             price=str(lastest_price),
                                                                                             period=str(self._time_limit),
                                                                                             precent=str(move_precent))
                        #self._send_func(msg)
                        self._logger.info(msg)
                else:
                    last_price = lastest_price
                time.sleep(self._time_limit)
            except Exception as e:
                self._logger.error(str(e))
                time.sleep(self._time_limit)

    def _update_config(self):
        while True:
            try:
                with open(self._config_path) as conf:
                    config = json.load(conf)
                    nonce = config['nonce']
                    if self._last_nonce != nonce:
                        self._monitor_value = config['monitor_value']
                        self._time_limit = config['time_limit']
                        self._last_nonce += 1
                time.sleep(10)
            except Exception as e:
                self._logger.error(str(e))
                time.sleep(10)
