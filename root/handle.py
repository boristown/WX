# -*- coding: utf-8 -*-
# filename: handle.py

import werobot
import werobot.client
import werobot.replies
import re
#import binance_api
from pymouse import PyMouse
from pykeyboard import PyKeyboard
from time import sleep,time
from multiprocessing import Process
import pyperclip
import pyscreenshot as ImageGrab
from Basic import *
from Media import *
import json
from collections import *
from sortedcontainers import SortedList
import bisect
import os
import datetime
import plotly.express as px
#import matplotlib.pyplot as plt
import pandas as pd

pic_url = ""

def process_task(s,user):
    m = PyMouse()
    k = PyKeyboard()
    m.click(60,95,1,1)
    pyperclip.copy(s)
    sleep(1)
    m.click(585,550,1,1)
    sleep(1)
    k.press_key(k.control_key)
    k.tap_key('v')
    k.release_key(k.control_key)
    k.tap_key(k.enter_key)

def save_img(user,target,ts):
    filename ='img/temp'+str(time.time()*1000)+'.jpg'
    im = ImageGrab.grab((450,70,1090,490))
    im.save(filename)
    im.close()
    pic_url = picture_url(filename)
    #return pic_url
    return werobot.replies.ImageReply(media_id=pic_url,target=user,source=target,time=ts)

pattern1 = r"1\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)"
patternc = r"c\s+(\d+)\s+(\d+)"

def screen_shot(user,target,ts,x1, y1, x2, y2):
    filename ='img/temp'+str(time.time()*1000)+'.jpg'
    #print(x1,y1,x2,y2)
    im = ImageGrab.grab(tuple(map(int,(x1, y1, x2, y2))))
    im.save(filename)
    im.close()
    pic_url = picture_url(filename)
    #return pic_url
    return werobot.replies.ImageReply(media_id=pic_url,target=user,source=target,time=ts)

current_contest = 1
current_contest_start_date = '20221221'
current_contest_duration = 3

contest_dict = {}

#“AI纪元”的第一轮量化交易竞赛将于北京时间2022年12月19日8点开始，持续三天，结束于2022年12月21日8点。
#本次竞赛的交易品种是BTCUSDT，交易所是Binance。
#每位选手的初始等级分为1500分，每位选手的初始资金为1000000美元，每位选手的最大杠杆为10倍，交易手续费为0.1%。
#选手可以使用杠杆做多或者做空，也可以不使用杠杆直接买入或者卖出。
#默认有一个虚拟的基准线选手参赛，基准线选手不发起交易，收益0，等级分1000。
#比赛结束后，根据每个参赛选手的资金余额，进行排名。
#除了基准线选手，其他选手的等级分根据ELO规则进行更新。
def load_reg_set():
    fname = 'data/reg_set'+str(current_contest)+'.json'
    fexist = os.path.exists(fname)
    if fexist:
        with open(fname, 'r+') as f:
            #如果文件f不为空，则载入到reg_set中，否则新建一个set
            reg_set = set(json.load(f))
    else:
        reg_set = set()
    return reg_set

def save_reg_set(reg_set):
    fname = 'data/reg_set'+str(current_contest)+'.json'
    print("save:"+fname)
    with open(fname, 'w+') as f:
        json.dump(list(reg_set), f)

def load_contest_rank():
    fname = 'data/contest_rank'+str(current_contest)+'.json'
    fexist = os.path.exists(fname)
    if fexist:
        with open(fname, 'r+') as f:
            #如果文件f不为空，则载入到contest_rank中，否则新建一个dict
            contest_rank = json.load(f)
    else:
        contest_rank = []
    return contest_rank

def save_contest_rank(contest_rank):
    fname = 'data/contest_rank'+str(current_contest)+'.json'
    with open(fname, 'w+') as f:
        json.dump(contest_rank, f)

def load_name_dict():
    fname = 'data/name_dict.json'
    fexist = os.path.exists(fname)
    if fexist:
        with open(fname, 'r+') as f:
            #如果文件f不为空，则载入到name_dict中，否则新建一个dict
            name_dict = json.load(f)
    else:
        name_dict = {}
    return name_dict

def save_name_dict(name_dict):
    fname = 'data/name_dict.json'
    with open(fname, 'w+') as f:
        json.dump(name_dict, f)

def load_elo_dict():
    fname = 'data/elo_dict.json'
    fexist = os.path.exists(fname)
    if fexist:
        with open(fname, 'r+') as f:
            #如果文件f不为空，则载入到elo_dict中，否则新建一个dict
            elo_dict = json.load(f)
    else:
        elo_dict = {}
    return elo_dict

def save_elo_dict(elo_dict):
    fname = 'data/elo_dict.json'
    with open(fname, 'w+') as f:
        json.dump(elo_dict, f)

def load_elo_list():
    fname = 'data/elo_list.json'
    fexist = os.path.exists(fname)
    if fexist:
        with open(fname, 'r+') as f:
            elo_list = SortedList(json.load(f))
    else:
        elo_list = SortedList()
    return elo_list

def save_elo_list(elo_list):
    fname = 'data/elo_list.json'
    with open(fname, 'w+') as f:
        json.dump(elo_list[:], f)
    
def chat_register(s,user):
    #如果输入信息为“注册比赛 [用户名]”,则将该用户名添加到user对应的字典reg_dict中,然后用json序列化并存储到本地文件reg_dict.data中
    match = re.match(r"注册比赛\s+(\S+)", s)
    if match:
        reg_set = load_reg_set()
        name_dict = load_name_dict()
        elo_dict = load_elo_dict()
        elo_list = load_elo_list()
        contest_rank = load_contest_rank()
        username = match.group(1)
        #判断该用户名是否已经被其它用户注册
        if username in name_dict:
            user2 = name_dict[username]
            if user2 != user:
                return "用户名'"+username+"'已被其它用户注册！"
        name_dict[username] = user
        save_name_dict(name_dict)
        #判断该用户是否已经注册过
        if username in reg_set:
            return "您已经注册过了！"
        last_name = ""
        for reg_user in reg_set:
            if user == name_dict[reg_user]:
                reg_set.remove(reg_user)
                last_name = reg_user
                break
        reg_set.add(username)
        save_reg_set(reg_set)
        if username not in elo_dict:
            elo_dict[username] = 1500
            elo_list.add(elo_dict[username])
        contest_rank.append([username,1000000])
        save_contest_rank(contest_rank)
        rank = elo_list.bisect_left(elo_dict[username]) + 1
        save_elo_dict(elo_dict)
        save_elo_list(elo_list)
        start_time = current_contest_start_date
        start_time = start_time[:4] + "年" + start_time[4:6] + "月" + start_time[6:] + "日"
        duration = current_contest_duration
        if not last_name:
            return str(username) + ',您好！\n' +\
            '欢迎注册AI纪元第' + str(current_contest) + '场量化交易比赛，您是本场比赛的第' + str(len(reg_set)) + '位注册选手，您的当前等级分是' + str(elo_dict[username]) + '分（全球第' + str(rank) + '/' + str(len(name_dict)) + '名）。\n' +\
            '比赛开始时间北京时间：' + str(start_time) +'8点，持续时间' + str(duration) + '天。\n' +\
            '本场比赛支持的交易品种是BTCUSDT（交易所Binance），初始资金为1000000 USDT，最大杠杆为10倍，交易手续费为0.1%。\n' +\
            '输入"指令"查看交易指令，输入"比赛排名"查看比赛排名，输入“取消注册比赛”取消注册比赛。'
        else:
            return str(username) + ',您好！\n' +\
            '欢迎注册AI纪元第' + str(current_contest) + '场量化交易比赛。\n您的参赛账号"' + last_name + '"已切换为"' + username + '"\n' +\
            '您是本场比赛的第' + str(len(reg_set)) + '位注册选手，您的当前等级分是' + str(elo_dict[username]) + '分（全球第' + str(rank) + '/' + str(len(name_dict)) + '名）。\n' +\
            '比赛开始时间北京时间：' + str(start_time) +'8点，持续时间' + str(duration) + '天。\n' +\
            '本场比赛支持的交易品种是BTCUSDT（交易所Binance），初始资金为1000000 USDT，最大杠杆为10倍，交易手续费为0.1%。\n' +\
            '输入"指令"查看交易指令，输入"比赛排名"查看比赛排名，输入“取消注册比赛”取消注册比赛。'
    else:
        return None

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

def draw_price_chart(user,target,ts):
    # 绘制BTCUSDT价格走势图(最近三天，1小时K线)，保存到img/btcusdt.png
    ohlcv_list = get_ohlcv_list()
    #print(ohlcv_list)
    df = pd.DataFrame(ohlcv_list, columns=['time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
    df['time'] = pd.to_datetime(df['time'], unit='ms')
    df['close_time'] = pd.to_datetime(df['close_time'], unit='ms')
    df = df.set_index('time')
    df = df[['open', 'high', 'low', 'close', 'volume']]
    df = df.iloc[-kline_cnt:]
    df['close'] = df['close'].astype(float)
    #print(df['close'])
    #填充为实心图
    fig = df['close'].plot.line(figsize=(16, 9), title='BTCUSDT 5 Days\n' +\
        str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    ).get_figure()
    filename = 'img/btcusdt.png'
    fig.savefig(filename)
    pic_url = picture_url(filename)
    #清空变量
    df = None
    fig = None
    ohlcv_list = None
    return werobot.replies.ImageReply(media_id=pic_url,target=user,source=target,time=ts)

def chat_command(s,user,target,ts):
    if s == '指令':
        return '可用指令：\n' +\
        '1.输入"价格"，查询当前binance交易所的BTCUSDT市场价格。\n' +\
        '2.输入"价格图表"，查询最近三天的价格曲线。\n' +\
        '2.输入"买入 金额"，例如"买入 10000"，表示买入价值10000USDT的BTC。\n' +\
        '3.输入"卖出 数量"，例如"卖出 1"，表示卖出1个BTC。\n' +\
        '4.输入"做多 金额"，例如"做多 10000"，表示做多价值10000USDT的BTC。\n' +\
        '5.输入"做空 数量"，例如"做空 1"，表示做空1个BTC。\n' +\
        '6.输入"持仓"，查看当前持仓。\n' +\
        '7.输入"资金"，查看当前资金。\n' +\
        '8.输入"比赛排名"，查看比赛排名。\n' +\
        '9.输入"注册比赛 用户名"，注册比赛或切换用户名。\n' +\
        '10.输入"取消注册比赛"，取消注册比赛。'
    elif s == '比赛排名':
        contest_rank = load_contest_rank()
        reg_set = load_reg_set()
        #contest_rank是一个list，每个元素是一个tuple，tuple的第一个元素是账号，第二个元素是余额
        #返回Top10排名
        #输出格式：比赛排名：\n1.账号1 余额1\n2.账号2 余额2\n...
        rank = 1
        res = '比赛排名：\n'
        #抬头信息
        res += '排名' + ' ' + '账号' + ' ' + '余额' + '\n'
        for name,profit in contest_rank:
            if name in reg_set:
                res += str(rank) + '.' + name + ' ' + str(profit) + '\n'
                rank += 1
            if rank > 10: break
        return res
    elif s == '取消注册比赛':
        reg_set = load_reg_set()
        name_dict = load_name_dict()
        for reg_name in reg_set:
            if name_dict[reg_name] == user:
                reg_set.remove(reg_name)
                save_reg_set(reg_set)
                return '您的参赛账号"' + reg_name + '"已取消注册比赛。'
        return '您未注册比赛。'
    elif s == '价格':
        return get_price()
    elif s == '价格图表':
        return draw_price_chart(user,target,ts)
    else:
        return '输入"指令"查看可用指令。'

def chat(s,user,target,ts):
    #if s == '1':
    #    return save_img(user,target,ts)
    #else:
        res = chat_register(s,user)
        if res: return res
        res = chat_command(s,user,target,ts)
        if res: return res
    #     match1 = re.match(pattern1, s)
    #     if match1:
    #         x1, y1, x2, y2 = match1.groups()
    #         return screen_shot(user,target,ts,x1, y1, x2, y2)
    #     matchc = re.match(patternc, s)
    #     if matchc:
    #         x,y = matchc.groups()
    #         LClick(x,y)
    #         return
    #     process_task(s,user)
    # ans = "您的输入信息已经发送给ChatGPT，输入'1'查看截图。"# + str(user)
    # return ans

def LClick(x, y):
    mouse = PyMouse()
    mouse.click(x,y,1,1)
    
def picture_url(picture_name):
    myMedia = Media()
    accessToken = Basic().get_access_token()
    filePath = picture_name
    mediaType = "image"
    murlResp = Media.uplaod(accessToken, filePath, mediaType)
    return murlResp
