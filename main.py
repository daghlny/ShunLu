#!/usr/bin/python3

import tornado.ioloop
import tornado.web
import redis
import json
import keys
import FinishOrder

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

        other_orders_keys  = self.rds.sdiff(keys.pending_orders_k, worker_key, master_key)
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
        worker_orders_array, master_orders_array, other_orders_array = self.service.getOrders(userid)

        worker_orders_str = "["
        master_orders_str = "["
        other_orders_str  = "["

        for i in range(0, len(worker_orders_array)):
            if i == 0:
                worker_orders_str += worker_orders_array[i]
            else:
                worker_orders_str += ","+worker_orders_array[i]

        for i in range(0, len(master_orders_array)):
            if i == 0:
                master_orders_str += master_orders_array[i]
            else:
                master_orders_str += ","+master_orders_array[i]

        for i in range(0, len(other_orders_array)):
            if i == 0:
                other_orders_str += other_orders_array[i]
            else:
                other_orders_str += ","+other_orders_array[i]

        worker_orders_str += "]"
        master_orders_str += "]"
        other_orders_str  += "]"
            
        result = "{\"my_worker_orders\": "+worker_orders_str+", " + "\"my_master_orders\": "+master_orders_str+", " + "\"other_orders\": "+other_orders_str+"}"

        print(result)
        print("------------------------------------------")
        print(json.dumps(json.loads(result)))
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        self.write(json.dumps(result))
        

def make_app():
    return tornado.web.Application([
        (r"/orders", OrdersHandler),
        (r"/finish_order", FinishOrder.FinishOrderHandler)
    ])


if __name__ == "__main__":
    app = make_app()
    app.listen(8011)
    tornado.ioloop.IOLoop.current().start()

