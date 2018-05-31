#!/bin/usr/env python3
# -*- coding:utf-8 -*-
__author__ = 'Leo Tao'
# ===============================================================================
# LIBRARIES
# ===============================================================================
import os,sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from Huobi.HBWebsocket import HuobiSocketManager
import json
import threading
import configparser
import datetime
# ===============================================================================
# ===============================================================================


class huobi_manager(HuobiSocketManager):
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('../strategies/apiKey.ini')
        api_key = config.get('huobi_01', 'api_key')
        api_secret = config.get('huobi_01', 'api_secret')
        HuobiSocketManager.__init__(self,api_key,api_secret)

    def depth_data_handler(self,msg):
        '''
        Handle the depth massage
        :param msg:
        :return:
        '''
        level = 0

        print(datetime.datetime.fromtimestamp(msg['ts']/1000))
        print('TS %s :level 2 : bid %s @ %s ask %s @ %s, spread: %s, profits: %s'%(
            datetime.datetime.fromtimestamp(msg['ts'] / 1000),msg['tick']['bids'][level][0],msg['tick']['bids'][level][1],
            msg['tick']['asks'][level][0],msg['tick']['asks'][level][1],
            msg['tick']['asks'][level][0] - msg['tick']['bids'][level][0],
            (msg['tick']['asks'][level][0] - msg['tick']['bids'][level][0] - (msg['tick']['asks'][level][0] + msg['tick']['bids'][level][0])*0.002)
            /(msg['tick']['asks'][level][0] - msg['tick']['bids'][level][0]) ))



    def streaming_depth(self,symbol, id_):
        '''
        start recording depth message
        :param symbol:
        :param id_:
        :return:
        '''
        self.start_market_depth(symbol,id_,self.depth_data_handler,step=0)

if __name__ == '__main__':
    huobi = huobi_manager()
    huobi.streaming_depth('zrxeth','123')