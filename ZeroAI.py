# -*- coding: utf-8 -*-
# filename: ZeroAI.py

from wordcloud import WordCloud, STOPWORDS
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
import glob

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

def chat(input_text):
  output_text = ''

  picture_path = 'Img/' + pinyin(input_text) + datetime.datetime.now().strftime('%Y%m%d%H') + '*.png'
  picture_cache = glob.glob(picture_path)
  if picture_cache:
    picture_name = picture_cache[0]
    myMedia = Media()
    accessToken = Basic().get_access_token()
    filePath = picture_name
    mediaType = "image"
    murlResp = Media.uplaod(accessToken, filePath, mediaType)
    print(murlResp)
    return murlResp

  mydb = mysql.connector.connect(
    host=mypsw.wechatguest.host,
    user=mypsw.wechatguest.user,
    passwd=mypsw.wechatguest.passwd,
    database=mypsw.wechatguest.database,
    auth_plugin='mysql_native_password'
    )

  mycursor = mydb.cursor()

  input_text = input_text.strip().upper()
  
  stopwords = set(STOPWORDS) 
  comment_words = ''
  word_list = []
  word_frequencies = {}

  word_in_color.word_in_rising_major = ''
  word_in_color.word_in_falling_major = ''
  word_in_color.word_in_comments = []
  word_in_color.word_in_rising_minor = []
  word_in_color.word_in_falling_minor = []

  if input_text == '帮助' or input_text == 'HELP':
    output_text = '您好！欢迎来到AI纪元，我是通向未来之路的向导。\n' \
    '请输入：“全球股指”、“商品期货”、“外汇”、“个股”或“加密货币”，获取实时的市场趋势强弱排名。\n' \
    '输入具体的市场代码如“上证指数”、“黄金”或“比特币”，获取市场未来十天的涨跌趋势。\n' \
    '请使用分散化与自动化的方式进行交易，并控制每笔交易的风险值小于1%。\n' \
    'Hello! Welcome to the AI Era, I am the guide to the future.\n' \
    'Please enter: "INDICES", "COMMODITIES", "CURRENCIES", "STOCKS" or "CRYPTOCURRENCY" to get real-time market trend rankings.\n' \
    'Enter specific market codes such as “SSE”, “Gold” or “Bitcoin” to get the market trending in the next 10 days.\n' \
    'Please use a decentralized and automated approach to trading and control the risk value of each transaction to less than 1%.\n'
    return output_text

  select_alias_statment = "SELECT * FROM symbol_alias WHERE symbol_alias = '" + input_text + "'"

  print(select_alias_statment)

  mycursor.execute(select_alias_statment)
  
  alias_results = mycursor.fetchall()
  
  if len(alias_results) == 0:
    
    input_text = input_text.replace("/","%").replace("-","%").replace("*","%").replace(" ","%")

    select_alias_statment = "SELECT * FROM symbol_alias WHERE symbol_alias LIKE '%" + input_text + "%' group by symbol"

    print(select_alias_statment)

    mycursor.execute(select_alias_statment)
  
    alias_results = mycursor.fetchall()
  
    if len(alias_results) == 0:
      
      select_alias_statment = "SELECT * FROM market_alias WHERE market_alias LIKE '%" + input_text + "%'"
    
      print(select_alias_statment)
      
      mycursor.execute(select_alias_statment)
  
      alias_results = mycursor.fetchall()
  
      if len(alias_results) == 0:
        output_text = "市场'" + input_text + "'不存在！请尝试查询其它市场（如上证指数、黄金、比特币），可输入“全球股指”、“商品期货”、“外汇”、“个股”或“加密货币”查询汇总信息！"
        return output_text
    
      select_alias_statment = "SELECT predictions.*, symbol_alias.SYMBOL_ALIAS FROM symbol_alias " \
      " inner join predictions on predictions.symbol = symbol_alias.symbol " \
      " WHERE symbol_alias.market_type = '" + alias_results[0][1] + "' AND symbol_alias.market_order > 0 ORDER BY symbol ASC, time DESC"
      
      print(select_alias_statment)
      
      mycursor.execute(select_alias_statment)
  
      alias_results = mycursor.fetchall()
    
    elif len(alias_results) > 1:
      
      select_alias_statment = "SELECT predictions.*, symbol_alias.SYMBOL_ALIAS FROM symbol_alias " \
      " inner join predictions on predictions.symbol = symbol_alias.symbol WHERE symbol_alias LIKE '%" + input_text + "%' ORDER BY symbol ASC"

      print(select_alias_statment)

      mycursor.execute(select_alias_statment)
  
      alias_results = mycursor.fetchall() 
    
  plt.rcParams['font.sans-serif']=['SimHei']
  plt.rcParams['axes.unicode_minus']=False
    
  if len(alias_results) == 0:
    output_text = "市场'" + input_text + "'不存在！请尝试查询其它市场（如上证指数、黄金、比特币），可输入“全球股指”、“商品期货”、“外汇”、“个股”或“加密货币”查询汇总信息！"
    return output_text
    
  if len(alias_results) == 1:
    
    plt.figure(figsize=(6.4,6.4), dpi=100)
    
    alias_result = alias_results[0]
  
    select_predictions_statment = "SELECT * FROM predictions WHERE symbol = '" + alias_result[1] + "' ORDER BY time DESC"

    print(select_predictions_statment)

    mycursor.execute(select_predictions_statment)
  
    predictions_results = mycursor.fetchall()
  
    if len(predictions_results) == 0:
      output_text = "很抱歉，未找到市场'" + input_text + "'的预测信息！请尝试查询其它市场（如上证指数、黄金、比特币），可输入“全球股指”、“商品期货”、“外汇”、“个股”或“加密货币”查询汇总信息！"
      return output_text
    
    #select_prices_statment = "SELECT * FROM prices WHERE symbol = '" + alias_result[1] + "' ORDER BY DAY_INDEX asc"
    select_prices_statment = "SELECT * FROM price WHERE symbol = '" + alias_result[1] + "'"

    print(select_prices_statment)

    mycursor.execute(select_prices_statment)
  
    prices_results = mycursor.fetchall()
    
    predictions_result = predictions_results[0]
    
    plt.subplot(211)
    
    x=[i for i in range(1,121)]
    y=[prices_results[0][121-price_index] for price_index in range(120)]
    
    plt.title( alias_result[2] + ":" + alias_result[0] + " " 
              + predictions_result[1].strftime('%Y-%m-%d %H:%M') 
              + " UTC\n预测结果由AI自动生成，不构成投资建议") #图标题 
    
    plt.xlabel(u'过去120天收盘价') #X轴标签
    
    plt.plot(x,y,"green",linewidth=1, label=u"价格")
    
    bbox_props = dict(boxstyle='round',fc='w', ec='k',lw=1)
    
    plt.annotate(xy=[122,prices_results[0][2]], s=prices_results[0][2], bbox=bbox_props)
    
    plt.subplot(212)
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
    
    output_text = '1天后：' + day_prediction_text(predictions_result[2])
    #output_text = output_text + '\n' + str(bestindex) + '天后：' + day_prediction_text(predictions_result[bestindex+1])
  
    plt.plot([0,10],[0,0],"k--",linewidth=1, 
            )
    plt.plot(x,y,"b-.",linewidth=3, marker='x', 
            )
    plt.annotate(output_text, xy=(bestindex, bestvalue), xytext=(bestindex - 1.8, bestvalue * 2.0 / 4.0),
                 arrowprops=dict(facecolor='black', shrink=0.05),
                )
    
    plt.xlabel(u'关注微信公众号:AI纪元，输入:' + alias_result[0]) #X轴标签
    plt.ylabel(u'未来10天涨跌趋势[-100到100]\n')  #Y轴标签 
    picture_name = 'Img/' + pinyin(alias_result[0]) + datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '.png'
    plt.savefig(picture_name)
    
  else:
    
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
      
      word_single = predictions_result[12]
      word_single = "/" + word_single + "/"
      market_list.append((word_single, bestvalue))
      wordcount = abs(bestvalue)
      if bestvalue >= 0:
        word_in_color.word_in_rising_minor.append(word_single)
      else:
        word_in_color.word_in_falling_minor.append(word_single)
      
        
      word_frequencies[word_single] = wordcount
    market_list.sort(key=lambda x:x[1], reverse=False)
    time_str = "Time:"+max( [alias_result[1] for alias_result in alias_results] ).strftime('%Y-%m-%d_%H:%M') + "_UTC"
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
    
    picture_name = 'Img/' + pinyin(input_text) + datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '.png'
    plt.savefig(picture_name)
    
  myMedia = Media()
  accessToken = Basic().get_access_token()
  filePath = picture_name
  mediaType = "image"
  murlResp = Media.uplaod(accessToken, filePath, mediaType)
  print(murlResp)

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
    postData, content_type = encode_multipart_formdata(param)

    postUrl = "https://api.weixin.qq.com/cgi-bin/media/upload?access_token=%s&type=%s" % (accessToken, mediaType)
    headers = {'Content-Type': content_type}
    files = {'media': open(filePath, "rb")}
    urlResp = requests.post(postUrl, files=files)
    print(urlResp.text)
    return json.loads(urlResp.text)['media_id']
