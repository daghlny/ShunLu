#!/usr/bin/python3

import tornado.web
import redis
import json
import keys
import shunlu_config

charset = "utf-8"

class ShunluPayService(object):
    def __init__(self):
        self.rds = redis.StrictRedis(shunlu_config.redis_ip, shunlu_config.redis_port)

    def shunluPay(self, userid, total_fee, orderid):
        if not self.rds.exists("user" + str(userid)):
            return -1
        balance = self.rds.hget("user"+str(userid), "balance")
        if(total_fee < 0):
            return -2
        if total_fee <= balance:
            balance -= total_fee
            json_str = self.rds.get(orderid).decode(charset)
            json_obj = json.loads(json_str)
            json_obj["status"] = 2
            str_userid = "user" + str(userid)
            self.rds.set(orderid, json.dump(json_obj))
            self.set(str_userid, user_json_obj)
            self.rds.sadd(keys.pending_orders_k, orderid)
            self.rds.sadd(keys.master_k_prefix+str(userid), orderid)
            return 1
        else:
            return 0

class ShunluPayHander(tornado.web.RequestHandler):
    service = ShunluPayService()

    def post(self):
        userid    = self.get_argument("user_id")
        total_fee = int(self.get_argument("money"))
        orderid   = str(self.get_argument("order_id"))
        pay_result = self.service.shunluPay(userid, total_fee, orderid)
        result = {"result": pay_result}
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        self.write(json.dumps(result))

