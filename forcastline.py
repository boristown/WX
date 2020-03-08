# -*- coding: utf-8 -*-
# filename: forcastline.py

import time
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pypinyin
import math

def get_version(input_text):
    if 'V1' in input_text:
        return input_text.replace("V1", "").strip(), "V1"
    if 'V2' in input_text:
        return input_text.replace("V2", "").strip(), "V2"
    return input_text.strip(), "V1"

def draw_single_v2(input_text, alias_results, mycursor):
    output_text = ""
    alias_result = alias_results[0]
    select_predictions_statment = "SELECT * FROM pricehistory WHERE symbol = '" + alias_result[1] + "' ORDER BY date DESC limit 0, 120"
    print(select_predictions_statment)
    mycursor.execute(select_predictions_statment)
    print("Fetching price history")
    predictions_results = mycursor.fetchall()
    print("price history len = " + str(len(predictions_results)))
    if len(predictions_results) == 0:
      output_text = text_no_market(input_text)
      return None, output_text
    #select_prices_statment = "SELECT * FROM price WHERE symbol = '" + alias_result[1] + "'"
    #print(select_prices_statment)
    #mycursor.execute(select_prices_statment)
    #prices_results = mycursor.fetchall()
    picture_name = draw_market_v2(alias_result, predictions_results)
    return picture_name, output_text

def draw_market_v2(alias_result, predictions_results):
    plt.figure(figsize=(6.4,6.4), dpi=100, facecolor='black')
    prediction_count = len(predictions_results)
    predictions_result = predictions_results[0]
    plt.style.use('dark_background')
    x = []
    y = []
    for predictions_result in predictions_results:
        x.append(predictions_result[1])
        y.append(predictions_result[5])
    x = x[-1::-1]
    y = y[-1::-1]
    plt.title( alias_result[2] + ":" + alias_result[0] + " "
              + predictions_result[8].strftime('%Y-%m-%d %H:%M')
              + " UTC\n微信公众号：AI纪元 WeChat Public Account: AI Era V2" ) #图标题 
    #prediction_text, nextprice = day_prediction_text(predictions_result[2],float(prices_results[0][2]),float(prices_results[0][122]))
    #plt.xlabel( prediction_text )
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.gca().xaxis.set_major_locator(mdates.DayLocator(bymonthday=None, interval=14, tz=None))
    #y.append(nextprice)
    #currentprice = prices_results[0][2]
    #if nextprice >= currentprice:
    atr = 0.0
    plt.plot(x,y,"white",label="ATR:"+ str(atr) + "%" )
    plt.gcf().autofmt_xdate()
    plt.fill_between(x,min(y),y,facecolor="white",alpha=0.3)
    #plt.plot(x,[currentprice] * 121, "w--", label="Price:"+str(currentprice))

    #else:
    #  plt.plot(x,y,"red", label="ATR:"+ str(float(prices_results[0][122])*100) + "%" )
    #  plt.fill_between(x,min(y),y,facecolor="red",alpha=0.3)
    #  plt.plot(x,[currentprice] * 121, "r--", label="Price:"+str(currentprice))
  
    #plt.annotate(xy=[122,currentprice], s=currentprice, bbox=None)

    #if nextprice >= currentprice:
    #  bbox_props = dict(boxstyle='round',fc='white', ec='k',lw=1)
    #  plt.annotate(xy=[122,nextprice], s=nextprice, color='white', bbox=None)
    #else:
    #  bbox_props = dict(boxstyle='round',fc='red', ec='k',lw=1)
    #  plt.annotate(xy=[122,nextprice], s=nextprice, color='red', bbox=None)
    
    plt.legend(loc = 2)
    
    picture_name = 'Img/' + pinyin(alias_result[0]) + "_V2" + datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '.png'
    plt.savefig(picture_name, facecolor='black')
    return picture_name

def day_prediction_text(prediction_result, price, atr):
  if prediction_result == 1:
    prediction_result = 0.99999
  if prediction_result == 0:
    prediction_result = 0.00001
  prediction_score = ( ( prediction_result * 2 - 1 ) ** 1 ) / 2 * math.pi 
  if prediction_score >= 0:
    nextprice = price * ( ( 1 + atr ) ** math.tan(prediction_score) )
  else:
    nextprice = price * ( ( 1 - atr ) ** abs(math.tan(prediction_score)) )
    
  return "Tomorrow price:" + str(nextprice), nextprice

def pinyin(word):
  s = ''
  for i in pypinyin.pinyin(word, style=pypinyin.NORMAL):
    s += ''.join(i)
  return s

def text_no_market(input_text):
    return "很抱歉，未找到市场'" + input_text + "'的预测信息！请尝试查询其它市场（如上证指数、黄金、比特币），可输入“全球股指”、“商品期货”、“外汇”、“个股”或“加密货币”查询汇总信息！"