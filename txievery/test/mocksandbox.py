"""
A mock Paypal sandbox.
"""
import urllib
import urlparse

from twisted.web import resource

from txievery.expresscheckout import nvp


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



def getPaymentRequests(details):
    requests = []
    firstEmptyIndex = 0
    indexes = xrange(10)

    for index in indexes:
        template = "PAYMENTREQUEST_{}_{{}}".format(index)
        if template.format("AMT") not in details:
            firstEmptyIndex = index
            break

        items = _getItemsInPaymentRequest(details, index)

    for remaining in indexes:
        if "PAYMENTREQUEST_{}_AMT".format(remaining) in details:
            raise ValueError("Payment request with index {} exists, but there"
                             " was no payment request with index {}"
                             .format(remaining, firstEmptyIndex))

    return requests


def _getItemsInPaymentRequest(details, paymentRequestIndex):
    items = []
    template = "L_PAYMENTREQUEST_{}_{{{}}}{{}}".format(paymentRequestIndex)


class Sandbox(object):
    def __init__(self):
        self._checkouts = {}


    def do_SetExpressCheckout(self, details):
        pass


    def do_GetExpressCheckoutDetails(self, details):
        pass