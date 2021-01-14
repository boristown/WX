import requests # 引入网络请求模块
import time
import json
import mypsw
import mysql.connector

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
      host=mypsw.host,
      user=mypsw.user,
      passwd=mypsw.passwd,
      database=mypsw.database,
      auth_plugin='mysql_native_password'
      )
    mycursor = myconnector.cursor()
    return myconnector, mycursor