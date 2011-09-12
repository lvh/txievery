"""
A mock Paypal sandbox.
"""
import urllib
import urlparse

from twisted.web import server


class APICallDetails(object):
    def __init__(self, pairs):
        self.pairs = pairs
        self.__iter__ = pairs.__iter__
        self.__getitem__ = dict(pairs).__getitem__



class Endpoint(server.Resource):
    def __init__(self):
        self.sandbox = Sandbox()


    def render_POST(self, request):
        requestPairs = urlparse.parse_qsl(request.content.read())
        callDetails = APICallDetails(requestPairs)
        try:
            method = getattr(self.sandbox, "do_" + callDetails["METHOD"])
        except KeyError:
            raise ValueError("No method specified")
        except AttributeError:
            raise ValueError("Unknown method: %r" % (callDetails["METHOD"],))
        responsePairs = method(callDetails)
        return urllib.urlencode(responsePairs)


class Sandbox(object):
    def __init__(self):
        self._checkouts = {}

    def do_SetExpressCheckout(self, details):
        pass

    def do_GetExpressCheckoutDetails(self, details):
        pass