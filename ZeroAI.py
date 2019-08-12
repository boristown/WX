# -*- coding: utf-8 -*-
# filename: ZeroAI.py

import mysql.connector
import mypsw

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

  select_alias_statment = "SELECT * FROM symbol_alias WHERE symbol = '" + input_text + "'"

  print(select_alias_statment)

  mycursor.execute(select_alias_statment)

  alias_result = mycursor.fetchone()
  
  if alias_result is None:
    output_text = "市场'" + input_text + "'不存在！请尝试查询其它市场（如BTCUSD）！"
    return output_text
    
  select_predictions_statment = "SELECT * FROM predictions WHERE symbol = '" + alias_result[1] + "'"

  print(select_predictions_statment)

  mycursor.execute(select_predictions_statment)

  predictions_result = mycursor.fetchone()
  
  if predictions_result is None:
    output_text = "很抱歉，未找到市场'" + input_text + "'的预测信息！请尝试查询其它市场（如BTCUSD）！"
    return output_text
  
  output_text = '市场编号:' + alias_result[1] + '\n' \
    '预测日期：' + predictions_result[1] + '\n' \
    '一天后：' + predictions_result[2] + '\n' \
    '两天后：' + predictions_result[3] + '\n' \
    '三天后：' + predictions_result[4] + '\n' \
    '四天后：' + predictions_result[5] + '\n' \
    '五天后：' + predictions_result[6] + '\n' \
    '六天后：' + predictions_result[7] + '\n' \
    '七天后：' + predictions_result[8] + '\n' \
    '八天后：' + predictions_result[9] + '\n' \
    '九天后：' + predictions_result[10] + '\n' \
    '十天后：' + predictions_result[11] + '\n'
    
  print(output_text)

  return output_text
