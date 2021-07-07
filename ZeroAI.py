﻿# -*- coding: utf-8 -*-
# filename: ZeroAI.py

#from wordcloud import WordCloud, STOPWORDS
import mysql.connector
import mypsw
import time
import datetime
import matplotlib.pyplot as plt
from basic import Basic
#from poster.streaminghttp import register_openers
import requests
from requests.packages.urllib3.filepost import encode_multipart_formdata
import json
import glob
import forcastline
import f50_market_spider
import f51_simulated_trading
import f52_db_simulated
import asyncio
import _thread
import math
import common
import requests

class word_in_color(object):
  word_in_rising_major = ''
  word_in_falling_major = ''
  word_in_comments = []
  word_in_rising_minor = []
  word_in_falling_minor = []

def color_word(word, *args, **kwargs):
  if (word == word_in_color.word_in_rising_major):
      color = '#ffffff' # red
  elif (word == word_in_color.word_in_falling_major):
      color = '#f44336' # green
  elif (word in word_in_color.word_in_comments):
      color = '#ffffff' if word_in_color.word_in_rising_major != '' else '#f44336' # grey
  elif (word in word_in_color.word_in_rising_minor):
      color = '#7f7f7f' # deepred
  elif (word in word_in_color.word_in_falling_minor):
      color = '#7a211b' # deepgreen
  else:
      color = '#000000' # black
  return color

def utc2local(utc_st):
    #UTC时间转本地时间（+8:00）
    now_stamp = time.time()
    local_time = datetime.datetime.fromtimestamp(now_stamp)
    utc_time = datetime.datetime.utcfromtimestamp(now_stamp)
    offset = local_time - utc_time
    local_st = utc_st + offset
    return local_st

input_days_len = 225

def simulated_trading(next_id, input_text):
    f52_db_simulated.save_result(next_id, '')
    symbol_list = input_text.split(' ')
    predict_list = []
    for symbol in symbol_list:
        while len(symbol) > 0:
            for _ in range(5):
                marketListString  = f50_market_spider.search_for_symbol(symbol)
                if marketListString != None:
                    break
            if len(marketListString) == 0:
                symbol = symbol[:-1]
            else:
                break
        if not marketListString:
            f52_db_simulated.save_result(next_id, '模拟失败，未找到市场'+symbol+'相关信息。')
        market, is_crypto = f50_market_spider.get_best_market(json.loads(marketListString))
        marketObj = market
        marketObj["name"] = marketObj["name"].replace("Investing.com","")
        timestamp_list, price_list, openprice_list, highprice_list, lowprice_list = f50_market_spider.get_history_price(str(marketObj["pairId"]), marketObj["pair_type"], 4800)
        if len(price_list) < f50_market_spider.input_days_len:
            continue
        turtlex_predict = f50_market_spider.predict(marketObj["symbol"]+marketObj["name"], timestamp_list, price_list, openprice_list, highprice_list, lowprice_list, 4500, is_crypto)
        predict_list.append(turtlex_predict)
    #if is_crypto:
    simulate_result, win_count, loss_count, draw_count, max_loss, max_loss_days, year_list, max_single_win, max_single_loss, strategy_count = f51_simulated_trading.simulate_trading11(predict_list)
    #else:
    #    simulate_result, win_count, loss_count, draw_count, max_loss, max_loss_days, year_list, max_single_win, max_single_loss, strategy_count = f51_simulated_trading.simulate_trading(predict_list)
    time_end=time.time()
    init_balance = simulate_result["balance_dynamic_list"][0]
    last_balance = simulate_result["balance_dynamic_list"][-1]
    years = len(simulate_result["symbol_list"]) / 365
    annual_yield =math.pow( last_balance / init_balance, 1 / years) * 100.0 - 100.0
    output_text = "模拟结果：\n" +str(input_text) + "\n海龟11量化交易决策引擎\n交易天数：" + str(len(simulate_result["symbol_list"])) + "\n盈利天数：" + str(win_count) + "\n亏损天数：" + str(loss_count) + "\n平局天数：" + str(draw_count)
    output_text += "\n胜率：" + str(round((win_count * 100.0 / (win_count + loss_count)),3) if (win_count + loss_count) > 0 else 0  ) + "%" + "\n最大亏损：" + str(round(max_loss * 100.0,3))  + '%' + "\n最长衰落期：" + str(max_loss_days) + "天"
    output_text += "\n初始余额：" + str(init_balance) + "\n最终余额：" + str(last_balance) + "\n年化收益：" + str(round(annual_yield,3)) + '%'
    output_text += "\n最大单日盈利：" + str(max_single_win) + "%\n最大单日亏损：" + str(max_single_loss) + '%' + "\n策略分布：" + json.dumps(strategy_count)
    output_text += "\n日期范围：[" + datetime.datetime.strftime(simulate_result["date_list"][0],f50_market_spider.dateformat) + ',' + datetime.datetime.strftime(simulate_result["date_list"][-1],f50_market_spider.dateformat) + ']\n历年收益：'
    for year_item in year_list:
        output_text += "\n"+str(year_item["year"])+":"+str(round(year_item["profit"],3)) + "%"
    output_text +=  "\n广告位：\n虚位以待……"
    f52_db_simulated.save_result(next_id, output_text)

def simulated_begin(next_id, input_text):
    simulated_trading(next_id,input_text.strip())

def simulated_end(input_text):
    next_id = int(input_text.strip())
    result = f52_db_simulated.read_result(next_id)
    if len(result) == 0:
        result = "模拟结果未生成，请稍后查询！"
    return result

def get_predict_info(exchange, symbol, prediction):
  strategy = prediction["strategy"]
  order_item = prediction["orders"]
  timeStamp = int(float(prediction["strategy"]["ai"])/1000.0)
  timeArray = datetime.datetime.utcfromtimestamp(timeStamp)
  #timeArray = time.localtime(timeStamp)
  otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S UTC".encode('unicode_escape').decode('utf8'), timeArray).encode('utf-8').decode('unicode_escape')
  
  sign_text = '\n——预言家/Prophet\n诞生Birth:' + otherStyleTime + '\n纪元Epoch:'+strategy['epoch'] + \
    '\n训练集Training:' + str(round(strategy["fitness"]*100.0,2)) + '%' \
    '\n验证集Validation:' + str(round(strategy["validation"]*100.0,2)) + '%'

  text = "市场Symbol:" + symbol + \
    '\n标准日期UTCDate:' + strategy["date"] + \
    '\n评分Score:' + str(strategy["score"]) + \
    '\n方向Side:' + strategy["side"] + \
    '\n止损Stop:' + str(strategy["stop"]) + "ATR" \
    '\n最高价HighPrice:' + str(strategy["high_price"]) + \
    '\n最低价LowPrice:' + str(strategy["low_price"]) + \
    '\n最新价ClosePrice:' + str(strategy["close_price"]) + \
    '\n均幅指标Atr20:' + str(strategy["atr"]) + "%" \
    '\n头寸大小Position:' + str(strategy["amount"]) + "%" \
    '\n镜像Mirror:' + str(strategy["mirror"]) + \
    '\n时间戳Timestamp:' + str(strategy["predict_timestamp"]) + \
    sign_text
  return text

def get_prediction_text(exchange, symbol, prediction):
  order_item = prediction["orders"]
  #for order_key in prediction["orders"]:
  #  order_item = prediction["orders"][order_key][0]
  timeStamp = int(float(prediction["strategy"]["ai"])/1000.0)
  timeArray = time.localtime(timeStamp)
  otherStyleTime = time.strftime("%Y年%m月%d日 %H时%M分%S秒".encode('unicode_escape').decode('utf8'), timeArray).encode('utf-8').decode('unicode_escape')
  sign_text = 'p.s. 海龟∞AI正在无限进化中，' \
    '于'+otherStyleTime+'完成了第'+str(prediction["strategy"]['epoch'])+'轮演化。\n' \
    '训练集年化：' + str(round(prediction["strategy"]["fitness"]*100.0,2)) + '%\n' \
    '验证集年化：' + str(round(prediction["strategy"]["validation"]*100.0,2)) + '%'
    
  if order_item:
    stop_loss_str = ('止损价：' + str(order_item["stop_loss_price"]) + '('+ str(order_item["stop_loss"]) +'ATR)') if prediction["strategy"]["trend_grid"] >= 0.5 else ('止损价：' + str(prediction["strategy"]['stop_loss_price']))
    text = "交易所：" + order_item["exchange"] + "\n市场：" + order_item["symbol"] + '\n' \
      '入场价：' + str(order_item["entry_price"]) + '\n' \
      '操作：' + ('网格' if prediction["strategy"]["trend_grid"] < 0.5 else ('做多' if prediction["strategy"]["long_short"] >= 0.5 else '做空')) + '\n' \
      '信心指数：' + str(prediction["strategy"]["trade"]*100.0) + '%(选择超过50%且信号最强的市场下单)\n' \
      'ATR：' + str(round(order_item["atr"],3)) + '%\n' + str(stop_loss_str) + '\n' \
      '头寸（仓位）：' + str(round(order_item["amount"],3)) + '%/天（每天的头寸总和）\n镜像K线：' + ('是' if prediction["strategy"]["mirror"] else '否') + '\n' + sign_text
      #'——AI海龟∞（编号：'+str(prediction["strategy"]["ai"])+'；回测年化：'+str(round(prediction["strategy"]["validation"]*100.0,2))+'%）'
  else:
    text = "交易所：" + exchange + "\n市场：" + symbol + '\n' \
      '操作：观望\n' \
      '信心指数：' + str(prediction["strategy"]["trade"]*100.0) + '%\n镜像K线：' + ('是' if prediction["strategy"]["mirror"] else '否') + '\n' + sign_text
      #'——AI海龟∞（编号：'+str(prediction["strategy"]["ai"])+'；回测年化：'+str(round(prediction["strategy"]["validation"]*100.0,2))+'%）'
  return text

def get_v1_prediction(exchange, symbol):
  url = "https://aitrad.in/api/v1/predict?exchange=" + exchange + "&symbol=" + symbol
  response = requests.get(url)
  prediction = json.loads(response.text)
  if prediction["code"] == 200:
    return get_predict_info(exchange, symbol, prediction)
  else:
    return prediction["msg"][:600]

def chat(origin_input):
  time_start=time.time()
  if '@' in origin_input and len(origin_input) >= 3:
    origin_input = origin_input.strip()
    # 替换空格
    origin_input = origin_input.replace(' ', '')
    # 替换换行
    origin_input = origin_input.replace('\n', '')
    # 替换换行
    origin_input = origin_input.replace('\r', '')
    split_str_list = origin_input.split('@',1)
    symbol = split_str_list[0]
    exchange = split_str_list[1]
    if symbol and exchange:
      return get_v1_prediction(exchange, symbol)
    else:
      return "请输入'市场@交易所'执行预测，例如：'BTCUSDT@binance'。"
    
  if origin_input[:2] == "模拟":
      max_id = f52_db_simulated.get_max_id()
      next_id = max_id + 1
      symbols_str = origin_input[2:].strip()
      symbol_list = symbols_str.split(' ')
      if len(symbol_list) == 0:
          return "请输入模拟+市场名1+市场名2+市场名3……市场名用空格分隔。"
      _thread.start_new_thread( simulated_begin, (next_id, symbols_str) )
      return "模拟开始，"+str(len(symbol_list)*5)+"分钟后输入'结果" + str(next_id) + "'查询模拟结果。"
  if origin_input[:2] == "结果":
      return simulated_end(origin_input[2:])
  marketListString = ""
  #while len(origin_input) > 0 and len(marketListString) == 0:
  marketListString  = f50_market_spider.search_for_symbol(origin_input)
  if not marketListString or len(marketListString) == 0:
      for char_index in range(len(origin_input)):
          char_index_end = len(origin_input) - char_index - 1
          if char_index == 0:
              new_input = origin_input[-char_index_end:]
          elif char_index_end == 0:
              new_input = origin_input[:char_index]
          else:
              new_input = origin_input[:char_index] + origin_input[-char_index_end:]
          marketListString  = f50_market_spider.search_for_symbol(new_input)
          if marketListString and len(marketListString) > 0:
              break
      #new_input = origin_input[:-1]
      origin_input = new_input
  #  else:
  #    break
  #market, is_crypto = f50_market_spider.get_best_market(json.loads(marketListString))
  response_result = f50_market_spider.get_all_markets(json.loads(marketListString))
  return response_result
  print(json.dumps(market))
  #marketString = json.dumps(market).encode('utf-8').decode('unicode_escape').replace("Investing.com","")
  #marketString = json.dumps(market).replace("Investing.com","")
  #print(marketString)
  #marketObj = json.loads(marketString)
  marketObj = market
  marketObj["name"] = marketObj["name"].replace("Investing.com","")
  #if is_crypto:
  #  sign_text = "——海龟11加密货币决策引擎\n广告位：\n虚位以待……"
  #else:
  #  sign_text = "——海龟X量化交易决策引擎\n广告位：\n虚位以待……"
  sign_text = "——海龟11量化交易决策引擎\n广告位：\n虚位以待……"
  timestamp_list, price_list, openprice_list, highprice_list, lowprice_list = f50_market_spider.get_history_price(str(marketObj["pairId"]), marketObj["pair_type"], 400)
  if len(price_list) < input_days_len + 20 - 1:
    return "市场名："+marketObj["symbol"] + marketObj["name"] + \
    "\n当前市场的数据仅"+str(len(price_list))+\
    "天，不足"+str(input_days_len + 20 - 1)+"天，无法执行预测！\n" + sign_text
  turtlex_predict = f50_market_spider.predict(marketObj["symbol"]+marketObj["name"], timestamp_list, price_list, openprice_list, highprice_list, lowprice_list, 20, is_crypto)
  #Get profit of past 20 days
  #if is_crypto:
  profit20 = f51_simulated_trading.get_past_profit11(turtlex_predict, -1, 20, False)

  turtlex_predict_mirror = f50_market_spider.predict(marketObj["symbol"]+marketObj["name"], timestamp_list, [1/i for i in price_list], [1/i for i in openprice_list], [1/i for i in lowprice_list], [1/i for i in highprice_list], 20, is_crypto)
  #Get profit of past 20 days
  #if is_crypto:
  profit20_mirror = f51_simulated_trading.get_past_profit11(turtlex_predict_mirror, -1, 20, False)

  #else:
  #  profit20 = f51_simulated_trading.get_past_profit(turtlex_predict, -1, 20, False)
  time_end=time.time()
  comment = """
  注释：
  symbol:市场名
  date_list:预测日期
  prob_list:上涨概率[0,1]
  side_list:买入buy，卖出sell
  score_list:趋势强弱[-100,100]
  price_list:收盘价
  atr_list:均幅指标(20日)
  stop_list:移动止损价(ATR/2)
  version:AI版本
  """
  
  base_price = float(turtlex_predict["price_list"][0])
  atr100 = float(turtlex_predict["atr_list"][0])
  
  #price_up_25 = format(base_price * (1 + atr100/100*0.25),'.7g')
  #price_down_25 = format(base_price / (1 + atr100/100*0.25),'.7g')
  #price_up_40 = format(base_price * (1 + atr100/100*0.4),'.7g')
  #price_down_40 = format(base_price / (1 + atr100/100*0.4),'.7g')
  #price_up_50 = format(base_price * (1 + atr100/100*0.5),'.7g')
  #price_down_50 = format(base_price / (1 + atr100/100*0.5),'.7g')
  #price_up_55 = format(base_price * (1 + atr100/100*0.55),'.7g')
  #price_down_55 = format(base_price / (1 + atr100/100*0.55),'.7g')
  #price_up_75 = format(base_price * (1 + atr100/100*0.75),'.7g')
  #price_down_75 = format(base_price / (1 + atr100/100*0.75),'.7g')
  #price_up_80 = format(base_price * (1 + atr100/100*0.8),'.7g')
  #price_down_80 = format(base_price / (1 + atr100/100*0.8),'.7g')
  #price_up_110 = format(base_price * (1 + atr100/100*1.1),'.7g')
  #price_down_110 = format(base_price / (1 + atr100/100*1.1),'.7g')
  #price_up_120 = format(base_price * (1 + atr100/100*1.2),'.7g')
  #price_down_120 = format(base_price / (1 + atr100/100*1.2),'.7g')
  #price_up_165 = format(base_price * (1 + atr100/100*1.65),'.7g')
  #price_down_165 = format(base_price / (1 + atr100/100*1.65),'.7g')
  #if is_crypto:
  strategy_text_dict = {
      0:"即将下跌，趋势追踪策略，卖出/做空，移动止损点：0.16ATR(止损价："+ format(base_price * (1 + atr100/100*0.16),'.7g') +")",
      1:"即将上涨，趋势追踪策略，买入/做多，移动止损点：0.16ATR(止损价："+ format(base_price / (1 + atr100/100*0.16),'.7g') +")",
      2:"即将下跌，趋势追踪策略，卖出/做空，移动止损点：0.24ATR(止损价:"+ format(base_price * (1 + atr100/100*0.24),'.7g') +")",
      3:"即将上涨，趋势追踪策略，买入/做多，移动止损点：0.24ATR(止损价："+ format(base_price / (1 + atr100/100*0.24),'.7g') +")",
      4:"即将下跌，趋势追踪策略，卖出/做空，移动止损点：0.36ATR(止损价："+ format(base_price * (1 + atr100/100*0.36),'.7g') +")",
      5:"即将上涨，趋势追踪策略，买入/做多，移动止损点：0.36ATR(止损价："+ format(base_price / (1 + atr100/100*0.36),'.7g') +")",
      6:"即将下跌，趋势追踪策略，卖出/做空，移动止损点：0.54ATR(止损价："+ format(base_price * (1 + atr100/100*0.54),'.7g') +")",
      7:"即将上涨，趋势追踪策略，买入/做多，移动止损点：0.54ATR(止损价："+ format(base_price / (1 + atr100/100*0.54),'.7g') +")",
      8:"震荡行情，网格策略，高抛低吸，以当前价格为基准，上下0.3ATR范围挂单，突破1.5ATR范围止损(买单："+ format(base_price / (1 + atr100/100*0.3),'.7g') + "，卖单：" + format(base_price * (1 + atr100/100*0.3),'.7g') +"，跌破止损："+ format(base_price / (1 + atr100/100*1.5),'.7g') + "，涨破止损：" + format(base_price * (1 + atr100/100*1.5),'.7g') +")",
      9:"震荡行情，网格策略，高抛低吸，以当前价格为基准，上下0.4ATR范围挂单，突破2.0ATR范围止损(买单："+ format(base_price / (1 + atr100/100*0.4),'.7g') + "，卖单：" + format(base_price * (1 + atr100/100*0.4),'.7g') +"，跌破止损："+ format(base_price / (1 + atr100/100*2.0),'.7g') + "，涨破止损：" + format(base_price * (1 + atr100/100*2.0),'.7g') +")",
      }
  #else:
  #    strategy_text_dict = {
  #        0:"做空/上涨0.16倍ATR时("+ format(base_price * (1 + atr100/100*0.16),'.7g') +")止损",
  #        1:"做多/下跌0.16倍ATR时("+ format(base_price / (1 + atr100/100*0.16),'.7g') +")止损",
  #        2:"做空/上涨0.24倍ATR时("+ format(base_price * (1 + atr100/100*0.24),'.7g') +")止损",
  #        3:"做多/下跌0.24倍ATR时("+ format(base_price / (1 + atr100/100*0.24),'.7g') +")止损",
  #        4:"做空/上涨0.36倍ATR时("+ format(base_price * (1 + atr100/100*0.36),'.7g') +")止损",
  #        5:"做多/下跌0.36倍ATR时("+ format(base_price / (1 + atr100/100*0.36),'.7g') +")止损",
  #        6:"做空/上涨0.54倍ATR时("+ format(base_price * (1 + atr100/100*0.54),'.7g') +")止损",
  #        7:"做多/下跌0.54倍ATR时("+ format(base_price / (1 + atr100/100*0.54),'.7g') +")止损",
  #        8:"做空/上涨0.81倍ATR时("+ format(base_price * (1 + atr100/100*0.81),'.7g') +")止损",
  #        9:"做多/下跌0.81倍ATR时("+ format(base_price / (1 + atr100/100*0.81),'.7g') +")止损",
  #        10:"网格/0.2倍ATR区间("+ format(base_price / (1 + atr100/100*0.2),'.7g') + "," + format(base_price * (1 + atr100/100*0.2),'.7g') +")挂单/突破0.4倍ATR("+ format(base_price / (1 + atr100/100*0.4),'.7g') + "," + format(base_price * (1 + atr100/100*0.4),'.7g') +")止损",
  #        11:"网格/0.4倍ATR区间("+ format(base_price / (1 + atr100/100*0.4),'.7g') + "," + format(base_price * (1 + atr100/100*0.4),'.7g') +")挂单/突破0.8倍ATR("+ format(base_price / (1 + atr100/100*0.8),'.7g') + "," + format(base_price * (1 + atr100/100*0.8),'.7g') +")止损",
  #        }
  
  strategy = turtlex_predict["strategy_list"][0]
  prob = turtlex_predict["prob_list"][0]

  kline_type = "实体"
  if profit20_mirror > profit20:
    kline_type = "镜像"
    strategy = common.stategy_mirror[turtlex_predict_mirror["strategy_list"][0]]
    prob = turtlex_predict_mirror["prob_list"][0]
    profit20 = profit20_mirror
  
  return_text = "[" + marketObj["pair_type"] + "/" + marketObj["flag"] + "]" + marketObj["symbol"]+marketObj["name"] + \
  "\n20日回测收益：" + str(profit20) + "%（单日最大风险：1.5%）" + \
  "\n当前价格：" + str(turtlex_predict["price_list"][0]) + \
  "\n交易策略" + str(strategy) + "：" + strategy_text_dict[strategy] + \
  "\nAI信心指数：" + str(prob) +"%" + \
  "\n均幅指标ATR：" + str(turtlex_predict["atr_list"][0]) + "%" + \
  "\n本次决策使用了" + kline_type + "K线" + \
  '\n响应耗时：' + str(round(time_end - time_start,3)) +"s\n" + sign_text
  return return_text

  origin_input = origin_input.strip().upper()
 
  origin_input, aiera_version = forcastline.get_version(origin_input)
  
  input_text, params = forcastline.command(origin_input)

  output_text = ''

  picture_path = 'Img/' + forcastline.pinyin(input_text) + "_" +  aiera_version + "_" + str(params["OFFSET"]) + "_" + str(params["LEN"]) + "_" + str(params["DATE"]) + "_" + datetime.datetime.now().strftime('%Y%m%d%H') + '*.jpg'
  picture_cache = glob.glob(picture_path)
  if picture_cache:
    picture_name = picture_cache[0]
    return picture_url(picture_name)
  
  mydb, mycursor = init_mycursor()

  if input_text == '帮助' or input_text == 'HELP':
    return help_text()

  select_alias_statment = "SELECT symbol_alias.* FROM symbol_alias " \
    " inner join predictlog on symbol_alias.symbol = predictlog.symbol and predictlog.LOADINGDATE > '1950-1-1' " \
    " WHERE symbol_alias.symbol_alias = '" + input_text + "'"

  #print(select_alias_statment)

  mycursor.execute(select_alias_statment)
  
  alias_results = mycursor.fetchall()
  
  tag_flag = False
  if len(alias_results) == 0:
    output_text, alias_results = fetch_tag(input_text, mycursor)
    if alias_results == None:
        return output_text
    
  plt.rcParams['font.sans-serif']=['SimHei']
  plt.rcParams['axes.unicode_minus']=False
    
  if len(alias_results) == 0:
    output_text = forcastline.text_no_market(input_text)
    return output_text
    
  #print("len(res)=" + str(len(alias_results)) + ";tag_flag=" + str(tag_flag))
  #print(str(alias_results[0]))
  if len(alias_results[0]) != 5:
      tag_flag = True
  if len(alias_results) == 1 and not tag_flag:
    picture_name, output_text = draw_single(aiera_version, input_text, alias_results, mycursor, params, origin_input)
    if picture_name == None:
        return output_text
  else:
    picture_name = draw_tag(aiera_version, input_text, alias_results)
    
  return picture_url(picture_name)

def draw_single(aiera_version, input_text, alias_results, mycursor, params, origin_input):
    if aiera_version == "V1":
        return draw_single_v1(input_text, alias_results, mycursor)
    if aiera_version == "V2":
        return forcastline.draw_single_v2(input_text, alias_results, mycursor, params, origin_input)

def draw_single_v1(input_text, alias_results, mycursor):
    output_text = ""
    alias_result = alias_results[0]
    select_predictions_statment = "SELECT * FROM predictions WHERE symbol = '" + alias_result[1] + "' ORDER BY time DESC"
    #print(select_predictions_statment)
    mycursor.execute(select_predictions_statment)
    predictions_results = mycursor.fetchall()
    if len(predictions_results) == 0:
      output_text = forcastline.text_no_market(input_text)
      return None, output_text
    select_prices_statment = "SELECT * FROM price WHERE symbol = '" + alias_result[1] + "'"
    #print(select_prices_statment)
    mycursor.execute(select_prices_statment)
    prices_results = mycursor.fetchall()
    picture_name = draw_market_v1(alias_result, prices_results, predictions_results)
    return picture_name, output_text

def help_text():
    output_text = '您好！欢迎来到AI纪元，我是通向未来之路的向导。\n' \
    '请输入：“全球股指”、“商品期货”、“外汇”、“个股”或“加密货币”，获取实时的市场趋势强弱排名。\n' \
    '输入具体的市场代码如“上证指数”、“黄金”或“比特币”，获取市场未来十天的涨跌趋势。\n' \
    '请使用分散化与自动化的方式进行交易，并控制每笔交易的风险值小于1%。\n' \
    'Hello! Welcome to the AI Era, I am the guide to the future.\n' \
    'Please enter: "INDICES", "COMMODITIES", "CURRENCIES", "STOCKS" or "CRYPTOCURRENCY" to get real-time market trend rankings.\n' \
    'Enter specific market codes such as “SSE”, “Gold” or “Bitcoin” to get the market trending in the next 10 days.\n' \
    'Please use a decentralized and automated approach to trading and control the risk value of each transaction to less than 1%.\n'
    return output_text 

def get_subtags(tagname, mycursor):
    subtags = []
    select_subtags_statment = "select * from subtags where tag = '" + tagname + "' and tag <> subtag"
    #print(select_subtags_statment)
    mycursor.execute(select_subtags_statment)
    subtags_results = mycursor.fetchall()
    for subtags_result in subtags_results:
        subtags.append(subtags_result[1])
    return subtags

def get_markets_from_endtags(endtags, mycursor):
    markets = []
    select_tags_statment = 'select * from tags where tag in (%s) ' % ','.join(['%s']*len(endtags))
    #print(select_tags_statment)
    mycursor.execute(select_tags_statment, endtags)
    tags_results = mycursor.fetchall()
    for tags_result in tags_results:
        markets.append(tags_result[1])
    return markets

def get_markets_from_tag(tagname, mycursor):
      nextsubtags = []
      endtags = []
      subtags = get_subtags(tagname, mycursor)
      if len(subtags) == 0:
          endtags.append(tagname)
      while len(subtags) > 0:
          for subtag in subtags:
              nextsubtag = get_subtags(subtag, mycursor)
              if len(nextsubtag) == 0:
                  endtags.append(subtag)
              else:
                  nextsubtags.extend(nextsubtag)
          subtags = nextsubtags
      markets = get_markets_from_endtags(endtags, mycursor)
      return markets

def fetch_tag(input_text, mycursor):

    tagname = input_text

    markets = get_markets_from_tag(tagname, mycursor)
  
    utc_today = datetime.datetime.utcnow()+datetime.timedelta(days=-10)
    today_str = utc_today.strftime("%Y-%m-%d")

    if len(markets) > 0:

        select_alias_statment = "SELECT pricehistory.SYMBOL, pricehistory.date, pricehistory.F, symbol_alias.SYMBOL_ALIAS FROM symbol_alias " \
        " inner join predictlog on symbol_alias.symbol = predictlog.symbol and predictlog.LOADINGDATE > '1950-1-1' and predictlog.MAXDATE >= '"+today_str+"' and predictlog.symbol in (%s)  " \
        " inner join pricehistory on pricehistory.symbol = symbol_alias.symbol and pricehistory.date = predictlog.maxdate and pricehistory.l <> pricehistory.h and pricehistory.c > 0 " \
        " ORDER BY pricehistory.SYMBOL" % ','.join(['%s']*len(markets))
      
        #print(select_alias_statment)
      
        mycursor.execute(select_alias_statment, markets)
  
        alias_results = mycursor.fetchall()
    
    else:
      
      input_text = input_text.replace("/","%").replace("-","%").replace("*","%").replace(" ","%").replace("?","%").replace("=","%")

      select_alias_statment = "SELECT * FROM symbol_alias WHERE symbol_alias LIKE '%" + input_text + "%' group by symbol"

      #print(select_alias_statment)

      mycursor.execute(select_alias_statment)
  
      alias_results = mycursor.fetchall()
    
      if len(alias_results) > 1:
        '''
        select_alias_statment = "SELECT predictions.*, symbol_alias.SYMBOL_ALIAS FROM symbol_alias " \
        " inner join predictions on predictions.symbol = symbol_alias.symbol WHERE symbol_alias LIKE '%" + input_text + "%' ORDER BY symbol ASC"
        '''

        select_alias_statment = "SELECT pricehistory.SYMBOL, pricehistory.date, pricehistory.F, symbol_alias.SYMBOL_ALIAS FROM symbol_alias " \
        " inner join predictlog on symbol_alias.symbol = predictlog.symbol and predictlog.LOADINGDATE > '1950-1-1' " \
        " inner join pricehistory on pricehistory.symbol = symbol_alias.symbol and pricehistory.date = predictlog.maxdate  and pricehistory.l <> pricehistory.h and pricehistory.c > 0 " \
        " WHERE symbol_alias LIKE '%" + input_text + "%' ORDER BY pricehistory.symbol ASC"

        #print(select_alias_statment)

        mycursor.execute(select_alias_statment)
  
        alias_results = mycursor.fetchall() 
    
    return "", alias_results

def init_mycursor():
    word_in_color.word_in_rising_major = ''
    word_in_color.word_in_falling_major = ''
    word_in_color.word_in_comments = []
    word_in_color.word_in_rising_minor = []
    word_in_color.word_in_falling_minor = []
    mydb = mysql.connector.connect(
      host=mypsw.wechatguest.host,
      user=mypsw.wechatguest.user,
      passwd=mypsw.wechatguest.passwd,
      database=mypsw.wechatguest.database,
      auth_plugin='mysql_native_password'
      )
    mycursor = mydb.cursor()
    return mydb, mycursor

def picture_url(picture_name):
    myMedia = Media()
    accessToken = Basic().get_access_token()
    filePath = picture_name
    mediaType = "image"
    murlResp = Media.uplaod(accessToken, filePath, mediaType)
    #print(murlResp)
    return murlResp

def draw_market_v1(alias_result, prices_results, predictions_results):
    plt.figure(figsize=(6.4,6.4), dpi=100, facecolor='black')

    predictions_result = predictions_results[0]
    
    #plt.subplot(211)

    plt.style.use('dark_background')

    x=[i for i in range(1,122)]
    y=[prices_results[0][121-price_index] for price_index in range(120)]
    
    plt.title( alias_result[2] + ":" + alias_result[0] + " " 
              + predictions_result[1].strftime('%Y-%m-%d %H:%M') 
              + " UTC\n微信公众号：AI纪元 WeChat Public Account: AI Era V1") #图标题 
    
    #plt.xlabel(u'过去120天收盘价') #X轴标签
    prediction_text, nextprice = forcastline.day_prediction_text(predictions_result[2],float(prices_results[0][2]),float(prices_results[0][122]))
    plt.xlabel( prediction_text ) #X轴标签
    
    #plt.plot(x,y,"green",linewidth=1, label=u"价格")
    y.append(nextprice)
    currentprice = prices_results[0][2]
    if nextprice >= currentprice:
      plt.plot(x,y,"white",label="ATR:"+ str(float(prices_results[0][122])*100) + "%" )
      plt.fill_between(x,min(y),y,facecolor="white",alpha=0.3)
      plt.plot(x,[currentprice] * 121, "w--", label="Price:"+str(currentprice))
    else:
      plt.plot(x,y,"red", label="ATR:"+ str(float(prices_results[0][122])*100) + "%" )
      plt.fill_between(x,min(y),y,facecolor="red",alpha=0.3)
      plt.plot(x,[currentprice] * 121, "r--", label="Price:"+str(currentprice))
  
    plt.annotate(xy=[122,currentprice], s=currentprice, bbox=None)

    if nextprice >= currentprice:
      bbox_props = dict(boxstyle='round',fc='white', ec='k',lw=1)
      plt.annotate(xy=[122,nextprice], s=nextprice, color='white', bbox=None)
    else:
      bbox_props = dict(boxstyle='round',fc='red', ec='k',lw=1)
      plt.annotate(xy=[122,nextprice], s=nextprice, color='red', bbox=None)
    
    plt.legend(loc = 2)
    
    picture_name = 'Img/' + forcastline.pinyin(alias_result[0]) + "_V1" + datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '.jpg'
    plt.savefig(picture_name, facecolor='black')
    return picture_name

def draw_tag(aiera_version, input_text, alias_results):
    stopwords = set(STOPWORDS) 
    word_frequencies = {}
    market_list = []
    for alias_result in alias_results:
      predictions_result = alias_result
      x=[0,1]
      y=[0.0, score(predictions_result[2])]

      maxvalue = max(y)
      minvalue = min(y)
      if abs(maxvalue) >= abs(minvalue):
        bestvalue = maxvalue
        bestindex = y.index(maxvalue)
      else:
        bestvalue = minvalue
        bestindex = y.index(minvalue)
      
      word_single = predictions_result[3]
      word_single = "/" + word_single + "/"
      market_list.append((word_single, bestvalue))
      wordcount = abs(bestvalue)
      if bestvalue >= 0:
        word_in_color.word_in_rising_minor.append(word_single)
      else:
        word_in_color.word_in_falling_minor.append(word_single)
      
        
      word_frequencies[word_single] = wordcount
    market_list.sort(key=lambda x:x[1], reverse=False)
    time_str = "Time:"+max( [alias_result[1] for alias_result in alias_results] ).strftime('%Y-%m-%d') + "_UTC"
    if abs(market_list[0][1]) > abs(market_list[-1][1]):
      word_in_color.word_in_falling_major = market_list[0][0]
      comment_frequency = int(abs(market_list[0][1]))
    else:
      word_in_color.word_in_rising_major = market_list[-1][0]
      comment_frequency = int(abs(market_list[-1][1]))
    word_in_color.word_in_comments = ['输入：'+input_text,time_str,'微信公众号：AI纪元']
    word_frequencies[word_in_color.word_in_comments[0]] = comment_frequency
    word_frequencies[word_in_color.word_in_comments[1]] = comment_frequency
    word_frequencies[word_in_color.word_in_comments[2]] = comment_frequency
    
    market_index = 0
    y_market = [market[0] for market in market_list]
    x_score = [market[1] for market in market_list]
    y_pos = [i for i, _ in enumerate(y_market)]
    
    wordcloud = WordCloud(width = 700, height = 700, 
                background_color ='black', 
                color_func=color_word,
                stopwords = stopwords,
                font_path='simhei.ttf',
                collocations=False
                ).generate_from_frequencies(word_frequencies)
    
    plt.figure(figsize = (7.0, 7.0), facecolor = None) 
    plt.imshow(wordcloud, interpolation="bilinear") 
    plt.axis("off") 
    plt.margins(x=0, y=0) 
    plt.tight_layout(pad = 0) 
    
    picture_name = 'Img/' + forcastline.pinyin(input_text) + "_" +  aiera_version + datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '.jpg'
    plt.savefig(picture_name)
    return picture_name

def score(prediction_result):
  return (prediction_result * 2 - 1) * 100

class Media(object):
  #def __init__(self):
    #register_openers()
  #上传图片
  def uplaod(accessToken, filePath, mediaType):
    openFile = open(filePath, "rb")
    param = {'media': openFile.read()}
    postData, content_type = encode_multipart_formdata(param)

    postUrl = "https://api.weixin.qq.com/cgi-bin/media/upload?access_token=%s&type=%s" % (accessToken, mediaType)
    headers = {'Content-Type': content_type}
    files = {'media': open(filePath, "rb")}
    urlResp = requests.post(postUrl, files=files)
    #print(urlResp.text)
    return json.loads(urlResp.text)['media_id']
