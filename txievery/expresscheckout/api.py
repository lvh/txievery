"""
Direct access to Paypal's Express Checkout API.
"""

class ExpressCheckoutClient(object):
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



ACTIONS = "Sale", "Authorization", "Order"



class PaymentRequest(object):
    def __init__(self, amount, currency, action="Sale"):
        self.amount = amount
        self.currency = currency

        if action not in actions:
            raise ValueError("Action should be one of %s" % (actions,))
        self.action = action



_ENCODE_ATTRKEYS = [("amount", "AMT"),
                    ("currency", "CURRENCYCODE"),
                    ("action", "PAYMENTACTION")]

_ENCODE_DETAILS = [(attr, "PAYMENTREQUEST_{{index}}_{key}".format(key=key))
                   for attr, key in _ENCODE_ATTRKEYS]


def encodePaymentRequests(*paymentRequests):
    """
    Encodes some payment requests in a request argument format.
    """
    args = {}

    for index, paymentRequest in enumerate(paymentRequests):
        for attr, keyTemplate in _ENCODE_DETAILS:
            key = keyTemplate.format(index)
            value = paymentRequest

        amountKey = "PAYMENTREQUEST_{0}_AMT".format(index)
        args[amountKey] = paymentRequest.amount

        currencyKey = "PAYMENTREQUEST_{0}_CURRENCYCODE".format(index)
        args[currencyKey] = paymentRequest.currency



class Checkout(object):
    implements(ICheckout)

    def __init__(self, client, token):
        self.client = client
        self.token = token


    def getDetails(self):
        return self.client.getCheckoutDetails(self.token)

