#!/usr/bin/python3

import tornado.web
import redis
import json
import keys
import shunlu_config
import FinishOrder

charset = "utf-8"

class NotifyHandler(tornado.web.RequestHandler):
    def get(self):
        pass
