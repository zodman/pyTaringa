#!/usr/bin/env python
# encoding=utf8
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
# made by zodman
import unittest
import mock
from pytaringa import Taringa, Shout
from pytaringa import TaringaRequest, BASE_URL
from kn3 import Kn3
import os

class PyTaringaTest(unittest.TestCase):
    def setUp(self):
        username = os.environ.get("U")
        password = os.environ.get("P")
        self.taringa = Taringa(username,password)


    @mock.patch("pytaringa.pytaringa.TaringaRequest.post_request")
    def _test_shout_add(self, get_mock_post_request):
        mock_post = mock.MagicMock()
        mock_post.text =  u""" text</i>
        <a href="/zodman/mi/test123" title="Hace instantes">Mira nomas</a> """
        get_mock_post_request.return_value = mock_post

        shout = Shout(self.taringa.cookie)
        res = shout.add("testing")
        assert "test123" in res, "not return url"

        shout.add("testing2",type_shout=Shout.LINK,attachment="http://google.com")
        assert "test123" in res, "not return url"

    def _test_post(self):
	import random
	import loremipsum
	title = "title %s" % random.randint(0,100)
	body = loremipsum.generate_paragraphs(5)
	body= "".join([i[2] for i in body])
	img1, img2 = "http://dummyimage.com/1080", "http://dummyimage.com/1080"
	self.taringa.post(title, body, "uno, dos,tres,cutra,cinco",img1,img2) 

    def test_like(self):
        shout = Shout(self.taringa.cookie)
        self.assertFalse(shout.like("75207986"), "not like")


class Kn3Test(unittest.TestCase):
    image_test = "https://cdn.awwni.me/tof8.jpg"

    def test_import(self):
        result = Kn3.import_to_kn3(self.image_test, "logo-r1.png")
        print result
        self.assertTrue('kn3.net' in result,"Not WOkrs")
