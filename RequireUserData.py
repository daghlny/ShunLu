#!/usr/bin/python3

import tornado.web
import redis
import json
import keys
import shunlu_config

charset = "utf-8"


class RequireUserDataService(object):
    def __init__(self):
        self.rds = redis.StrictRedis("localhost", 6379)

    def getUserData(self, userid):
        useridInRedis = "user" + str(userid)
        # 用户不存在时的返回值, 待确定
        if not self.rds.exists(useridInRedis):
            return -1
        else:
            user_info_keys = self.rds.hgetall(useridInRedis)
        return user_info_keys


class RequireUserDataHandler(tornado.web.RequestHandler):
    service = RequireUserDataService()

    def get(self):
        userid = self.get_argument("user_id")
        user_info_dict = self.service.getUserData(userid)
        if user_info_dict == -1:
            username = 'NULL'
            balance = 0
        else:
            username = user_info_dict.get(b"user_name", "NULL").decode(charset)
            balance = user_info_dict.get(b"balance", 0)
        #result = "{\"userid\": "+userid+", " + "\"username\": "+username+", " + "\"balance\": "+balance+"}"
        result = {
            "userid": str(userid),
            "username": str(username),
            "balance": int(balance),
        }
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        self.write(json.dumps(result))

