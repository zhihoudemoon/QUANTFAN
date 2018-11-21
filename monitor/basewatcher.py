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
        _threads = self._dispatcher()
        update_worker = threading.Thread(target=self._update_config, name="update worker")
        _threads.append(update_worker)

        for each_thread in _threads:
            each_thread.daemon = True
            each_thread.start()
            self._logger.info("{0} start...".format(each_thread.name))

        # runforever
        while True:
	    pass


    def fetch_market_price(self, symbol):
        return (0.0, 0.0)


    def send_msg(self, message):
        self._logger.info(message)


    def _dispatcher(self):
        threads = []
        for symbol in self.symbols:
            t = threading.Thread(target=self._generate_msg, args=(symbol,), name="{0} watcher".format(symbol))
            threads.append(t)
        return threads


    def _parse_config(self):
        with open(self._config_path) as conf:
            config = json.load(conf)
            self.symbols = config['symbols']
            self.url = config['url']
            self._monitor_value = config['monitor_value']
            self._time_limit = config['time_limit']
            self._send_func_dict = config['send']
            self.debug = config['debug']
            if self.debug:
                self._logger = logger()
            else:
                self._logger = logger(config['log_path'])


    def _generate_msg(self, symbol):
        last_price = 0.0
        while True:
            bid, ask = self.fetch_market_price(symbol)
            lastest_price = (bid + ask) / 2.0
            if last_price != 0.0:
                move_precent = round(((lastest_price - last_price) / lastest_price)*100, 3)
                last_price = lastest_price
                if move_precent > (self._monitor_value * 100):
                    msg = "{symbol}\n最新价格: {price}\n{period}秒价格上涨{precent}%".format(symbol=str(symbol),
                                                                                          price=str(lastest_price),
                                                                                          period=str(self._time_limit),
                                                                                          precent=str(move_precent))
                    self.send_msg(msg)
                elif move_precent < -(self._monitor_value * 100):
                    msg = "{symbol}\n最新价格: {price}\n{period}秒价格下跌{precent}%".format(symbol=str(symbol),
                                                                                          price=str(lastest_price),
                                                                                          period=str(self._time_limit),
                                                                                          precent=str(move_precent))
                    self.send_msg(msg)
            else:
                last_price = lastest_price
            time.sleep(self._time_limit)

    def _update_config(self):
        while True:
            with open(self._config_path) as conf:
                config = json.load(conf)
                nonce = config['nonce']
                if self._last_nonce != nonce:
                    self._monitor_value = config['monitor_value']
                    self._time_limit = config['time_limit']
                    self._last_nonce += 1
            time.sleep(10)
