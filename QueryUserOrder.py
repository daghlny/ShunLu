#!/usr/bin/python3

import tornado.ioloop
import tornado.web
import redis
import json
import keys

charset = "utf-8"


class QueryUserOrdersService(object):
    def __init__(self):
        self.rds = redis.StrictRedis("localhost", 6379)

    def getOrders(self, userid):

        useridInRedis = "user" + str(userid)
        # 用户不存在时的返回值, 待确定
        if ~self.rds.exists(useridInRedis):
            return [-1]

        finished_orders = list()
        worker_orders = list()
        master_orders = list()

        worker_key = keys.worker_k_prefix + str(userid)
        master_key = keys.master_k_prefix + str(userid)
        finished_key = keys.finished_k_predix + str(userid)

        worker_orders_keys = self.rds.smembers(worker_key)
        master_orders_keys = self.rds.smembers(master_key)
        finished_orders_keys = self.rds.smembers(finished_key)

        for key in worker_orders_keys:
            worker_orders.append(self.rds.get(key).decode(charset))
        for key in master_orders_keys:
            master_orders.append(self.rds.get(key).decode(charset))
        for key in finished_orders_keys:
            finished_orders.append(self.rds.get(key).decode(charset))

        return worker_orders, master_orders, finished_orders


class QueryUserOrdersHandler(tornado.web.RequestHandler):
    service = QueryUserOrdersService()

    def get(self):
        userid = self.get_argument("user_id")
        worker_orders_array, master_orders_array, finished_orders_array = self.service.getOrders(userid)

        worker_orders_str = "["
        master_orders_str = "["
        finished_orders_str = "["

        for i in range(0, len(worker_orders_array)):
            if i == 0:
                worker_orders_str += worker_orders_array[i]
            else:
                worker_orders_str += "," + worker_orders_array[i]

        for i in range(0, len(master_orders_array)):
            if i == 0:
                master_orders_str += master_orders_array[i]
            else:
                master_orders_str += "," + master_orders_array[i]

        for i in range(0, len(finished_orders_array)):
            if i == 0:
                finished_orders_str += finished_orders_array[i]
            else:
                finished_orders_str += "," + finished_orders_array[i]

        worker_orders_str += "]"
        master_orders_str += "]"
        finished_orders_str += "]"

        result = "{\"worker_orders\": " + worker_orders_str + ", " + "\"master_orders\": " + master_orders_str + ", " + "\"finished_orders\": " + finished_orders_str + "}"

        print(result)
        print("------------------------------------------")
        print(json.dumps(json.loads(result)))
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        self.write(json.dumps(result))

