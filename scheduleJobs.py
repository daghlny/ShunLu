#!/usr/bin/python3

import time
from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
import redis
import FinishOrder

charset = "utf-8"
seconds_in_oneday = 86400
notfinished_flag = ("notpaid", "pending", "doing")

# 如果这个订单无人确认，那么就会将这个订单放到 "canceled" 状态
# 如果 worker 确认了这个订单，就会将订单放到 "finished" 状态
def checkNotFinishedOrders():
    current_timestamp = time.time()
    rds = redis.StrictRedis("localhost", 6379)
    for flag in notfinished_flag:
        orders_byte_array = rds.smembers(flag)
        for order_byte in orders_byte_array:
            json_obj = json.loads(rds.get(order_byte.decode(charset)))
            if current_timestamp - json_obj["deadline_time"] >= seconds_in_oneday:
                CancelOrder.cancel_order(json_obj["order_id"], flag)

    orders_byte_array = rds.smembers("worker_confirmed")
    service = FinishOrder.FinishOrderService()
    for order_byte in orders_byte_array:
        json_obj = json.loads(rds.get(order_byte.decode(charset)))
        if current_timestamp - json_obj["deadline_time"] >= seconds_in_oneday:
            service.finish_order(json_obj["order_id"])

if __name__ == "__main__":
    scheduler = BlockingScheduler()
    start_date_arg = '2018-07-08 19:00:00'
    end_date_arg   = '2018-09-08 19:00:01'
    scheduler.add_job(checkNotFinishedOrders, 'interval', hours=1, start_date=start_date_arg, end_date=end_date_arg)
    scheduler.start()

