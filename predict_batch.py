import requests
import json
import mypsw
import urllib3

group_set = {"BINANCE":5}

def get_prediction(group,openID):
    urllib3.disable_warnings()
    if group not in group_set:
        return ""
    url = "https://35.236.157.42/api/v1/predict_batch?group=" + str(group) + "&secret=" + mypsw.api_secret
    response = requests.get(url,verify=False)
    prediction = json.loads(response.text)
    if prediction["code"] == 200:
        return get_batch_predict_info(group, prediction)
    else:
        return prediction["msg"][:600]

def side_text_zh(side):
    if str(side).upper() == 'BUY':
        return "买入"
    return "卖出"

def get_batch_predict_info(group, prediction):
    strategies = prediction["strategies"]
    n=len(strategies)
    if n>10: #截取前10个市场
        n=10
        strategies = strategies[:10]
    text=group+"批量预测 by 预言家III\n"
    text+="按评分倒序排列\n"
    text+="市场/方向/评分\n"
    for i,strategy in enumerate(strategies):
        text+=str(strategy["symbol"]).replace("/","")
        if group_set[group] == 5:
            text+="@"+str(strategy["exchange"])
        text+=" " + side_text_zh(strategy["side"]) + " " + str(round(float(strategy["score"]),2)) + "\n"
    text +="输入市场名查询详细预测结果。\n"
    text +="预测结果基于最近128日K线自动生成，仅供参考。"
    return text