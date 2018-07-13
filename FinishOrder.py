#!/usr/bin/python3

import tornado.ioloop
import tornado.web
import redis
import json
import keys

charset = "utf-8"

# 这里只会处理主动关闭的订单

class FinishOrderService(object):
    def __init__(self):
        self.rds = redis.StrictRedis("localhost", 6379)

    def finish_order(self, orderid):
        orderid = str(orderid)
        print(orderid)
        # if the order is not in "doing" or "worker_confirmed" sets, there must exist an error
        if self.rds.sismember("doing", orderid):
            self.rds.srem("doing", orderid)
        elif self.rds.sismember("worker_confirmed", orderid):
            self.rds.srem("worker_confirmed", orderid)
        else:
            return -1
        self.rds.sadd("finished", orderid)
        json_str = self.rds.get(orderid).decode(charset)
        json_obj = json.loads(json_str)
        worker_id = json_obj["worker_id"]
        master_id = json_obj["master_id"]
        # set the status of order to "finished"
        json_obj["status"] = 6 
        # move the orderid from worker and master's "not finished" set to "finished" set
        self.rds.srem("worker"+str(worker_id), orderid)
        self.rds.srem("master"+str(master_id), orderid)
        self.rds.sadd("finished"+str(worker_id), orderid)
        self.rds.sadd("finished"+str(master_id), orderid)   
        return 1

class FinishOrderHandler(tornado.web.RequestHandler):
    service = FinishOrderService()
    def get(self):
        orderid = self.get_argument("order_id")
        ret = self.service.finish_order(orderid)
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        result = {"result": ret}
        self.write(json.dumps(result))


        
