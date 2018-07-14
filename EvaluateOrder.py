#!/usr/bin/python3

import tornado.web
import redis
import json
import shunlu_config

charset = "utf-8"

class EvaluateOrdersService(object):
    def __init__(self):
        self.rds = redis.StrictRedis(shunlu_config.redis_ip, shunlu_config.redis_port)

    def setEvaluateOrder(self, orderid, userid, score):
        orderid  = str(orderid)
        userid = str(userid)
        score  = int(score)

        json_obj = json.loads(self.rds.get(orderid).decode(charset))

        if userid == json_obj["worker_id"] :
            if self.rds.sismember("worker_confirmed", orderid):
                json_obj["worker_score"] = int(score)
            elif self.rds.sismember("finished", orderid):
                json_obj["worker_score"] = int(score)
            else:
                return -1
        elif userid == json_obj["master_id"] :
            if self.rds.sismember("finished", orderid):
                json_obj["master_score"] = int(score)
            else:
                return -1
        else:
            return -1
        self.rds.set(orderid, json.dumps(json_obj))
        return 1

class EvaluateOrdersHandler(tornado.web.RequestHandler):
    service = EvaluateOrdersService()
    def get(self):
        orderid = self.get_argument("order_id")
        userid = self.get_argument("user_id")
        score = self.get_argument("score")

        ret = self.service.setEvaluateOrder(orderid, userid, score)

        result = {}
        result["result"] = ret

        self.set_header("Content-Type", "application/json; charset=UTF-8")
        self.write(json.dumps(result))


