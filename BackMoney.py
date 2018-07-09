
import redis

# method: 
#   1 -> back to balance
#   2 -> back by using wechat bonus(微信红包)

def refund_to_master(orderid, masterid, money, method=2):
    rds = redis.StrictRedis("localhost", 6379)
    if method == 1:
        rds.incr("user"+masterid, "balance", money)
    else:
        refund_to_master_by_bonus(masterid, money)

#FIXME: finish this function
def refund_to_master_by_bonus(masterid, money):
    pass

