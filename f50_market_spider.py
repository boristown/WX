import requests
import json
#import common
import re
import datetime
import time
import math
import common
import asyncio
import mypsw
#from pyppeteer import launch

#import f51_simulated_trading

#一次爬取所有市场的爬虫程序
#加密货币:
#ID长度：7位
#ID规则:1[01][678]____

#个股
#ID长度：

#https://cn.investing.com/search/?q=BTC
#window.allResultsQuotesDataArray = [{"pairId":"{1}"……"symbol":"{2}"……

time_start = None
dateformat = "%Y-%m-%d"
input_days_len = 225
atr_len = 20
#predict_len = 4500
risk_factor = 1.5
#startdays = 4800
predict_batch = 50

side_dict = {0:"sell",1:"buy",2:"sell",3:"buy",4:"sell",5:"buy",6:"sell",7:"buy",8:"sell",9:"buy"}

stop_loss_dict = {0:0.16,1:0.16,
                  2:0.24,3:0.24,
                  4:0.36,5:0.36,
                  6:0.54,7:0.54,
                  8:0.81,9:0.81,
                  #10:0.40,11:0.80}
                  10:1.00,11:2.00}
order_range_dict = {10:0.20,11:0.40}

stop_loss_dict11 = {0:0.16,1:0.16,
                  2:0.24,3:0.24,
                  4:0.36,5:0.36,
                  6:0.54,7:0.54,
                  8:1.50, 9:2.00}

order_range_dict11 = {8:0.30,9:0.40}

spiral_matrix  = [
    0,     1,     2,    3,     4,      5,    6,     7,      8,    9,   10,   11,   12,  13,  14,
  55,   56,   57,  58,    59,   60,  61,   62,    63,  64,   65,   66,   67,  68,  15,
  54, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114,  69, 16,
  53, 102, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 115,  70, 17,
  52, 101, 142, 175, 176, 177, 178, 179, 180, 181, 182, 153, 116,  71, 18,
  51, 100, 141, 174, 199, 200, 201, 202, 203, 204, 183, 154, 117,  72, 19,
  50,  99, 140, 173, 198, 215, 216, 217, 218, 205, 184, 155, 118,  73,  20,
  49,  98, 139, 172, 197, 214, 223, 224, 219, 206, 185, 156, 119,  74,  21,
  48,  97, 138, 171, 196, 213, 222, 221, 220, 207, 186, 157, 120,  75,  22,
  47,  96, 137, 170, 195, 212, 211, 210, 209, 208, 187, 158, 121,  76,  23,
  46,  95, 136, 169, 194, 193, 192, 191, 190, 189, 188, 159, 122,  77,  24,
  45,  94, 135, 168, 167, 166, 165, 164, 163, 162, 161, 160, 123,  78,  25,
  44,  93, 134, 133, 132, 131, 130, 129, 128, 127, 126, 125, 124,  79,  26,
  43,  92,   91,   90,   89,  88,    87,   86,   85,   84,   83,   82,   81,  80,  27,
  42,  41,   40,   39,   38,  37,    36,   35,   34,   33,   32,   31,   30,  29,  28
  ]

def save_symbol_search(symbol, response):
    print("Saving " + symbol + str(response))
    myconnector, mycursor = common.local_cursor()
    statement = '''
    insert into
    `symbol_search` ( `symbol`, `response` )
    values ( %s, %s )
    ON DUPLICATE KEY UPDATE
    `symbol` = VALUES(`symbol`), 
    `response` = VALUES(`response`)
    ;
    '''
    #print(simulate_result)
    mycursor.execute(statement, (symbol, response))
    myconnector.commit()
    return mycursor.rowcount

def read_symbol_search(symbol):
    print("Reading " + symbol)
    myconnector, mycursor = common.local_cursor()
    statement = '''
    select
    `symbol`,
    `response`
    from 
    `symbol_search`
    where 
    `symbol` = %s
    ;
    '''
    mycursor.execute(statement, (symbol, ))
    list_results = mycursor.fetchall()
    response = ""
    for list_result in list_results:
        response = str(list_result[1])
    return response

def search_for_symbol(symbol):
    response = read_symbol_search(symbol)
    if len(response) == 0: 
        url = "https://cn.investing.com/search/?q=" + symbol
        headers={"user-agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36"}
        response = requests.get(url, headers=headers)
        marketListString = ""
        if response.status_code == 200:
            string = response.text
            #print(string)
            pattern = 'allResultsQuotesDataArray\s+?=\s+?(\[.+?\]);\s+?</script>'
            searchObj = re.search(pattern, string, flags=0)
            if searchObj:
                marketListString = searchObj.group(1)
            if marketListString:
                save_symbol_search(symbol, marketListString)
            return marketListString
    else:
        return response

def screen_size():
    """使用tkinter获取屏幕大小"""
    import tkinter
    tk = tkinter.Tk()
    width = tk.winfo_screenwidth()
    height = tk.winfo_screenheight()
    tk.quit()
    return width, height

async def search_for_symbol_pyppeteer(symbol):
    response = read_symbol_search(symbol)
    if len(response) == 0:
        from pyppeteer import launch
        url = "https://cn.investing.com/search/?q=" + symbol
        headers={"user-agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36"}
        width, height = screen_size()
        browser = await launch(headless=False, args=[f'--window-size={width},{height}'])
        page = await browser.newPage()
        await page.setViewport({'width': width, 'height': height})
        await page.setJavaScriptEnabled(enabled=True)
        await page.goto(url)
        await asyncio.sleep(10)
        response = await page.content()
        print(response)
        browser.close()
        #response = requests.get(url, headers=headers)
        marketListString = ""
        #if response.status_code == 200:
            #string = response.text
        string = response.text
        #print(string)
        pattern = 'allResultsQuotesDataArray\s+?=\s+?(\[.+?\]);\s+?</script>'
        searchObj = re.search(pattern, string, flags=0)
        if searchObj:
            marketListString = searchObj.group(1)
        save_symbol_search(symbol, marketListString)
        return marketListString
    else:
        return response

def get_best_market(marketList):
    is_crypto = False
    if len(marketList) > 0:
        marketList = sorted(marketList, key = lambda marketList: marketList["pairId"])
        if marketList[0]["pair_type"] == "equities":
            for market in marketList:
                if market["flag"] == "China" and market["pair_type"] == "equities":
                    return market, is_crypto
            for market in marketList:
                if market["flag"] == "Hong_Kong" and market["pair_type"] == "equities":
                    return market, is_crypto
            for market in marketList:
                if market["flag"] == "USA" and market["pair_type"] == "equities":
                    return market, is_crypto
        if marketList[0]["pair_type"] == "indice":
            for market in marketList:
                if market["flag"] == "China" and market["pair_type"] == "indice":
                    return market, is_crypto
            for market in marketList:
                if market["flag"] == "Hong_Kong" and market["pair_type"] == "indice":
                    return market, is_crypto
            for market in marketList:
                if market["flag"] == "USA" and market["pair_type"] == "indice":
                    return market, is_crypto
        for market in marketList:
            is_crypto = market["isCrypto"] or (market["pair_type"] == "indice" and market["flag"] != "USA" and market["flag"] != "Hong_Kong" and market["flag"] != "China")
            return market, is_crypto
    return None, is_crypto

def get_v1_prediction(exchange, symbol, category, exchange_text, symbol_text):
  url = "https://aitrad.in/api/v1/predict?category=" + str(category) + "&exchange=" + exchange + "&symbol=" + symbol + "&secret=" + mypsw.api_secret
  response = requests.get(url)
  prediction = json.loads(response.text)
  if prediction["code"] == 200:
    return get_predict_info(exchange_text, symbol_text, prediction)
  else:
    return prediction["msg"][:600]

def get_best_response(marketList):
    market_index = 0
    response_text = "市场清单："
    for market in marketList:
        market_index += 1
        name = market["name"].replace("Investing.com","")
        exchange = market["exchange"]
        return get_v1_prediction("exchange",str(market["pairId"]),1,exchange,name)

def side_text(side):
    if str(side).upper() == 'BUY':
        return "买入Buy"
    return "卖出Sell"

def bool_text(bl):
    if bl:
        return "是True"
    else:
        return "否False"

def timestampToLocal(ts):
    return time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(float(ts)/1000))

def get_predict_info(exchange_text, symbol_text, prediction):
  strategy = prediction["strategy"]
  if not exchange_text:
      exchange_text = strategy["exchange"]
      symbol_text = strategy["symbol"]
  order_item = prediction["orders"]
  #timeStamp = int(float(prediction["strategy"]["ai"])/1000.0)
  #timeArray = datetime.datetime.utcfromtimestamp(timeStamp)
  #timeArray = time.localtime(timeStamp)
  #otherStyleTime = timeArray.strftime("%Y-%m-%d %H:%M:%S")
  
  sign_text = '\n——预言家/Prophet\n诞生Birth:' + timestampToLocal(strategy["ai"]) + '\n纪元Epoch:' + str(strategy['epoch']) + \
    '\n训练集Training:' + str(round(strategy["fitness"]*100.0,2)) + '%' \
    '\n验证集Validation:' + str(round(strategy["validation"]*100.0,2)) + '%' \
    '\n提示Tips：' + \
    '\n以上预测结果由“预言家II”AI基于128日K线自动生成，仅供参考。\n请结合多个市场的预测结果，以评分Score超过50分的预测结果为准。\n请在浮动亏损超过0.5ATR或本金的1%时止损。'

  text = "市场Symbol:" + symbol_text + \
    '\n交易所Exchange:' + exchange_text +\
    '\n日期UTC:' + strategy["date"] + \
    '\n评分Score:' + str(strategy["score"]) + \
    '\n方向Side:' + side_text(strategy["side"]) + \
    '\n最新价ClosePrice:' + str(strategy["close_price"]) + \
    '\n当日最高价HighPrice:' + str(strategy["high_price"]) + \
    '\n当日最低价LowPrice:' + str(strategy["low_price"]) + \
    '\n均幅指标ATR(20):' + str(strategy["atr"]) + "%" \
    '\n头寸大小Position:' + str(strategy["amount"]) + "%" \
    '\n交易率TradeProb:' + str(float(strategy["trade_prob"])*100) + "%" \
    '\n镜像Mirror:' + bool_text(strategy["mirror"]) + \
    '\n预测时间PredictAt:' + timestampToLocal(strategy["predict_timestamp"]) + \
    sign_text
  return text

def get_all_markets(marketList):
    market_index = 0
    response_text = "市场清单："
    for market in marketList:
        market_index += 1
        url = "aitrad.in/api/v1/predict?category=1&symbol=" + str(market["pairId"]) + "&secret=" + mypsw.api_secret
        name = market["name"].replace("Investing.com","")
        exchange = market["exchange"]
        response_text += "\n" + str(market_index) + " " + name + " " + exchange + ":\n" + url
        #insert_val.append((str(market["pairId"]), json.dumps(market)))
    sign_text = "——预言家/Prophet\n"
    response_text += "\n请复制链接到浏览器中查看决策结果！\n"+sign_text
    #mycursor.executemany(statement, insert_val)
    #myconnector.commit()
    return response_text

def get_history_price(pairId, pair_type, startdays):
    priceList = []
    if pair_type == "currency":
        smlID_str = '1072600'
    else:
        smlID_str = '25609849'

    url = "https://cn.investing.com/instruments/HistoricalDataAjax"

    headers = {
        'accept': "text/plain, */*; q=0.01",
        'origin': "https://cn.investing.com",
        'x-requested-with': "XMLHttpRequest",
        'user-agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36",
        'content-type': "application/x-www-form-urlencoded",
        'cache-control': "no-cache",
        'postman-token': "17db1643-3ef6-fa9e-157b-9d5058f391e4"
        }
    st_date_str = (datetime.datetime.utcnow() + datetime.timedelta(days = -startdays)).strftime(dateformat).replace("-","%2F")
    end_date_str = (datetime.datetime.utcnow()).strftime(dateformat).replace("-","%2F")
    payload = "action=historical_data&curr_id="+ pairId +"&end_date=" + end_date_str + "&header=null&interval_sec=Daily&smlID=" + smlID_str + "&sort_col=date&sort_ord=DESC&st_date=" + st_date_str
    print(payload)
    try:
        response = requests.request("POST", url, data=payload, headers=headers, verify=False, timeout=40)
    except Exception as e:
        time.sleep(7)
    if response == None:
        pass
    print(response.text)
    table_pattern = r'<tr>.+?<td.+?data-real-value="([^><"]+?)".+?</td>' \
            '.+?data-real-value="([^><"]+?)".+?</td>.+?data-real-value="([^><"]+?)".+?</td>'  \
            '.+?data-real-value="([^><"]+?)".+?</td>.+?data-real-value="([^><"]+?)".+?</td>'  \
            '.+?</tr>'
    row_matchs = re.finditer(table_pattern,response.text,re.S)
    timestamp_list = []
    price_list = []
    openprice_list = []
    highprice_list = []
    lowprice_list = []
    price_count = 0
    insert_val = []
    #print(str(response.text))
    lastclose = -1
    for cell_matchs in row_matchs:
        price_count += 1
        #print(str(cell_matchs.group(0)))
        timestamp = int(str(cell_matchs.group(1)))
        price = float(str(cell_matchs.group(2)).replace(",",""))
        openprice = float(str(cell_matchs.group(3)).replace(",",""))
        highprice = float(str(cell_matchs.group(4)).replace(",",""))
        lowprice = float(str(cell_matchs.group(5)).replace(",",""))
        if lastclose == -1:
            lastclose = openprice
        #if price_count == 1 or price != price_list[price_count-2]:
        if lastclose > 0 and price > 0 and openprice > 0 and highprice > 0 and lowprice > 0 and (highprice != lastclose or lowprice != lastclose) \
            and highprice / lowprice <= 1000 and (highprice / openprice <= 10 or highprice / price <= 10) and (lowprice / openprice >= 0.1 or lowprice / price >= 0.1) \
            and openprice / lastclose <= 5 and openprice / lastclose >= 0.2:
            timestamp_list.append(timestamp)
            price_list.append(price)
            openprice_list.append(openprice)
            highprice_list.append(highprice)
            lowprice_list.append(lowprice)
            lastclose = price
    return timestamp_list, price_list, openprice_list, highprice_list, lowprice_list

REQUEST_URL_V7 = "http://47.94.154.29:8501/v1/models/turtle7:predict"
REQUEST_URL_V8 = "http://47.94.154.29:8501/v1/models/turtle8:predict"
REQUEST_URL_VX = "http://47.94.154.29:8501/v1/models/turtlex:predict"
REQUEST_URL_V11C = "http://47.94.154.29:8501/v1/models/crypto11:predict"
REQUEST_URL_V11 = "http://47.94.154.29:8501/v1/models/turtle11:predict"

def predict(symbol, timestamp_list, price_list, openprice_list, highprice_list, lowprice_list, predict_len, isCrypto):
    print("isCrypto:"+str(isCrypto))
    timestamp_list = timestamp_list[0:input_days_len+predict_len-1]
    price_list = price_list[0:input_days_len+predict_len-1]
    openprice_list = openprice_list[0:input_days_len+predict_len-1]
    highprice_list = highprice_list[0:input_days_len+predict_len-1]
    lowprice_list = lowprice_list[0:input_days_len+predict_len-1]
    price_log_list = [math.log(i) if i > 0 else 0 for i in price_list]
    highprice_log_list = [math.log(i) if i > 0 else 0 for i in highprice_list]
    lowprice_log_list = [math.log(i) if i > 0 else 0 for i in lowprice_list]
    price_len = len(price_list)
    predict_len = price_len - input_days_len + 1
    predict_batch_count = math.ceil(float(predict_len)/predict_batch)
    riseProb_vx_list = []
    for predict_batch_index in range(predict_batch_count):
        print(symbol + " predicting " + str(predict_batch_index+1) + " of " + str(predict_batch_count))
        inputObj = {"Prices":[]}
        price_list_obj = []
        for predict_index in range(predict_batch):
            absolute_predict_index = predict_batch_index*predict_batch+predict_index
            if absolute_predict_index >= predict_len:
                break
            priceObj = {"Close":[],"High":[],"Low":[]}
            priceObj_log = {"Close":[],"High":[],"Low":[]}
            for price_index in range(input_days_len):
                absolute_price_index = absolute_predict_index + price_index
                priceObj["Close"].append(
                    price_list[absolute_price_index])
                priceObj["High"].append(
                    highprice_list[absolute_price_index])
                priceObj["Low"].append(
                    lowprice_list[absolute_price_index])
                priceObj_log["Close"].append(
                    price_log_list[absolute_price_index])
                priceObj_log["High"].append(
                    highprice_log_list[absolute_price_index])
                priceObj_log["Low"].append(
                    lowprice_log_list[absolute_price_index])
            inputObj["Prices"].append(priceObj)
            price_list_obj.append(priceObj_log)
        HEADER = {'Content-Type':'application/json; charset=utf-8'}
        #inputpricelist = getInputPriceList11(inputObj)
        inputpricelist = getInputPriceList11(price_list_obj)
        requestDict = {"instances": inputpricelist}
        rsp_vx = requests.post(REQUEST_URL_V11, data=json.dumps(requestDict), headers=HEADER)
        #riseProb_vx = GetPredictResult11(symbol, json.loads(rsp_vx.text), inputObj["Prices"], "X", timestamp_list[predict_batch_index*predict_batch:predict_batch_index*predict_batch+input_days_len])
        riseProb_vx = GetPredictResult11(symbol, json.loads(rsp_vx.text), inputObj["Prices"], "X", timestamp_list[predict_batch_index*predict_batch:predict_batch_index*predict_batch+input_days_len])
        riseProb_vx_list.append(riseProb_vx)
    global time_start
    time_end=time.time()
    return combine_predict_result_list(riseProb_vx_list)

def getInputPriceList(inputObj):
    pricelistsymbols = inputObj["Prices"]
    inputPriceListSymbols = []
    inputPriceListSymbols2 = []
    symbolCount = len(pricelistsymbols)
    dayscount = len(pricelistsymbols[0]["Close"])
    for pricelistsymbol in pricelistsymbols:
        #Desc by date
        closelist = [math.log(closePrice) if closePrice > 0 else 0 for closePrice in pricelistsymbol["Close"]]
        highlist = [math.log(highPrice) if highPrice > 0 else 0 for highPrice in pricelistsymbol["High"]]
        lowlist = [math.log(lowPrice) if lowPrice > 0 else 0 for lowPrice in pricelistsymbol["Low"]]
        maxprice = max(highlist)
        minprice = min(lowlist)
        rangePrice = maxprice - minprice
        closelistscaled = [(closePrice - minprice) / rangePrice for closePrice in closelist]
        highlistscaled = [(highPrice - minprice) / rangePrice for highPrice in highlist]
        lowlistscaled = [(lowPrice - minprice) / rangePrice for lowPrice in lowlist]
        inputPriceList = []
        for dayindex in range(dayscount):
            inputPriceList.extend([highlistscaled[dayindex],closelistscaled[dayindex],lowlistscaled[dayindex]])
        inputPriceListSymbols.append(inputPriceList)
    for dayindex in range(dayscount*3):
        for symbolindex in range(symbolCount):
            inputPriceListSymbols2.append(inputPriceListSymbols[symbolindex][dayindex])
    return inputPriceListSymbols2


#def getInputPriceList11(inputObj):
def getInputPriceList11(price_list_obj):
    #pricelistsymbols = inputObj["Prices"]
    pricelistsymbols = price_list_obj
    inputPriceListSymbols = []
    inputPriceListSymbols2 = []
    symbolCount = len(pricelistsymbols)
    dayscount = len(pricelistsymbols[0]["Close"])
    for pricelistsymbol in pricelistsymbols:
        #Desc by date
        #closelist = [math.log(closePrice) if closePrice > 0 else 0 for closePrice in pricelistsymbol["Close"]]
        #highlist = [math.log(highPrice) if highPrice > 0 else 0 for highPrice in pricelistsymbol["High"]]
        #lowlist = [math.log(lowPrice) if lowPrice > 0 else 0 for lowPrice in pricelistsymbol["Low"]]
        closelist = pricelistsymbol["Close"]
        highlist = pricelistsymbol["High"]
        lowlist = pricelistsymbol["Low"]
        maxprice = max(highlist)
        minprice = min(lowlist)
        rangePrice = maxprice - minprice
        closelistscaled = [(closePrice - minprice) / rangePrice for closePrice in closelist][::-1]
        highlistscaled = [(highPrice - minprice) / rangePrice for highPrice in highlist][::-1]
        lowlistscaled = [(lowPrice - minprice) / rangePrice for lowPrice in lowlist][::-1]
        closelistscaled = [closelistscaled[spiral_matrix[index]] for index in range(input_days_len)]
        highlistscaled = [highlistscaled[spiral_matrix[index]] for index in range(input_days_len)]
        lowlistscaled = [lowlistscaled[spiral_matrix[index]] for index in range(input_days_len)]
        inputPriceList = []
        for dayindex in range(dayscount):
            inputPriceList.extend([highlistscaled[dayindex],closelistscaled[dayindex],lowlistscaled[dayindex]])
        inputPriceListSymbols.append(inputPriceList)
    for dayindex in range(dayscount*3):
        for symbolindex in range(symbolCount):
            inputPriceListSymbols2.append(inputPriceListSymbols[symbolindex][dayindex])
    return inputPriceListSymbols2

def getInputPriceList_efficientnet(inputObj):
    pricelistsymbols = inputObj["Prices"]
    inputPriceListSymbols = []
    inputPriceListSymbols2 = []
    symbolCount = len(pricelistsymbols)
    dayscount = len(pricelistsymbols[0]["Close"])
    for pricelistsymbol in pricelistsymbols:
        #Desc by date
        closelist = [math.log(closePrice) if closePrice > 0 else 0 for closePrice in pricelistsymbol["Close"]]
        highlist = [math.log(highPrice) if highPrice > 0 else 0 for highPrice in pricelistsymbol["High"]]
        lowlist = [math.log(lowPrice) if lowPrice > 0 else 0 for lowPrice in pricelistsymbol["Low"]]
        maxprice = max(highlist)
        minprice = min(lowlist)
        rangePrice = maxprice - minprice
        #print("maxprice:" + str(maxprice) + "/minprice:" + str(minprice) + "/rangePrice:" + str(rangePrice))
        closelistscaled = [(closePrice - minprice) / rangePrice for closePrice in closelist]
        highlistscaled = [(highPrice - minprice) / rangePrice for highPrice in highlist]
        lowlistscaled = [(lowPrice - minprice) / rangePrice for lowPrice in lowlist]
        inputPriceList = []
        height = 15
        width = 15
        list1 = []
        for height_index in range(height):
            list2 = []
            for width_index in range(width):
                dayindex = height_index * width + width_index
                list3 = [highlistscaled[dayindex],closelistscaled[dayindex],lowlistscaled[dayindex]]
                #list3 = [1,1,1]
                list2.append(list3)
            list1.append(list2)
        #for dayindex in range(dayscount):
        #    #inputPriceList.extend([highlistscaled[dayindex],closelistscaled[dayindex],lowlistscaled[dayindex]])
        #    inputPriceList.append([highlistscaled[dayindex],closelistscaled[dayindex],lowlistscaled[dayindex]])
        #inputPriceList = list1
        inputPriceListSymbols.append(list1)
    #for dayindex in range(dayscount*3):
    #    for symbolindex in range(symbolCount):
    #        inputPriceListSymbols2.append(inputPriceListSymbols[symbolindex][dayindex])
    #return inputPriceListSymbols2
    return inputPriceListSymbols

def GetPredictResult(symbol, predictRsp, price_data, version, timestamp_list):
    date_list = []
    side_list = []
    strategy_list = []
    prob_list = []
    price_list = []
    atr_list = []
    stop_list = []
    stop_loss_list = []
    position_list = []
    high_list = []
    low_list = []
    predict_len = len(price_data["Prices"])
    #print(str(predictRsp))
    #for probitem in predictRsp["predictions"]:
    #    print(json.dumps(probitem))
        #probitem = list(map(float, probitem))
    #Get Best Strategy
    maxproblist = [max(probitem["probabilities"][:10]) for probitem in predictRsp["predictions"]]
    #maxproblist = [max(probitem["probabilities"][:12]) for probitem in predictRsp["predictions"]]
    problist = [predictRsp["predictions"][probitemindex]["probabilities"].index(maxproblist[probitemindex]) for probitemindex in range(len(predictRsp["predictions"]))]
    for predict_index in range(predict_len):
        date = datetime.datetime.fromtimestamp(timestamp_list[predict_index])
        datestr = date.strftime("%Y-%m-%d")
        prices = price_data["Prices"][predict_index]
        closes = prices["Close"][:atr_len]
        highs = prices["High"][:atr_len]
        lows = prices["Low"][:atr_len]
        for i in range(atr_len -1):
            highs[i] = max(highs[i], closes[i+1])
            lows[i] = min(lows[i], closes[i+1])
        tr_list = [highs[i] / lows[i] - 1 for i in range(atr_len)]
        atr = (sum(tr_list) / len(tr_list))
        price = float(closes[0])
        high = float(highs[0])
        low = float(lows[0])
        if 'error' in predictRsp:
            return predictRsp
        #riseProb = problist[predict_index]
        prob = maxproblist[predict_index]
        strategy = problist[predict_index]
        
        #riseProb = 1 - riseProb #反转AI

        side = ""
        stop_price = 0
        stop_loss = 0
        position = 0

        if strategy < 10:
            side = side_dict[strategy]
            stop_loss = stop_loss_dict[strategy]
            if side == "buy":
                stop_price = price / (1 + atr * stop_loss)
            else: #sell
                stop_price = price * (1 + atr * stop_loss)
            position = round(risk_factor / atr / stop_loss, 2)
        elif strategy >= 10:
            stop_loss = stop_loss_dict[strategy]
            order_range = order_range_dict[strategy]
            #position = round(risk_factor / atr / (order_range - stop_loss), 2)
            position = round(risk_factor / atr / (stop_loss - order_range), 2)

        date_list.append(datestr)
        #score = (riseProb * 2 - 1)*100
        score = 0
        side_list.append(side)
        #score_list.append(round(score,2))
        strategy_list.append(strategy)
        prob_list.append(round(float(prob * 100),2))
        price_list.append(price)
        high_list.append(high)
        low_list.append(low)
        atr_list.append(round(float(atr * 100),2))
        position_list.append(position)
        stop_list.append(float(format(float(stop_price), '.7g')))
        stop_loss_list.append(stop_loss)
    outputRiseProb = {"symbol": symbol, 
                      "date_list": date_list, 
                      #"prob_list": [round(probval,4) for probval in problist], 
                      "side_list" : side_list, 
                      "strategy_list" : strategy_list, 
                      "prob_list" : prob_list,
                      "price_list" : price_list, 
                      "high_list" : high_list, 
                      "low_list" : low_list, 
                      "atr_list" : atr_list, 
                      "stop_list" : stop_list, 
                      "stop_loss_list" : stop_loss_list, 
                      "position_list": position_list, 
                      "version" : version}
    return outputRiseProb

def GetPredictResult11(symbol, predictRsp, price_obj, version, timestamp_list):
    date_list = []
    side_list = []
    strategy_list = []
    prob_list = []
    price_list = []
    atr_list = []
    stop_list = []
    stop_loss_list = []
    position_list = []
    high_list = []
    low_list = []
    predict_len = len(price_obj)
    #Get Best Strategy
    maxproblist = [max(probitem["probabilities"][:10]) for probitem in predictRsp["predictions"]]
    problist = [predictRsp["predictions"][probitemindex]["probabilities"].index(maxproblist[probitemindex]) for probitemindex in range(len(predictRsp["predictions"]))]
    for predict_index in range(predict_len):
        date = datetime.datetime.fromtimestamp(timestamp_list[predict_index])
        datestr = date.strftime("%Y-%m-%d")
        prices = price_obj[predict_index]
        closes = prices["Close"][:atr_len]
        highs = prices["High"][:atr_len]
        lows = prices["Low"][:atr_len]
        for i in range(atr_len -1):
            highs[i] = max(highs[i], closes[i+1])
            lows[i] = min(lows[i], closes[i+1])
        tr_list = [highs[i] / lows[i] - 1 for i in range(atr_len)]
        atr = (sum(tr_list) / len(tr_list))
        price = float(closes[0])
        high = float(highs[0])
        low = float(lows[0])
        if 'error' in predictRsp:
            return predictRsp
        #riseProb = problist[predict_index]
        prob = maxproblist[predict_index]
        strategy = problist[predict_index]
        
        side = ""
        stop_price = 0
        stop_loss = 0
        position = 0

        if strategy < 8:
            side = side_dict[strategy]
            stop_loss = stop_loss_dict[strategy]
            if side == "buy":
                stop_price = price / (1 + atr * stop_loss)
            else: #sell
                stop_price = price * (1 + atr * stop_loss)
            position = round(risk_factor / atr / stop_loss, 2)
        elif strategy >= 8:
            stop_loss = stop_loss_dict11[strategy]
            order_range = order_range_dict11[strategy]
            #position = round(risk_factor / atr / (order_range - stop_loss), 2)
            position = round(risk_factor / atr / (stop_loss - order_range), 2)

        date_list.append(datestr)
        #score = (riseProb * 2 - 1)*100
        score = 0
        side_list.append(side)
        #score_list.append(round(score,2))
        strategy_list.append(strategy)
        prob_list.append(round(float(prob * 100),2))
        price_list.append(price)
        high_list.append(high)
        low_list.append(low)
        atr_list.append(round(float(atr * 100),2))
        position_list.append(position)
        stop_list.append(float(format(float(stop_price), '.7g')))
        stop_loss_list.append(stop_loss)
    outputRiseProb = {"symbol": symbol, 
                      "date_list": date_list, 
                      #"prob_list": [round(probval,4) for probval in problist], 
                      "side_list" : side_list, 
                      "strategy_list" : strategy_list, 
                      "prob_list" : prob_list,
                      "price_list" : price_list, 
                      "high_list" : high_list, 
                      "low_list" : low_list, 
                      "atr_list" : atr_list, 
                      "stop_list" : stop_list, 
                      "stop_loss_list" : stop_loss_list, 
                      "position_list": position_list, 
                      "version" : version}
    return outputRiseProb

def combine_predict_result_list(predict_result_list):
    if len(predict_result_list) == 0:
        return None
    date_list = []
    side_list = []
    strategy_list = []
    prob_list = []
    price_list = []
    high_list = []
    low_list = []
    atr_list = []
    stop_list = []
    stop_loss_list = []
    position_list = []
    for predict_result in predict_result_list:
        date_list += predict_result["date_list"]
        side_list += predict_result["side_list"]
        strategy_list += predict_result["strategy_list"]
        prob_list += predict_result["prob_list"]
        price_list += predict_result["price_list"]
        high_list += predict_result["high_list"]
        low_list += predict_result["low_list"]
        atr_list += predict_result["atr_list"]
        stop_list += predict_result["stop_list"]
        stop_loss_list += predict_result["stop_loss_list"]
        position_list += predict_result["position_list"]
    predict_result_combined = {"symbol": predict_result_list[0]["symbol"], 
                      "date_list": date_list, 
                      #"prob_list": [round(probval,4) for probval in problist], 
                      "side_list" : side_list, 
                      "strategy_list" : strategy_list, 
                      "prob_list" : prob_list,
                      "price_list" : price_list, 
                      "high_list" : high_list, 
                      "low_list" : low_list, 
                      "atr_list" : atr_list, 
                      "stop_list" : stop_list, 
                      "stop_loss_list" : stop_loss_list, 
                      "position_list": position_list, 
                      "version" : predict_result_list[0]["version"]}
    return predict_result_combined

if __name__ == "__main__":
    symbol = input("Input a symbol:")
    marketListString  = search_for_symbol(symbol)
    #print("marketListString = " + marketListString)
    time_start=time.time()
    market, is_crypto = get_best_market(json.loads(marketListString))
    marketString = json.dumps(market).encode('utf-8').decode('unicode_escape')
    print("best market = " +  marketString)
    marketObj = json.loads(marketString)
    timestamp_list, price_list, openprice_list, highprice_list, lowprice_list = get_history_price(str(marketObj["pairId"]), marketObj["pair_type"], 4800)
    time_end=time.time()
    print('totally cost',time_end-time_start,"s")
    '''
    print("date", "close","open","high","low")
    for i in range(len(price_list)):
        date = datetime.datetime.fromtimestamp(timestamp_list[i])
        datestr = date.strftime("%Y-%m-%d")
        print(datestr, price_list[i], openprice_list[i], highprice_list[i], lowprice_list[i])
    '''
    #Predict
    #turtle7_predict, turtlex_predict = predict(price_list, openprice_list, highprice_list, lowprice_list)
    turtlex_predict = predict(marketObj["symbol"], timestamp_list, price_list, openprice_list, highprice_list, lowprice_list, 4500, is_crypto)
    #print(json.dumps(turtle7_predict), json.dumps(turtlex_predict))
    
    print(json.dumps(turtlex_predict))
    time_end=time.time()
    print('totally cost',time_end-time_start,"s")