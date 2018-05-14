#!/bin/usr/env python3
# -*- coding:utf-8 -*-
__author__ = 'Leo Tao'
# ===============================================================================
# LIBRARIES
# ===============================================================================
import os,sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import json
import pandas as pd
# ===============================================================================
# ===============================================================================



def read_last_trade_data(symbol,length_of_read):
    head = open(symbol + 'tradeRecord.p','r').readlines()
    for i in range(length_of_read):
        i = head[-length_of_read+i]
        a = json.loads(i)
        print(a)
        a = pd.DataFrame().append(a,ignore_index=True)
        print(a)
        break

def read_last_depth(symbol,length_of_read):
    head = open(symbol + 'depth.p', 'r').readlines()
    bid = []
    ask = []
    spread = []
    ts = []
    quantity_bid = []
    quantity_ask = []
    for i in range(length_of_read):
        i = head[-length_of_read + i]
        a = json.loads(i)
        bid_p = []
        bid_q = []
        ask_p = []
        ask_q = []
        bid.append(float(a['bids'][0][0]))
        ask.append(float(a['asks'][0][0]))
        quantity_bid.append(float(a['bids'][0][1]))
        quantity_ask.append(float(a['asks'][0][1]))
        ts.append(a['TS'])
        # for bid in a['bids']:
        #     bid_p.append(float(bid[0]))
        #     bid_q.append(float(bid[1]))
        #
        # for ask in a['asks']:
        #     ask_p.append(float(ask[0]))
        #     ask_q.append(float(ask[1]))
        # break
    d = pd.DataFrame({'ts':ts,'bid':bid,'ask':ask,'q_bid':quantity_bid,'q_ask':quantity_ask})
    return d

if __name__ == '__main__':
    d = read_last_depth('LOOMETH',10000)