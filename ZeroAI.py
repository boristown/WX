# -*- coding: utf-8 -*-
# filename: ZeroAI.py

import mysql.connector
import mypsw
import time
import datetime
import matplotlib.pyplot as plt

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
      output_text = "市场'" + input_text + "'不存在！请尝试查询其它市场（如上证指数、黄金、比特币）！"
      return output_text
  
  alias_result = alias_results[0]
  
  select_predictions_statment = "SELECT * FROM predictions WHERE symbol = '" + alias_result[1] + "' ORDER BY time DESC"

  print(select_predictions_statment)

  mycursor.execute(select_predictions_statment)
  
  predictions_results = mycursor.fetchall()
  
  if len(predictions_results) == 0:
    output_text = "很抱歉，未找到市场'" + input_text + "'的预测信息！请尝试查询其它市场（如上证指数、黄金、比特币）！"
    return output_text
  
  predictions_result = predictions_results[0]
  
  output_text = '市场名:' + alias_result[0] + '\n' \
    '市场类型：' + alias_result[2] + '\n' \
    '预测时间：' + utc2local(predictions_result[1]).strftime('%Y-%m-%d %H:%M') + '\n' \
    '一天后：' + day_prediction_text(predictions_result[2]) + '\n' \
    '两天后：' + day_prediction_text(predictions_result[3]) + '\n' \
    '三天后：' + day_prediction_text(predictions_result[4]) + '\n' \
    '四天后：' + day_prediction_text(predictions_result[5]) + '\n' \
    '五天后：' + day_prediction_text(predictions_result[6]) + '\n' \
    '六天后：' + day_prediction_text(predictions_result[7]) + '\n' \
    '七天后：' + day_prediction_text(predictions_result[8]) + '\n' \
    '八天后：' + day_prediction_text(predictions_result[9]) + '\n' \
    '九天后：' + day_prediction_text(predictions_result[10]) + '\n' \
    '十天后：' + day_prediction_text(predictions_result[11]) + '\n'
    
  print(output_text)
  
  x=[1,2,3,4,5,6,7,8,9,10]
  y=[predictions_result[2],predictions_result[3],predictions_result[4],
     predictions_result[5],predictions_result[6],predictions_result[7],
     predictions_result[8],predictions_result[9],predictions_result[10],
     predictions_result[11]
    ]
  plt.rcParams['font.sans-serif']=['SimHei']
  plt.rcParams['axes.unicode_minus']=False
  plt.figure()
  plt.plot(x,y,"b--",linewidth=1)
  plt.xlabel(u'天数') #X轴标签
  plt.ylabel(u'涨跌概率')  #Y轴标签
  plt.title(alias_result[0]) #图标题
  picture_name = alias_result[0] + datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '.png'
  plt.savefig(picture_name)
  
  return output_text

def day_prediction_text(prediction_result):
  prediction_score = ( ( prediction_result * 2 - 1 ) ** 1 ) / 2
  if prediction_score >= 0:
    return "上涨概率:" + ("%.3f" % ((prediction_score+0.5)*100) ) + "%"
  return "下跌概率:" + ("%.3f" % ((0.5-prediction_score)*100) ) + "%"
