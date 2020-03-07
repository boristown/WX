# -*- coding: utf-8 -*-
# filename: forcastline.py

import time
import datetime
import matplotlib.pyplot as plt

def get_version(input_text):
    if 'V1' in input_text:
        return input_text.replace("V1", "").strip(), "V1"
    if 'V2' in input_text:
        return input_text.replace("V2", "").strip(), "V2"
    return input_text.strip(), "V1"

def draw_single_v2(aiera_version, input_text, alias_results):
    output_text = ""
    alias_result = alias_results[0]
    select_predictions_statment = "SELECT * FROM predictions WHERE symbol = '" + alias_result[1] + "' ORDER BY time DESC"
    print(select_predictions_statment)
    mycursor.execute(select_predictions_statment)
    predictions_results = mycursor.fetchall()
    if len(predictions_results) == 0:
      output_text = "�ܱ�Ǹ��δ�ҵ��г�'" + input_text + "'��Ԥ����Ϣ���볢�Բ�ѯ�����г�������ָ֤�����ƽ𡢱��رң��������롰ȫ���ָ��������Ʒ�ڻ���������㡱�������ɡ��򡰼��ܻ��ҡ���ѯ������Ϣ��"
      return None, output_text
    select_prices_statment = "SELECT * FROM price WHERE symbol = '" + alias_result[1] + "'"
    print(select_prices_statment)
    mycursor.execute(select_prices_statment)
    prices_results = mycursor.fetchall()
    picture_name = draw_market(aiera_version, alias_result, prices_results, predictions_results)
    return picture_name, output_text

def draw_market(aiera_version, alias_result, prices_results, predictions_results):
    plt.figure(figsize=(6.4,6.4), dpi=100, facecolor='black')
    predictions_result = predictions_results[0]
    #plt.subplot(211)
    plt.style.use('dark_background')
    x=[i for i in range(1,122)]
    y=[prices_results[0][121-price_index] for price_index in range(120)]
    plt.title( alias_result[2] + ":" + alias_result[0] + " " 
              + predictions_result[1].strftime('%Y-%m-%d %H:%M') 
              + " UTC\n΢�Ź��ںţ�AI��Ԫ WeChat Public Account: AI Era " + aiera_version) #ͼ���� 
    #plt.xlabel(u'��ȥ120�����̼�') #X���ǩ
    prediction_text, nextprice = day_prediction_text(predictions_result[2],float(prices_results[0][2]),float(prices_results[0][122]))
    plt.xlabel( prediction_text ) #X���ǩ
    #plt.plot(x,y,"green",linewidth=1, label=u"�۸�")
    y.append(nextprice)
    currentprice = prices_results[0][2]
    if nextprice >= currentprice:
      plt.plot(x,y,"white",label="ATR��"+ str(float(prices_results[0][122])*100) + "%" )
      plt.fill_between(x,min(y),y,facecolor="white",alpha=0.3)
      plt.plot(x,[currentprice] * 121, "w--", label="Price:"+str(currentprice))
    else:
      plt.plot(x,y,"red", label="ATR��"+ str(float(prices_results[0][122])*100) + "%" )
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
    
    picture_name = 'Img/' + pinyin(alias_result[0]) + "_" +  aiera_version + datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '.png'
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
    
  return "���ռ۸�Tomorrow price:" + str(nextprice), nextprice

# ����������(style=pypinyin.NORMAL)
def pinyin(word):
  s = ''
  for i in pypinyin.pinyin(word, style=pypinyin.NORMAL):
    s += ''.join(i)
  return s