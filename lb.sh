#!/bin/sh
limit=10
load1="$(curl -s -m 2 http://47.91.227.238:8011/cpu_info)"
load2="$(curl -s -m 2 http://47.91.227.238:8011/cpu_info)"
weight1=0.5

l1_10="$(echo "$load1<$limit"|bc)"
l2_10="$(echo "$load2<$limit"|bc)"
l1_01="$(echo "$load1<0.1"|bc)"
l2_01="$(echo "$load2<0.1"|bc)"

if [ $l1_10 = 1 ] && [ $l2_10 = 1 ]; then
	weight1=0.5;
elif [ $l1_10 = 0 ] && [ $l2_01 = 1 ]; then
	weight1=0.95;
elif [ $l2_10 = 0 ] && [ $l1_01 = 1 ]; then
	weight1=0.05;
else
	weight1="$(echo "scale=2;$load1/($load1+$load2)"|bc)";
fi

iptables -t nat -R balance1 1 -m statistic --mode random --probability $weight1 -j balance_svr1
echo "load: $load1, $load2; set svr1 $weight1"
echo "$l1_10, $l2_10, $l1_01, $l2_01"
