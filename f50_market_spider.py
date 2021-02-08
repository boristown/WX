import requests
import json
#import common
import re
import datetime
import time
import math

#一次爬取所有市场的爬虫程序
#加密货币:
#ID长度：7位
#ID规则:1[01][678]____

#个股
#ID长度：

#https://www.investing.com/search/?q=BTC
#window.allResultsQuotesDataArray = [{"pairId":"{1}"……"symbol":"{2}"……

time_start = None
dateformat = "%Y-%m-%d"
input_days_len = 225
atr_len = 20
#predict_len = 4500
risk_factor = 1.5
#startdays = 4800
predict_batch = 50

def search_for_symbol(symbol):
    url = "https://www.investing.com/search/?q=" + symbol
    headers={"user-agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36"}
    response = requests.get(url, headers=headers)
    marketListString = ""
    if response.status_code == 200:
        string = response.text
        pattern = 'allResultsQuotesDataArray\s+?=\s+?(\[.+?\]);\s+?</script>'
        searchObj = re.search(pattern, string, flags=0)
        if searchObj:
            marketListString = searchObj.group(1)
        return marketListString

def get_best_market(marketList):
    if len(marketList) > 0:
        if marketList[0]["pair_type"] == "equities":
            for market in marketList:
                if market["flag"] == "China" and market["pair_type"] == "equities":
                    return market
            for market in marketList:
                if market["flag"] == "Hong_Kong" and market["pair_type"] == "equities":
                    return market
            for market in marketList:
                if market["flag"] == "USA" and market["pair_type"] == "equities":
                    return market
        for market in marketList:
            return market
    return None

def get_history_price(pairId, pair_type, startdays):
    priceList = []
    if pair_type == "currency":
        smlID_str = '1072600'
    else:
        smlID_str = '25609849'

    url = "https://cn.investing.com/instruments/HistoricalDataAjax"

    headers = {
        'accept': "text/plain, */*; q=0.01",
        'origin': "https://www.investing.com",
        'x-requested-with': "XMLHttpRequest",
        'user-agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36",
        'content-type': "application/x-www-form-urlencoded",
        'cache-control': "no-cache",
        'postman-token': "17db1643-3ef6-fa9e-157b-9d5058f391e4"
        }
    st_date_str = (datetime.datetime.utcnow() + datetime.timedelta(days = -startdays)).strftime(dateformat).replace("-","%2F")
    end_date_str = (datetime.datetime.utcnow()).strftime(dateformat).replace("-","%2F")
    payload = "action=historical_data&curr_id="+ pairId +"&end_date=" + end_date_str + "&header=null&interval_sec=Daily&smlID=" + smlID_str + "&sort_col=date&sort_ord=DESC&st_date=" + st_date_str
    try:
        response = requests.request("POST", url, data=payload, headers=headers, verify=False, timeout=40)
    except Exception as e:
        time.sleep(7)
    if response == None:
        pass
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
        if price > 0 and openprice > 0 and highprice > 0 and lowprice > 0 and (highprice != lastclose or lowprice != lastclose) \
            and highprice / lowprice <= 1000 and openprice / lastclose <= 5 and openprice / lastclose >= 0.2:
            timestamp_list.append(timestamp)
            price_list.append(price)
            openprice_list.append(openprice)
            highprice_list.append(highprice)
            lowprice_list.append(lowprice)
            lastclose = price
    return timestamp_list, price_list, openprice_list, highprice_list, lowprice_list

#REQUEST_URL_V7 = "http://47.94.154.29:8501/v1/models/turtle7:predict"
REQUEST_URL_V8 = "http://47.94.154.29:8501/v1/models/turtle8:predict"

def predict(symbol, timestamp_list, price_list, openprice_list, highprice_list, lowprice_list, predict_len):
    #turtle7_predict = []
    #turtle8_predict = []
    print("predicting")
    timestamp_list = timestamp_list[0:input_days_len+predict_len-1]
    price_list = price_list[0:input_days_len+predict_len-1]
    openprice_list = openprice_list[0:input_days_len+predict_len-1]
    highprice_list = highprice_list[0:input_days_len+predict_len-1]
    lowprice_list = lowprice_list[0:input_days_len+predict_len-1]
    price_len = len(price_list)
    predict_len = price_len - input_days_len + 1
    predict_batch_count = math.ceil(float(predict_len)/predict_batch)
    riseProb_v8_list = []
    for predict_batch_index in range(predict_batch_count):
        print("predicting " + str(predict_batch_index+1) + " of " + str(predict_batch_count))
        inputObj = {"Prices":[]}
        for predict_index in range(predict_batch):
            absolute_predict_index = predict_batch_index*predict_batch+predict_index
            if absolute_predict_index >= predict_len:
                break
            priceObj = {"Close":[],"High":[],"Low":[]}
            for price_index in range(input_days_len):
                absolute_price_index = absolute_predict_index + price_index
                priceObj["Close"].append(
                    price_list[absolute_price_index])
                priceObj["High"].append(
                    highprice_list[absolute_price_index])
                priceObj["Low"].append(
                    lowprice_list[absolute_price_index])
            inputObj["Prices"].append(priceObj)
        HEADER = {'Content-Type':'application/json; charset=utf-8'}
        inputpricelist = getInputPriceList(inputObj)
        requestDict = {"instances": inputpricelist}
        rsp_v8 = requests.post(REQUEST_URL_V8, data=json.dumps(requestDict), headers=HEADER)
        riseProb_v8 = GetPredictResult(symbol, json.loads(rsp_v8.text), inputObj, "v8", timestamp_list[predict_batch_index*predict_batch:predict_batch_index*predict_batch+input_days_len])
        riseProb_v8_list.append(riseProb_v8)
    global time_start
    time_end=time.time()
    return combine_predict_result_list(riseProb_v8_list)

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

def GetPredictResult(symbol, predictRsp, price_data, version, timestamp_list):
    date_list = []
    side_list = []
    score_list = []
    price_list = []
    atr_list = []
    stop_list = []
    position_list = []
    high_list = []
    low_list = []
    predict_len = len(price_data["Prices"])
    problist = [probitem["probabilities"][1] for probitem in predictRsp["predictions"]]
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
        riseProb = problist[predict_index]
        
        #riseProb = 1 - riseProb #反转AI

        if riseProb >= 0.5:
            side = "buy"
            stop_price = price / (1 + atr / 2)
        else:
            side = "sell"
            stop_price = price * (1 + atr / 2)
        date_list.append(datestr)
        score = (riseProb * 2 - 1)*100
        side_list.append(side)
        score_list.append(round(score,2))
        price_list.append(price)
        high_list.append(high)
        low_list.append(low)
        atr_list.append(round(float(atr * 100),2))
        position_list.append(round(risk_factor / atr, 2))
        stop_list.append(float(format(float(stop_price), '.7g')))
    outputRiseProb = {"symbol": symbol, 
                      "date_list": date_list, 
                      #"prob_list": [round(probval,4) for probval in problist], 
                      "side_list" : side_list, 
                      "score_list" : score_list, 
                      "price_list" : price_list, 
                      "high_list" : high_list, 
                      "low_list" : low_list, 
                      "atr_list" : atr_list, 
                      "stop_list" : stop_list, 
                      #"position_list": position_list, 
                      "version" : version}
    return outputRiseProb

def combine_predict_result_list(predict_result_list):
    if len(predict_result_list) == 0:
        return None
    date_list = []
    side_list = []
    score_list = []
    price_list = []
    high_list = []
    low_list = []
    atr_list = []
    stop_list = []
    for predict_result in predict_result_list:
        date_list += predict_result["date_list"]
        side_list += predict_result["side_list"]
        score_list += predict_result["score_list"]
        price_list += predict_result["price_list"]
        high_list += predict_result["high_list"]
        low_list += predict_result["low_list"]
        atr_list += predict_result["atr_list"]
        stop_list += predict_result["stop_list"]
    predict_result_combined = {"symbol": predict_result_list[0]["symbol"], 
                      "date_list": date_list, 
                      #"prob_list": [round(probval,4) for probval in problist], 
                      "side_list" : side_list, 
                      "score_list" : score_list, 
                      "price_list" : price_list, 
                      "high_list" : high_list, 
                      "low_list" : low_list, 
                      "atr_list" : atr_list, 
                      "stop_list" : stop_list, 
                      #"position_list": position_list, 
                      "version" : predict_result_list[0]["version"]}
    return predict_result_combined

if __name__ == "__main__":
    symbol = input("Input a symbol:")
    marketListString  = search_for_symbol(symbol)
    #print("marketListString = " + marketListString)
    time_start=time.time()
    market = get_best_market(json.loads(marketListString))
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
    #turtle7_predict, turtle8_predict = predict(price_list, openprice_list, highprice_list, lowprice_list)
    turtle8_predict = predict(marketObj["symbol"], timestamp_list, price_list, openprice_list, highprice_list, lowprice_list, 4500)
    #print(json.dumps(turtle7_predict), json.dumps(turtle8_predict))
    
    print(json.dumps(turtle8_predict))
    time_end=time.time()
    print('totally cost',time_end-time_start,"s")