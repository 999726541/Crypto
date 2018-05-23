import gzip
import websocket
import threading
import time
import json
from Huobi.client import Client

class HuobiSocketManager():

    STREAM_URL = "wss://api.huobipro.com/ws"

    WEBSOCKET_DEPTH_5 = '5'
    WEBSOCKET_DEPTH_10 = '10'
    WEBSOCKET_DEPTH_20 = '20'

    _user_timeout = 30 * 60  # 30 minutes

    def __init__(self,acc_key,sec_key):
        self._con = {}
        self.client = Client(acc_key,sec_key)

    def _start_socket(self, requests, symbol, callback):
        '''

        订阅成功返回数据的例子
        {
          "id": "id1",
          "status": "ok",
          "subbed": "market.btcusdt.depth.step0",
          "ts": 1489474081631
        }

        '''
        ws = websocket.create_connection(self.STREAM_URL)
        ws.send(requests)
        while self._con[symbol] == True:
            compressData = ws.recv()
            result = gzip.decompress(compressData).decode('utf-8')
            if result[:7] == '{"ping"':
                ts = result[8:21]
                pong = '{"pong":' + ts + '}'
                ws.send(pong)
                ws.send(requests)
            else:
                result = json.loads(result)
                if 'status' in result.keys(): print(result)
                else:
                    callback(result)
        ws.close()
        print(symbol, ' Closed ....')

    def start_market_candle(self, symbol, id_, callback = '', span = '1min'):

        """
        {
          "sub": "market.$symbol.kline.$period",
          "id": "id generate by client"
        }


        {
          "ch": "market.btcusdt.kline.1min",
          "ts": 1489474082831,
          "tick": {
            "id": 1489464480,
            "amount": 0.0,
            "count": 0,
            "open": 7962.62,
            "close": 7962.62,
            "low": 7962.62,
            "high": 7962.62,
            "vol": 0.0   成交额, 即 sum(每一笔成交价 * 该笔的成交量)
          }
        }

        span: 1min, 5min, 15min, 30min, 60min, 1day, 1mon, 1week, 1year

        """
        if callback == '': callback = self.on_message
        tradeStr = """{"sub": "market.""" + symbol +""".kline.""" + str(span)+ """","id": """+str(id_)+"""} """
        self._con[symbol] = True
        t = threading.Thread(target=self._start_socket,kwargs={'requests':tradeStr,'symbol':symbol, 'callback':callback})
        t.start()

    def start_market_depth(self,symbol, id_, callback = '', step = 5):
        '''


        {
          "sub": "market.btcusdt.depth.step0",
          "id": "id1"
        }



        每当 depth 有更新时，client 会收到数据，例子

        {
          "ch": "market.btcusdt.depth.step0",
          "ts": 1489474082831,
          "tick": {
            "bids": [
            [9999.3900,0.0098], // [price, amount]
            [9992.5947,0.0560],
            // more Market Depth data here
            ]
            "asks": [
            [10010.9800,0.0099]
            [10011.3900,2.0000]
            //more data here
            ]
          }
        }

        :param symbol:
        :param id_:
        :param callback:
        :param step:
        :return:
        '''
        if callback == '': callback = self.on_message
        tradeStr = """{"sub": "market.""" + symbol +""".depth.step""" + str(step)+ """","id": """+str(id_)+"""} """
        self._con[symbol] = True
        t = threading.Thread(target=self._start_socket,kwargs={'requests':tradeStr,'symbol':symbol, 'callback':callback})
        t.start()

    def start_market_trade(self,symbol, id_, callback = ''):
        '''


        send:

        {
          "sub": "market.btcusdt.trade.detail",
          "id": "id1"
        }



        received:

        {
          "ch": "market.btcusdt.trade.detail",
          "ts": 1489474082831,
          "data": [
            {
              "id":        601595424,
              "price":     10195.64,
              "time":      1494495766,
              "amount":    0.2943,
              "direction": "buy",
              "tradeId":   601595424,
              "ts":        1494495766000
            },
            {
              "id":        601595423,
              "price":     10195.64,
              "time":      1494495711,
              "amount":    0.2430,
              "direction": "buy",
              "tradeId":   601595423,
              "ts":        1494495711000
            },
            // more Trade Detail data here
          ]
          }
        }
        '''
        if callback == '': callback = self.on_message
        tradeStr = """{"sub": "market.""" + symbol +""".trade.detail","id": """+str(id_)+"""} """
        self._con[symbol] = True
        t = threading.Thread(target=self._start_socket,kwargs={'requests':tradeStr,'symbol':symbol, 'callback':callback})
        t.start()

    def close_by_id(self,symbol):
        self._con[symbol] = False

    def on_message(self,msg):
        print(msg)


if __name__ == '__main__':
    import configparser
    config = configparser.ConfigParser()
    config.read('../strategies/apiKey.ini')
    api_key = config.get('huobi_01', 'api_key')
    api_secret = config.get('huobi_01', 'api_secret')
    huobi = HuobiSocketManager(api_key, api_secret)
    # huobi.start_market_candle('btcusdt','99',span='1week')
    # time.sleep(5)
    # huobi.close_by_id('btcusdt')
    #print(huobi.client.orders_list('htusdt','submitted'))
    #huobi.client.cancel_order(4795110491)