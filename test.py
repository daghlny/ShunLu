#!/usr/bin/python3

import wzhifuSDK

uorder = wzhifuSDK.UnifiedOrder_pub()
uorder.createXml()
prepayid = uorder.getPrepayId()
print(prepayid)

