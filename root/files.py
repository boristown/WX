import os
import json
from sortedcontainers import SortedList

current_contest = 1

def load_reg_set():
    fname = 'data/reg_set'+str(current_contest)+'.json'
    fexist = os.path.exists(fname)
    if fexist:
        with open(fname, 'r+') as f:
            #如果文件f不为空，则载入到reg_set中，否则新建一个set
            reg_set = set(json.load(f))
    else:
        reg_set = set()
    return reg_set

def save_reg_set(reg_set):
    fname = 'data/reg_set'+str(current_contest)+'.json'
    print("save:"+fname)
    with open(fname, 'w+') as f:
        json.dump(list(reg_set), f)

def load_orders():
    fname = 'data/orders.json'
    fexist = os.path.exists(fname)
    if fexist:
        with open(fname, 'r+') as f:
            #如果文件f不为空，则载入到orders中，否则新建一个list
            orders = json.load(f)
    else:
        orders = []
    return orders

def save_orders(orders):
    fname = 'data/orders.json'
    with open(fname, 'w+') as f:
        json.dump(orders, f)


# def load_contest_rank():
#     fname = 'data/contest_rank'+str(current_contest)+'.json'
#     fexist = os.path.exists(fname)
#     if fexist:
#         with open(fname, 'r+') as f:
#             #如果 文件f不为空，则载入到contest_rank中，否则新建一个dict
#             contest_rank = json.load(f)
#     else:
#         contest_rank = []
#     return contest_rank

# def save_contest_rank(contest_rank):
#     fname = 'data/contest_rank'+str(current_contest)+'.json'
#     with open(fname, 'w+') as f:
#         json.dump(contest_rank, f)

def load_name_dict():
    fname = 'data/name_dict.json'
    fexist = os.path.exists(fname)
    if fexist:
        with open(fname, 'r+') as f:
            #如果文件f不为空，则载入到name_dict中，否则新建一个dict
            name_dict = json.load(f)
    else:
        name_dict = {}
    return name_dict

def save_name_dict(name_dict):
    fname = 'data/name_dict.json'
    with open(fname, 'w+') as f:
        json.dump(name_dict, f)

def load_elo_dict():
    fname = 'data/elo_dict.json'
    fexist = os.path.exists(fname)
    if fexist:
        with open(fname, 'r+') as f:
            #如果文件f不为空，则载入到elo_dict中，否则新建一个dict
            elo_dict = json.load(f)
    else:
        elo_dict = {}
    return elo_dict

def save_elo_dict(elo_dict):
    fname = 'data/elo_dict.json'
    with open(fname, 'w+') as f:
        json.dump(elo_dict, f)

def load_contest_history():
    fname = 'data/contest_history.json'
    fexist = os.path.exists(fname)
    if fexist:
        with open(fname, 'r+') as f:
            #如果文件f不为空，则载入到contest_history中，否则新建一个dict
            contest_history = json.load(f)
    else:
        contest_history = {}
    return contest_history

def save_contest_history(contest_history):
    fname = 'data/contest_history.json'
    with open(fname, 'w+') as f:
        json.dump(contest_history, f)

def load_status():
    fname = 'data/status.json'
    fexist = os.path.exists(fname)
    if fexist:
        with open(fname, 'r+') as f:
            #如果文件f不为空，则载入到status中，否则新建一个dict
            status = json.load(f)
    else:
        status = {}
    return status

def save_status(status):
    fname = 'data/status.json'
    with open(fname, 'w+') as f:
        json.dump(status, f)
        
# def load_elo_list():
#     fname = 'data/elo_list.json'
#     fexist = os.path.exists(fname)
#     if fexist:
#         with open(fname, 'r+') as f:
#             elo_list = SortedList(json.load(f))
#     else:
#         elo_list = SortedList()
#     return elo_list

# def save_elo_list(elo_list):
#     fname = 'data/elo_list.json'
#     with open(fname, 'w+') as f:
#         json.dump(elo_list[:], f)

def load_user_account(user):
    fname = 'data/account_'+user+'.json'
    fexist = os.path.exists(fname)
    if fexist:
        with open(fname, 'r+') as f:
            user_account = json.load(f)
    else:
        user_account = {"BTC":0,"USDT":1000000}
    return user_account

def save_user_account(user,user_account):
    fname = 'data/account_'+user+'.json'
    with open(fname, 'w+') as f:
        json.dump(user_account, f)
