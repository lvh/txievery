"""
Tests for the mock sandbox.
"""
import mock
import StringIO
import urllib
import urlparse

from twisted.trial import unittest

from txievery.test import mocksandbox


class APICallDetailsTest(unittest.TestCase):
    def test_itemAccess(self):
        pairs = [("a", "b"), ("c", "d")]
        acd = mocksandbox.APICallDetails(pairs)
        self.assertEquals(acd["a"], "b")
        self.assertEquals(acd["c"], "d")
        self.assertRaises(KeyError, lambda: acd["z"])


    def test_containment(self):
        pairs = [("a", "b"), ("c", "d")]
        acd = mocksandbox.APICallDetails(pairs)
        self.assertIn("a", acd)
        self.assertNotIn("e", acd)


    def test_iteration(self):
        pairs = [("a", "b"), ("c", "d")]
        self.assertEquals(list(mocksandbox.APICallDetails(pairs)), pairs)


    def test_duplicatePairs(self):
        pairs = [("a", "b"), ("a", "c")]
        self.assertRaises(ValueError, mocksandbox.APICallDetails, pairs)



class EndpointTest(unittest.TestCase):
    def setUp(self):
        self.endpoint = mocksandbox.Endpoint()

    def _sendRequest(self, pairs):
        request = type("FakeRequest", (), {})()
        content = urllib.urlencode(pairs)
        request.content = StringIO.StringIO(content)
        response = self.endpoint.render_POST(request)
        return urlparse.parse_qsl(response)

    
    def test_dispatch(self):
        sandbox = self.endpoint.sandbox = mock.Mock()
        expectedResponse = [("GARAAARASDFSSDF!!!!", "ARAWERSS")]
        sandbox.do_AWESOME.return_value = expectedResponse
        pairs = [("METHOD", "AWESOME"), ("DOCUMENTATION", "ARCANE")]
        response = self._sendRequest(pairs)

        details = sandbox.do_AWESOME.call_args[0][0]
        self.assertEqual(details.pairs, pairs)
        self.assertEqual(response, expectedResponse)


    def test_unknownMethod(self):
        pairs = [("METHOD", "BOGUS")]
        self.assertRaises(ValueError, self._sendRequest, pairs)


    def test_missingMethod(self):
        self.assertRaises(ValueError, self._sendRequest, [])



class SandboxTest(unittest.TestCase):
    def setUp(self):
        self.sandbox = mocksandbox.Sandbox()


    def test_setExpressCheckout(self):
        details = []
        self.assertEqual(len(self.sandbox._checkouts), 0)
        response = self.sandbox.do_SetExpressCheckout(details)
        self.assertEqual(len(self.sandbox._checkouts), 1)
        response = dict(response)
        for mandatoryKey in ("TOKEN", "ACK", "VERSION", "BUILD"):
            self.assertIn(mandatoryKey, response)