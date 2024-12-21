import unittest
from django.test import Client

class SimpleTest(unittest.TestCase):

    def test_status_url_available(self):
        client = Client()
        response = client.get('/toolscan/status/')
        self.assertEqual(response.status_code, 200)

    def test_status_is_ok(self):
        client = Client()
        response = client.get('/toolscan/status/')
        self.assertEqual(response.content, b'1')




