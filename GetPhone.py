#!/usr/bin/python3

import tornado.web
import redis
import json
import keys
import shunlu_config
import FinishOrder
import WXBizDataCrypt

charset = "utf-8"

class GetPhoneService(object):
    def __init__(self):
        self.rds = redis.StrictRedis(shunlu_config.redis_ip, shunlu_config.redis_port)

    def getPhone(self, userid, ecry_data, iv):
        session_key = (self.rds.hmget("user"+userid, b"session_key")[0]).decode(charset)
        pc = WXBizDataCrypt.WXBizDataCrypt(shunlu_config.appid, session_key)
        json_obj = pc.decrypt(ecry_data, iv)
        print("get phone: " + json.dumps(json_obj))
        return json_obj["phoneNumber"]
   

class GetPhoneHandler(tornado.web.RequestHandler):
    service = GetPhoneService()
    def post(self):
        userid = self.get_argument("user_id")
        ecry_data = self.get_argument("encrypted_data")
        iv = self.get_argument("iv")
        print("## userid:"+userid)
        print("## encrypted_data:"+ecry_data)
        print("## encrypted_data:"+iv)
        phoneNumber = self.service.getPhone(userid, ecry_data, iv)
        result = {
            "userid": userid,
            "phonenumber": phoneNumber
        }
        print(result)
        print("------------------------------------------")
        self.set_header("Content-Type", "text/plain; charset=UTF-8")
        self.write(json.dumps(result))

