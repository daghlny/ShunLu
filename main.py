#!/usr/bin/python3

import tornado.ioloop
import tornado.web
import redis
import json
import keys
import FinishOrder
import OrdersList
import PickOrder
import QueryUserOrder

charset = "utf-8"
def make_app():
    return tornado.web.Application([
        (r"/orders", OrdersList.OrdersHandler),
        (r"/finish_order", FinishOrder.FinishOrderHandler),
        (r"/pick_order", PickOrder.PickOrderHandler),
        (r"/user_orders", QueryUserOrder.QueryUserOrdersHandler),
    ])


if __name__ == "__main__":
    app = make_app()
    app.listen(8011)
    tornado.ioloop.IOLoop.current().start()

