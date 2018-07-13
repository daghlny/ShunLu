#!/usr/bin/python3

import redis
import json
import sys
import os
import time
import random

users = {"1": "光头强", "2": "熊大", "3": "熊二", "4": "小姐姐", "5": "小哥哥", "6": "小妹妹", "7": "弟弟", "8": "佩奇", "9":"代古拉", "10":"Pony"}
addresses = ["学生1超市", "女生宿舍楼下", "万利达2楼", "小树林", "霍格沃兹", "临冬城", "海拉尔", "潇湘馆", "TongFu Hotel", "Dead HuTong"]
shijian = ["今天中午", "明天下午", "明天早上", "今天下午", "明年今日"]
kuaidi  = ["中通", "韵达", "京东", "顺丰", "外卖"]

count = 10

if __name__ == "__main__":
    redisDB = redis.StrictRedis("localhost", 6379)
    
    for i in range(1, count+1):
        json_obj = dict()
        json_obj["status"]   = random.randint(2, 3)
        json_obj["order_id"] = i;
        json_obj["master_id"] = str(random.randint(1, len(users)))
        json_obj["master_name"] = users[json_obj["master_id"]]
        if json_obj["status"] == 2:
            json_obj["worker_id"] = 0
            json_obj["worker_name"] = ""
        else:
            json_obj["worker_id"] = str(random.randint(1, len(users)))
            while json_obj["worker_id"] == json_obj["master_id"]:
                json_obj["worker_id"] = str(random.randint(1, len(users)))
            json_obj["worker_name"] = users[json_obj["worker_id"]]
        json_obj["order_type"] = 1
        json_obj["source_location"]  = addresses[random.randint(0, len(addresses)-1)]
        json_obj["destination_location"]  = addresses[random.randint(0, len(addresses)-1)]
        owner_name = users[str(random.randint(1, len(users)))]
        owner_phone = random.randint(1, 100000000000)
        owner_number = random.randint(1, 100000)
        json_obj["owner_info"] = {
            "owner_name": owner_name,
            "owner_phone": owner_phone,
            "owner_number": owner_number
        }
        json_obj["sending_start_time"] = int(time.time() + random.randint(0, 86400*2) - random.randint(0, 86400*2))
        json_obj["sending_end_time"]   = json_obj["sending_start_time"] + random.randint(0, 86400)
        json_obj["money"] = random.randint(1, 100)*50
        json_obj["package_weight"] = random.randint(1, 3)
        json_obj["note"] = shijian[random.randint(0, len(shijian)-1)] + kuaidi[random.randint(0, len(kuaidi)-1)]
        json_obj["worker_score"] = 0
        json_obj["master_score"] = 0
        json_obj["worker_phone"] = random.randint(1, 100000)
        if json_obj["status"] == 2:
            redisDB.sadd("pending", i)
            redisDB.sadd("master"+str(json_obj["master_id"]), i)
        elif json_obj["status"] == 3:
            redisDB.sadd("doing", i)
            redisDB.sadd("master"+str(json_obj["master_id"]), i)
            redisDB.sadd("worker"+str(json_obj["worker_id"]), i)
        json_obj["create_time"] = json_obj["sending_start_time"] - random.randint(0, 86400)
        redisDB.set(i, json.dumps(json_obj))

    for userid in users:
        username = users[userid]
        redisDB.hmset("user"+userid, {"user_name": str(username), "balance": random.randint(100, 10000)})

