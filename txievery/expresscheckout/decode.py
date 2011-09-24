"""
Support for decoding NVP API to Express Checkout API objects.
"""
from txievery.expresscheckout import api


def parseCheckout(details):
    paymentRequests = _parsePaymentRequests(details)
    return api.Checkout(paymentRequests)


def _parsePaymentRequests(details):
    requests = []
    firstEmptyIndex = 0
    indexes = xrange(10)

    for index in indexes:
        template = "PAYMENTREQUEST_{}_{{}}".format(index)
        if template.format("AMT") not in details:
            firstEmptyIndex = index
            break

        itemDetails = _parseItemDetails(details, index)
        request = api.PaymentRequest(itemDetails)
        requests.append(request)

    for remaining in indexes:
        if "PAYMENTREQUEST_{}_AMT".format(remaining) in details:
            raise ValueError("Payment request with index {} exists, but there"
                             " was no payment request with index {}"
                             .format(remaining, firstEmptyIndex))

    return requests


def _parseItemDetails(details, paymentRequestIndex):
    """
    Gets the item details from payment request details.

    Since the payment request details may contain multiple payment requests,
    you must specify the index of the payment request you want to get the
    items from.
    """
    itemDetails = []
    template = "L_PAYMENTREQUEST_{0}_{{{0}}}{{0}}".format(paymentRequestIndex)
    firstEmptyIndex = 0
    indexes = xrange(10)

    for index in indexes:
        itemTemplate = template.format(index)
        if template.format("AMT") not in details:
            firstEmptyIndex = index
            break

        itemDetails.append(_parseItem(details, template))

    return itemDetails


def _parseItem(details, template):
    pass