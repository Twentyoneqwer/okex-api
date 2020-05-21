import okex.account_api as account
import okex.futures_api as future
import okex.lever_api as lever
import okex.spot_api as spot
import okex.swap_api as swap
import okex.index_api as index
import json
import logging
import datetime
import time
import okex.swap_api as swap
import requests
from pymongo import MongoClient
import numpy as np
import random
import okex.function as function



def trend_judge(self):
    i = 0
    Tmax = 0.0
    Tmin = 100000.0
    a = [0] * 50
    while i <= 10:
        BTC_Ticker = swapAPI.get_specific_ticker('BTC-USDT-SWAP')
        a[i] = float(BTC_Ticker['last'])
        print(a[i])
        if Tmax < a[i]:
            Tmax = a[i]
        if Tmin > a[i]:
            Tmin = a[i]
        time.sleep(1)
        i += 1

    bef = sum(a[0:5])
    print(bef)
    aft = sum(a[5:10])
    print(aft)

    bef_avg = bef / 5
    aft_avg = aft / 5
    if bef_avg > aft_avg:
        trend = 1
    else:
        trend = 2
    return trend, Tmax, Tmin