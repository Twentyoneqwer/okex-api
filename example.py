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


# log_format = '%(asctime)s - %(levelname)s - %(message)s'
# logging.basicConfig(filename='mylog-rest.json', filemode='a', format=log_format, level=logging.INFO)


# logging.warning('warn message')
# logging.info('info message')
# logging.debug('debug message')
# logging.error('error message')
# logging.critical('critical message')


def get_timestamp():
    now = datetime.datetime.now()
    t = now.isoformat("T", "milliseconds")
    return t + "Z"


def trend_judge():
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


def trend_short_judge():
    i = 0
    Tmax = 0.0
    Tmin = 100000.0
    a = [0] * 50
    while i <= 5:
        BTC_Ticker = swapAPI.get_specific_ticker('BTC-USDT-SWAP')
        a[i] = float(BTC_Ticker['last'])
        print(a[i])
        if Tmax < a[i]:
            Tmax = a[i]
        if Tmin > a[i]:
            Tmin = a[i]
        time.sleep(0.5)
        i += 1

    bef = sum(a[0:3])
    print(bef)
    aft = sum(a[3:6])
    print(aft)

    bef_avg = bef / 3
    aft_avg = aft / 3
    if bef_avg > aft_avg:
        trend = 1
    else:
        trend = 2
    return trend, Tmax, Tmin


def low_position(x, y):
    BTC_Ticker = swapAPI.get_specific_ticker('BTC-USDT-SWAP')
    Last_price = float(BTC_Ticker['last'])
    Account = swapAPI.get_coin_account('BTC-USDT-SWAP')
    Account_num = float(Account['info']['equity'])
    n = int((Account_num / Last_price) * 500)
    if x < Last_price < y:
        print("处于", x, "--", y, "阶段")
        Exis = 0
        read_db = db.find({})
        for i in db.find({}):
            print('订单查询中')
            print(i['订单号'])
            get_order_info = swapAPI.get_order_info('BTC-USDT-SWAP', i['订单号'])
            print('order state:', get_order_info['state'])

            # 如果订单中已有此区间成交的多单
            if get_order_info['type'] == "1" and x < float(get_order_info['price']) < y:
                print('此区间内已有多单')
                Exis = 1

        if Exis == 0:
            take_order = swapAPI.take_orders('BTC-USDT-SWAP', [
                {"type": "1", "price": Last_price, "size": n}
            ])
            order_id = take_order['order_info'][0]['order_id']  # 获取订单id
            get_order_info = swapAPI.get_order_info('BTC-USDT-SWAP', order_id)

            datalist = [{
                "订单号": get_order_info['order_id'],
                "价格": get_order_info['price'],
                "状态": get_order_info['state'],
                "方向": get_order_info['type']
            }]
            db.insert_many(datalist)

        read_db = db.find({})
        for i in db.find({}):
            print('订单查询中')
            print(i['订单号'])
            get_order_info = swapAPI.get_order_info('BTC-USDT-SWAP', i['订单号'])
            print('order state:', get_order_info['state'])

            # 如果订单已成交且为开空
            if get_order_info['state'] == "2" and get_order_info['type'] == "2" and float(
                    get_order_info['price']) - Last_price > 40:
                print('开空订单已成交')
                # 删除数据库中数据
                myquery = {"订单号": i['订单号']}
                db.delete_one(myquery)
                # 下一个平空单
                take_order = swapAPI.take_orders('BTC-USDT-SWAP', [
                    {"type": "4",
                     "price": float(BTC_Ticker['last']),
                     "size": n}
                ])

        while x < Last_price < y:
            print("仍处于", x, "--", y, "阶段")
            time.sleep(2)
            BTC_Ticker = swapAPI.get_specific_ticker('BTC-USDT-SWAP')
            Last_price = float(BTC_Ticker['last'])


def high_position(x, y):
    BTC_Ticker = swapAPI.get_specific_ticker('BTC-USDT-SWAP')
    Last_price = float(BTC_Ticker['last'])
    Account = swapAPI.get_coin_account('BTC-USDT-SWAP')
    Account_num = float(Account['info']['equity'])
    n = int((Account_num / Last_price) * 1000)
    if x < Last_price < y:
        print("处于", x, "--", y, "阶段")
        Exis = 0
        read_db = db.find({})
        for i in db.find({}):
            print('订单查询中')
            print(i['订单号'])
            get_order_info = swapAPI.get_order_info('BTC-USDT-SWAP', i['订单号'])
            print('order state:', get_order_info['state'])

            # 如果订单中已有此区间成交的空单
            if get_order_info['type'] == "2" and x < float(get_order_info['price']) < y:
                print('此区间内已有空单')
                Exis = 1

        if Exis == 0:
            take_order = swapAPI.take_orders('BTC-USDT-SWAP', [
                {"type": "2", "price": Last_price, "size": n}
            ])
            order_id = take_order['order_info'][0]['order_id']  # 获取订单id
            get_order_info = swapAPI.get_order_info('BTC-USDT-SWAP', order_id)

            datalist = [{
                "订单号": get_order_info['order_id'],
                "价格": get_order_info['price'],
                "状态": get_order_info['state'],
                "方向": get_order_info['type']
            }]
            db.insert_many(datalist)

        read_db = db.find({})
        for i in db.find({}):
            print('订单查询中')
            print(i['订单号'])
            get_order_info = swapAPI.get_order_info('BTC-USDT-SWAP', i['订单号'])
            print('order state:', get_order_info['state'])

            # 如果订单已成交且为开多
            if get_order_info['state'] == "2" and get_order_info['type'] == "1" and Last_price - float(
                    get_order_info['price']) > 40:
                print('开多订单已成交')
                # 删除数据库中数据
                myquery = {"订单号": i['订单号']}
                db.delete_one(myquery)
                # 下一个平多单
                take_order = swapAPI.take_orders('BTC-USDT-SWAP', [
                    {"type": "3",
                     "price": float(BTC_Ticker['last']),
                     "size": n}
                ])

        while x < Last_price < y:
            print("仍处于", x, "--", y, "阶段")
            time.sleep(2)
            BTC_Ticker = swapAPI.get_specific_ticker('BTC-USDT-SWAP')
            Last_price = float(BTC_Ticker['last'])


Time = get_timestamp()

if __name__ == '__main__':

    api_key = ""
    seceret_key = ""
    passphrase = ""

    # 永续合约API
    swapAPI = swap.SwapAPI(api_key, seceret_key, passphrase, True)

    # trend = trend_judge()
    # print(trend[0])
    # print("区间没最大值为：", trend[1])
    # print("区间内最小值为：", trend[2])
    # if trend[0] == 1:
    #     print("此时趋势为下降")
    # if trend[0] == 2:
    #     print("此时趋势为上升")

    # 找到最近两小时内的最大值与最小值

    # BTC_Line = swapAPI.get_kline('BTC-USDT-SWAP', '2020-04-23T14:22:00.977Z', Time, 60)
    #
    # print(BTC_Line)
    # price_line = [0] * 40
    # price_max = [0] * 40
    # price_min = [0] * 40
    # i = 0
    # while i < 40:
    #     price_line[i] = BTC_Line[i][1]
    #     price_max[i] = float(BTC_Line[i][2])
    #     price_min[i] = float(BTC_Line[i][3])
    #     i += 1
    # print(price_line)
    # Tmax = max(price_max)
    # print(Tmax)
    # Tmin = min(price_min)
    # print(Tmin)
    # dif = Tmax - Tmin

    Tmax = 9900
    Tmin = 9400
    dif = Tmax - Tmin
    BTC_Ticker = swapAPI.get_specific_ticker('BTC-USDT-SWAP')
    # print(BTC_Ticker)
    Last_price = float(BTC_Ticker['last'])
    # print("最新价格:", Last_price)
    Account = swapAPI.get_coin_account('BTC-USDT-SWAP')
    Account_num = float(Account['info']['equity'])
    n = int((Account_num / Last_price) * 500)
    print("n的数值", n)

    client = MongoClient("localhost", 27017)
    db = client['BTC']['OKEXLONG']
    # db.drop()  # 初始化数据库
    # datalist = [{
    #     "订单号": 56,
    #     "价格": 43,
    #     "状态": 0,
    #     "方向": 40
    # }]
    # db.insert_many(datalist)
    #
    # db = client['BTC']['OKEXSHORT']

    # datalist = [{
    #     "订单号": 56,
    #     "价格": 43,
    #     "状态": 1,
    #     "方向": 40
    # }]
    # db.insert_many(datalist)

    # db = client['BTC']['OKEXSHORT']

    while Tmax + 50 > Last_price > Tmin - 50:
        print("处于价格区间内,寻找趋势中...")
        # s = requests.session()
        # s.keep_alive = False
        trend = trend_short_judge()
        BTC_Ticker = swapAPI.get_specific_ticker('BTC-USDT-SWAP')
        Last_price = float(BTC_Ticker['last'])
        print("最新价格:", Last_price)

        if trend[0] == 2 and Tmin < Last_price < (Tmin + (0.3 * dif)):  # 上涨中且处于低点位置
            print("当前处于震荡低点")
            if Last_price < (Tmin + (0.1 * dif)):
                print("处于低点第一阶段")
                low_position(Tmin, Tmin + (0.1 * dif))

            if (Tmin + (0.1 * dif)) < Last_price < (Tmin + (0.2 * dif)):
                print("处于低点第二阶段")
                low_position(Tmin + (0.1 * dif), Tmin + (0.2 * dif))

            if (Tmin + (0.2 * dif)) < Last_price < (Tmin + (0.3 * dif)):
                print("处于低点第三阶段")
                low_position(Tmin + (0.2 * dif), Tmin + (0.3 * dif))

        if trend[0] == 1 and Tmax > Last_price > (Tmax - (0.3 * dif)):  # 下跌中且处于高点位置
            print("当前处于震荡高点")
            if Last_price > (Tmax - (0.1 * dif)):
                print("处于高点第一阶段")
                high_position(Tmax - (0.1 * dif), Tmax)

            if (Tmax - (0.2 * dif)) < Last_price < (Tmax - (0.1 * dif)):
                print("处于高点第二阶段")
                high_position(Tmax - (0.2 * dif), Tmax - (0.1 * dif))

            if (Tmax - (0.3 * dif)) < Last_price < (Tmax - (0.2 * dif)):
                print("处于高点第三阶段")
                high_position(Tmax - (0.3 * dif), Tmax - (0.2 * dif))

        if Last_price > Tmax + (0.1 * dif):
            print("上涨超过区间，平空单，做多单")
            read_db = db.find({})
            for i in db.find({}):
                print('订单查询中')
                print(i['订单号'])
                get_order_info = swapAPI.get_order_info('BTC-USDT-SWAP', i['订单号'])
                print('order state:', get_order_info['state'])

                # 如果订单已成交且为开空
                if get_order_info['state'] == "2" and get_order_info['type'] == "2":
                    print('开空订单已成交')
                    # 删除数据库中数据
                    myquery = {"订单号": i['订单号']}
                    db.delete_one(myquery)
                    # 下一个平空单
                    BTC_Ticker = swapAPI.get_specific_ticker('BTC-USDT-SWAP')
                    take_order = swapAPI.take_orders('BTC-USDT-SWAP', [
                        {"type": "4",
                         "price": float(swapAPI.get_specific_ticker('BTC-USDT-SWAP')['last']),
                         "size": n}
                    ])

            # 立马反向做多单
            take_order = swapAPI.take_orders('BTC-USDT-SWAP', [
                {"type": "1", "price": float(swapAPI.get_specific_ticker('BTC-USDT-SWAP')['last']), "size": 2 * n}
            ])
            order_id = take_order['order_info'][0]['order_id']  # 获取订单id
            get_order_info = swapAPI.get_order_info('BTC-USDT-SWAP', order_id)

            datalist = [{
                "订单号": get_order_info['order_id'],
                "价格": get_order_info['price'],
                "状态": get_order_info['state'],
                "方向": get_order_info['type']
            }]
            db.insert_many(datalist)

            # 循环寻找刚做的多单，在合适的价格平多
            while float(swapAPI.get_specific_ticker('BTC-USDT-SWAP')['last']) > Tmax + (0.1 * dif):
                trend_short = trend_short_judge()
                for i in db.find({}):
                    print('订单查询中')
                    print(i['订单号'])
                    get_order_info = swapAPI.get_order_info('BTC-USDT-SWAP', i['订单号'])
                    print('order state:', get_order_info['state'])

                    # 如果多已成交且价格且高出50
                    if get_order_info['state'] == "2" and get_order_info['type'] == "1" and float(
                            swapAPI.get_specific_ticker('BTC-USDT-SWAP')['last']) - float(
                        get_order_info['price']) > 60 and trend_short[0] == 1:
                        print('开多订单已成交且已达到目标位')
                        # 删除数据库中数据
                        myquery = {"订单号": i['订单号']}
                        db.delete_one(myquery)
                        # 下一个平多单
                        BTC_Ticker = swapAPI.get_specific_ticker('BTC-USDT-SWAP')
                        take_order = swapAPI.take_orders('BTC-USDT-SWAP', [
                            {"type": "3",
                             "price": float(swapAPI.get_specific_ticker('BTC-USDT-SWAP')['last']),
                             "size": 2 * n}
                        ])

        if Last_price < Tmin - (0.2 * dif):
            print("下跌超过区间，平多单，做空单")
            read_db = db.find({})
            for i in db.find({}):
                print('订单查询中')
                print(i['订单号'])
                get_order_info = swapAPI.get_order_info('BTC-USDT-SWAP', i['订单号'])
                print('order state:', get_order_info['state'])

                # 如果订单已成交且为开多
                if get_order_info['state'] == "2" and get_order_info['type'] == "1":
                    print('开多订单已成交')
                    # 删除数据库中数据
                    myquery = {"订单号": i['订单号']}
                    db.delete_one(myquery)
                    # 下一个平多单
                    BTC_Ticker = swapAPI.get_specific_ticker('BTC-USDT-SWAP')
                    take_order = swapAPI.take_orders('BTC-USDT-SWAP', [
                        {"type": "3",
                         "price": float(BTC_Ticker['last']),
                         "size": n}
                    ])
