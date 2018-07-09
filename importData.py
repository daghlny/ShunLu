#!/usr/bin/python3

import redis
import json
import sys
import os

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("USAGE: Program <order_data> <user_data>")
        exit(-1)
    order_file = open(sys.argv[1], 'r')
    user_file  = open(sys.argv[2], 'r')
    redisDB = redis.StrictRedis("localhost", 6379)
    

    for line in order_file:
        json_obj = json.loads(line)
        orderid = json_obj["order_id"]
        redisDB.set(orderid, json.dumps(json_obj))

        if json_obj["status"] == 2:
            redisDB.sadd("pending", orderid)
            redisDB.sadd("master"+str(json_obj["master_id"]), orderid)
        elif json_obj["status"] == 3:
            redisDB.sadd("doing", orderid)
            redisDB.sadd("master"+str(json_obj["master_id"]), orderid)
            redisDB.sadd("worker"+str(json_obj["worker_id"]), orderid)

    for line in user_file:
        json_obj = json.loads(line)
        redisDB.hmset("user"+json_obj["user_id"], {"user_name": str(json_obj["user_name"]), "balance": int(json_obj["balance"])})

