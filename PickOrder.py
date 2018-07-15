#!/usr/bin/python3

import tornado.web
import redis
import shunlu_config
import json
import keys

charset = "utf-8"

class PickOrderService(object):
    def __init__(self):
        self.rds = redis.StrictRedis(shunlu_config.redis_ip, shunlu_config.redis_port)

    def isOrderPending(self, userid, orderid):
        master_key = keys.master_k_prefix + str(userid)
        other_orders_keys = self.rds.sdiff(keys.pending_orders_k, master_key)
        b_orderid = bytes(orderid, encoding=charset)
        if b_orderid in other_orders_keys:
            return True
        else:
            return False

    def pickOrder(self, userid, orderid):
        order_lock = keys.order_lock_prefix + str(orderid)
        worker_key = keys.worker_k_prefix + str(userid)
        pipe = self.rds.pipeline()

        if not self.isOrderPending(userid, orderid):
            print("user %s, order %s not available or already picked"%(userid, orderid))
            return -1

        self.rds.srem(keys.pending_orders_k, orderid)
        self.rds.sadd(worker_key, orderid)
        self.rds.sadd(keys.doing_orders_k, orderid)
        json_str = self.rds.get(orderid)
        json_obj = json.loads(json_str.decode("utf-8"))
        json_obj["status"] = "3"
        if json_obj["master_id"] == userid:
            return -2
        self.rds.set(orderid, json.dumps(json_obj))

        #for i in range(3):
        #    try:
        #        pipe.execute()
        #        print("user %s pick order %s succ."%(userid, orderid))
        #        return True
        #    except Exception:
        #        print("user %s pick order %s fail, try %d/3" % (userid, orderid, i))
        #        continue
        return 1

    def getUserNickName(self, userid):
        user_key = keys.user_k_prefix + str(userid)
        user_name = (self.rds.hmget(user_key, "user_name")[0]).decode(charset)
        return user_name

    def setOrderWorker(self, userid, orderid):
        order_lock = keys.order_lock_prefix + str(orderid)
        pipe = self.rds.pipeline()

        order_str = self.rds.get(orderid).decode(charset)
        json_obj = json.loads(order_str)
        json_obj["worker_id"] = userid
        json_obj["worker_name"] = self.getUserNickName(userid)
        self.rds.set(orderid, json.dumps(json_obj))

        return True


class PickOrderHandler(tornado.web.RequestHandler):
    service = PickOrderService()

    def get(self):
        userid = self.get_argument("user_id")
        orderid = self.get_argument("order_id")
        print("Get a PickOrder request with userid="+str(userid)+" orderid="+str(orderid))
        ret = self.service.pickOrder(userid, orderid)
        result = {}
        result["order_id"] = orderid
        result["status"] = ret
        self.service.setOrderWorker(userid, orderid)
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        self.write(json.dumps(result))

