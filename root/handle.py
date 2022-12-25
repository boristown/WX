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
from files import *
from Binance import *
from elo import *
import math

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
current_contest_duration = 4

contest_dict = {}

#“AI纪元”的第一轮量化交易竞赛将于北京时间2022年12月19日8点开始，持续三天，结束于2022年12月21日8点。
#本次竞赛的交易品种是BTCUSDT，交易所是Binance。
#每位选手的初始等级分为1500分，每位选手的初始资金为1000000美元，每位选手的最大杠杆为10倍，交易手续费为0.1%。
#选手可以使用杠杆做多或者做空，也可以不使用杠杆直接买入或者卖出。
#默认有一个虚拟的基准线选手参赛，基准线选手不发起交易，收益0，等级分1000。
#比赛结束后，根据每个参赛选手的资金余额，进行排名。
#除了基准线选手，其他选手的等级分根据ELO规则进行更新。

def chat_register(s,user):
    #如果输入信息为“注册比赛 [用户名]”,则将该用户名添加到user对应的字典reg_dict中,然后用json序列化并存储到本地文件reg_dict.data中
    match = re.match(r"注册比赛\s+(\S+)", s)
    if match:
        reg_set = load_reg_set()
        name_dict = load_name_dict()
        elo_dict = load_elo_dict()
        #elo_list = load_elo_list()
        #contest_rank = load_contest_rank()
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
        elo_list = []
        if username not in elo_dict:
            elo_dict[username] = 1500
        for username in elo_dict:
            elo_list.append(elo_dict[username])
        elo_list.sort()
        #contest_rank.append([username,1000000])
        #save_contest_rank(contest_rank)
        rank = elo_list.bisect_left(elo_dict[username]) + 1
        save_elo_dict(elo_dict)
        #save_elo_list(elo_list)
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

def draw_price_chart(user,target,ts):
    # 绘制BTCUSDT价格走势图(最近三天，1小时K线)，保存到img/btcusdt.png
    ohlcv_list = get_ohlcv_list()
    #print(ohlcv_list)
    df = pd.DataFrame(ohlcv_list, columns=['time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
    df['time'] = pd.to_datetime(df['time'], unit='ms')
    df['close_time'] = pd.to_datetime(df['close_time'], unit='ms')
    df = df.set_index('time')
    df = df[['open', 'high', 'low', 'close', 'volume']]
    df = df.iloc[:]
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
        '【BTCUSDT价格】：查询BTCUSDT市场最近五天的价格曲线。\n' +\
        '【买入/做多 BTCUSDT 金额U】：例如"买入 10000U"，表示买入价值10000USDT的BTC（买入时默认此单位）。\n' +\
        '【买入/做多 BTCUSDT 数量B】：例如"做多 1B"，表示做多1个BTC。\n' +\
        '【卖出/做空 BTCUSDT 金额U】：例如"卖出 10000U"，表示卖出价值10000USDT的BTC。\n' +\
        '【卖出/做空 BTCUSDT 数量B】：例如"做空 1B"，表示做空1个BTC。（卖出时默认此单位）\n' +\
        '【买入/做多 ETHBTC 数量ETH】：例如"买入 ETHBTC 100ETH"，表示在ETHBTC市场买入100个ETH。\n' +\
        '【买入/做多 ETHBTC 数量BTC】或【买入/做多 ETHBTC 数量B】：例如"买入 ETHBTC 1BTC"，表示在ETHBTC市场用1个BTC买入ETH。（买入时默认此单位）\n' +\
        '【买入/做多 ETHBTC 金额USDT】或【买入/做多 ETHBTC 金额U】：例如"买入 ETHBTC 10000U"，表示在ETHBTC市场买入价值10000USDT的ETH。\n' +\
        '【持仓】或【资金】：查看当前持仓和资金。\n' +\
        '【比赛排名】：查看比赛排名。\n' +\
        '【注册比赛 用户名】：注册比赛或切换用户名。\n' +\
        '【取消注册比赛】：取消注册比赛。\n' +\
        '【比赛结果】：查看最近一轮比赛结果。'
    elif s == '比赛排名' or s == '排名' or s == '排行榜' or s == '排行' or s == '比赛排行':
        return show_contest_rank()
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
    elif s == '持仓' or s == '资金':
        return get_position(user)
    elif s == '价格图表' or s == '价格曲线':
        return draw_price_chart(user,target,ts)
    elif s == '重置比赛':
        return reset_contest(user)
    elif s == '比赛结果':
        return show_contest_result()
    else:
        #字符串分割
        #字符串格式：side symbol amount unit
        #其中side为买入/卖出/做多/做空
        #symbol为字母序列
        #amount为数字序列
        #unit为U/B，对于买入/做多指令，unit默认为U，对于卖出/做空指令，unit默认为B
        #side symbol amount unit之间可以有任意多个空格，也可以没有空格
        def get_symbol_amount_unit(s):
            #将字符串s分割为side symbol amount unit
            #返回值为(side,symbol,amount,unit)
            #如果s格式错误，返回值为(None,None,None,None)
            #注意：side symbol amount unit之间可以有任意多个空格，也可以没有空格
            #可以没有unit：对于买入/做多指令，unit默认为U，对于卖出/做空指令，unit默认为B
            s = s.upper()
            s.strip()
            n = len(s)
            if n<2:
                return (None,None,None,None)
            side = s[:2]
            if side != '买入' and side != '卖出' and side != '做多' and side != '做空':
                return (None,None,None,None,"无效指令，输入'指令'查看可用指令列表。")
            s = s[2:]
            s.strip()
            symbol = ''
            for i in range(len(s)):
                if s[i].isalpha():
                    symbol += s[i]
                else:
                    break
            s = s[len(symbol):]
            s.strip()
            if symbol == '':
                symbol = 'BTCUSDT'
            curr1,curr2 = split_symbol(symbol)
            amount = 0
            for i in range(len(s)):
                if s[i].isdigit():
                    amount = amount*10 + int(s[i])
                else:
                    break
            s = s[len(str(amount)):]
            s.strip()
            if amount == 0:
                return (None,None,None,None,"数量不能为0")
            unit = ''
            for i in range(len(s)):
                if s[i].isalpha():
                    unit += s[i]
                else:
                    break
            if unit == '':
                if side == '买入' or side == '做多':
                    unit = curr2
                else:
                    unit = curr1
            if unit == 'U':
                unit = 'USDT'
            elif unit == 'B':
                unit = 'BTC'
            return (side,symbol,amount,unit,"")

        side,symbol,amount,unit,msg = get_symbol_amount_unit(s)
        if not side:
            return msg
        if side == '买入':
            return buy(user,symbol,amount,unit,False)
        elif side == '卖出':
            return sell(user,symbol,amount,unit,False)
        elif side == '做多':
            return buy(user,symbol,amount,unit,True)
        elif side == '做空':
            return sell(user,symbol,amount,unit,True)
        else:
            return '输入"指令"查看可用指令。'

def show_contest_result():
    roundx = str(get_current_round() - 1)
    ch = load_contest_history()
    reg_set = load_reg_set()
    if roundx in ch:
        contest = ch[roundx]
        #显示排行榜
        res = '第' + roundx + '轮比赛结果：\n'
        res += '排名' + ' ' + '账号' + ' ' + '余额' + ' ' + '表现分' + ' ' + 'ELO分' + '\n'
        rank = 0
        for plyer in contest:
            if plyer['name'] in reg_set:
                delta = plyer['new_rate'] - plyer['rate']
                SIGN = '+' if delta >= 0 else ''
                res += str(plyer['rank']) + ' ' + plyer['name'] + ' ' + str(round(plyer['score'],2)) + ' ' + str(plyer['performance']) + ' ' + str(plyer['new_rate'])+'('+SIGN+str(delta)+')' + '\n'
                rank += 1
            if rank > 10: break
        return res
    else:
        return str(roundx) + '轮比赛尚未结束。'

def get_current_round():
    #获取当前轮数
    #输出格式：当前轮数
    #效果：返回当前轮数
    start_date = current_contest_start_date #开始日期UTC时间：格式：'20200101'
    duration = current_contest_duration #天数，格式：'1'
    #计算比赛持续的时间
    start_date = datetime.datetime.strptime(start_date,'%Y%m%d')
    end_date = start_date + datetime.timedelta(days=int(duration))
    #根据当前时间计算比赛进行到第几分钟
    now = datetime.datetime.utcnow()
    #if now > end_date:
    #    return '比赛已经结束。'
    #print((now - end_date).seconds)
    roundx = math.ceil((now - end_date).seconds/(7*24*60*60)) + 1
    return roundx

def reset_contest(user):
    #重置比赛
    #只有用户"AI纪元"可以使用此指令
    #输出格式：重置成功
    #效果：重置所有用户的余额为1000000USDT
    #抬头信息
    reg_set = load_reg_set()
    name_dict = load_name_dict()
    #contest_rank = load_contest_rank()
    if name_dict["AI纪元"] != user:
        return '您无权使用此指令。'
    for reg_name in reg_set:
        user_id = name_dict[reg_name]
        user_account = load_user_account(user_id)
        user_account['USDT'] = 1000000
        user_account['BTC'] = 0
        save_user_account(user_id,user_account)
    #n = len(contest_rank)
    #for i in range(n):
    #    contest_rank[i][1] = 1000000
    #save_contest_rank(contest_rank)
    return '重置成功。'

def get_position(user):
    #返回用户的持仓和资金
    #输出格式：用户：用户名：\nBTC:数量\nUSDT:余额\n估值：估值\n杠杆率：杠杆率
    #抬头信息
    reg_set = load_reg_set()
    name_dict = load_name_dict()
    user_name = ""
    for reg_name in reg_set:
        if name_dict[reg_name] == user:
            user_name = reg_name
            break
    if user_name == "":
        return '您未注册比赛，输入"注册比赛 用户名"注册比赛。'
    user_account = load_user_account(user)
    #格式：{'BTC':0,'USDT':1000}
    price = get_price_btc()
    #格式：{'BTC':10000,'USDT':1}
    res = get_contest_text() + '\n'
    res += '用户：' + user_name + '\n'
    res += 'BTC：' + str(user_account['BTC']) + '\n'
    res += 'USDT：' + str(user_account['USDT']) + '\n'
    res += '估值：' + str(user_account['BTC']*price + user_account['USDT']) + '\n'
    res += '杠杆率：' + str(get_leverage(user_account))
    return res

def get_contest_text():
    #已知第一场比赛的开始日期是current_contest_start_date，比赛的持续时间是current_contest_duration天
    #从第二场比赛开始，每场比赛的开始时间是上一场比赛的结束时间，持续时间变为7天
    #比赛的轮数是从1开始计数的

    #返回比赛信息
    #输出格式：第几轮比赛，第几分钟，距离比赛结束还有几分钟
    status = load_status()
    #抬头信息
    start_date = current_contest_start_date #开始日期UTC时间：格式：'20200101'
    duration = current_contest_duration #天数，格式：'1'
    #计算比赛持续的时间
    start_date = datetime.datetime.strptime(start_date,'%Y%m%d')
    end_date = start_date + datetime.timedelta(days=int(duration))
    #根据当前时间计算比赛进行到第几分钟
    now = datetime.datetime.utcnow()
    if now < start_date:
        return '比赛还未开始。'
    #if now > end_date:
    #    return '比赛已经结束。'
    #print((now - end_date).seconds)
    roundx = math.ceil((now - end_date).seconds/(7*24*60*60)) + 1
    if roundx > 1:
        start_date = end_date + datetime.timedelta(days=(roundx-2)*7)
        duration = 7
    if status["settled"] < roundx - 1:
        settle_contest(roundx - 1)
    delta = now - start_date
    delta_minutes = delta.days*24*60 + delta.seconds//60
    #计算比赛还有多少分钟
    left_minutes = 60*24*int(duration) - delta_minutes
    #计算比赛还有多少天
    left_days = left_minutes//(24*60)
    left_hours = (left_minutes - left_days*24*60)//60
    left_minutes = left_minutes - left_days*24*60 - left_hours*60
    #计算比赛进行到第几天
    delta_days = delta_minutes//(24*60)
    delta_hours = (delta_minutes - delta_days*24*60)//60
    delta_minutes = delta_minutes - delta_days*24*60 - delta_hours*60

    contest_text = '第' + str(roundx) + '轮比赛，第' + str(delta_days) + '天' \
    + str(delta_hours) + '小时' + str(delta_minutes) + '分钟，距离比赛结束还有' \
    + str(left_days) + '天' + str(left_hours) + '小时' + str(left_minutes) + '分钟。'
    return contest_text

def settle_contest(roundx):
    #更新选手的ELO分，然后重置选手的账户
    reg_set = load_reg_set()
    name_dict = load_name_dict()
    #contest_rank = load_contest_rank()
    elo_dict = load_elo_dict()
    contest_history = load_contest_history()
    #计算ELO分
    price = get_price_btc()
    contest_rank_new = []
    for name in reg_set:
        #if name in reg_set:
        user_account = load_user_account(name_dict[name])
        score = user_account['BTC']*price + user_account['USDT']
        rate = elo_dict[name]
        contest_rank_new.append({'name':name,'rate':rate,'score':score})
    elo.init_players(contest_rank_new)
    elo.calc_performance(contest_rank_new)
    for player in contest_rank_new:
        elo_dict[player['name']] = player['new_rate']
    del contest_history[roundx]
    contest_history[roundx] = contest_rank_new
    save_contest_history(contest_history)
    save_elo_dict(elo_dict)
    for reg_name in reg_set:
        user_id = name_dict[reg_name]
        user_account = load_user_account(user_id)
        for currency in user_account:
            if currency == 'USDT':
                user_account[currency] = 1000000
            else:
                user_account[currency] = 0
        save_user_account(user_id,user_account)
    #reset_contest()
    status = load_status()
    status["settled"] = roundx
    save_status(status)

class elo:
    #等级分差 = 对手等级分 - 自己等级分
    def get_rate_diff(rate_other, rate_self):
        return rate_other - rate_self

    #胜率计算公式：胜率 = 1 / (1 + 10 ^ (等级分差 / 400))
    def get_win_rate(rate_diff):
        return 1 / (1 + math.pow(10, rate_diff / 400))

    #通过以上函数的反函数计算等级分差：等级分差 = 400 * ln(1 / 胜率 - 1)
    def get_rate_diff_by_win_rate(win_rate):
        if win_rate == 1:
            return -float("inf")
        if win_rate == 0:
            return float("inf")
        return 400 * math.log(1 / win_rate - 1, 10)
    
    #其他选手的等级分的平均值 = 所有其他选手的等级分的和 / 所有其他选手的数量
    def get_rate_other_avg(rate_other_list):
        return sum(rate_other_list) / len(rate_other_list)
    
    #相对于其它选手的胜率 = 相对于其它选手的胜出次数 / 所有其他选手的数量
    def get_win_rate_other(win_rate_other_list):
        return sum(win_rate_other_list) / len(win_rate_other_list)
    
    def init_players(plyers):
        #格式：[{'name': '选手1', 'rate': 1000, 'score': 100.0}, {'name': '选手2', 'rate': 1000, 'score': 99.0}, {'name': '选手3', 'rate': 1000, 'score': 101.0}]
        n = len(plyers)
        if n == 1:
            n = 2
            plyers.append({'name': '选手2', 'rate': 1500, 'score': 1000000.0})
        plyers.sort(key=lambda x: x['score'], reverse=True)
        lst = float('inf')
        for i in range(n):
            if plyers[i]['score'] != lst:
                lst = plyers[i]['score']
                rk = i + 1
            plyers[i]['rank'] = rk

    #表现分计算公式：表现分 = 其他选手的等级分的平均值 + 400 * ln(1 / 相对于其它选手的胜率 - 1) if 0 < 相对于其它选手的胜率 < 1
    def calc_performance(plyers):
        n = len(plyers)
        rate_sum = sum(plyers[i]['rate'] for i in range(n))
        rank_list = [plyers[i]['rank'] for i in range(n)]
        print(rank_list)
        for i in range(n):
            rate_other_avg = (rate_sum - plyers[i]['rate']) / (n - 1)
            p1 = bisect.bisect_left(rank_list, plyers[i]['rank'])
            p2 = bisect.bisect_right(rank_list, plyers[i]['rank'])
            print(p1,p2,plyers[i]['rank'])
            win_cnt = n-p2
            draw_cnt = p2-p1-1
            win_rate = (win_cnt+0.5*draw_cnt)/(n-1)
            plyers[i]['performance'] = rate_other_avg - elo.get_rate_diff_by_win_rate(win_rate)
            x = sum(elo.get_win_rate(plyers[j]['rate']-plyers[i]['rate']) for j in range(n) if j != i)
            plyers[i]['new_rate'] = plyers[i]['rate'] + 30 * (win_cnt + 0.5 * draw_cnt - x)
            plyers[i]['new_rate'] = round(plyers[i]['new_rate'],2)
            plyers[i]["performance"] = round(plyers[i]["performance"],2)

def show_contest_rank():
    #contest_rank = load_contest_rank()
    reg_set = load_reg_set()
    name_dict = load_name_dict()
    rate_dict = load_elo_dict()
    #contest_rank是一个list，每个元素是一个tuple，tuple的第一个元素是账号，第二个元素是余额
    #返回Top10排名
    #输出格式：比赛排名：\n1.账号1 余额1\n2.账号2 余额2\n...
    rank = 1
    res = get_contest_text() + '\n比赛排名：\n'
    price = get_price_btc()
    #抬头信息
    
    contest_rank_new = []
    for name in reg_set:
        #if name in reg_set:
        user_account = load_user_account(name_dict[name])
        score = user_account['BTC']*price + user_account['USDT']
        rate = rate_dict[name]
        contest_rank_new.append({'name':name,'rate':rate,'score':score})
            #res += str(rank) + '.' + name + ' ' + str(profit) + '\n'
            #rank += 1
        #if rank > 10: break
    elo.init_players(contest_rank_new)
    elo.calc_performance(contest_rank_new)
    #contest_rank_new.sort(key=lambda x:x[1],reverse=True)
    #save_contest_rank([[plyer["name"],plyer["score"]] for plyer in contest_rank_new])
    res += '排名' + ' ' + '账号' + ' ' + '余额' + ' ' + '表现分' + ' ' + 'ELO分' + '\n'
    for plyer in contest_rank_new:
        if plyer['name'] in reg_set:
            delta = plyer['new_rate'] - plyer['rate']
            SIGN = '+' if delta >= 0 else ''
            res += str(plyer['rank']) + ' ' + plyer['name'] + ' ' + str(round(plyer['score'],2)) + ' ' + str(plyer['performance']) + ' ' + str(plyer['new_rate'])+'('+SIGN+str(delta)+')' + '\n'
            rank += 1
        if rank > 10: break
    return res

def split_symbol(symbol):
    #symbol是一个字符串，以BTC或USDT或ETH或USD结尾，表示交易对
    #返回交易对的两个币种
    #例如输入BTCUSDT，返回BTC和USDT
    #删除字符串中的斜杠和空格
    symbol = symbol.replace('/','').replace(' ','').upper()
    if symbol[-3:] == 'BTC':
        return symbol[:-3],'BTC'
    elif symbol[-4:] == 'USDT':
        return symbol[:-4],'USDT'
    elif symbol[-3:] == 'ETH':
        return symbol[:-3],'ETH'
    elif symbol[-3:] == 'USD':
        return symbol[:-3],'USDT'
    else:
        return symbol,''
    
def buy(user,symbol,amount,currency,margin):
    currency = currency.upper()
    curr1,curr2 = split_symbol(symbol)
    curr_usdt = curr1 + 'USDT'
    #买入amount USDT的BTC
    #返回买入成功或失败的信息
    reg_set = load_reg_set()
    name_dict = load_name_dict()
    T = get_contest_text()
    user_name = ""
    for reg_name in reg_set:
        if name_dict[reg_name] == user:
            user_name = reg_name
            break
    if user_name == "":
        return '您未注册比赛，输入"注册比赛 用户名"注册比赛。'
    user_account = load_user_account(user)
    price_btc = get_price_btc()
    price_eth = get_price_eth()
    price_symbol = get_price_symbol(curr_usdt)
    #格式：{'BTC':0,'USDT':1000}
    #对于买入操作来说，默认的交易单位是curr2(USDT,BTC,ETH)
    #用户输入的单位是currency(BTC,USDT,ETH,curr1)
    #直接枚举所有3*4=12种情况
    if curr2 == 'BTC':
        if currency == 'BTC':
            amount = amount * price_btc / price_btc
        elif currency == 'ETH':
            amount = amount * price_eth / price_btc
        elif currency == 'USDT':
            amount = amount / price_btc
        elif currency == curr1:
            amount = amount * price_symbol / price_btc
        else:
            return '输入的单位不正确。'
    elif curr2 == 'ETH':
        if currency == 'BTC':
            amount = amount * price_btc / price_eth
        elif currency == 'ETH':
            amount = amount * price_eth / price_eth
        elif currency == 'USDT':
            amount = amount / price_eth
        elif currency == curr1:
            amount = amount * price_symbol / price_eth
        else:
            return '输入的单位不正确。'
    elif curr2 == 'USDT':
        if currency == 'BTC':
            amount = amount * price_btc
        elif currency == 'ETH':
            amount = amount * price_eth
        elif currency == 'USDT':
            amount = amount
        elif currency == curr1:
            amount = amount * price_symbol
        else:
            return '输入的单位不正确。'
    #BTC是用户持有的BTC数量，USDT是用户持有的USDT数量
    if not margin and user_account.get(curr2,0) < amount:
        return '余额不足。(余额：' + str(user_account.get(curr2,0)) + ')'
    fee = amount * 0.001
    act_amount = amount - fee
    next_account = user_account.copy()
    next_account[curr2] = next_account[curr2] - amount if curr2 in next_account else -amount
    if curr2 == 'BTC':
        amount_curr1 = act_amount * price_btc / price_symbol
    elif curr2 == 'ETH':
        amount_curr1 = act_amount * price_eth / price_symbol
    elif curr2 == 'USDT':
        amount_curr1 = act_amount / price_symbol
    next_account[curr1] = next_account[curr1] + amount_curr1 if curr1 in next_account else amount_curr1
    #杠杆率不能超过20倍
    if get_leverage(next_account) > 20:
        return '杠杆率超过20倍，无法买入。'
    #执行交易
    #user_account['USDT'] -= amount
    #user_account['BTC'] += act_amount / price
    user_account = next_account
    save_user_account(user, user_account)
    #update_contest_rank(user_name, user_account, price)
    op = '做多' if margin else '买入'
    bs = get_balance_str(user_account)
    #计算估值
    market_cap = get_market_cap(user_account)
    return T + '\n' + op + '成功，手续费:'+ str(fee) + curr2 + '。\n余额：\n' + bs +\
        '估值：' + str(market_cap) + 'USDT。\n杠杆率：' + str(get_leverage(user_account)) + '倍。'

def get_market_cap(user_account):
    #杠杆率
    #本金 = USDT余额 + BTC数量*当前价格
    # 当USDT余额为负数时，杠杆率为:abs(USDT余额)/本金
    # 当BTC数量为负数时，杠杆率为:abs(BTC数量)*当前价格/本金
    price_btc = get_price_btc()
    price_eth = get_price_eth()
    balance = 0
    for symbol in user_account:
        if symbol == 'USDT':
            delta = user_account[symbol]
        elif symbol == 'BTC':
            delta = user_account[symbol] * price_btc
        elif symbol == 'ETH':
            delta = user_account[symbol] * price_eth
        else:
            curr_usdt = symbol + 'USDT'
            price_symbol = get_price_symbol(curr_usdt)
            delta = user_account[symbol] * price_symbol
        balance += delta
    return balance
    
def get_balance_str(user_account):
    ans = ""
    for key in user_account:
        ans += str(user_account[key]) + key + '\n'
    return ans

def long(user,amount,currency):
    currency = currency.upper()
    #做多amount USDT的BTC
    #返回做多成功或失败的信息
    reg_set = load_reg_set()
    name_dict = load_name_dict()
    T = get_contest_text()
    user_name = ""
    for reg_name in reg_set:
        if name_dict[reg_name] == user:
            user_name = reg_name
            break
    if user_name == "":
        return '您未注册比赛，输入"注册比赛 用户名"注册比赛。'
    user_account = load_user_account(user)
    #格式：{'BTC':0,'USDT':1000}
    #BTC是用户持有的BTC数量，USDT是用户持有的USDT数量
    #做多允许用户持有的USDT为负数，因此不需要判断余额
    #if user_account['USDT'] < amount:
    #    return '余额不足。(余额：' + str(user_account['USDT']) + ')'
    price = get_price_btc()
    if currency == 'B':
        amount = amount * price
    fee = amount * 0.001
    act_amount = amount - fee
    #杠杆率不能超过20倍
    if get_leverage({
        "USDT":user_account['USDT'] - amount,
        "BTC":user_account['BTC'] + act_amount / price}) > 20:
        return '杠杆率超过20倍，无法做多。'
    #执行交易
    user_account['USDT'] -= amount
    user_account['BTC'] += act_amount / price
    save_user_account(user, user_account)
    #update_contest_rank(user_name, user_account, price)
    return T + '\n做多成功，手续费:'+ str(fee) +'USDT。\n余额：\n' + str(user_account['USDT']) + 'USDT,\n'+ str(user_account['BTC']) + 'BTC\n' +\
        '估值：' + str(user_account['USDT'] + user_account['BTC'] * price) + 'USDT。\n杠杆率：' + str(get_leverage(user_account)) + '倍。'

def get_leverage(user_account):
    #杠杆率
    #本金 = USDT余额 + BTC数量*当前价格
    # 当USDT余额为负数时，杠杆率为:abs(USDT余额)/本金
    # 当BTC数量为负数时，杠杆率为:abs(BTC数量)*当前价格/本金
    leverage = 0
    price_btc = get_price_btc()
    price_eth = get_price_eth()
    #price_symbol = get_price_symbol(curr_usdt)
    balance = leverage_amount = 0
    for symbol in user_account:
        if symbol == 'USDT':
            delta = user_account[symbol]
        elif symbol == 'BTC':
            delta = user_account[symbol] * price_btc
        elif symbol == 'ETH':
            delta = user_account[symbol] * price_eth
        else:
            curr_usdt = symbol + 'USDT'
            price_symbol = get_price_symbol(curr_usdt)
            delta = user_account[symbol] * price_symbol
        if delta < 0:
            leverage_amount -= delta
        balance += delta
    leverage = leverage_amount / balance
    return leverage

def sell(user,symbol,amount,currency,margin):
    currency = currency.upper()
    curr1,curr2 = split_symbol(symbol)
    curr_usdt = curr1 + 'USDT'
    #买入amount USDT的BTC
    #返回买入成功或失败的信息
    reg_set = load_reg_set()
    name_dict = load_name_dict()
    T = get_contest_text()
    user_name = ""
    for reg_name in reg_set:
        if name_dict[reg_name] == user:
            user_name = reg_name
            break
    if user_name == "":
        return '您未注册比赛，输入"注册比赛 用户名"注册比赛。'
    user_account = load_user_account(user)
    price_btc = get_price_btc()
    price_eth = get_price_eth()
    price_symbol = get_price_symbol(curr_usdt)
    #格式：{'BTC':0,'USDT':1000}
    #对于卖出操作来说，默认的交易单位是curr1(USDT,BTC,ETH)
    #用户输入的单位是currency(BTC,USDT,ETH,curr1)
    #直接枚举所有3*4=12种情况
    if currency == 'BTC':
        amount = amount * price_btc / price_symbol
    elif currency == 'ETH':
        amount = amount * price_eth / price_symbol
    elif currency == 'USDT':
        amount = amount / price_symbol
    elif currency == curr1:
        amount = amount * price_symbol / price_symbol
    else:
        return '输入的单位不正确。'
    #BTC是用户持有的BTC数量，USDT是用户持有的USDT数量
    if not margin and user_account.get(curr1,0) < amount:
        return '余额不足。(余额：' + str(user_account.get(curr1,0)) + ')'
    fee = amount * 0.001
    act_amount = amount - fee
    next_account = user_account.copy()
    next_account[curr1] = next_account[curr1] - amount if curr1 in next_account else -amount
    if curr2 == 'BTC':
        amount_curr2 = act_amount * price_symbol / price_btc
    elif curr2 == 'ETH':
        amount_curr2 = act_amount * price_symbol / price_eth
    elif curr2 == 'USDT':
        amount_curr2 = act_amount * price_symbol
    next_account[curr2] = next_account[curr2] + amount_curr2 if curr2 in next_account else amount_curr2
    #杠杆率不能超过20倍
    if get_leverage(next_account) > 20:
        return '杠杆率超过20倍，无法买入。'
    #执行交易
    #user_account['USDT'] -= amount
    #user_account['BTC'] += act_amount / price
    user_account = next_account
    save_user_account(user, user_account)
    #update_contest_rank(user_name, user_account, price)
    op = '做空' if margin else '卖出'
    bs = get_balance_str(user_account)
    #计算估值
    market_cap = get_market_cap(user_account)
    return T + '\n' + op + '成功，手续费:'+ str(fee) + curr2 + '。\n余额：\n' + bs +\
        '估值：' + str(market_cap) + 'USDT。\n杠杆率：' + str(get_leverage(user_account)) + '倍。'

def short(user,amount,currency):
    currency = currency.upper()
    #做空amount个USDT
    #返回做空成功或失败的信息
    reg_set = load_reg_set()
    name_dict = load_name_dict()
    T = get_contest_text()
    user_name = ""
    for reg_name in reg_set:
        if name_dict[reg_name] == user:
            user_name = reg_name
            break
    if user_name == "":
        return '您未注册比赛，输入"注册比赛 用户名"注册比赛。'
    user_account = load_user_account(user)
    #格式：{'BTC':0,'USDT':1000}
    #BTC是用户持有的BTC数量，USDT是用户持有的USDT数量
    #做空允许用户持有的BTC为负数，因此不需要判断余额
    #if user_account['BTC'] < amount:
    #    return '余额不足。(余额：' + str(user_account['BTC']) + ')'
    price = get_price_btc()
    if currency == 'U':
        amount = amount / price
    fee = amount * 0.001
    act_amount = amount - fee
    #杠杆率不能超过20倍
    if get_leverage({
        "BTC":user_account['BTC'] - amount,
        "USDT":user_account['USDT'] + act_amount * price}) > 20:
        return '杠杆率超过20倍，无法做空。'
    #执行交易
    user_account['BTC'] -= amount
    user_account['USDT'] += act_amount * price
    save_user_account(user, user_account)
    #update_contest_rank(user_name, user_account, price)
    return T + '\n做空成功，手续费:'+ str(fee) +'BTC。\n余额：\n' + str(user_account['USDT']) + 'USDT,\n'+ str(user_account['BTC']) + 'BTC\n' +\
        '估值：' + str(user_account['USDT'] + user_account['BTC'] * price) + 'USDT。\n杠杆率：' + str(get_leverage(user_account)) + '倍。'

# def update_contest_rank(user_name, user_account, price):
#     #更新比赛排名
#     #contest_rank是一个list，每个元素是一个tuple，tuple的第一个元素是账号，第二个元素是余额
#     value = user_account['USDT'] + user_account['BTC'] * price
#     contest_rank = load_contest_rank()
#     for i in range(len(contest_rank)):
#         if contest_rank[i][0] == user_name:
#             contest_rank[i][1] = value
#             break
#     contest_rank.sort(key=lambda x:x[1],reverse=True)
#     save_contest_rank(contest_rank)

def chat(s,user,target,ts):
    res = chat_register(s,user)
    if res: return res
    res = chat_command(s,user,target,ts)
    if res: return res

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
