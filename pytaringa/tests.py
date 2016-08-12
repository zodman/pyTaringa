import unittest
import mock
from pytaringa import Taringa, Shout
from pytaringa import TaringaRequest, BASE_URL
import os

class PyTaringaTest(unittest.TestCase):
    def setUp(self):
        username = os.environ.get("U")
        password = os.environ.get("P")
        self.taringa = Taringa(username,password)


    @mock.patch("pytaringa.pytaringa.TaringaRequest.post_request")
    def test_shout_add(self, get_mock_post_request):
        mock_post = mock.MagicMock()
        mock_post.text = u""" text</i>
        <a href="/zodman/mi/test123" title="Hace instantes">Mira nomas</a> """
        get_mock_post_request.return_value = mock_post

        shout = Shout(self.taringa.cookie)
        res = shout.add("testing")
        assert "test123" in res, "not return url"
        

        
        
