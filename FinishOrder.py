#!/usr/bin/python3

import tornado.ioloop
import tornado.web
import redis
import json
import keys

charset = "utf-8"

class FinishOrderService(object):
    def __init__(self):
        self.rds = redis.StrictRedis("localhost", 6379)

    def finish_order(self, orderid):
        if self.rds.sismember("doing", orderid):
            self.rds.srem("doing", orderid)
        elif self.rds.sismember("worker_confirmed", orderid):
            self.rds.srem("worker_confirmed", orderid)
        else:
            return -1
        self.rds.sadd("finished", orderid)
        json_str = self.rds.get(orderid)
        json_obj = json.loads(json_str)
        worker_id = json_obj["worker_id"]
        master_id = json_obj["master_id"]
        self.rds.srem("worker"+str(worker_id), orderid)
        self.rds.srem("master"+str(master_id), orderid)
        self.rds.sadd("finished"+str(worker_id), orderid)
        self.rds.sadd("finished"+str(master_id), orderid)   
        return 0

class FinishOrderHandler(tornado.web.RequestHandler):
    service = OrdersService()
    def get(self):
        userid = self.get_argument("order_id")
        ret = self.service.finish_order(orderid)
        self.set_header("Content-Type", "application/text; charset=UTF-8")
        self.write(str(ret))
        
