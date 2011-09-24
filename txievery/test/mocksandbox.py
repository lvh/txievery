"""
A mock Paypal sandbox.
"""
import urllib
import urlparse
import itertools

from twisted.web import resource

from txievery.expresscheckout import encode, decode


class APICallDetails(object):
    def __init__(self, pairs):
        self.pairs = pairs
        self._pairsMap = pairsMap = dict(pairs)
        if len(pairsMap) != len(pairs):
            duplicates = [p for p in pairs if p[0] in pairsMap]
            raise ValueError("Duplicate pairs: {}".format(duplicates))


    def __contains__(self, key):
        return key in self._pairsMap


    def __getitem__(self, key):
        return self._pairsMap[key]


    def __iter__(self):
        return iter(self.pairs)



class Endpoint(resource.Resource):
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
        self._tokens = (str(i) for i in itertools.count())


    def do_SetExpressCheckout(self, details):
        checkout = decode.decodeCheckout(details)
        token = self._tokens.next()
        self._checkouts[token] = checkout
        return {"TOKEN": token}


    def do_GetExpressCheckoutDetails(self, details):
        checkout = self._checkouts[details["TOKEN"]]
        return encode.encodeCheckout(checkout)