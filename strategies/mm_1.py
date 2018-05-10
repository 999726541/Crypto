#!/bin/usr/env python3
# -*- coding:utf-8 -*-
__author__ = 'Leo Tao'
# ===============================================================================
# LIBRARIES
# ===============================================================================
from Binance.client import Client
import configparser
import os
import time
from Binance.websockets import BinanceSocketManager
import json
import threading
# ===============================================================================
# ===============================================================================


class binance_wrapper(BinanceSocketManager):
    def __init__(self):
        config = configparser.ConfigParser()
        config.read(os.path.join(os.path.dirname(__file__)) + '/apiKey.ini')
        api_key = config.get('binance_02','api_key')
        api_secret = config.get('binance_02','api_secret')

        client = Client(api_key, api_secret)
        BinanceSocketManager.__init__(self,client)
        self.trade_count = 0
        self.processing_order = False
        self.locker = threading.Lock()

    def process_depth_message(self,msg):
        msg['TS'] = time.strftime('%Y-%m-%d %T')
        j_str = json.dumps(msg) + '\n'
        open('EoSdepth.p','a').write(j_str)

        _bid = round(float(msg['bids'][3][0]) * 1.00001,6)
        _ask = round(float(msg['asks'][3][0]) * 0.99999,6)
        fee = _bid*0.0005 + _ask*0.0005


        profit = _ask - _bid
        # print(time.strftime('%Y-%m-%d %T'),'XXXXX++> bid : %s,ask : %s, cost/profit : %s, profit : %s ETH'%
        #       (_bid,_ask, fee/profit,( profit - fee )*3.88))
        if profit != 0:
            if fee / profit < .32 and fee / profit > .1 and self.processing_order is False:
                dic = {
                    'bid':_bid,
                    'ask':_ask,
                    'fee':fee,
                    'profit':profit
                }
                t = threading.Thread(target=self._process_my_order,kwargs = dic)
                t.start()




    def process_trade_message(self,msg):
        msg['TS'] = time.strftime('%Y-%m-%d %T')
        j_str = json.dumps(msg) + '\n'
        open('EoStradeRecord', 'a').write(j_str)


    def _process_my_order(self,bid, ask, fee, profit):
        print('processing order .........')
        self.processing_order = True
        time.sleep(2)
        my_orders = self._client.get_open_orders()
        my_orders_len = len([i['side'] for i in my_orders if i['symbol'] == 'EOSETH'])
        time.sleep(1)
        number_of_one_side_order = abs(
            len([i['side'] for i in my_orders if i['side'] == 'SELL' and i['symbol'] == 'EOSETH']) - \
            len([i['side'] for i in my_orders if i['side'] == 'BUY' and i['symbol'] == 'EOSETH']))
        if number_of_one_side_order < 6 and my_orders_len < 10:
            self.trade_count += 1
            self._client.order_limit_buy(symbol='EOSETH', quantity=3.88, price=str(bid))
            self._client.order_limit_sell(symbol='EOSETH', quantity=3.88, price=str(ask))
            print(time.strftime('%Y-%m-%d %T'),
                  'trade %s ++> SET =====> |||| bid : %s,ask : %s, fees : %s, profit : %s ||||' % (self.trade_count
                                                                                                   , bid, ask,
                                                                                                   fee * 3.88,
                                                                                                   3.88 * (
                                                                                                   profit - fee)))
        time.sleep(360)
        self.processing_order = False


    def start_depth(self, symbol):
        self.start_depth_socket(symbol,self.process_depth_message,'20')

    def start_trade(self, symbol):
        self.start_trade_socket(symbol, self.process_trade_message)



        # bm = BinanceSocketManager(client)
        # # streaming depth data
        # bm.start_depth_socket('LOOMETH',process_depth_message,'20')
        # bm.start_trade_socket('LOOMETH',process_depth_message)
        #
        # bm.run()

    # get market depth
    # trade_count = 0
    # while True:
    #     depth = client.get_order_book(symbol='LOOMETH')
    #     depth['TS'] = time.strftime('%Y-%m-%d %T')
    #
    #     _bid = round(float(depth['bids'][0][0]) * 1.00001,8)
    #     _ask = round(float(depth['asks'][0][0]) * 0.99999,8)
    #     fee = _bid*0.001 + _ask*0.001
    #     profit = _ask - _bid
    #     print(time.strftime('%Y-%m-%d %T'),'XXXXX++> bid : %s,ask : %s, cost/profit : %s, profit : %s ETH'%
    #           (_bid,_ask, fee/profit,( profit - fee )*88))
    #     my_orders = client.get_open_orders()
    #     number_of_one_side_order = abs(len([i['side'] for i in my_orders if i['side'] == 'SELL']) - \
    #                                len([i['side'] for i in my_orders if i['side'] == 'BUY']))
    #     j_str = json.dumps(depth) + '\n'
    #     open('depth.p','a').write(j_str)
    #
    #
    #
    #     if fee/profit < .4 and number_of_one_side_order < 2 and len(my_orders) < 7:
    #         #client.order_limit_buy(symbol = 'LOOMETH',quantity = 88, price = str(_bid))
    #         #client.order_limit_sell(symbol='LOOMETH', quantity=88, price=str(_ask))
    #         trade_count += 1
    #         print(time.strftime('%Y-%m-%d %T'),
    #               'trade %s ++> SET =====> |||| bid : %s,ask : %s, fees : %s, profit : %s ||||' % (trade_count
    #                                                                                                ,_bid, _ask, fee*88,
    #                                                                                                88*( profit - fee )))
    #         my_account = []
    #         my_account.append(client.get_asset_balance(asset='ETH'))
    #         my_account.append((client.get_asset_balance(asset='LOOM')))
    #         my_account.append(time.strftime('%Y-%m-%d %T'))
    #
    #         j_str = json.dumps(my_account) + '\n'
    #         open('tradeRecords', 'a').write(j_str)
    #
    #     time.sleep(5)


def read_data():
    for i in open('depth.p','r').readlines():
        a = json.loads(i)
        print(a['TS'])


def trade():
    config = configparser.ConfigParser()
    config.read(os.path.join(os.path.dirname(__file__)) + '/apiKey.ini')
    api_key = config.get('binance_02', 'api_key')
    api_secret = config.get('binance_02', 'api_secret')
    client = Client(api_key, api_secret)
    #client.order_limit_sell(symbol = 'LOOMETH',quantity = 8, price ='0.00088180')
    a = client.get_open_orders()
    print(a)


if __name__ == '__main__':
    s = binance_wrapper()
    s.start_trade('EOSETH')
    s.start_depth('EOSETH')
    s.run()
    # trade()