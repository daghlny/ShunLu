#!/usr/bin/python3

import tornado.web
import redis
import json
import keys
import shunlu_config
import random

charset = "utf-8"


class ValidUserService(object):
    def __init__(self):
        self.rds = redis.StrictRedis("localhost", 6379)

    def ifValid(self, userid):
        useridInRedis = "user" + str(userid)
        valided = "-1"
        # 用户不存在时的返回值, 待确定
        if self.rds.exists(useridInRedis):
            #FIXME: For test
            if not self.rds.hexists(useridInRedis, "valided"): 
                self.rds.hset(useridInRedis, "valided", "-1")
            valided = self.rds.hget(useridInRedis, "valided").decode("utf-8")
        if valided == "-1":
            self.rds.hset(useridInRedis, "valided", "1")
            self.rds.hset(useridInRedis, "balance", "1000")
            names = ["小猪", "小狗", "小熊", "小麻雀", "小傻瓜"]
            self.rds.hset(useridInRedis, "user_name", names[random.randint(0, len(names)-1)])
            # 需要增加一个添加用户名的
            #self.rds.hset(useridInRedis, )
        return valided


class ValidUserHandler(tornado.web.RequestHandler):
    service = ValidUserService()

    def get(self):
        userid = self.get_argument("user_id")
        print("get a ValidUser request with userid="+str(userid))
        ifvalid = self.service.ifValid(userid)
        print("return value:"+ str(ifvalid))
        #result = "{\"userid\": "+userid+", " + "\"username\": "+username+", " + "\"balance\": "+balance+"}"
        result = {}
        result["status"] = str(ifvalid)
        self.set_header("Content-Type", "text/plain; charset=UTF-8")
        self.write(str(ifvalid))

