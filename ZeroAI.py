# -*- coding: utf-8 -*-
# filename: ZeroAI.py

import mysql.connector
import mypsw

def chat(input_text):
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
   
  select_predictions_statment = "SELECT * FROM predictions WHERE symbol = '" + input_text + "'"

  print(select_predictions_statment)

  mycursor.execute(select_predictions_statment)

  predictions_result = mycursor.fetchone()
  
  print(predictions_result)
    
  return predictions_result
