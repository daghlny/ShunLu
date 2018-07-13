#!/usr/bin/python3

import sys
import json

import tornado.ioloop
import tornado.web
import tornado.httpserver
import redis
import keys
import FinishOrder
import OrdersList
import PickOrder
import QueryUserOrder
import RefundMoney
import EvaluateOrder
import CancelOrder
import RequireOpenID
import BloomFilter

charset = "utf-8"
def make_app():
    return tornado.web.Application([
        # 抓取订单
        (r"/orders", OrdersList.OrdersHandler),
        # 完成订单（"确认订单"逻辑)
        (r"/finish_order", FinishOrder.FinishOrderHandler),
        # 抢单
        (r"/pick_order", PickOrder.PickOrderHandler),
        # 获取指定用户历史订单
        (r"/user_orders", QueryUserOrder.QueryUserOrdersHandler),
        # 订单评价
        (r"/comment_order", EvaluateOrder.EvaluateOrdersHandler),
        # 取消订单
        (r"/cancel_order", CancelOrder.CancelOrderHandler),
        # 登录
        (r"/login", RequireOpenID.LoginHandler)
        # 查询敏感词
        (r"/sensitive_word", SensitiveDict.FilterHandler)
    ])


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("USAGE: Program wordDict")
        exit(-1)
    sens_words_filter = BFilter(1000000, 20)
    sens_words_filter.load_words(sys.argv[1])
    app = make_app()
    http_server = tornado.httpserver.HTTPServer(app, ssl_options={
        "certfile": "/etc/nginx/ssl/fullchain.cer",
        "keyfile": "/etc/nginx/ssl/daghlny.com.key"
    })
    http_server.listen(443)
    tornado.ioloop.IOLoop.instance().start()
    #tornado.ioloop.IOLoop.current().start()

