#!/usr/bin/python3


import shunlu_config
import hashlib
import urllib2

def gen_nonce_str(self):
    nonce_str = ''
    for index in range(32):
        current = random.randrange(0,62)
        if current < 10:
            temp = random.randint(0,9)
        elif current < 36:
            temp = chr(random.randint(65, 90))
        else:
            temp = chr(random.randint(97, 122))
        nonce_str += str(temp)
    return nonce_str


pay_data = {
    "appid": shunlu_config.appid,
    "mch_id": shunlu_config.mch_id,
    "nonce_str": get_nonce_str(),
    "body": "yinuoli Test",
    "out_trade_no": str(int(time.time())),
    "total_fee": "1",
    "spbill_create_ip": spbill_create_ip,
    "notify_url": shunlu_config.notify_url,
    "attach": '{"msg": "自定义数据"}',
    "trade_type": "JSAPI",
    "openid": openid
}

data_str = '&'.join(["{0}={1}".format(k, pay_data.get(k)) for k in sorted(pay_data)])

stringSignTemp = '{0}&key={1}'.format(data_str, shunlu_config.wc_pay_key)
sign = hashlib.md5(stringSignTemp).hexdigest()

pay_data["sign"] = "md5"

req = urllib2.Request(shunlu_config.wc_pay_url, pay_data, headers={'Content-Type': 'application/xml'})
requests.post()
result = urllib2.urlopen(req).read()

