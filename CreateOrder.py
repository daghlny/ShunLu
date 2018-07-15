#!/usr/bin/python3

import tornado.web
import redis
import json
import time
import keys
import shunlu_config
import jieba
import BloomFilter

charset = "utf-8"


class CreateOrdersService(object):
    def __init__(self):
        self.rds = redis.StrictRedis(shunlu_config.redis_ip, shunlu_config.redis_port)

    def haveSensWord(self, note):
        words = jieba.cut(note)
        ret = 1
        for word in words:
            print(word)
            if word in BloomFilter.sens_words_dict:
                ret = -1
                break
        return ret

    def saveOrder(self, data):
        if self.haveSensWord(data["note"]) == -1:
            return -3
        order_id = -1
        if self.rds.exists(keys.newest_k):
            order_id = self.rds.get(keys.newest_k)
            order_id = int(order_id)
            self.rds.set(keys.newest_k, str(order_id+1))
        else:
            return -1

        print("-----------master_id: "+data["master_id"])
        balance = int(self.rds.hget("user"+str(data["master_id"]), b"balance").decode(charset))

        if data["pay_method"] == "1":
            if balance < int(data["money"]) :
                return -2
            else:
                self.rds.hset("user"+str(data["master_id"]), "balance", balance-int(data["money"]))

        data["status"] = 2
        data["worker_score"] = 0
        data["master_score"] = 0
        data["worker_phone"] = ""
        data["master_name"]  = self.getUserNickName(data["master_id"])
        data["create_time"]  = time.time()


        json_str = json.dumps(data)
        self.rds.set(str(order_id), json_str)
        master_key = keys.master_k_prefix + str(data["master_id"])
        self.rds.sadd(master_key, order_id)
        self.rds.sadd(keys.pending_orders_k, order_id)

        return order_id


    def getUserNickName(self, user_id):
        user_key = keys.user_k_prefix + str(user_id)
        user_name = (self.rds.hmget(user_key, "user_name")[0]).decode(charset)
        return user_name



class CreateOrdersHandler(tornado.web.RequestHandler):
    service = CreateOrdersService()

    def post(self):
        #worker_id = self.get_argument("worker_id") #接单人id
        #master_id = self.get_argument("master_id") #发单人id
        # FIXME: here should edit
        worker_id = ""
        print(self.request.body)
        worker_id = ""
        master_id = self.get_argument("master_id")
        source_location = self.get_argument("source_location") #订单来源地
        order_type = self.get_argument("order_type") #订单类型
        destination_location = self.get_argument("destination_location") #订单送达目的地
        sending_start_time = self.get_argument("sending_start_time") #订单开始时间
        sending_end_time = self.get_argument("sending_end_time") #订单截止时间
        money = self.get_argument("money") #订单金额
        package_weight = self.get_argument("package_weight") #包裹重量
        note = self.get_argument("note") #备注
        pay_method = self.get_argument("pay_method") # 付款方式 "1":余额支付, "2": 微信支付
        # owner_info = self.get_argument("owner_info")#拥有者信息
        owner_name =   self.get_argument("owner_name")
        owner_phone =  self.get_argument("owner_phone")
        owner_number = self.get_argument("owner_number")
        owner_info = {
            "owner_name": owner_name,
            "owner_phone": owner_phone,
            "owner_number": owner_number
        }

        data = {"worker_id" : str(worker_id),
                "master_id" : str(master_id),
                "order_type": int(order_type),
                "source_location": str(source_location),
                "destination_location":str(destination_location),
                "sending_start_time":int(sending_start_time),
                "sending_end_time":int(sending_end_time),
                "money":int(money),
                "package_weight":int(package_weight),
                "owner_info": owner_info,
                "note":str(note),
                "pay_method": str(pay_method)
                }

        result_number = self.service.saveOrder(data)

        self.set_header("Content-Type", "text/plain; charset=UTF-8")
        print(result_number)
        self.write(str(result_number))

