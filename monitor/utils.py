# -*- coding: utf-8 -*-
import os
import logging
import requests

def dingding_send_msg(url, msg, phones, isAtAll=True):
    data = {
        "msgtype": "text",
        "text": {
            "content": content
        },
        "at": {
            "atMobiles": phones,
            "isAtAll": isAtAll
        }
    }
    message = json.dumps(data)
    header = {"content-type": "application/json"}
    msg = json.dumps(message) if isinstance(message, dict) else str(message)
    try:
        req = requests.post(url, data=msg, headers=header)
        ret = json.loads(req.text)
        if ret.get("errcode") == 0 and ret.get("errmsg") == "ok":
            #sysLog().info('send alarm!!!')
            logger(log_path='log/ding.log', console=False).info("send msg...")
            return True
    except Exception as err:
        return None

def logger(name="root", log_level=logging.INFO, console=True, log_path=""):
    fmt = "%(asctime)-15s %(levelname)s %(module)s %(message)s"
    formatter = logging.Formatter(fmt)
    if console:
        handler = logging.StreamHandler()
    else:
        handler = logging.FileHandler(log_path)
    handler.setFormatter(formatter)
    _logger = logging.getLogger(name)
    _logger.setLevel(log_level)
    _logger.addHandler(handler)
    return _logger
