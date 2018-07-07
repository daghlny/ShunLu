#!/usr/bin/python3

import tornado.ioloop
import tornado.web
import redis
import json
import keys

charset = "utf-8"

class OrdersService(object):
    def __init__(self):
        self.rds = redis.StrictRedis("localhost", 6379)

    def getOrders(self, userid):

        other_orders = list()
        worker_orders = list()
        master_orders = list()

        worker_key = keys.worker_k_prefix + str(userid)
        master_key = keys.master_k_prefix + str(userid)

        other_orders_keys = self.rds.sdiff(keys.pending_orders_k, worker_key, master_key)
        worker_orders_keys = self.rds.smembers(worker_key)
        master_orders_keys = self.rds.smembers(master_key)

        for key in other_orders_keys:
            other_orders.append(self.rds.get(key).decode(charset))
        for key in worker_orders_keys:
            worker_orders.append(self.rds.get(key).decode(charset))
        for key in master_orders_keys:
            master_orders.append(self.rds.get(key).decode(charset))

        return worker_orders, master_orders, other_orders
   

class OrdersHandler(tornado.web.RequestHandler):
    service = OrdersService()
    def get(self):
        userid = self.get_argument("user_id")
        my_worker_orders, my_master_orders, my_other_orders = self.service.getOrders(userid)

        worker_orders = list()
        master_orders = list()
        other_orders  = list()

        for order_str in my_worker_orders:
            order_obj = json.loads(order_str)
            worker_orders.append(order_obj)
        for order_str in my_master_orders:
            order_obj = json.loads(order_str)
            master_orders.append(order_obj)
        for order_str in other_orders:
            order_obj = json.loads(order_str)
            other_orders.append(order_obj)
            
        result = {
            "my_worker_orders": worker_orders,
            "my_master_orders": master_orders,
            "other_orders": other_orders
        }
        print(result)
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        self.write(json.dumps(result))
        

def make_app():
    return tornado.web.Application([
        (r"/orders", OrdersHandler),
    ])


if __name__ == "__main__":
    app = make_app()
    app.listen(8011)
    tornado.ioloop.IOLoop.current().start()

