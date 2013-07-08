#!/usr/bin/env python
#-*- coding:utf-8 -*-
# Time-stamp: <2013-01-15 11:28:52 by Yu Yang>

"""
upload video to tudou.com
"""
from TudouSdk import Tudou
app_key = ''
app_secret = ''
t = Tudou(app_key, app_secret)
t.auth()
# t.auth(username, password)
t.upload('/home/yangyu/Downloads/Screencast.mp4', 'emacs视频', '一个emacs演示视频', 'emacs', '科技')
