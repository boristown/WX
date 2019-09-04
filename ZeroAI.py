# -*- coding: utf-8 -*-
# filename: ZeroAI.py

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
import pypinyin

def utc2local(utc_st):
    #UTC时间转本地时间（+8:00）
    now_stamp = time.time()
    local_time = datetime.datetime.fromtimestamp(now_stamp)
    utc_time = datetime.datetime.utcfromtimestamp(now_stamp)
    offset = local_time - utc_time
    local_st = utc_st + offset
    return local_st

def chat(input_text):
  
  output_text = ''
  
  mydb = mysql.connector.connect(
    host=mypsw.wechatguest.host,
    user=mypsw.wechatguest.user,
    passwd=mypsw.wechatguest.passwd,
    database=mypsw.wechatguest.database,
    auth_plugin='mysql_native_password'
    )

  mycursor = mydb.cursor()

  input_text = input_text.strip().upper()
  
  select_alias_statment = "SELECT * FROM symbol_alias WHERE symbol_alias = '" + input_text + "'"

  print(select_alias_statment)

  mycursor.execute(select_alias_statment)
  
  alias_results = mycursor.fetchall()
  
  if len(alias_results) == 0:
    
    input_text = input_text.replace("/","%").replace("-","%").replace("*","%").replace(" ","%")

    select_alias_statment = "SELECT * FROM symbol_alias WHERE symbol_alias LIKE '%" + input_text + "%'"

    print(select_alias_statment)

    mycursor.execute(select_alias_statment)
  
    alias_results = mycursor.fetchall()
  
    if len(alias_results) == 0:
        
      select_alias_statment = "SELECT * FROM market_alias WHERE market_alias LIKE '%" + input_text + "%'"
    
      print(select_alias_statment)
      
      mycursor.execute(select_alias_statment)
  
      alias_results = mycursor.fetchall()
  
      if len(alias_results) == 0:
        output_text = "市场'" + input_text + "'不存在！请尝试查询其它市场（如上证指数、黄金、比特币），可输入“加密货币”查询汇总信息！"
        return output_text
      
      select_alias_statment = "SELECT predictions.*, symbol_alias.SYMBOL_ALIAS FROM symbol_alias " \
      " inner join predictions on predictions.symbol = symbol_alias.symbol " \
      " inner join (select symbol, max(time) as time from predictions group by symbol) as t1 " \
      " on predictions.symbol = t1.symbol and predictions.time = t1.time " \
      " WHERE symbol_alias.market_type = '" + input_text + "' AND symbol_alias.market_order > 0 group by symbol ORDER BY time DESC"
      
      print(select_alias_statment)
      
      mycursor.execute(select_alias_statment)
  
      alias_results = mycursor.fetchall()
    
  plt.rcParams['font.sans-serif']=['SimHei']
  plt.rcParams['axes.unicode_minus']=False

  if len(alias_results) == 1:
    
    plt.figure(figsize=(6.4,4.8), dpi=100)
    
    alias_result = alias_results[0]
  
    select_predictions_statment = "SELECT * FROM predictions WHERE symbol = '" + alias_result[1] + "' ORDER BY time DESC"

    print(select_predictions_statment)

    mycursor.execute(select_predictions_statment)
  
    predictions_results = mycursor.fetchall()
  
    if len(predictions_results) == 0:
      output_text = "很抱歉，未找到市场'" + input_text + "'的预测信息！请尝试查询其它市场（如上证指数、黄金、比特币）！"
      return output_text
  
    predictions_result = predictions_results[0]  
    output_text = '一天后：' + day_prediction_text(predictions_result[2]) + '\n' \
    #'市场名:' + alias_result[0] + '\n' \
    #'市场类型：' + alias_result[2] + '\n' \
    #'预测时间：' + utc2local(predictions_result[1]).strftime('%Y-%m-%d %H:%M') + '\n' \
    '两天后：' + day_prediction_text(predictions_result[3]) + '\n' \
    '三天后：' + day_prediction_text(predictions_result[4]) + '\n' \
    '四天后：' + day_prediction_text(predictions_result[5]) + '\n' \
    '五天后：' + day_prediction_text(predictions_result[6]) + '\n' \
    '六天后：' + day_prediction_text(predictions_result[7]) + '\n' \
    '七天后：' + day_prediction_text(predictions_result[8]) + '\n' \
    '八天后：' + day_prediction_text(predictions_result[9]) + '\n' \
    '九天后：' + day_prediction_text(predictions_result[10]) + '\n' \
    '十天后：' + day_prediction_text(predictions_result[11]) + '\n'

    #print(output_text)
  
    x=[0,1,2,3,4,5,6,7,8,9,10]
    y=[0.0, score(predictions_result[2]),score(predictions_result[3]),score(predictions_result[4]),
       score(predictions_result[5]),score(predictions_result[6]),score(predictions_result[7]),
       score(predictions_result[8]),score(predictions_result[9]),score(predictions_result[10]),
       score(predictions_result[11])
      ]

    maxvalue = max(y)
    minvalue = min(y)
    if abs(maxvalue) >= abs(minvalue):
      bestvalue = maxvalue
      bestindex = y.index(maxvalue)
    else:
      bestvalue = minvalue
      bestindex = y.index(minvalue)
    
    output_text = str(bestindex) + '天后：' + day_prediction_text(predictions_result[bestindex+1])
  
    
    #plt.plot(x,y,"b--",linewidth=3)
    plt.plot([0,10],[0,0],"k--",linewidth=1, label='当前价格')
    plt.plot(x,y,"b-.",linewidth=3, label=output_text, marker='x')
    plt.hlines(bestvalue, 0, 10, colors = "c", linestyles = "dotted")
    plt.vlines(bestindex, minvalue, maxvalue, colors = "c", linestyles = "dotted")
    plt.legend()
    plt.xlabel(u'未来10天的趋势。关注微信公众号:AI纪元，输入:' + alias_result[0]) #X轴标签
    plt.ylabel(u'分数[-100到100]\n绝对值越大代表上涨/下跌概率越高')  #Y轴标签 
    plt.title( alias_result[2] + ":" + alias_result[0] + " " 
              + utc2local(predictions_result[1]).strftime('%Y-%m-%d %H:%M') 
              + "\n预测结果由AI自动生成，不构成投资建议") #图标题 
    picture_name = 'Img/' + pinyin(alias_result[0]) + datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '.png'
    plt.savefig(picture_name)
    
  else:
    
    plt.figure(figsize=(10, 2 + len(alias_results)*0.12), dpi=100)
    
    market_list = []
    for alias_result in alias_results:

      #print(select_predictions_statment)

      #mycursor.execute(select_predictions_statment)
  
      #predictions_results = mycursor.fetchall()
  
      #if len(predictions_results) == 0:
      #  continue
  
      #predictions_result = predictions_results[0]
      predictions_result = alias_result
      x=[0,1,2,3,4,5,6,7,8,9,10]
      y=[0.0, score(predictions_result[2]),score(predictions_result[3]),score(predictions_result[4]),
         score(predictions_result[5]),score(predictions_result[6]),score(predictions_result[7]),
         score(predictions_result[8]),score(predictions_result[9]),score(predictions_result[10]),
         score(predictions_result[11])
        ]

      maxvalue = max(y)
      minvalue = min(y)
      if abs(maxvalue) >= abs(minvalue):
        bestvalue = maxvalue
        bestindex = y.index(maxvalue)
      else:
        bestvalue = minvalue
        bestindex = y.index(minvalue)
      
      market_list.append((predictions_result[12], bestvalue))
      
      #output_text = str(bestindex) + '天后：' + day_prediction_text(predictions_result[bestindex+1])
    market_list.sort(key=lambda x:x[1], reverse=False)
    market_index = 0
    y_market = [market[0] for market in market_list]
    x_score = [market[1] for market in market_list]
    y_pos = [i for i, _ in enumerate(y_market)]
    plt.barh(y_pos, x_score, color='green')
    plt.xlabel(u"强弱得分。关注微信公众号:AI纪元，输入:"+input_text)
    plt.ylabel(u"市场名称")
    plt.title(u"市场强弱排名:" + input_text + " " 
              + utc2local( max( [alias_result[1] for alias_result in alias_results] ) ).strftime('%Y-%m-%d %H:%M') 
              + "\n预测结果由AI自动生成，不构成投资建议")
    plt.yticks(y_pos, y_market)
    # Turn on the grid
    #plt.minorticks_on()
    #plt.grid(which='major', linestyle='-', linewidth='0.5', color='black')
    # Customize the minor grid
    #plt.grid(which='minor', linestyle=':', linewidth='0.5', color='gray')
    picture_name = 'Img/' + pinyin(input_text) + datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '.png'
    plt.savefig(picture_name)
    
  myMedia = Media()
  accessToken = Basic().get_access_token()
  filePath = picture_name
  mediaType = "image"
  murlResp = Media.uplaod(accessToken, filePath, mediaType)
  print(murlResp)

  #return output_text
  return murlResp

def day_prediction_text(prediction_result):
  prediction_score = ( ( prediction_result * 2 - 1 ) ** 1 ) / 2
  if prediction_score >= 0:
    return "上涨概率:" + ("%.3f" % ((prediction_score+0.5)*100) ) + "%"
  return "下跌概率:" + ("%.3f" % ((0.5-prediction_score)*100) ) + "%"

def score(prediction_result):
  return (prediction_result * 2 - 1) * 100

# 不带声调的(style=pypinyin.NORMAL)
def pinyin(word):
  s = ''
  for i in pypinyin.pinyin(word, style=pypinyin.NORMAL):
    s += ''.join(i)
  return s

class Media(object):
  #def __init__(self):
    #register_openers()
  #上传图片
  def uplaod(accessToken, filePath, mediaType):
    openFile = open(filePath, "rb")
    param = {'media': openFile.read()}
    #postData, postHeaders = poster.encode.multipart_encode(param)
    postData, content_type = encode_multipart_formdata(param)

    postUrl = "https://api.weixin.qq.com/cgi-bin/media/upload?access_token=%s&type=%s" % (accessToken, mediaType)
    #request = urllib2.Request(postUrl, postData, postHeaders)
    #urlResp = urllib2.urlopen(request)
    headers = {'Content-Type': content_type}
    files = {'media': open(filePath, "rb")}
    #urlResp = requests.post(postUrl, data=postData, headers=headers, files=files)
    urlResp = requests.post(postUrl, files=files)
    print(urlResp.text)
    return json.loads(urlResp.text)['media_id']
