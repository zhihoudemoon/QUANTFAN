# -*- coding: utf-8 -*-
import os
import requests
from basewatcher import watcher
from utils import dingding_send_msg

class BinanceWathcher(watcher):
    """
    you need rewrite fetch_market_price & send_msg
    """
    def __init__(self, config_path):
        super(BinanceWathcher, self).__init__(config_path)
        self.exchange = 'biance'

    def __repr__(self):
        return "watcher: {exchange}".format(self.exchange)

    def send_msg(self, message):
        _url = "https://oapi.dingtalk.com/robot/send?access_token={0}".format(self._send_func_dict['ding_token'])
        _users = self._send_func_dict['phones']
        dingding_send_msg(url=_url, phones=_users, msg=message, isAtAll=False)


    def fetch_market_price(self, symbol):
        resp = requests.get(self.url % (symbol,))
        data = resp.json()
        if len(data["bids"]) == 0:
            bid = 0.0
        else:
            bid = float(data["bids"][0][0])
        if len(data["asks"]) == 0:
            ask = 0.0
        else:
            ask = float(data["asks"][0][0])
        return bid, ask


if __name__ == '__main__':
    config_path = os.path.join('config', 'binance.config')
    send_type = "dingding"
    binance_watcher = BinanceWathcher(config_path, send_type)
    binance_watcher.start()
