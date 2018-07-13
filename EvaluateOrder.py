#!/usr/bin/python3

import tornado.web
import redis
import json
import shunlu_config

charset = "utf-8"

class EvaluateOrdersService(object):
    def __init__(self):
        self.rds = redis.StrictRedis(shunlu_config.redis_ip, shunlu_config.redis_port)

    def setEvaluateOrder(self, orderid, aspect, score):
        order_key  = str(orderid)
        aspect_key = str(aspect)
        score_key  = int(score)

        order_str = self.rds.get(order_key).decode(charset)
        order_obj = json.loads(order_str)
        if aspect_key == '0':
            order_obj['worker_score'] = score_key
        elif aspect_key == '1':
            order_obj['master_score'] = score_key
        re = self.rds.set(order_key, json.dumps(order_obj))
        if re:
            return 1
        else:
            return -1

class EvaluateOrdersHandler(tornado.web.RequestHandler):
    service = EvaluateOrdersService()
    def get(self):
        orderid = self.get_argument("order_id")
        aspect = self.get_argument("aspect")
        score = self.get_argument("score")

        result_json = self.service.setEvaluateOrder(orderid, aspect, score)

        result = {
            "result" : result_json
        }

        self.set_header("Content-Type", "application/json; charset=UTF-8")
        self.write(json.dumps(result))

        return result


