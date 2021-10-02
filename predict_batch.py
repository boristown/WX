import requests
import json
import mypsw

group_set = {"BINANCE":5}

def get_prediction(group):
    if group not in group_set:
        return ""
    url = "https://aitrad.in/api/v1/predict_batch?group=" + str(group) + "&secret=" + mypsw.api_secret
    response = requests.get(url)
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
    if n>5: #截取前5个市场
        n=5
        strategies = strategies[:5]
    text="批量预测 by 预言家III\n"
    text+="组：binance\n"
    text+="排序/市场/方向/评分\n"
    for i,strategy in enumerate(strategies):
        text+=str(i+1)+" "+ str(strategy["symbol"]).replace("/","")
        if group_set[group] == '5':
            text+="@"+str(strategy["exchange"])
        text+=" " + side_text_zh() + " " + str(strategy["score"]) + "\n"
    text +="提示Tips：\n"
    text +="输入市场名查询详细预测结果。\n"
    text +="预测结果基于最近128日K线自动生成，仅供参考。\n"
    return text