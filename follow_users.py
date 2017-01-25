#!/usr/bin/env python
# encoding=utf8
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
# made by zodman

import requests 
from webscraping import xpath
import os
from pytaringa import Taringa
import time
import  logging

from lockfile import locked


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

@locked("/tmp/%s"%(__name__, ),timeout=0)
def main():
    username, password = os.environ.get("U"), os.environ.get("P")
    tar = Taringa(username, password)
    
    for page in xrange(1, 10):
        res = requests.get("http://www.taringa.net/serv/more/trend?page={}".format(page))
        uids =xpath.search(res.content, "//div[@class='shout-user-info']/a/@data-uid")
        for i in uids:
            ret = tar.follow_user(i)
            if ret:
                "follow {}".format(i)
            time.sleep(60*10)

if __name__ == "__main__":
    main()
