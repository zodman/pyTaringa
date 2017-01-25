#!/usr/bin/env python
# encoding=utf8
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
# made by zodman

import requests 
from webscraping import xpath
import os
from pytaringa import Taringa, Shout
from pytaringa.pytaringa import  TaringaRequest
import time
import walrus
import logging
from lockfile import locked

logger = logging.getLogger(__name__)


@locked("/tmp/%s" % __name__ ,timeout=0)
def main():
    username, password = os.environ.get("U"), os.environ.get("P")
    tar = Taringa(username, password)
    shou = Shout(tar.cookie)
    w = walrus.Walrus()
    likes  = w.List("likes")
    for page in xrange(1, 10):
        key = tar.cookie.get("user_key")
        url = "http://www.taringa.net/serv/more/hashtag?tag=anime&page={}&key={}".format(page, key)
        req = TaringaRequest(tar.cookie)
        res = req.get_request(url)
        uids =xpath.search(res.content, "//a[@class='icon-pulgararriba shout-action-like require-login']/@data-id")
        for i in uids:
            if not i in likes:
                success = shou.like(i)
                if success:
                    likes.extend([i])                    
            time.sleep(60)
        #time.sleep(30)

if __name__ == "__main__":
    main()
