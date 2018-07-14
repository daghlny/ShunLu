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
        user_json_str = self.rds.get("user" + str(userid))
        user_json_obj = json.loads(user_json_str)
        balance = user_json_obj["balance"]
        if(total_fee < 0):
            return -2
        if total_fee <= balance:
            user_json_obj["balance"] = balance - total_fee
            if not self.rds.exists("user" + str(userid)):
                return -1
            else:
                orderid = str(orderid)
                json_str = self.rds.get(orderid).decode(charset)
                json_obj = json.loads(json_str)
                json_obj["status"] = 2
                pipe = self.rds.pipeline()
                try:
                    order_lock = keys.newest_k + str(order_id)
                    str_userid = "user" + str(userid)
                    pipe.watch(order_lock)
                    pipe.set(order_lock, 1)
                    pipe.set(orderid, json.dump(json_obj))
                    pipe.set(str_userid, user_json_obj)
                    pipe.sadd(keys.pending_orders_k, orderid)
                    pipe.sadd(keys.master_k_prefix+str(userid), orderid)
                    pipe.set(order_lock, 0)
                    pipe.execute()
                    return 1
                except Exception:
                    print("Pay error")
                    return -1
        else:
            return 0

class ShunluPayHander(tornado.web.RequestHandler):
    service = ShunluPayService()

    def post(self):
        userid = self.get_argument("user_id")
        total_fee = int(self.get_argument("money"))
        orderid = str(self.get_argument("order_id"))
        pay_result = self.service.shunluPay(userid, total_fee, orderid)
        result = {"result":pay_result}
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        self.write(json.dumps(result))

