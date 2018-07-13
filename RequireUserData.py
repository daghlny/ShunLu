#!/usr/bin/python3

import tornado.web
import redis
import json
import keys
import shunlu_config

charset = "utf-8"


class RequireUserDataService(object):
    def __init__(self):
        self.rds = redis.StrictRedis(shunlu_config.redis_ip, shunlu_config.redis_port)

    def getUserData(self, userid):
        useridInRedis = "user" + str(userid)
        # 用户不存在时的返回值, 待确定
        if ~self.rds.exists(useridInRedis):
            return -1
        user_key = keys.user_k_prefix + str(userid)
        if ~self.rds.exists(user_key):
            return {}
        else:
            user_info_keys = self.rds.hgetall(user_key)
        return user_info_keys


class RequireUserDataHandler(tornado.web.RequestHandler):
    service = RequireUserDataService()

    def get(self):
        userid = self.get_argument("user_id")
        user_info_dict = self.service.getOrders(userid)
        if not user_info_dict:
            username = '-2'
            balance = -2
        else:
            username = user_info_dict.get("username", "-1")
            balance = user_info_dict.get("balance", -1)
        #result = "{\"userid\": "+userid+", " + "\"username\": "+username+", " + "\"balance\": "+balance+"}"
        result = {
            "userid": str(userid),
            "username": str(username),
            "balance": int(balance),
        }
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        self.write(json.dumps(result))

