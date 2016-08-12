# -*- coding: utf-8 -*-
import time
import sys
import os
from pytaringa import Taringa, Shout, Kn3

if __name__ == '__main__':
    username = os.environ.get("USERNAME")
    password = os.environ.get("PASSWORD")
    taringa = Taringa(username,password)
    shout =  Shout(taringa.cookie)
    print taringa.username
    print taringa.password
    print taringa.user_key
    print taringa.user_id
    print taringa.cookie
  #  print shout.add("Hola a todos")
  #  print shout.add("#PyT ImageShout",Shout.IMAGE,attachment=Kn3.import_to_kn3("http://traduccionesyedra.files.wordpress.com/2012/04/testing.jpg"))
   # time.sleep(5)
   # print "attach a link link"
   # print shout.add("#PyT google http://google.com",Shout.LINK,attachment="http://google.com")
    print shout.add("#PyT google http://google.com",type_shout=Shout.VIDEO,
           attachment="https://www.youtube.com/watch?v=ugkK6_XmsaQ")
    # print taringa.get_user_id_from_nick("anpep")
    # print taringa.get_user_id_from_nick("overjt")
    # print shout.like("50735408","19963011")
    # print shout.delete("50735241")
    # print shout.get_object("47420358")["body"]
    # lastShout = shout.get_last_shout_from_id("19963011")
    # print lastShout
    # print shout.get_object(lastShout)["body"]
    # print Kn3.import_to_kn3("http://conociendogithub.readthedocs.org/en/latest/_images/GitHub.png")
