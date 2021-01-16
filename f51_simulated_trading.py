import requests
import f50_market_spider
import json
import datetime
import time
import math

time_start = None
fee_ratio = 0.001
no_filter = False
grid_profit = f50_market_spider.risk_factor / 100

def simulate_trading(predict_list):
    simulate_result = {"date_list":[], 
                       "symbol_list":[],
                       "score_list":[],
                       "atr_list":[],
                       'entry_price_list':[],
                       #'exit_price_list':[],
                       'high_price_list':[],
                       'low_price_list':[],
                       "position_list":[],
                       "stop_list": [],
                       "stop_flag":[],
                       "profit_list":[],
                       "balance_list":[],
                       "balance_dynamic_list":[],
                       "max_balance_list":[],
                       "max_banlance_date":[],
                       "grid_symbol_list":[],
                       "grid_atr_list":[],
                       'grid_entry_price_list':[],
                       'grid_high_price_list':[],
                       'grid_low_price_list':[],
                       "grid_position_list":[],
                       "grid_stop_flag":[],
                       "grid_profit_list":[],
                       }
    min_date_list = [
        datetime.datetime.strptime(
        predict_symbol["date_list"][-1],
        f50_market_spider.dateformat)
        for predict_symbol in predict_list
        ]
    min_date = min(min_date_list)
    max_date_list = [ 
        datetime.datetime.strptime(
        predict_symbol["date_list"][0],
        f50_market_spider.dateformat)
        for predict_symbol in predict_list
        ]
    max_date = max(max_date_list)
    current_date = min_date
    date_list = []
    while current_date <= max_date:
        date_list.append(current_date)
        current_date += datetime.timedelta(days = 1)
    simulate_result["date_list"] = date_list
    date_index_list = [len(predict_symbol["date_list"]) - 1 for predict_symbol in predict_list]
    init_balance = 100.0
    init_year = simulate_result["date_list"][0].year
    #无过滤器
    #初始余额为100
    current_balance = init_balance
    current_dynamic_balance = init_balance
    max_balance = init_balance
    max_loss = 0
    max_loss_days = 0
    win_count = 0
    loss_count = 0
    draw_count = 0
    max_banlance_date = simulate_result["date_list"][0]
    #活动订单
    active_orders = []
    #活动网格
    active_grids = []
    #年度收益
    year_list = []
    year_last_balance = {}
    #年度
    year_last_balance[init_year] = init_balance
    
    #循环遍历每一个交易日
    for date in simulate_result["date_list"]:
        #每日可交易币种清单
        symbols_available = []
        #循环遍历每一个币种
        for predict_symbol_index in range(len(predict_list)):
            #从币种的第一天开始搜索，找到匹配的日期，当匹配成功或查找到的日期大于目标日期时退出
            #由于日期是倒序排列，所以从最后一个元素开始向前查找
            while date_index_list[predict_symbol_index] >= 0:
                date_symbol = datetime.datetime.strptime(predict_list[predict_symbol_index]["date_list"][date_index_list[predict_symbol_index]], f50_market_spider.dateformat)
                if date_symbol == date:
                    symbols_available.append((predict_symbol_index, date_index_list[predict_symbol_index]))
                    break
                if date_symbol > date:
                    break
                date_index_list[predict_symbol_index] -= 1
        trade_flag = False
        grid_flag = False
        #如果当日存在可交易的币种
        if len(symbols_available) > 0:
            #遍历未止盈止损的活动订单(倒序循环时才能删除元素)
            for active_order in active_orders[::-1]:
                #获取当前市场数据
                symbol_index = simulate_result["symbol_list"][active_order]
                find_symbol = False
                for symbol_available in symbols_available:
                    if symbol_available[0] == symbol_index:
                        find_symbol = True
                        high_price = predict_list[symbol_index]["high_list"][symbol_available[1]]
                        low_price = predict_list[symbol_index]["low_list"][symbol_available[1]]
                        atr_price = predict_list[symbol_index]["atr_list"][symbol_available[1]]
                        break
                if not find_symbol:
                    continue
                #计算入场金额
                entry_amount = simulate_result["position_list"][active_order] * simulate_result["balance_dynamic_list"][active_order]
                #做多订单
                if simulate_result["score_list"][active_order]  > 0:
                    #先用当日最低价判断是否止损，再用当日最高价更新止损价
                    if low_price < simulate_result["stop_list"][active_order]:
                        simulate_result["stop_flag"][active_order] = 'X'
                        entry_price = simulate_result["entry_price_list"][active_order]
                        stop_price = simulate_result["stop_list"][active_order]
                        #simulate_result["exit_price_list"][active_order] = stop_price
                        #计算离场金额
                        exit_amount = entry_amount / entry_price * stop_price
                        #计算收益时，考虑交易手续费fee_ratio
                        simulate_result["profit_list"][active_order] = exit_amount * (1 - fee_ratio) - entry_amount * (1 + fee_ratio)
                        #更新静态余额
                        current_balance += simulate_result["profit_list"][active_order]
                        #删除活动订单
                        active_orders.remove(active_order)
                    else:
                        #print("low:"+str(low_price) + ">=stop:" + str(simulate_result["stop_list"][active_order]))
                        if high_price > simulate_result["high_price_list"][active_order]:
                            simulate_result["high_price_list"][active_order] = high_price
                            simulate_result["stop_list"][active_order] = high_price / (1 + atr/100 / 2)
                        #计算离场金额
                        exit_amount = entry_amount / entry_price * entry_price
                        #计算收益时，考虑交易手续费fee_ratio
                        simulate_result["profit_list"][active_order] = exit_amount * (1 - fee_ratio) - entry_amount * (1 + fee_ratio)
                #做空订单
                else:
                    #先用当日最高价判断是否止损，再用当日最低价更新止损价
                    if high_price > simulate_result["stop_list"][active_order]:
                        simulate_result["stop_flag"][active_order] = 'X'
                        entry_price = simulate_result["entry_price_list"][active_order]
                        stop_price = simulate_result["stop_list"][active_order]
                        #simulate_result["exit_price_list"][active_order] = stop_price
                        #计算离场金额
                        exit_amount = entry_amount / entry_price * stop_price
                        #计算收益时，考虑交易手续费fee_ratio
                        simulate_result["profit_list"][active_order] = entry_amount * (1 - fee_ratio) - exit_amount * (1 + fee_ratio)
                        #更新静态余额
                        current_balance += simulate_result["profit_list"][active_order]
                        #删除活动订单
                        active_orders.remove(active_order)
                    else:
                        #print("high:"+str(high_price) + "<=stop:" + str(simulate_result["stop_list"][active_order]))
                        if low_price < simulate_result["low_price_list"][active_order]:
                            simulate_result["low_price_list"][active_order] = low_price
                            simulate_result["stop_list"][active_order] = low_price * (1 + atr/100 / 2)
                        #计算离场金额
                        exit_amount = entry_amount / entry_price * entry_price
                        #计算收益时，考虑交易手续费fee_ratio
                        simulate_result["profit_list"][active_order] = entry_amount * (1 - fee_ratio) - exit_amount * (1 + fee_ratio)
            #遍历活动网格(倒序循环时才能删除元素)
            for active_grid in active_grids[::-1]:
                #获取当前市场数据
                symbol_index = simulate_result["grid_symbol_list"][active_grid]
                grid_atr = simulate_result["grid_atr_list"][active_grid] / 100
                grid_price = simulate_result["grid_entry_price_list"][active_grid]
                grid_high_limit = grid_price * (1 + grid_atr / 2)
                grid_low_limit = grid_price / (1 + grid_atr / 2)
                grid_high_stop = grid_price * (1 + grid_atr * 3 / 4)
                grid_low_stop = grid_price / (1 + grid_atr * 3 / 4)
                find_symbol = False
                for symbol_available in symbols_available:
                    if symbol_available[0] == symbol_index:
                        find_symbol = True
                        high_price = predict_list[symbol_index]["high_list"][symbol_available[1]]
                        low_price = predict_list[symbol_index]["low_list"][symbol_available[1]]
                        atr_price = predict_list[symbol_index]["atr_list"][symbol_available[1]]
                        break
                if not find_symbol:
                    continue
                #计算入场金额
                entry_amount = simulate_result["grid_position_list"][active_grid] * simulate_result["balance_dynamic_list"][active_grid]
                #计算网格最大收益
                grid_max_profit = grid_profit * simulate_result["balance_dynamic_list"][active_grid] - entry_amount * fee_ratio * 2
                #计算网格的最大亏损
                grid_max_loss = grid_profit * simulate_result["balance_dynamic_list"][active_grid] + entry_amount * fee_ratio * 2
                #计算更新网格状态
                if high_price > simulate_result["grid_high_price_list"][active_grid]:
                    simulate_result["grid_high_price_list"][active_grid] = min(high_price,grid_high_limit)
                if low_price < simulate_result["grid_low_price_list"][active_grid]:
                    simulate_result["grid_low_price_list"][active_grid] = max(low_price,grid_low_limit)
                #计算网格收益
                sell_ratio = (simulate_result["grid_high_price_list"][active_grid] - grid_price) / (grid_high_limit - grid_price)
                buy_ratio = (grid_price - simulate_result["grid_low_price_list"][active_grid]) / (grid_price - grid_low_limit)
                grid_profit_ratio = math.pow(min(sell_ratio, buy_ratio), 2)
                grid_loss_ratio = math.pow(1-min(sell_ratio, buy_ratio), 2)
                simulate_result["grid_profit_list"][active_grid] = grid_max_profit * grid_profit_ratio - grid_max_loss * grid_loss_ratio
                #退出网格
                if high_price >= grid_high_stop or low_price <= grid_low_stop:
                    simulate_result["grid_stop_flag"][active_grid] = 'X'
                    #更新静态余额
                    current_balance += simulate_result["grid_profit_list"][active_order]
                    #删除活动订单
                    active_grids.remove(active_grid)
                
            #新余额等于静态余额加动态收益
            current_dynamic_balance = current_balance
            #趋势收益
            for active_order in active_orders:
                current_dynamic_balance += simulate_result["profit_list"][active_order]
            #网格收益
            for active_grid in active_grids:
                current_dynamic_balance += simulate_result["grid_profit_list"][active_grid]
            #更新最大收益值
            if current_dynamic_balance > max_balance:
                max_balance = current_dynamic_balance
                max_banlance_date = simulate_result["date_list"][len(simulate_result["symbol_list"])-1]
                
            print("date:"+datetime.datetime.strftime(date, f50_market_spider.dateformat)
                  +";balance:"+str(current_balance)
                  +";dynamic balance:"+str(current_dynamic_balance)
                  +";active_orders:"+str(len(active_orders))
                  +";active_grids:"+str(len(active_grids))
                  )
            #找到最优币种
            min_profit = 999999
            max_abs_score = -1 #网格交易
            best_symbol_available = symbols_available[0]
            best_grid_symbol = symbols_available[0]
            for symbol_available in symbols_available:
                predict_symbol = predict_list[symbol_available[0]]
                score_abs = abs(float(predict_symbol["score_list"][symbol_available[1]]))
                #Get profit of past 20 days
                past_profit = get_past_profit(predict_list[symbol_available[0]], date_index_list[symbol_available[0]], 20, False)
                past_profit_reversed = get_past_profit(predict_list[symbol_available[0]], date_index_list[symbol_available[0]], 20, True)
                past_profit_grid = past_profit + past_profit_reversed
                if score_abs > max_abs_score:
                    if past_profit > 0 or no_filter: #无过滤器时直接通过
                        max_abs_score = score_abs
                        best_symbol_available = symbol_available
                if past_profit_grid < 0 and past_profit_grid < min_profit and not no_filter: #无过滤器时不执行
                    min_profit = past_profit_grid
                    best_grid_symbol = symbol_available
            if max_abs_score > -1:
                simulate_result["symbol_list"].append(best_symbol_available[0])
                score = predict_list[best_symbol_available[0]]["score_list"][best_symbol_available[1]]
                simulate_result["score_list"].append(score)
                atr = predict_list[best_symbol_available[0]]["atr_list"][best_symbol_available[1]]
                simulate_result["atr_list"].append(atr)
                entry_price = predict_list[best_symbol_available[0]]["price_list"][best_symbol_available[1]]
                simulate_result["entry_price_list"].append(entry_price)
                high_price = predict_list[best_symbol_available[0]]["high_list"][best_symbol_available[1]]
                simulate_result["high_price_list"].append(entry_price)
                low_price = predict_list[best_symbol_available[0]]["low_list"][best_symbol_available[1]]
                simulate_result["low_price_list"].append(entry_price)
                position = round(f50_market_spider.risk_factor / atr, 2)
                simulate_result["position_list"].append(position)
                stop_price = predict_list[best_symbol_available[0]]["stop_list"][best_symbol_available[1]]
                #print("symbol:"+str(best_symbol_available[0])+";price:"+str(entry_price)+";high:"+str(high_price)+";low:"+str(low_price)+";stop:"+str(stop_price)+";position:"+str(position)+";atr:"+str(atr)+";score:"+str(score))
                simulate_result["stop_list"].append(stop_price)
                simulate_result["stop_flag"].append("")
                simulate_result["profit_list"].append(0)
                #添加新订单到活动订单
                active_orders.append(len(simulate_result["symbol_list"])-1)
                trade_flag = True
            if min_profit < 999999:
                simulate_result["grid_symbol_list"].append(best_grid_symbol[0])
                atr = predict_list[best_grid_symbol[0]]["atr_list"][best_grid_symbol[1]]
                simulate_result["grid_atr_list"].append(atr)
                entry_price = predict_list[best_grid_symbol[0]]["price_list"][best_grid_symbol[1]]
                simulate_result["grid_entry_price_list"].append(entry_price)
                high_price = predict_list[best_grid_symbol[0]]["high_list"][best_grid_symbol[1]]
                simulate_result["grid_high_price_list"].append(entry_price)
                low_price = predict_list[best_grid_symbol[0]]["low_list"][best_grid_symbol[1]]
                simulate_result["grid_low_price_list"].append(entry_price)
                position = round(f50_market_spider.risk_factor / atr, 2)
                simulate_result["grid_position_list"].append(position)
                simulate_result["grid_stop_flag"].append("")
                simulate_result["grid_profit_list"].append(0)
                #添加新订单到活动订单
                active_grids.append(len(simulate_result["symbol_list"])-1)
                grid_flag = True
        if not trade_flag:
            simulate_result["symbol_list"].append(-1)
            simulate_result["score_list"].append(0)
            simulate_result["atr_list"].append(0)
            simulate_result["entry_price_list"].append(0)
            #simulate_result["exit_price_list"].append(0)
            simulate_result["high_price_list"].append(0)
            simulate_result["low_price_list"].append(0)
            simulate_result["position_list"].append(0)
            simulate_result["stop_list"].append(0)
            simulate_result["stop_flag"].append("")
            simulate_result["profit_list"].append(0)
        if not grid_flag:
            simulate_result["grid_symbol_list"].append(-1)
            simulate_result["grid_atr_list"].append(0)
            simulate_result["grid_entry_price_list"].append(0)
            simulate_result["grid_high_price_list"].append(0)
            simulate_result["grid_low_price_list"].append(0)
            simulate_result["grid_position_list"].append(0)
            simulate_result["grid_stop_flag"].append("")
            simulate_result["grid_profit_list"].append(0)
        simulate_result["balance_list"].append(current_balance)
        simulate_result["balance_dynamic_list"].append(current_dynamic_balance)
        simulate_result["max_balance_list"].append(max_balance)
        simulate_result["max_banlance_date"].append(max_banlance_date)
        current_loss = (max_balance - current_dynamic_balance) / max_balance
        max_loss = max(max_loss, current_loss)
        current_loss_days = (date - max_banlance_date).days
        max_loss_days = max(max_loss_days, current_loss_days)
        #年度
        current_year = date.year
        year_last_balance[current_year] = current_dynamic_balance

        if len(simulate_result["balance_dynamic_list"]) > 1:
            if simulate_result["balance_dynamic_list"][-1] > simulate_result["balance_dynamic_list"][-2]:
                win_count += 1
            elif simulate_result["balance_dynamic_list"][-1] < simulate_result["balance_dynamic_list"][-2]:
                loss_count += 1
            else:
                draw_count += 1
    for year_item in year_last_balance:
        if year_item == init_year:
            profit = ( year_last_balance[year_item] / init_balance - 1 ) * 100
        else:
            profit = ( year_last_balance[year_item] / year_last_balance[year_item-1] - 1 ) * 100
        year_list.append({"year":year_item,"profit":profit})
    return simulate_result, win_count, loss_count, draw_count, max_loss, max_loss_days, year_list

#Get profit of past 20 days
def get_past_profit(predict_symbol, date_index, days_count, reversed):
    total_len = len(predict_symbol["date_list"])
    date_end_index = date_index + 1
    date_begin_index = date_index + days_count
    if date_begin_index >= total_len:
        return 0
    #活动订单
    active_orders = []
    #初始余额为100
    init_balance = 100.0
    current_balance = init_balance
    current_dynamic_balance = init_balance
    date_list = predict_symbol["date_list"][date_end_index:date_begin_index+1][::-1]
    score_list = predict_symbol["score_list"][date_end_index:date_begin_index+1][::-1]
    atr_list = predict_symbol["atr_list"][date_end_index:date_begin_index+1][::-1]
    price_list = predict_symbol["price_list"][date_end_index:date_begin_index+1][::-1]
    high_list = predict_symbol["high_list"][date_end_index:date_begin_index+1][::-1]
    low_list = predict_symbol["low_list"][date_end_index:date_begin_index+1][::-1]
    stop_list = predict_symbol["stop_list"][date_end_index:date_begin_index+1][::-1]
    #活动订单
    active_orders = []
    for day_index in range(days_count):
        score = score_list[day_index]
        if reversed: #预测反转
            score *= -1
        atr = atr_list[day_index]
        entry_price = price_list[day_index]
        high_price = high_list[day_index]
        low_price = low_list[day_index]
        position = round(f50_market_spider.risk_factor / atr, 2)
        stop_price = stop_list[day_index]
        new_order = {"score":score, "atr":atr, "entry_price":entry_price, "high_price":entry_price, "low_price":entry_price, "position":position, "stop_price":stop_price,"balance_dynamic": current_dynamic_balance, "stop_flag":"", "profit" : 0}

        #遍历未止盈止损的活动订单(倒序循环时才能删除元素)
        for active_order in active_orders[::-1]:
            #计算入场金额
            entry_amount = active_order["position"] * active_order["balance_dynamic"]
            #做多订单
            if active_order["score"]  > 0:
                #先用当日最低价判断是否止损，再用当日最高价更新止损价
                if low_price < active_order["stop_price"]:
                    active_order["stop_flag"] = 'X'
                    entry_price = active_order["entry_price"]
                    stop_price = active_order["stop_price"]
                    #计算离场金额
                    exit_amount = entry_amount / entry_price * stop_price
                    #计算收益时，考虑交易手续费fee_ratio
                    active_order["profit"] = exit_amount * (1 - fee_ratio) - entry_amount * (1 + fee_ratio)
                    #更新静态余额
                    current_balance += active_order["profit"]
                    #删除活动订单
                    active_orders.remove(active_order)
                else:
                    if high_price > active_order["high_price"]:
                        active_order["high_price"] = high_price
                        active_order["stop_price"] = high_price / (1 + atr / 100 / 2)
                    #计算离场金额
                    exit_amount = entry_amount / entry_price * entry_price
                    #计算收益时，考虑交易手续费fee_ratio
                    active_order["profit"] = exit_amount * (1 - fee_ratio) - entry_amount * (1 + fee_ratio)
            #做空订单
            else:
                #先用当日最低价判断是否止损，再用当日最高价更新止损价
                if low_price > active_order["stop_price"]:
                    active_order["stop_flag"] = 'X'
                    entry_price = active_order["entry_price"]
                    stop_price = active_order["stop_price"]
                    #计算离场金额
                    exit_amount = entry_amount / entry_price * stop_price
                    #计算收益时，考虑交易手续费fee_ratio
                    active_order["profit"] = entry_amount * (1 - fee_ratio) - exit_amount * (1 + fee_ratio)
                    #更新静态余额
                    current_balance += active_order["profit"]
                    #删除活动订单
                    active_orders.remove(active_order)
                else:
                    if low_price < active_order["low_price"]:
                        active_order["low_price"] = low_price
                        active_order["stop_price"] = low_price * (1 + atr / 100 / 2)
                    #计算离场金额
                    exit_amount = entry_amount / entry_price * entry_price
                    #计算收益时，考虑交易手续费fee_ratio
                    active_order["profit"] = entry_amount * (1 - fee_ratio) - exit_amount * (1 + fee_ratio)   
        #新余额等于静态余额加动态收益
        current_dynamic_balance = current_balance
        #当前余额
        for active_order in active_orders:
            current_dynamic_balance += active_order["profit"]
        active_orders.append(new_order)
    profit_past = (current_dynamic_balance / init_balance - 1) * 100
    #print("date:" + str(date_list[-1]) + " profit:" + str(profit_past))
    return profit_past

#模拟交易
#Simulated Trading
if __name__ == "__main__":
    symbols = input("Input symbols separated by space:")
    time_start=time.time()
    symbol_list = symbols.split(' ')
    predict_list = []
    for symbol in symbol_list:
        while len(symbol) > 0:
            marketListString  = f50_market_spider.search_for_symbol(symbol)
            if len(marketListString) == 0:
                symbol = symbol[:-1]
            else:
                break
        market = f50_market_spider.get_best_market(json.loads(marketListString))
        marketObj = market
        marketObj["name"] = marketObj["name"].replace("Investing.com","")
        timestamp_list, price_list, openprice_list, highprice_list, lowprice_list = f50_market_spider.get_history_price(str(marketObj["pairId"]), marketObj["pair_type"], 4800)
        if len(price_list) < f50_market_spider.input_days_len:
            continue
        turtle8_predict = f50_market_spider.predict(marketObj["symbol"]+marketObj["name"], timestamp_list, price_list, openprice_list, highprice_list, lowprice_list, 4500)
        predict_list.append(turtle8_predict)
    simulate_result, win_count, loss_count, draw_count, max_loss, max_loss_days, year_list = simulate_trading(predict_list)
    time_end=time.time()
    init_balance = simulate_result["balance_dynamic_list"][0]
    last_balance = simulate_result["balance_dynamic_list"][-1]
    years = len(simulate_result["symbol_list"]) / 365
    annual_yield =math.pow( last_balance / init_balance, 1 / years) * 100.0 - 100.0
    print('totally cost',time_end-time_start,"s")
    print('input:'+symbols)
    print("count = " + str(len(simulate_result["symbol_list"])) #交易天数
          + "\nwin = " + str(win_count)  #盈利次数
          + "\nloss = " + str(loss_count) #亏损次数
          + "\ndraw = " + str(draw_count) #平局次数 
          + "\nwinrate = " + str(win_count * 100.0 / (win_count + loss_count)  ) + "%" #胜率
          + "\nmax_loss = " + str(max_loss * 100.0)  + '%'#最大亏损
          #+ "max_single_loss = " + str(max_single_loss) + '%' #最大单次亏损
          #+ "max_single_win = " + str(max_single_win) + '%'  #最大单次盈利
          #+ "max_single_win_date = " + str(max_single_win_date) + '%'  #最大单次盈利日期
          + "\nmax_loss_period = " + str(max_loss_days) + "days" #最长亏损期
          + "\ninit_balance = " + str(init_balance)  #初始余额
          + "\nlast_balance = " + str(last_balance)  #最终余额
          + "\nannual_yield = " + str(annual_yield) + '%'  #年化收益
          + "\ndate_range = ["
          + datetime.datetime.strftime(simulate_result["date_list"][0],f50_market_spider.dateformat) + ',' 
          + datetime.datetime.strftime(simulate_result["date_list"][-1],f50_market_spider.dateformat) + ']')
    for year_item in year_list:
        print(str(year_item["year"])+":"+str(year_item["profit"]) + "%")
