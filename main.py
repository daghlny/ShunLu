#!/usr/bin/python3

import sys
import json

import tornado.ioloop
import tornado.web
import redis
import keys
import FinishOrder
import OrdersList
import PickOrder
import RefundMoney
import EvaluateOrder
import CancelOrder
import RequireOpenID
import sllog

charset = "utf-8"
def make_app():
    return tornado.web.Application([
        # 抓取订单
        (r"/orders", OrdersList.OrdersHandler),
        # 完成订单（"确认订单"逻辑)
        (r"/finish_order", FinishOrder.FinishOrderHandler),
        # 抢单
        (r"/pick_order", PickOrder.PickOrderHandler),
        # 订单评价
        (r"/comment_order", EvaluateOrder.EvaluateOrdersHandler),
        # 取消订单
        (r"/cancel_order", CancelOrder.CancelOrderHandler),
        # 登录
        (r"/login", RequireOpenID.LoginHandler)
    ])


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("USAGE: Program <logpath>")
    sllog.initlog(sys.argv[1])
    app = make_app()
    app.listen(8011)
    tornado.ioloop.IOLoop.current().start()

