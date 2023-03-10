import websocket
import datetime
import pandas as pd
import json

class WebsocketService(object):
    def __init__(self):
        pass
    
    @classmethod
    def binanceWebsocket(self, currency):
        websocket.enableTrace(False)
        socket = f'wss://stream.binancefuture.com/ws/{currency}@kline_1m'
        ws = websocket.WebSocketApp(socket,
                                    on_message=self.binance_on_message,
                                    on_error=self.on_error,
                                    on_close=self.on_close,
                                    on_pong=self.on_pong)
        ws.run_forever(ping_interval=25, ping_timeout=10) # 25秒發一次ping，10秒沒收到pong就斷線，官方api文件說ping_interval設25秒可以避免斷線
    
    @classmethod
    def okxWebsocket(self):
        socket = 'wss://ws.okx.com:8443/ws/v5/public'
        wsapp = websocket.WebSocketApp(socket,
                                    on_message=self.okx_on_message,
                                    on_error=self.on_error,
                                    on_close=self.on_close,
                                    on_open=self.okx_on_open,
                                    on_pong=self.on_pong)
        wsapp.run_forever(ping_interval=25, ping_timeout=10)

    @classmethod
    def binance_on_message(self, ws, message):
        try:
            json_result = json.loads(message)
            o = json_result['k']['o']
            l = json_result['k']['l']
            h = json_result['k']['h']
            c = json_result['k']['c']
            v = json_result['k']['v']
            data = {
                'time': [str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))],
                'open': [float(o)],
                'high': [float(h)],
                'low': [float(l)],
                'close': [float(c)],
                'volume': [float(v)],
            }
            df = pd.DataFrame(data)
            df.to_csv('./Application/Api/Service/LivePrice/binance_btc.csv')
            print(df)
        except Exception as e:
            print(e)
    
    @classmethod
    def okx_on_message(self, wsapp, message):
        try:
            json_result = json.loads(message)
            result = json_result['data'][0][0:6]
            data = {
                'time': [str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))],
                'open': [float(result[1])],
                'high': [float(result[2])],
                'low': [float(result[3])],
                'close': [float(result[4])],
                'volume': [float(result[5])],
            }
            df = pd.DataFrame(data)
            df.to_csv('./Application/Api/Service/LivePrice/okx_btc.csv')
            print(df)
        except Exception as e:
            print(e)
    
    @classmethod
    def okx_on_open(self, wsapp):
        wsapp.send(json.dumps({
            "op": "subscribe",
            "args": [{
                "channel": "candle1M",
                "instId": "BTC-USDT-SWAP",
            }]
        }))

    @classmethod
    def on_error(self, ws, error):
        print(error)

    @classmethod
    def on_close(self, close_msg):
        print("### closed ###" + close_msg)

    @classmethod
    def on_pong(self, wsapp, message):
        print("Got a pong! No need to respond")
