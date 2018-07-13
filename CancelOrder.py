#!/usr/bin/python3

import tornado.web
import redis
import shunlu_config
import json
import keys
import time

charset = "utf-8"

class CancelOrderService(object):
    def __init__(self):
        self.rds = redis.StrictRedis(shunlu_config.redis_ip, shunlu_config.redis_port)

    def isOrderCancelable(self, userid, orderid):
        master_key = keys.master_k_prefix + str(userid)
        master_orders = self.rds.smembers(master_key)

        pending_orders = self.rds.smembers(keys.pending_orders_k)
        order = self.rds.get(orderid)
        json_obj = json.loads(order.decode(charset))

        # TODO 不知道格式，假定是unix时间戳
        time_order = json_obj["create_time"]
        time_now = time.time()
        time_in_range = (time_now-time_order < 120 and time_now>time_order)

        b_orderid = bytes(orderid, encoding=charset)

        isUserOrder = b_orderid in master_orders
        isPendingOrder = b_orderid in pending_orders
        isOrderExisted = not not order

        print("user %s check order %s cancelable, isUserOrder: %s, isPendingOrder: %s, isOrderExisted: %s, isTimeLess2Min: %s"%(userid, orderid, isUserOrder, isPendingOrder, isOrderExisted, time_in_range))

        if isUserOrder and isPendingOrder and isOrderExisted and time_in_range:
            return True
        return False

    def cancelOrder(self, userid, orderid):

        if not self.isOrderCancelable(userid, orderid):
            print("order %s can not be canceled" % (orderid))
            return False

        order_lock = keys.order_lock_prefix + str(orderid)
        pipe = self.rds.pipeline()

        for i in range(3):
            try:
                pipe.watch(order_lock)
                pipe.set(order_lock, 3)

                pipe.srem(keys.pending_orders_k, orderid)

                order_str = pipe.get(orderid).decode(charset)
                json_obj = json.loads(order_str)
                json_obj["status"] = 7
                pipe.set(orderid, json.dumps(json_obj))

                pipe.set(order_lock, 0)
                pipe.execute()
                print("user %s cancel order %s succ."%(userid, orderid))
                return True
            except Exception:
                print("user %s cancel order %s fail, try %d/3" % (userid, orderid, i))
                continue

        return False

class CancelOrderHandler(tornado.web.RequestHandler):
    service = CancelOrderService()

    def get(self):
        userid = self.get_argument("user_id")
        orderid = self.get_argument("order_id")

        ret = self.service.cancelOrder(userid, orderid)

        result = {}
        result["order_id"] = orderid
        result["status"] = 1 if ret else -1

        self.set_header("Content-Type", "application/json; charset=UTF-8")
        self.write(json.dumps(result))

