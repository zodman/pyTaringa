# -*- coding: utf-8 -*-

from functools import wraps
from datetime import datetime
import re
import json
import requests
import time
import os
import logging
from kn3 import Kn3

USER_AGENT = 'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:29.0) '
USER_AGENT += 'Gecko/20100101 Firefox/29.0'

BASE_URL = 'http://www.taringa.net'
API_URL = 'http://api.taringa.net'

HEADERS = {'Referer': 'http://www.taringa.net',
           'User-Agent': USER_AGENT}
FORMAT_LOGGIN= '%(asctime)-15s  %(levelname)s  %(module)s:%(funcName)s+%(lineno)d %(message)s'

logger = logging.getLogger(__name__)
logging.basicConfig(format=FORMAT_LOGGIN)
debug = logger.debug


def response_successful(f):
    @wraps(f)
    def inner(*args, **kwargs):
        response = f(*args, **kwargs)
        if response and response.status_code == 200:
            return response
        elif response and response.status_code==403:
            raise TaringaRequestException(response.content)
        else:
            raise TaringaRequestException('Response was not succesful: %s' % response.content)
    return inner


class TaringaException(Exception):
    def __init__(self, message):
        debug(message)


class TaringaRequestException(Exception):
    def __init__(self, message):
        debug(message)


class TaringaRequest(object):
    def __init__(self, headers=HEADERS, cookie=None):
        self.headers = headers
        self.cookie = cookie

    @response_successful
    def get_request(self, url):
        if self.cookie:
            request = requests.get(url, headers=self.headers,
                                   cookies=self.cookie)
        else:
            request = requests.get(url, headers=self.headers)

        return request

    @response_successful
    def post_request(self, url, data, is_ajax=False):
        headers = self.headers
        if is_ajax:
            headers.update({
                'X-Requested-With':'XMLHttpRequest'
            })
        data = {'data':data, 'headers':headers}
        if self.cookie:
            request = requests.post(url, cookies=self.cookie,
                                    **data)
        else:
            request = requests.post(url, **data)

        return request


def user_logged_in(fun):
    def inner(self, *args, **kwargs):
        if self.cookie:
            return fun(self, *args, **kwargs)
    return inner


class Taringa(object):
    def __init__(self, username=None, password=None, cookie=None,
                 user_key=None):
        self.cookie = cookie
        self.user_key = user_key
        self.user_id = None
        self.username = username
        self.password = password
        self.base_url = BASE_URL
        self.api_url = API_URL
        self.realtime = None

        if self.cookie is None:
            self.login()
            self.store_user_key()
            self.store_user_id()
            # TODO: it is necesary ?
            #self.store_realtime_data()

    def login(self):
        data = {
            'nick': self.username,
            'pass': self.password,
            'redirect': '/',
            'connect': ''
        }

        url = self.base_url + '/registro/login-submit.php'

        try:
            request = TaringaRequest().post_request(url, data)
        except TaringaRequestException:
            raise TaringaException('Login failed: Request was not succesful')
            return

        response = json.loads(request.text)

        if not response.get('status'):
            raise TaringaException('Login failed: Wrong auth data?')
        else:
            cookie = {}

            cookie['ln'] = request.cookies.get('ln', '')
            cookie['tid'] = request.cookies.get('tid', '')
            cookie['trngssn'] = request.cookies.get('trngssn', '')

            self.cookie = cookie
            debug('Logged in succesfuly as %s' % self.username)

    @user_logged_in
    def store_user_id(self):
        self.user_id = self.cookie.get('tid').rsplit('%3A%3A')[0]
        self.cookie.update({'user_id': self.user_id})

    @user_logged_in
    def store_realtime_data(self):
        regex = r'new Realtime\({\"host\"\:\"([\w\.]+)\",\"port\":([\d]+).*}\)'
        request = TaringaRequest(cookie=self.cookie).get_request(self.base_url)

        realtime = re.findall(regex, request.text, re.DOTALL)
        if len(realtime) > 0:
            if len(realtime[0]) == 2:
                self.realtime = realtime[0]
            else:
                raise TaringaException('Login failed: Wrong auth data?')
        else:
            raise TaringaException('Login failed: Wrong auth data?')
            
    @user_logged_in
    def store_user_key(self):
        regex = r'var global_data = { user: \'.*?\', user_key: \'(.*?)\''
        request = TaringaRequest(cookie=self.cookie).get_request(self.base_url)

        user_key = re.findall(regex, request.text, re.DOTALL)

        if len(user_key) > 0:
            self.user_key = user_key[0]
            self.cookie.update({'user_key': user_key[0]})
        else:
            return debug('Could not obtain user_key')

    @user_logged_in
    def get_url(self,url):
        request = TaringaRequest(cookie=self.cookie).get_request(self.base_url + "/" + url)

    def get_user_id_from_nick(self, user_nick):
        url = self.api_url + '/user/nick/view/%s' % user_nick
        request = TaringaRequest().get_request(url)
        response = json.loads(request.text)
        if "code" in response:
            return None
        else:
            return response["id"]

    @user_logged_in
    def follow_user(self, user_id):
        data = {
            'key': self.cookie.get('user_key'),
            'type':'user',
            'obj':str(user_id),
            'action':'follow'
        }

        url = self.base_url + '/notificaciones-ajax.php'
        request = TaringaRequest(cookie=self.cookie).post_request(url, data=data, is_ajax=True)
        if request.status_code ==200:
            if request.content == "":
                return False
            else:
                response = request.json()
                logger.info(response)
                if response.get("status", None) == 3:
                    raise TaringaRequestException(response["data"])
                else:
                    return True

        else:
            return False

    def get_wallpost(self, link):
        regex = r'<div class=\"activity-content\">(?:\s+)<span class=\"dialog\"></span>(?:\s+)<div class=\"activity-header clearfix\">(?:\s+)@<a class="hovercard"(?:.*?)<\/div>(?:\s+)<p>(.*?)<\/p>'
        url = self.base_url + link
        request = TaringaRequest(cookie=self.cookie).get_request(url)

        content = re.findall(regex, request.text, re.MULTILINE | re.DOTALL)

        if len(content) > 0:
            return content[0]
        else:
            debug('Could not obtain the wallpost content')
            return None

    def get_replies_comment(self, comment_id, obj_id, obj_owner,obj_type):
        data = {
            'key': self.cookie.get('user_key'),
            'objectType':obj_type,
            'objectId':obj_id,
            'objectOwner':obj_owner,
            'commentId':comment_id,
            'page':'-200'
        }

        url = self.base_url + '/ajax/comments/get-replies'
        request = TaringaRequest(cookie=self.cookie).post_request(url, data=data)
        response = json.loads(request.text)
        if "code" in response:
            return None
        else:
            return response

    def get_signature_comment(self, comment_id, obj_id,obj_type):
        data = {
            'key': self.cookie.get('user_key'),
            'objectType':obj_type,
            'objectId':obj_id,
            'commentId':comment_id,
        }
        regex = r'<div class=\"comment clearfix(?:.*?)\" data-id="(?:\d+)"(?:.*?)data-signature="(.*?)"'
        url = self.base_url + '/ajax/comments/get'
        request = TaringaRequest(cookie=self.cookie).post_request(url, data=data)
        content = re.findall(regex, request.text, re.DOTALL)

        if len(content) > 0:
            return content[0]
        else:
            debug('Could not obtain the signature')
            return None

    def post(self, title, body, tags, image_1x1, image_4x3):
        # kn3 from taringa!!!!
        image_1x1= Kn3.import_to_kn3(image_1x1)
        image_4x3= Kn3.import_to_kn3(image_4x3)
        print image_1x1, image_4x3
        data = {
            'id':'',
            'titulo': title,
            'cuerpo': body,
            'categoria':7,
            'tags': tags,
            'image_1x1':image_1x1,
            'image_4x3':image_4x3,
            'own-source':1,
            'sin_comentarios':0,
            'twitter-vinculation':"false",
            'facebook-vinculation':"false",
            'vinculation_offer':'false',
            'key': self.cookie.get('user_key'),

        }
        url = self.base_url +"/ajax/post/add"
        request  = TaringaRequest(cookie=self.cookie).post_request(url, data=data)
        print request.content


class Shout(object):
    IMAGE = 1
    LINK = 3
    VIDEO = 2
    TEXT = 0
    PRIVACY_ON = 1
    PRIVACY_OFF = 0

    def __init__(self, cookie):
        self.cookie = cookie
        self.base_url = BASE_URL
        self.api_url = API_URL

    @user_logged_in
    def add(self, body, type_shout=TEXT, privacy=PRIVACY_OFF, attachment=''):
        data = {
            'key': self.cookie.get('user_key'),
            'attachment': attachment,
            'attachment_type': type_shout,
            'privacy': privacy,
            'body': body
        }
        if type_shout in ( self.LINK,):
            new_data = {
                    'key': self.cookie.get("user_key"), 'islink': 1,
                    'url': attachment
                    }
            attach_id = self._attach_link(new_data)
            assert not attach_id is None, "id not returned"
            data.update({'attachment': attach_id})

        url = self.base_url + '/ajax/shout/add'
        regex = r'</i>.*?<a href="(.*?)" title="Hace instantes"'
        request = TaringaRequest(cookie=self.cookie).post_request(url, data=data)
        #debug("debug code %s",(request.text,))
        urlshout = re.findall(regex, request.text, re.DOTALL)
        #debug("find url %s",urlshout)
        if len(urlshout) > 0:
            return self.base_url + urlshout[0]
        else:
            return debug('Could not obtain shout url')

    def _attach_link(self, data):
        url = self.base_url+ "/ajax/shout/attach"
        response = TaringaRequest(cookie=self.cookie).post_request(url, data=data)
        debug("attach response %s", response.text)
        return response.json().get("data").get("id")


    @user_logged_in
    def add_comment(self, comment, obj_id, obj_owner, obj_type):
        data = {
            'key': self.cookie.get('user_key'),
            'comment': comment,
            'objectId': obj_id,
            'objectOwner': obj_owner,
            'objectType': obj_type,
            'show':'true'
        }
        url = self.base_url + '/ajax/comments/add'
        request = TaringaRequest(cookie=self.cookie).post_request(url, data=data)

    def add_reply_comment(self, comment, obj_id, obj_owner, obj_type, parent, parentOwner,signature):
        data = {
            'key': self.cookie.get('user_key'),
            'comment': comment,
            'objectId': obj_id,
            'objectOwner': obj_owner,
            'objectType': obj_type,
            'show':'true',
            'parent':parent,
            'parentOwner':parentOwner,
            'signature':signature

        }
        url = self.base_url + '/ajax/comments/add'
        request = TaringaRequest(cookie=self.cookie).post_request(url, data=data)
        
    @user_logged_in
    def like(self, shout_id):
        data = {
            'key': self.cookie.get('user_key'),
            'object_id': shout_id
        }

        url = self.base_url + '/serv/shout/like'
        logger.info("data to send %s", data)
        try:
            request = TaringaRequest(cookie=self.cookie).post_request(url, data=data, is_ajax=True)
        except TaringaRequestException:
            return False
        logger.info("response..... %s",request.content)
        if request.status_code == 200:
            return True
        else:
            return False


    @user_logged_in
    def old_like(self, shout_id, owner_id):
        data = {
            'key': self.cookie.get('user_key'),
            'owner': owner_id,
            'uuid': shout_id,
            'score': '1'
        }

        url = self.base_url + '/ajax/shout/vote'
        request = TaringaRequest(cookie=self.cookie).post_request(url, data=data)
        response = json.loads(request.text)
        if response["status"] == 1:
            return 1
        else:
            return "0 " + response["data"]

    def delete(self, shout_id):
        data = {
            'owner': self.cookie.get('user_id'),
            'key': self.cookie.get('user_key'),
            'id': shout_id
        }

        url = self.base_url + '/ajax/shout/delete'
        TaringaRequest(cookie=self.cookie).post_request(url, data=data)

    def get_object(self, shout_id):
        url = self.api_url + '/shout/view/%s' % shout_id
        request = TaringaRequest().get_request(url)
        response = json.loads(request.text)

        return response

    def get_last_shout_from_id(self, user_id):
        url = self.api_url + '/shout/user/view/%s?trim_user=true' % user_id
        request = TaringaRequest().get_request(url)
        response = json.loads(request.text)

        if "code" in response:
            return None
        else:
            for shout in response:
                if shout["owner"] == str(user_id):
                    return shout["id"]
            return None


