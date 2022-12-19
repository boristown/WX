import requests
import datetime

def get_price():
    # 获取当前BTCUSDT价格
    url = 'https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT'
    r = requests.get(url)
    price = float(r.json()['price'])
    #输出格式：Binance交易所的当前BTCUSDT价格为：price
    #北京时间：2020年12月25日 15:00:00
    return 'Binance交易所的当前BTCUSDT价格为：' + str(price) + '\n' +\
    '北京时间：' + str(datetime.datetime.now().strftime('%Y年%m月%d日 %H:%M:%S'))

kline_cnt = 4*24*5

def get_ohlcv_list():
    # 获取最近五天的BTCUSDT 15分钟K线数据
    url = 'https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=15m&limit=' + str(kline_cnt)
    #url = 'https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1h&limit=72'
    r = requests.get(url)
    ohlcv_list = r.json()
    return ohlcv_list