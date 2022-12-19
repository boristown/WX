import os
import json

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

def load_contest_rank():
    fname = 'data/contest_rank'+str(current_contest)+'.json'
    fexist = os.path.exists(fname)
    if fexist:
        with open(fname, 'r+') as f:
            #如果文件f不为空，则载入到contest_rank中，否则新建一个dict
            contest_rank = json.load(f)
    else:
        contest_rank = []
    return contest_rank

def save_contest_rank(contest_rank):
    fname = 'data/contest_rank'+str(current_contest)+'.json'
    with open(fname, 'w+') as f:
        json.dump(contest_rank, f)

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

def load_elo_list():
    fname = 'data/elo_list.json'
    fexist = os.path.exists(fname)
    if fexist:
        with open(fname, 'r+') as f:
            elo_list = SortedList(json.load(f))
    else:
        elo_list = SortedList()
    return elo_list

def save_elo_list(elo_list):
    fname = 'data/elo_list.json'
    with open(fname, 'w+') as f:
        json.dump(elo_list[:], f)