#!/usr/bin/python3

import redis
import json
import sys
import os

if __name__ == "__main__":
    ifile = open(sys.argv[1], 'r')
    redisDB = redis.StrictRedis("localhost", 6379)
    

    for line in ifile:
        json_obj = json.loads(line)
        orderid = json_obj["order_id"]
        redisDB.set(orderid, json.dumps(json_obj))

        if json_obj["worker_id"] == 0:
            redisDB.sadd("pending", orderid)
            redisDB.sadd("master"+str(json_obj["master_id"]), orderid)
        else:
            redisDB.sadd("doing", orderid)
            redisDB.sadd("master"+str(json_obj["master_id"]), orderid)
            redisDB.sadd("worker"+str(json_obj["worker_id"]), orderid)

