#!/usr/bin/python3

import tornado.ioloop
import tornado.web
import redis
import json
import time
import keys

charset = "utf-8"


class CreateOrdersService(object):
    def __init__(self):
        self.rds = redis.StrictRedis("localhost", 6379)

    def saveOrder(self, data):

        order_id = -1
        if self.rds.exists(keys.newest_k):
            order_id = self.rds.get(keys.newest_k)
        data["status"] = 2
        data["worker_score"] = 0
        data["master_score"] = 0
        data["worker_phone"] = ""
        user_id = data["master_id"]
        user_name = self.getUserNickName(user_id)
        data["master_name"] = user_name

        json_str = json.dumps(data)

        create_time = time.time()
        order_dict = {
            "create_time": create_time,
            "data": json_str
        }

        order_id = order_id + 1
        order_lock = keys.newest_k + str(order_id)

        for i in range(3):
            try:
                self.rds.watch(order_lock)
                self.rds.set(order_lock,1)
                self.rds.set(str(order_id) , order_dict)
                master_key = keys.master_k_prefix + str(user_id)
                self.rds.sadd(master_key, order_id)
                self.rds.sadd(keys.pending_orders_k, order_id)
                self.rds.set(keys.newest_k, order_id)
                self.rds.set(order_lock,0)
                return order_id

            except Exception:
                print('save order failed!')
                continue

        return -1


    def getUserNickName(self, user_id):
        user_key = keys.user_k_prefix + str(user_id)
        user_name = (self.rds.hmget(user_key, "user_name")[0]).decode(charset)
        return user_name



class CreateOrdersHandler(tornado.web.RequestHandler):
    service = CreateOrdersService()

    def post(self):
        worker_id = self.get_argument("worker_id") #接单人id
        master_id = self.get_argument("master_id") #发单人id
        order_type = self.get_argument("order_type") #订单类型
        source_location = self.get_argument("source_location") #订单来源地
        destination_location = self.get_argument("destination_location") #订单送达目的地
        sending_start_time = self.get_argument("sending_start_time") #订单开始时间
        sending_end_time = self.get_argument("sending_end_time") #订单截止时间
        money = self.get_argument("money") #订单金额
        package_weight = self.get_argument("package_weight") #包裹重量
        note = self.get_argument("note") #备注
        # owner_info = self.get_argument("owner_info")#拥有者信息

        data = {"worker_id" : str(worker_id),
                "master_id" : str(master_id),
                "order_type": int(order_type),
                "source_location": str(source_location),
                "destination_location":str(destination_location),
                "sending_start_time":int(sending_start_time),
                "sending_end_time":int(sending_end_time),
                "money":int(money),
                "package_weight":int(package_weight),
                "note":str(note)}

        result_number = self.service.saveOrder(data)
        result = {
            "result": result_number
        }

        self.set_header("Content-Type", "application/json; charset=UTF-8")
        self.write(json.dumps(result))

        return result


def make_app():
    return tornado.web.Application([
        (r"/create_order", SaveOrdersHandler),
    ])

if __name__ == '__main__':
    app = make_app()
    app.listen(8011)
    tornado.ioloop.IOLoop.current().start()