#!/usr/bin/python3

import tornado.web
import redis
import json
import keys
import shunlu_config

charset = "utf-8"

# 这里只会处理主动关闭的订单

class FinishOrderService(object):
    def __init__(self):
        self.rds = redis.StrictRedis(shunlu_config.redis_ip, shunlu_config.redis_port)

    def finish_order(self, orderid, operatorid):
        orderid = str(orderid)
        print(orderid)

        json_str = self.rds.get(orderid).decode(charset)
        json_obj = json.loads(json_str)
        worker_id = json_obj["worker_id"]
        master_id = json_obj["master_id"]

        if operatorid == worker_id:
            if self.rds.sismember("doing", orderid) :
                self.rds.srem("doing", orderid)
                self.rds.sadd("worker_confirmed", orderid)
            else:
                return -1
            json_obj["status"] = 5
        elif operatorid == master_id:
            if self.rds.sismember("worker_confirmed", orderid) :
                self.rds.srem("worker_confirmed", orderid)
                self.rds.sadd("finished", orderid)
            elif self.rds.sismember("doing", orderid):
                self.rds.srem("doing", orderid)
                self.rds.sadd("finished", orderid)
            else:
                return -1
            json_obj["status"] = 6
            self.rds.srem("worker"+str(worker_id), orderid)
            self.rds.srem("master"+str(master_id), orderid)
            self.rds.sadd("finished"+str(worker_id), orderid)
            self.rds.sadd("finished"+str(master_id), orderid)

        self.rds.set(orderid, json.dumps(json_obj))
        return 1

class FinishOrderHandler(tornado.web.RequestHandler):
    service = FinishOrderService()
    def get(self):
        orderid = self.get_argument("order_id")
        operatorid = self.get_argument("user_id") #操作人id，需要判断操作人是 worker 还是 master
        ret = self.service.finish_order(orderid, operatorid)
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        result = {"result": ret}
        self.write(json.dumps(result))


        
