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
    def test_shout_add(self, get_mock_post_request):
        mock_post = mock.MagicMock()
        mock_post.text =  u""" text</i>
        <a href="/zodman/mi/test123" title="Hace instantes">Mira nomas</a> """
        get_mock_post_request.return_value = mock_post

        shout = Shout(self.taringa.cookie)
        res = shout.add("testing")
        assert "test123" in res, "not return url"

        shout.add("testing2",type_shout=Shout.LINK,attachment="http://google.com")
        assert "test123" in res, "not return url"
        

        
class Kn3Test(unittest.TestCase):
    image_test = "https://cdn.awwni.me/tof8.jpg"

    def test_import(self):
        result = Kn3.import_to_kn3(self.image_test, "logo-r1.png")
        print result
        self.assertTrue('kn3.net' in result,"Not WOkrs")
