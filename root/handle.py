# -*- coding: utf-8 -*-
# filename: handle.py

import werobot
import werobot.client
import werobot.replies
import re
import binance_api
from pymouse import PyMouse
from pykeyboard import PyKeyboard
from time import sleep,time
from multiprocessing import Process
import pyperclip
import pyscreenshot as ImageGrab
from Basic import *
from Media import *

pic_url = ""

def process_task(s,user):
    m = PyMouse()
    k = PyKeyboard()
    m.click(60,95,1,1)
    pyperclip.copy(s)
    sleep(1)
    m.click(585,550,1,1)
    sleep(1)
    k.press_key(k.control_key)
    k.tap_key('v')
    k.release_key(k.control_key)
    k.tap_key(k.enter_key)

def save_img(user,target,ts):
    filename ='img/temp'+str(time.time()*1000)+'.jpg'
    im = ImageGrab.grab((450,70,1090,490))
    im.save(filename)
    im.close()
    pic_url = picture_url(filename)
    #return pic_url
    return werobot.replies.ImageReply(media_id=pic_url,target=user,source=target,time=ts)

pattern1 = r"1\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)"
patternc = r"c\s+(\d+)\s+(\d+)"

def screen_shot(user,target,ts,x1, y1, x2, y2):
    filename ='img/temp'+str(time.time()*1000)+'.jpg'
    #print(x1,y1,x2,y2)
    im = ImageGrab.grab(tuple(map(int,(x1, y1, x2, y2))))
    im.save(filename)
    im.close()
    pic_url = picture_url(filename)
    #return pic_url
    return werobot.replies.ImageReply(media_id=pic_url,target=user,source=target,time=ts)
    
def chat(s,user,target,ts):
    if s == '1':
        return save_img(user,target,ts)
    else:
        match1 = re.match(pattern1, s)
        if match1:
            x1, y1, x2, y2 = match1.groups()
            return screen_shot(user,target,ts,x1, y1, x2, y2)
        matchc = re.match(patternc, s)
        if matchc:
            x,y = matchc.groups()
            LClick(x,y)
            return
        process_task(s,user)
    ans = "您的输入信息已经发送给ChatGPT，输入'1'查看截图。"# + str(user)
    return ans

def LClick(x, y):
    mouse = PyMouse()
    mouse.click(x,y,1,1)
    
def picture_url(picture_name):
    myMedia = Media()
    accessToken = Basic().get_access_token()
    filePath = picture_name
    mediaType = "image"
    murlResp = Media.uplaod(accessToken, filePath, mediaType)
    return murlResp
