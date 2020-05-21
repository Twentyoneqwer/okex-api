from .swap_api import SwapAPI
import time
from .client import Client
from .consts import *


class Function(Client):
    def __init__(self, api_key, api_seceret_key, passphrase, use_server_time=False):
        Client.__init__(self, api_key, api_seceret_key, passphrase, use_server_time)

    def trend_judge(self):
        i = 0
        Tmax = 0.0
        Tmin = 100000.0
        a = [0] * 50
        while i <= 10:
            BTC_Ticker = SwapAPI.get_specific_ticker('BTC-USDT-SWAP')
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
