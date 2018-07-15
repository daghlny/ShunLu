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
import RequireUserData
import BloomFilter
import CreateOrder
import GetPhone
import shunlu_config
import NotifyPay


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
        (r"/login", RequireOpenID.LoginHandler),
        # 获取用户信息
        (r"/query_user", RequireUserData.RequireUserDataHandler),
        # 查询敏感词
        (r"/sensitive_word", BloomFilter.SensFilterHandler),
        # 创建订单
        (r"/create_order", CreateOrder.CreateOrdersHandler),
        # 获取手机号
        (r"/get_phone", GetPhone.GetPhoneHandler),
        # 微信支付 Notify
        (r"/notify", NotifyPay.NotifyHandler),
        # 查询用户之前是否认证过
        (r"/valid_user", ValidUser.ValidUserHandler)
    ])


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("USAGE: Program wordDict")
        exit(-1)
    BloomFilter.sens_words_dict = BloomFilter.BFilter(1000000, 20)
    BloomFilter.sens_words_dict.load_words(sys.argv[1])
    app = make_app()
    http_server = tornado.httpserver.HTTPServer(app, ssl_options={
        "certfile": "/etc/nginx/ssl/fullchain.cer",
        "keyfile": "/etc/nginx/ssl/daghlny.com.key"
    })
    http_server.listen(443)
    tornado.ioloop.IOLoop.instance().start()
    #tornado.ioloop.IOLoop.current().start()

