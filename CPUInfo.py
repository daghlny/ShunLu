#!/usr/bin/python3

import tornado.web
import psutil

charset = "utf-8"

class CPUInfoHandler(tornado.web.RequestHandler):

    def getCPUstate(self):
        return (str(psutil.cpu_percent(interval=0.2)))

    def get(self):
        self.set_header("Content-Type", "text/plain; charset=UTF-8")
        self.write(self.getCPUstate())
