import requests # 引入网络请求模块
import time
import json
import mypsw
import mysql.connector

stategy_mirror = {0:1, 1:0, 2:3, 3:2, 4:5, 5:4, 6:7, 7:6, 8:8, 9:9}

def load_response(response):
    if response.status_code == 200:
        resultObj = json.loads(response.text)
    elif response.status_code == 429:
        #return json.dumps({"retry-after": response.headers["Retry-After"]})
        time.sleep(int(response.headers["Retry-After"]))
        return None
    else:
        return None
    return resultObj

def init_mycursor():
    myconnector = mysql.connector.connect(
      host=mypsw.wechatadmin.host,
      user=mypsw.wechatadmin.user,
      passwd=mypsw.wechatadmin.passwd,
      database=mypsw.wechatadmin.database,
      auth_plugin='mysql_native_password'
      )
    mycursor = myconnector.cursor()
    return myconnector, mycursor

def local_cursor():
    myconnector = mysql.connector.connect(
      host=mypsw.localserver.host,
      user=mypsw.localserver.user,
      passwd=mypsw.localserver.passwd,
      database=mypsw.localserver.database,
      auth_plugin='mysql_native_password'
      )
    mycursor = myconnector.cursor()
    return myconnector, mycursor

def init_aitradin_cursor():
    myconnector = mysql.connector.connect(
      host=mypsw.host,
      user=mypsw.user,
      passwd=mypsw.passwd,
      database=mypsw.database,
      auth_plugin='mysql_native_password'
      )
    mycursor = myconnector.cursor()
    return myconnector, mycursor

def init_localcursor():
    myconnector = mysql.connector.connect(
      host=mypsw.loacalhost,
      user=mypsw.loacaluser,
      passwd=mypsw.loacalpasswd,
      database=mypsw.loacaldatabase,
      auth_plugin='mysql_native_password'
      )
    mycursor = myconnector.cursor()
    return myconnector, mycursor
    