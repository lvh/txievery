"""
Direct access to Paypal's Express Checkout API.
"""
import decimal
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



def _combinedAmount(attr):
    getAmount = operator.attrgetter(attr)

    @property
    def combinedAmount(self):
        return getAmount(self) + sum(getAmount(item) for item in self.items)

    return combinedAmount


class NewPaymentRequest(object):
    handlingAmount = shippingAmount = taxAmount = decimal.Decimal("0")
    
    def __init__(self, itemDetails, action=interface.SALE):
        self.itemDetails = itemDetails


    @property
    def items(self):
        return (item for item, qty in self.itemDetails)

        
    @property
    def itemAmount(self):
        return sum(qty * item.amount for item, qty in self.itemDetails)


    totalHandlingAmount = _combinedAmount("handlingAmount")
    totalShippingAmount = _combinedAmount("shippingAmount")
    totalTaxAmount = _combinedAmount("taxAmount")



def _twoDecimalPlaces(amount):
    """
    Quantizes to two decimal places.
    """
    return decimal.Decimal(amount).quantize(decimal.Decimal("0.01"))



class Item(object):
    implements(interface.IItem)

    def __init__(self, amount, currency):
        self.amount = _twoDecimalPlaces(amount)
        self.currency = currency



def _intersperse(iterable, delimiter):
    """
    Intersperses elements of ``iterable`` with ``delimiter``.

    Like ``str.join``, but lazy. Alternately yields an element from
    ``iterable`` and ``delimiter``.  Technically works on arbitrary
    objects, not just strings, although that's what it was written
    for.
    """
    it = iter(iterable)
    yield next(it)
    for element in it:
        yield delimiter
        yield element


def interspersed(delimiter):
    """
    Decorates a generator function so that its output becomes
    interspersed with ``delimiter``.
    """
    def decorator(f):
        """
        Decorates a generator function using ``intersperse``.
        """
        def decorated(*a, **kw):
            """
            Returns a generator that yields all of the elements of
            another generator, interspersed with {delimiter}.

            The original, wrapped generator function used to produce
            the generator of which the elements will be interspersed
            can be accessed via the ``original`` attribute on this
            function.
            """.format(delimiter=delimiter)
            return _intersperse(f(*a, **kw), delimiter)

        decorated.original = f
        return decorated

    return decorator


_ENCODE_ATTRKEYS = [("amount", "AMT"),
                    ("currency", "CURRENCYCODE"),
                    ("action", "PAYMENTACTION")]
_TEMPLATE = "PAYMENTREQUEST_{{index}}_{key}={{value}}"
_ENCODE_DETAILS = [(attr, _TEMPLATE.format(key=key))
                   for attr, key in _ENCODE_ATTRKEYS]


@interspersed("&")
def encodePaymentRequests(*requests):
    """
    Encodes some payment requests into something closer to Paypal's
    NVP standard, commonly known as URI query strings.

    Returns an iterable of lines. Each line is an NVP entry, like:

    ::

        PAYMENTREQUEST_0_AMT=100.00

    Note the lack of ``&`` at the end of that line. This is added by the
    ``interspersed`` decorator.
    """
    for index, paymentRequest in enumerate(requests):
        for attr, template in _ENCODE_DETAILS:
            value = quote_plus(str(getattr(paymentRequest, attr)))
            entry = template.format(index=index, value=value)
            yield entry



class Checkout(object):
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
