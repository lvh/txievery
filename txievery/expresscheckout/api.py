"""
Direct access to PayPal's Express Checkout API.
"""
import decimal
import itertools
import operator

from zope.interface import implements

from txievery.expresscheckout import interface, nvp
from txievery.expresscheckout.nvp import encodePaymentRequests


SANDBOX_SIGNATURE_URI = "https://api-3t.sandbox.paypal.com/nvp"
SANDBOX_CERTIFICATE_URI = "https://api.sandbox.paypal.com/nvp"

LIVE_SIGNATURE_URI = "https://api-3t.paypal.com/nvp"
LIVE_CERTIFICATE_URI = "https://api.paypal.com/nvp"



class Client(object):
    """
    A client for dealing with Paypal's Express Checkout NVP API.
    """
    API_VERSION = "74.0"
    MAX_PAYMENT_REQUESTS = 10
    
    def __init__(self, returnURL, cancelURL, apiURL=SANDBOX_CERTIFICATE_URI):
        self._defaultPairs = [("VERSION", self.API_VERSION),
                              ("RETURNURL", returnURL),
                              ("CANCELURL", cancelURL)]

        self.agent = nvp.NVPAgent(apiURL)


    def _makeRequest(self, method, extraPairs):
        prefixPairs = [("METHOD", method), self._defaultPairs]
        pairs = itertools.chain(prefixPairs, extraPairs)
        return self.agent.makeRequest(pairs)


    def createCheckout(self, *paymentRequests):
        """
        Creates a new checkout.

        Returns a deferred ``ICheckout``.

        This maps to the ``SetExpressCheckout`` NVP API call.
        """
        if len(paymentRequests) > self.MAX_PAYMENT_REQUESTS:
            msg = ("{0.__class__} supports up to {0.MAX_PAYMENT_REQUESTS}, "
                   "requested {1}".format(self, len(paymentRequests)))
            raise ValueError(msg)

        pairs = encodePaymentRequests(paymentRequests)
        d = self._makeRequest("SetExpressCheckout", pairs)
        d.addCallback(self._instantiateCheckout, paymentRequests)
        return d


    def _instantiateCheckout(self, response, paymentRequests):
        """
        Instantiates a checkout object.
        """
        return Checkout(self, response["TOKEN"], paymentRequests)


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
    handlingAmount = shippingAmount = taxAmount = ZERO

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
