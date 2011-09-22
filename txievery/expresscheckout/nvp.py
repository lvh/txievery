"""
Support for PayPal's NVP API.
"""
import itertools
import urllib

from twisted.internet import reactor
from twisted.web import client, http_headers


class NVPAgent(object):
    def __init__(self, apiURL):
        self.apiURL = apiURL
        self._agent = client.Agent(reactor)


    def makeRequest(self, pairs):
        headers = http_headers.Headers()
        bodyProducer = NVPProducer(pairs)
        d = self._agent.request("GET", self.apiURL, headers, bodyProducer)
        return d



class NVPProducer(object):
    """
    A producer for a body consisting of NVP parts.
    """
    def __init__(self, pairs):
        self.content = urllib.urlencode(pairs)
        self.length = len(self.content)


    def startProducing(self, consumer):
        consumer.write(self.content)


    def pauseProducing(self):
        pass


    def stopProducing(self):
        pass



REQUEST_KEYS = [("AMT", "totalAmount")]
ITEM_KEYS = [("ITEMCATEGORY", "category")]


def encodePaymentRequests(*requests):
    """
    Encodes a bunch of payment requests as pairs.
    """
    encodedRequests = itertools.starmap(_encodeRequest, enumerate(requests))
    return itertools.chain.from_iterable(encodedRequests)


def _encodeRequest(requestIndex, request):
    """
    Encodes a payment request as (name, value) pairs.
    """
    requestTemplate = "PAYMENTREQUEST_{0}_{{0}}".format(requestIndex)
    requestPairs = _encodeAttributes(request, requestTemplate, REQUEST_KEYS)

    encodedItems = (_encodeItem(requestTemplate, itemIndex, item, quantity)
                    for itemIndex, (item, quantity)
                    in enumerate(request.itemDetails))
    itemPairs = itertools.chain.from_iterable(encodedItems)

    return itertools.chain(requestPairs, itemPairs)


def _encodeItem(requestTemplate, index, item, quantity):
    """
    Encodes a single item inside a payment request as (name, value) pairs.
    """
    itemTemplate = "L_{0}{1}".format(requestTemplate, index)
    quantityPairs = [(itemTemplate.format("QTY"), quantity)]
    itemPairs = _encodeAttributes(item, itemTemplate, ITEM_KEYS)
    return itertools.chain(quantityPairs, itemPairs)


def _encodeAttributes(obj, template, keysAndAttributes):
    """
    Encodes the attributes of an object as key, value pairs.
    """
    for key, attribute in keysAndAttributes:
        value = getattr(obj, attribute, None)
        if value is not None:
            yield template.format(key), value
