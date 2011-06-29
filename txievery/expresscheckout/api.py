"""
Direct access to Paypal's Express Checkout API.
"""
from decimal import Decimal
from functools import wraps
from urllib import quote_plus

from zope.interface import implements

from txievery.expresscheckout import interfaces


class Client(object):
    """
    A client for dealing with Paypal's Express Checkout API.
    """
    def __init__(self, returnURL, cancelURL):
        self.returnURL = returnURL
        self.cancelURL = cancelURL


    def createCheckout(self, *paymentRequests):
        """
        Creates a new checkout.

        Returns a deferred ``ICheckout``.

        This maps to the ``SetExpressCheckout`` call.
        """
        @d.addCallback
        def instantiateCheckout(token):
            return Checkout(self, token)


    def getCheckoutDetails(self, token):
        """
        Gets the details of a particular checkout.

        This should almost always be called by an ``ICheckout``.
        """



_TWO_PLACES = Decimal("0.01")


def _twoDecimalPlaces(amount):
    """
    Quantizes to two decimal places.
    """
    return Decimal(amount).quantize(_TWO_PLACES)



class PaymentRequest(object):
    def __init__(self, amount, currency, action="Sale"):
        self.amount = _twoDecimalPlaces(amount)
        self.currency = currency

        if action not in interfaces.ACTIONS:
            raise ValueError("Unsupported action")
        self.action = action



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

    Note the lack of ``&`` at the end of that line.
    """
    for index, paymentRequest in enumerate(requests):
        for attr, template in _ENCODE_DETAILS:
            value = quote_plus(str(getattr(paymentRequest, attr)))
            entry = template.format(index=index, value=value)
            yield entry



class Checkout(object):
    implements(interfaces.ICheckout)

    def __init__(self, client, token):
        self.client = client
        self.token = token


    def getDetails(self):
        return self.client.getCheckoutDetails(self.token)
