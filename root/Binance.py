import requests
import datetime
from collections import *

get_price_btc_ts = 0
get_price_btc_price = 0

def get_price_btc():
    #增加缓存，同一秒钟内只获取一次价格
    global get_price_btc_ts, get_price_btc_price
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if timestamp == get_price_btc_ts:
        return get_price_btc_price
    else:
        get_price_btc_ts = timestamp
        # 获取当前BTCUSDT价格
        url = 'https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT'
        r = requests.get(url)
        price = float(r.json()['price'])
        get_price_btc_price = price
        return price

get_price_eth_ts = 0
get_price_eth_price = 0

def get_price_eth():
    #增加缓存，同一秒钟内只获取一次价格
    global get_price_eth_ts, get_price_eth_price
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if timestamp == get_price_eth_ts:
        return get_price_eth_price
    else:
        get_price_eth_ts = timestamp
        # 获取当前ETHUSDT价格
        url = 'https://api.binance.com/api/v3/ticker/price?symbol=ETHUSDT'
        r = requests.get(url)
        price = float(r.json()['price'])
        get_price_eth_price = price
        return price

get_price_symbol_ts = defaultdict(int)
get_price_symbol_price = {}

def get_price_symbol(symbol):
    #增加缓存，同一秒钟内只获取一次价格
    global get_price_symbol_ts, get_price_symbol_price
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if timestamp == get_price_symbol_ts[symbol]:
        return get_price_symbol_price[symbol]
    else:
        get_price_symbol_ts[symbol] = timestamp
        # 获取当前symbol价格
        url = 'https://api.binance.com/api/v3/ticker/price?symbol=' + symbol
        r = requests.get(url)
        price = float(r.json()['price'])
        get_price_symbol_price[symbol] = price
        return price
    
def get_price():
    # 获取当前BTCUSDT价格
    price = get_price_btc()
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
