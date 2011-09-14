"""
Direct access to Paypal's Express Checkout API.
"""
import decimal
import itertools
import operator
import urllib
import urlparse

from zope.interface import implements

from twisted.internet import reactor
from twisted.web import client, http_headers

from txievery.expresscheckout import interface


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



class Client(object):
    """
    A client for dealing with Paypal's Express Checkout NVP API.
    """
    API_VERSION = "74.0"
    MAX_PAYMENT_REQUESTS = 10
    
    def __init__(self, returnURL, cancelURL, apiURL):
        self._defaultPairs = [("VERSION", self.API_VERSION),
                              ("RETURNURL", returnURL),
                              ("CANCELURL", cancelURL)]

        self.apiURL = apiURL
        self.agent = client.Agent(reactor)


    def _makeRequest(self, method, extraPairs):
        headers = http_headers.Headers()
        pairs = [("METHOD", method)] + self.defaultNVPData + extraPairs
        bodyProducer = NVPProducer(pairs)
        d = self.agent.request("GET", self.apiURL, headers, bodyProducer)
        return d


    def createCheckout(self, paymentRequests):
        """
        Creates a new checkout.

        Returns a deferred ``ICheckout``.

        This maps to the ``SetExpressCheckout`` NVP API call.
        """
        if len(paymentRequests) > self.MAX_PAYMENT_REQUESTS:
            msg = ("{0.__class__} supports up to {0.MAX_PAYMENT_REQUESTS}, "
                   "requested {1}".format(self, len(paymentRequests)))
            raise ValueError(msg)

        pairs = paymentRequests
        d = self._makeRequest("SetExpressCheckout", pairs)
        d.addCallback(self._instantiateCheckout, paymentRequests)


    def _instantiateCheckout(self, responseContent, paymentRequests):
        """
        Instantiates a checkout object.
        """
        token = urlparse.parse_qs(responseContent)["TOKEN"]
        return Checkout(self, token)


    def getCheckoutDetails(self, token):
        """
        Gets the details of a particular checkout.

        This maps to the ``GetExpressCheckoutDetails`` NVP API call.
        
        This should almost always be called by an ``ICheckout``.
        """
        d = self._makeRequest("GetExpressCheckoutDetails", token)
        return d



ZERO = decimal.Decimal("0")


def _combinedAmount(attr):
    getAmount = operator.attrgetter(attr)

    @property
    def combinedAmount(self):
        return getAmount(self) + sum(getAmount(item) for item in self.items)

    return combinedAmount



class PaymentRequest(object):
    handlingAmount = shippingAmount = taxAmount = ZERO
    
    def __init__(self, itemDetails, action=interface.SALE):
        self.itemDetails = itemDetails


    @property
    def items(self):
        return (item for item, qty in self.itemDetails)


    @property
    def totalAmount(self):
        return (self.itemAmount + self.totalTaxAmount
                + self.totalHandlingAmount + self.totalShippingAmount)
        
    @property
    def itemAmount(self):
        return sum(qty * item.amount for item, qty in self.itemDetails)


    totalHandlingAmount = _combinedAmount("handlingAmount")
    totalShippingAmount = _combinedAmount("shippingAmount")
    totalTaxAmount = _combinedAmount("taxAmount")



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
    requestTemplate = "PAYMENTREQUEST_{}_{{}}".format(requestIndex)
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
    itemTemplate = "L_{}_{{}}{}".format(requestTemplate, index)
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
        

def _twoDecimalPlaces(amount):
    """
    Quantizes to two decimal places.
    """
    return decimal.Decimal(amount).quantize(decimal.Decimal("0.01"))



class Item(object):
    """
    An item in a payment request.
    """
    implements(interface.IItem)

    def __init__(self, amount, currency="USD"):
        self.amount = _twoDecimalPlaces(amount)
        self.currency = currency

    
    _category = interface.PHYSICAL
    @property
    def category(self):
        return self._category

    @category.setter
    def category(self, category):
        if category not in interface.CATEGORIES:
            raise ValueError("Cateogry must be one of {}, was {}"
                             .format(interface.CATEGORIES, category))

        self._category = category



class Checkout(object):
    """
    A checkout.
    """
    implements(interface.ICheckout)

    def __init__(self, client, token, paymentRequests):
        self.client = client
        self.token = token
        self.paymentRequests = paymentRequests


    def getDetails(self):
        return self.client.getCheckoutDetails(self.token)


    def complete(self, paymentRequests=interface.UNCHANGED):
        if paymentRequests is interface.UNCHANGED:
            paymentRequests = self.paymentRequests

        # TODO: ACTUALLY COMPLETE THIS CHECKOUT
