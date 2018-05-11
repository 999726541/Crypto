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
        open(self.trade_symbol+'depth.p','a').write(j_str)

        _bid = round(float(msg['bids'][self.trade_depth][0]) * 1.00001,6)
        _ask = round(float(msg['asks'][self.trade_depth][0]) * 0.99999,6)
        fee = _bid*0.0005 + _ask*0.0005


        profit = _ask - _bid + 0.0000000001

        print(time.strftime('%Y-%m-%d %T'),'XXXXX++> bid : %s,ask : %s, cost/profit : %s, profit : %s ETH'%
              (_bid,_ask, fee/profit,( profit - fee )*88))
        if profit != 0:
            if fee / profit < self.trade_margin and self.processing_order is False:
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
        open(self.trade_symbol+'tradeRecord.p', 'a').write(j_str)



    def print_message(self,msg):
        print(msg)

    def _process_my_order(self,bid, ask, fee, profit):
        print('processing order .........')
        # Lock the order
        self.processing_order = True
        time.sleep(2)
        if self.simple_risk():
            self.trade_count += 1
            self._client.order_limit_buy(symbol=self.trade_symbol, quantity=self.trade_quantity, price=str(bid))
            self._client.order_limit_sell(symbol=self.trade_symbol, quantity=self.trade_quantity, price=str(ask))
            print(time.strftime('%Y-%m-%d %T'),
                  'trade %s ++> SET =====> |||| bid : %s,ask : %s, fees : %s, profit : %s ||||' % (self.trade_count
                                                                                                   , bid, ask,
                                                                                                   fee * self.trade_quantity,
                                                                                                   self.trade_quantity * (
                                                                                                   profit - fee)))
        # in order to separate order
        time.sleep(60)
        self.processing_order = False


    def start_depth(self, symbol,quantity,margin,orderDepth,numOrder):
        self.trade_quantity = quantity
        self.trade_margin = margin
        self.trade_depth = orderDepth
        self.trade_symbol = symbol
        self.trade_numOrder = numOrder
        self.start_depth_socket(symbol,self.process_depth_message,'20')

    def start_trade(self, symbol):
        self.start_trade_socket(symbol, self.process_trade_message)

    def find_bid_ask_skewness(self):
        pass
        # @TODO

    def simple_risk(self):
        my_orders = self._client.get_open_orders()
        my_orders_len = len([i['side'] for i in my_orders if i['symbol'] == self.trade_symbol])
        time.sleep(1)
        number_of_one_side_order = abs(
            len([i['side'] for i in my_orders if i['side'] == 'SELL' and i['symbol'] == self.trade_symbol]) - \
            len([i['side'] for i in my_orders if i['side'] == 'BUY' and i['symbol'] == self.trade_symbol]))
        return number_of_one_side_order < self.trade_numOrder and my_orders_len < self.trade_numOrder*2

def read_last_line_data(symbol):
    head = open(symbol + 'tradeRecord','r').readlines()
    i = head[-3]
    a = json.loads(i)
    print(a)

def print_message(msg):
    print(msg)



if __name__ == '__main__':
    s = binance_wrapper()
    # print(s._client.get_order_book(symbol='LOOMETH'))
    s.start_trade('LOOMETH')
    s.start_depth('LOOMETH',88,0.17,0,7)
    # s.start_trade('EOSETH')
    # s.start_depth('EOSETH', 4.88, 0.52, 1, 10)
    s.run()
