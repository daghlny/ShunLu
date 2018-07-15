#!/usr/bin/python3

import tornado.web
import redis
import json
import keys
import shunlu_config
import FinishOrder

charset = "utf-8"

class OrdersService(object):
    def __init__(self):
        self.rds = redis.StrictRedis(shunlu_config.redis_ip, shunlu_config.redis_port)

    def getOrders(self, userid):

        other_orders = list()
        worker_orders = list()
        master_orders = list()
        canceled_orders = list()

        worker_key = keys.worker_k_prefix + str(userid)
        master_key = keys.master_k_prefix + str(userid)
        canceled_key = keys.canceled_k_prefix + str(userid)

        other_orders_keys  = self.rds.sdiff(keys.pending_orders_k, worker_key, master_key)
        worker_orders_keys = self.rds.smembers(worker_key)
        master_orders_keys = self.rds.smembers(master_key)
        canceled_orders_keys = self.rds.smembers(canceled_key)

        print("other: ", end="")
        for key in other_orders_keys:
            key = key.decode(charset)
            print(str(key)+" ", end=" ")
            json_obj = json.loads(self.rds.get(key).decode(charset))
            json_obj["order_id"] = key
            other_orders.append(json_obj)
        print(" | ", end="")

        print("worker: ", end="")
        for key in worker_orders_keys:
            key = key.decode(charset)
            print(str(key)+" ", end=" ")
            json_obj = json.loads(self.rds.get(key).decode(charset))
            json_obj["order_id"] = key
            worker_orders.append(json_obj)
        print(" | ", end="")

        print("master: ", end="")
        for key in master_orders_keys:
            key = key.decode(charset)
            print(str(key)+" ", end=" ")
            json_obj = json.loads(self.rds.get(key).decode(charset))
            json_obj["order_id"] = key
            master_orders.append(json_obj)
        print(" | ", end="")

        print("canceled: ", end="")
        for key in canceled_orders_keys:
            key = key.decode(charset)
            print(str(key)+" ", end=" ")
            json_obj = json.loads(self.rds.get(key).decode(charset))
            json_obj["order_id"] = key
            canceled_orders.append(json_obj)
        print(" ")

        return worker_orders, master_orders, other_orders, canceled_orders
   

class OrdersHandler(tornado.web.RequestHandler):
    service = OrdersService()
    def get(self):
        userid = self.get_argument("user_id")
        worker_orders_array, master_orders_array, other_orders_array, canceled_orders_array = self.service.getOrders(userid)
        print("Get a request of OrderList user_id="+userid)

        #for i in range(0, len(worker_str_array)):
        #    worker_orders_array.append(json.loads(worker_str_array[i]))

        #for i in range(0, len(master_str_array)):
        #    master_orders_array.append(json.loads(master_str_array[i]))

        #for i in range(0, len(other_str_array)):
        #    #print(other_str_array[i])
        #    other_orders_array.append(json.loads(other_str_array[i]))

        #for i in range(0, len(canceled_str_array)):
        #    canceled_orders_array.append(json.loads(canceled_str_array[i]))

            
        #result = "{\"my_worker_orders\": "+worker_orders_str+", " + "\"my_master_orders\": "+master_orders_str+", " + "\"other_orders\": "+other_orders_str+"}"
        result = {
            "my_worker_orders": worker_orders_array,
            "my_master_orders": master_orders_array,
            "my_canceled_orders": canceled_orders_array,
            "other_orders": other_orders_array
        }

        self.set_header("Content-Type", "application/json; charset=UTF-8")
        self.write(json.dumps(result))

