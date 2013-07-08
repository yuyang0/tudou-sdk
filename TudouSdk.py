#!/usr/bin/env python
#-*- coding:utf-8 -*-
# Time-stamp: <2013-01-15 11:28:52 by Yu Yang>

"""
tudou sdk
"""
import sys
import requests
import socket
import os, os.path
from rauth import OAuth1Service, OAuth1Session
import webbrowser
import pickle

def getNetworkIp():
    '''
    get ip address of local computer
    '''
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('google.com', 0))
    return s.getsockname()[0]

def check_channel(channel):
    """
    check if the channel is correct
    Arguments:
    - `channel`:
    """
    channels = {
        '娱乐'   : 1,
        '乐活'   : 3,
        '搞笑'   : 5,
        '动画'   : 9,
        '游戏'   : 10,
        '音乐'   : 14,
        '体育'   : 15,
        '科技'   : 21,
        '电影'   : 22,
        '财富'   : 24,
        '教育'   : 25,
        '汽车'   : 26,
        '女性'   : 27,
        '纪录片' : 28,
        '热点'   : 29,
        '电视剧' : 30,
        '综艺'   : 31,
        '风尚'   : 32,
        '原创'   : 99
    }
    if channel not in channels.keys():
        print '频道指定错误'
        sys.exit(1)
    channelId = channels[channel]
    return channelId

class Tudou(object):
    """
    """

    def __init__(self, app_key, app_secret):
        """

        Arguments:
        - `app_key`: app key
        - `app_secret`:app secret
        """
        self.app_key = app_key
        self.app_secret = app_secret
        self.api_url = 'http://api.tudou.com/v3/gw'
        self.basic_auth = False
        self.session = False

    def __basic_authentication(self, username, password):
        """
        use basic authentication(suggest Oauth)
        Arguments:
        - `username`:username of tudou account
        - `password`:password of the Tudou account
        """
        self.basic_auth = True
        self.username = username
        self.password = password

    def __Oauth(self, redirect_url):
        """
        use Oauth
        """
        if self.session:
            return self.session

        access_token_pickle = 'access_token.pickle'
        try:
            with open(access_token_pickle, 'rb') as f:
                access_token, access_token_secret = pickle.load(f)
                self.session = OAuth1Session(self.app_key, self.app_secret, access_token, access_token_secret)
                return self.session
        except :
            pass

        tudou = OAuth1Service(
            name='tudou',
            consumer_key= self.app_key,
            consumer_secret= self.app_secret,
            request_token_url='http://api.tudou.com/auth/request_token.oauth',
            access_token_url='http://api.tudou.com/auth/access_token.oauth',
            authorize_url='http://api.tudou.com/auth/authorize.oauth',
            base_url='http://api.tudou.com/'
        )
        request_token, request_token_secret = tudou.get_request_token()
        print 'request_token %s' % request_token
        params = {'oauth_callback': redirect_url}
        authorize_url = tudou.get_authorize_url(request_token, **params)

        webbrowser.open(authorize_url)
        a = raw_input('press Enter to continue: ')
        access_token, access_token_secret = tudou.get_access_token(request_token, request_token_secret)
        # self.session = tudou.get_auth_session(request_token, request_token_secret)
        self.session = OAuth1Session(self.app_key, self.app_secret, access_token, access_token_secret)
        try:
            with open(access_token_pickle, 'wb') as f:
                pickle.dump((access_token, access_token_secret), f)
        except:
            print 'can not open %s to store the access token' % access_token_pickle
        return self.session

    def auth(self, username = '', password = '', redirect_url = 'http://www.tudou.com'):
        """
        there are two way to authenticate the app: the Basic Authentication and oauth
        if you specified username and password, the program will use Basic Authentication
        otherwith it will use Oauth, you specify the optional argument redirect_url
        """
        if username and password:
            self.__basic_authentication(username, password)
        else:
            self.__Oauth(redirect_url)

    def search(self, kw, **kwargs):
        """
        search in tudou.com
        Arguments:
        - `kw`:keyword
        """
        kwargs.update({'method': 'item.search', 'appKey': self.app_key, 'kw':kw})
        r = requests.get(self.api_url, params = kwargs)
        return r.json()

    def info(self, item_codes):
        """
        get information of the video specified by item_codes
        Arguments:
        - `item_codes`:
        """
        payload = {'method':'item.info.get', 'appKey':self.app_key, 'itemCodes':item_codes}
        r = requests.get(self.api_url, params = payload)
        return r.json()

    def rank(self, **kwargs):
        """
        """
        kwargs.update({'method':"item.ranking", 'appKey':self.app_key})
        r = requests.get(self.api_url, params = kwargs)
        return r.json()

    def state(self, item_codes):
        """
        get the state of the video specified by item code
        Arguments:
        - `item_codes`:the codes of videos
        """
        payload = {'method':'item.state.get', 'appKey':self.app_key, 'itemCodes':item_codes}
        r = requests.get(self.api_url, params = payload)
        return r.json()

    def comment(self, item_code, **kwargs):
        """
        get comment of the video specified by item code
        Arguments:
        - `item_code`:the video's code'
        """
        kwargs.update({'method':'item.comment.get', 'appKey':self.app_key, 'itemCode':item_code})
        r = requests.get(self.api_url, params = kwargs)
        return r.json()

    def download(self, item_code, **kwargs):
        """
        get download address of the video specified by item code
        Arguments:
        - `item_code`:
        - `**kwargs`:
        """
        kwargs.update({'method':'item.download', 'itemCode':item_code})
        r = requests.get(self.api_url, params = kwargs)
        return r.json()

    def __get_uploadurl(self, title, content, tags, channel):
        """
        get the upload url
        Arguments:
        - `title`:
        - `content`:
        - `tags`:
        - `channelId`:
        """
        channelId = check_channel(channel)
        video_info = {
            'title':title,
            'content':content,
            'tags':tags,
            'channelId':str(channelId),
            'ipAddr':getNetworkIp()
        }
        payload = video_info
        payload.update({'method':'item.upload', 'appKey':self.app_key})
        if self.basic_auth:
            r = requests.get(self.api_url, params = payload, auth = (self.username, self.password))
        else:
            session = self.session
            r = session.get(self.api_url, params = payload)
        return r.json()['itemUploadInfo']['uploadUrl']

    def upload(self, filename, title, content, tags, channelId):
        """
        upload a video to tudou.com
        Arguments:
        - `filename`:the video you want to upload
        """
        filename = os.path.expanduser(filename)
        if not os.path.isfile(filename):
            print 'the video filename is incorrect'
            sys.exit(1)
        upload_url = self.__get_uploadurl(title, content, tags, channelId)
        print 'upload video.....'
        files = {'file': open(filename, 'rb')}
        requests.post(upload_url, files = files)
        print 'finished'

    def user_info(self, username):
        """
        get user's information
        Arguments:
        - `username`:
        """
        payload = {'method':'user.info.get', 'appKey':self.app_key, 'user': username}
        r = requests.get(self.api_url, params = payload)
        return r.json()

    def user_video(self, username, page_num = 1, page_size = 10):
        '''
        用户的视频
        '''
        payload = {
            'method':'user.item.get', 'appKey':self.app_key,
            'user':username, 'pageNo':page_num, 'pageSize':page_size
        }
        r = requests.get(self.api_url, params = payload)
        return r.json()

    def user_playlist(self, username, page_num = 1, page_size = 10):
        '''
        用户的豆单
        '''
        payload = {
            'method':'user.playlist.get', 'appKey':self.app_key,
            'user':username, 'pageNo':page_num, 'pageSize':page_size
        }
        r = requests.get(self.api_url, params = payload)
        return r.json()
