# -*- coding: utf-8 -*-
# filename: forcastline.py

import time
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pypinyin
import math
import re

def get_version(input_text):
    if 'V1' in input_text:
        return input_text.replace("V1", "").strip(), "V1"
    if 'V2' in input_text:
        return input_text.replace("V2", "").strip(), "V2"
    return input_text.strip(), "V2"

def dateoffset(inputstr):
    keystr = ""
    valuedata = ""
    try:
        valuedata =  datetime.datetime.strptime(inputstr, '%Y-%m-%d')
        keystr = "DATE"
    except :
        try:
            valuedata = datetime.datetime.strptime(inputstr, '%Y/%m/%d')
            keystr = "DATE"
        except Exception as e:
            try:
                valuedata = datetime.datetime.strptime(inputstr, '%Y%m%d')
                keystr = "DATE"
            except Exception as e:
                try:
                    valuedata = int(inputstr)
                    keystr = "OFFSET"
                except Exception as e:
                    pass
    return keystr, valuedata

def command(input):
    symbol = input
    params = {}
    params["LEN"] = 120
    params["OFFSET"] = 0
    params["DATE"] = datetime.datetime.utcnow()+datetime.timedelta(days=0)

    #startdate = ""
    #len = 0
    pattern = r'([^-=\[\]\s]+)'
    matchs = re.finditer(pattern,input,re.S)
    for cell_matchs in matchs:
        symbol = str(cell_matchs.group(1))
        break
    
    pattern = r'\[([^:\[\]]*)\]'
    matchs = re.finditer(pattern,input,re.S)
    for cell_matchs in matchs:
        if str(cell_matchs.group(1)):
            keystr, valuedata = dateoffset(str(cell_matchs.group(1)))
            if keystr:
                params[keystr] = valuedata

    pattern = r'\[([^:\[\]]*):([^:\[\]]*)\]'
    matchs = re.finditer(pattern,input,re.S)
    for cell_matchs in matchs:
        if str(cell_matchs.group(1)):
            keystr, valuedata = dateoffset(str(cell_matchs.group(1)))
            if keystr:
                params[keystr] = valuedata
        if str(cell_matchs.group(2)):
            params["LEN"] = str(cell_matchs.group(2))
    #pattern = r'(.+?)\s+?-([^-=]+)=([^-=]+)\s+?-([^-=]+)=([^-=]+)'
    pattern = r'-([^-=\s]+)=([^-=\s]+)'
    matchs = re.finditer(pattern,input,re.S)
    for cell_matchs in matchs:
        params[str(cell_matchs.group(1))] = str(cell_matchs.group(2))
    params["DATE"] = params["DATE"].strftime("%Y-%m-%d")
    return symbol, params

def draw_single_v2(input_text, alias_results, mycursor, params, origin_input):
    output_text = ""
    alias_result = alias_results[0]
    select_predictions_statment = "SELECT pricehistory.* FROM pricehistory " \
    " inner join predictlog on pricehistory.symbol = predictlog.symbol and predictlog.PREDICTDATE > '1950-1-1' " \
    " WHERE pricehistory.l > 0 and pricehistory.c > 0 and pricehistory.symbol = '" + alias_result[1] + "' and pricehistory.date <= '" + params["DATE"] + "' " \
    " ORDER BY pricehistory.date "  \
    " DESC limit "  + str(abs(int(params["OFFSET"]))) + " , " + str(abs(int(params["LEN"])))
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
    picture_name = draw_market_v2(alias_result, predictions_results, params, origin_input)
    return picture_name, output_text

def draw_market_v2(alias_result, predictions_results, params, origin_input):
    #plt.figure(figsize=(6.4,6.4), dpi=100, facecolor='black')
    plt.figure(figsize=(8,8), dpi=150, facecolor='black')
    prediction_count = len(predictions_results)
    predictions_result = predictions_results[0]
    plt.style.use('dark_background')
    o = []
    h = []
    l = []
    c = []
    v = []
    f = []
    date = []
    date_predict = []
    for predictions_result in predictions_results:
        date.append(predictions_result[1])
        date_predict.append(predictions_result[1]+datetime.timedelta(days=1))
        o.append(predictions_result[2])
        h.append(predictions_result[3])
        l.append(predictions_result[4])
        c.append(predictions_result[5])
        v.append(predictions_result[6])
        f.append(predictions_result[7])
    o = o[-1::-1]
    h = h[-1::-1]
    l = l[-1::-1]
    c = c[-1::-1]
    v = v[-1::-1]
    f = f[-1::-1]
    date = date[-1::-1]
    date_predict = date_predict[-1::-1]
    lastclose = o[0]
    trsum = 0.0
    for priceIndex in range(len(c)):
        maxp = max(lastclose, o[priceIndex], h[priceIndex], l[priceIndex], c[priceIndex])
        minp = min(lastclose, o[priceIndex], h[priceIndex], l[priceIndex], c[priceIndex])
        tr = maxp - minp
        if tr > 0 and minp > 0:
          tr = tr / minp
        else:
          tr = 0
        trsum += tr
        lastclose = c[priceIndex]
    atr = trsum / (len(c) * 1.0)
    forcast_price_list = [forcast_price(f[n],c[n],atr) for n in range(len(c))]
    #plt.title( alias_result[2] + ":" + alias_result[0] + " "
    plt.title( alias_result[2] + ":" + origin_input + " "
              + predictions_results[0][1].strftime('%Y-%m-%d')
              + " UTC\n预测模型：海龟二号" ) #图标题 
    #prediction_text, nextprice = day_prediction_text(predictions_result[2],float(prices_results[0][2]),float(prices_results[0][122]))
    plt.xlabel( "均幅指标ATR:" + str(atr * 100) + "%\n红色是错误的预测，绿色是正确的预测，紫色是对未来的预测。")
    #fig = plt.figure()
    #ax = fig.add_axes([0, 0, 1, 1])
    plt.text(0.5, 0.5, '红色',
        horizontalalignment='center',
        verticalalignment='center',
        fontsize=20, color='red',
        #transform=ax.transAxes
        )
    #ax.set_axis_off()
    locator = mdates.AutoDateLocator()
    formatter = mdates.ConciseDateFormatter(locator)
    plt.gca().xaxis.set_major_locator(locator)
    plt.gca().xaxis.set_major_formatter(formatter)
    #plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    #plt.gca().xaxis.set_major_locator(mdates.DayLocator(bymonthday=None, interval=14, tz=None))
    #y.append(nextprice)
    currentprice = predictions_results[0][5]
    #if nextprice >= currentprice:
    #plt.plot(date,o,"yellow",label="Open")
    plt.plot(date,h,"gray",label="最高价High")
    plt.plot(date,c,"white",label="收盘价Close", marker = ".")
    plt.plot(date,l,"gray",label="最低价Low")
    if atr > 0:
        for priceIndex in range(len(c)):
            if priceIndex < (len(c) -1):
                if c[priceIndex] > 0 and c[priceIndex + 1] > 0:
                    changerate = max(c[priceIndex],c[priceIndex + 1]) / min(c[priceIndex],c[priceIndex + 1])
                else:
                    changerate = 1.0
                if changerate > 0 and 1 + atr > 0:
                    #print(changerate, 1 + atr)
                    changeatr = math.log(changerate, 1 + atr)
                else:
                    changeatr = 0
                alpha = math.atan(changeatr * 1.5) * 2 / math.pi 
                linewidth = 2
                if c[priceIndex + 1] >= c[priceIndex] and forcast_price_list[priceIndex] >= c[priceIndex] or c[priceIndex + 1] <= c[priceIndex] and forcast_price_list[priceIndex] <= c[priceIndex]:
                    color = "limegreen"
                else:
                    color = "crimson"
            else:
                color = "darkviolet"
                alpha = 1
                linewidth = 2
            plt.plot([date[priceIndex], date_predict[priceIndex]],[c[priceIndex], forcast_price_list[priceIndex]], color = color, marker = "o", alpha = alpha, linewidth = linewidth, markevery=[1])
        #plt.arrow(date[priceIndex], c[priceIndex], 1, forcast_price_list[priceIndex]-c[priceIndex], fc=color, ec=color, head_width=4, head_length=6)

    #plt.plot(date,v,"white",label="Volume")
    #plt.gcf().autofmt_xdate()
    #plt.fill_between(date,min(c),c,facecolor="white",alpha=0.3)
    plt.fill_between(date,l,h,facecolor="gray",alpha=0.3)
    #plt.fill_between(date,min(l),v,facecolor="white",alpha=0.3)
    plt.plot(date,[currentprice] * int(params["LEN"]), "w--", label="当前价Current:"+str(currentprice))
    plt.plot(date_predict,[forcast_price_list[-1]] * int(params["LEN"]), color = "darkviolet", linestyle = "--", label="预测价Forcast:"+str(forcast_price_list[-1]))
    #plt.fill_between(date_predict[:-1],c[1:],forcast_price_list[:-1],facecolor="darkviolet", alpha=0.5)
    #plt.fill_between(date_predict, c, forcast_price_list,facecolor="darkviolet", alpha=0.5)
    correctflag, predicttext, predictxy, predicttextxy = getpredicttext(date, c, forcast_price_list)
    plt.annotate(predicttext, xy=predictxy, xytext=predicttextxy, arrowprops=dict(facecolor='limegreen' if correctflag else 'crimson', shrink=0.05), bbox=dict(boxstyle="round,pad=0.5", fc='limegreen' if correctflag else 'crimson', ec='white', lw=1, alpha = 0.3))

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
    
    picture_name = 'Img/' + pinyin(alias_result[0]) + "_V2" + "_" + str(params["OFFSET"]) + "_" + str(params["LEN"]) + "_" + str(params["DATE"]) + "_" + datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '.png'
    plt.savefig(picture_name, facecolor='black')
    return picture_name

def getpredicttext(date, c, forcast_price_list):
    predicttext = ""
    maxratio = 0.0
    maxindex = 0
    riseorfall = ""
    for priceindex in range(len(c)):
        if priceindex > 0:
            ratio = max(c[priceindex], c[priceindex-1]) / min(c[priceindex], c[priceindex-1])
            if ratio > maxratio:
                maxratio = ratio
                maxindex = priceindex
                if c[priceindex] >= c[priceindex-1]:
                    riseorfall = "暴涨"
                    if forcast_price_list[priceindex-1] >= c[priceindex-1]:
                        correctflag = True
                    else:
                        correctflag = False
                else:
                    riseorfall = "暴跌"
                    if forcast_price_list[priceindex-1] < c[priceindex-1]:
                        correctflag = True
                    else:
                        correctflag = False
    yrange = max(max(c),max(forcast_price_list)) - min(min(c),min(forcast_price_list))
    ymiddle =max(max(c),max(forcast_price_list)) / 2 + min(min(c),min(forcast_price_list)) / 2 
    datetext = date[maxindex].strftime('%Y{y}%m{m}%d{d}').format(y='年', m='月', d='日')
    if correctflag:
        correcttext = "成功预测到"
    else:
        correcttext = "未能预测到"
    predicttext = datetext + "，\nAI" + correcttext + "\n市场价格" +  riseorfall

    predictxy = (date[maxindex],forcast_price_list[maxindex-1])
    #x position
    if (maxindex + 1) / len(c) > 0.5:
        textx = int(maxindex - 0.25 * len(c))
    else:
        textx = int(maxindex + 0.1 * len(c))
    #y position
    if forcast_price_list[maxindex] > ymiddle:
        texty = forcast_price_list[maxindex-1] - 0.25 *  yrange
    else:
        texty = forcast_price_list[maxindex-1] + 0.1 *  yrange
    predicttextxy = (date[textx],texty)

    return correctflag, predicttext, predictxy, predicttextxy

def day_prediction_text(prediction_result, price, atr):
  if prediction_result > 0.95:
    prediction_result = 0.95
  if prediction_result < 0.05:
    prediction_result = 0.05
  prediction_score = ( ( prediction_result * 2 - 1 ) ** 1 ) / 2 * math.pi 
  if prediction_score >= 0:
    nextprice = price * ( ( 1 + atr ) ** math.tan(prediction_score) )
  else:
    nextprice = price / ( ( 1 + atr ) ** abs(math.tan(prediction_score)) )
    
  return "Tomorrow price:" + str(nextprice), nextprice

def forcast_price(prediction_result, price, atr):
  if prediction_result > 0.95:
    prediction_result = 0.95
  if prediction_result < 0.05:
    prediction_result = 0.05
  prediction_score = ( ( prediction_result * 2 - 1 ) ** 1 ) / 2 * math.pi 
  if prediction_score >= 0:
    nextprice = price * ( ( 1 + atr ) ** math.tan(prediction_score) )
  else:
    nextprice = price / ( ( 1 + atr ) ** abs(math.tan(prediction_score)) )
  return nextprice

def pinyin(word):
  s = ''
  for i in pypinyin.pinyin(word, style=pypinyin.NORMAL):
    s += ''.join(i)
  return s

def text_no_market(input_text):
    return "很抱歉，未找到市场'" + input_text + "'的预测信息！请尝试查询其它市场（如上证指数、黄金、比特币），可输入“全球股指”、“商品期货”、“外汇”、“个股”或“加密货币”查询汇总信息！"