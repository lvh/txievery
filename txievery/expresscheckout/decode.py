"""
Support for decoding NVP API to Express Checkout API objects.
"""
from functools import partial

from txievery.expresscheckout import api


def decodeCheckout(details):
    paymentRequests = _decodePaymentRequests(details)
    return api.Checkout(paymentRequests)


baseTemplate = "PAYMENTREQUEST_{requestIndex}_{key}".format
baseListTemplate = "L_PAYMENTREQUEST_{requestIndex}_{key}{itemIndex}".format


def _decodePaymentRequests(details):
    requests = []
    firstEmpty = 0
    idxs = iter(xrange(10))

    for idx in idxs:
        template = partial(baseTemplate, requestIndex=idx)
        if template(key="AMT") not in details:
            firstEmpty = idx
            break

        itemDetails = _decodeItemDetails(details, idx)
        request = api.PaymentRequest(itemDetails)
        requests.append(request)

    verifyTemplate = partial(baseTemplate, key="AMT")
    _verifyLastElement(firstEmpty, verifyTemplate, idxs, details)

    return requests


def _decodeItemDetails(details, requestIndex):
    """
    Gets the item details from payment request details.

    Since the payment request details may contain multiple payment requests,
    you must specify the index of the payment request you want to get the
    items from.
    """
    itemDetails = []
    itemTemplate = partial(baseListTemplate, requestIndex=requestIndex)
    firstEmpty = 0
    idxs = iter(xrange(10))
    
    for idx in idxs:
        keyTemplate = partial(itemTemplate, itemIndex=idx)
        if keyTemplate(key="AMT") not in details:
            firstEmpty = idx
            break

        item, qty = _decodeItem(details, keyTemplate)
        itemDetails.append((item, qty))

    verifyTemplate = partial(itemTemplate, key="AMT")
    _verifyLastElement(firstEmpty, verifyTemplate, idxs, details)

    return itemDetails


ITEM_KEYS = [("ITEMCATEGORY", "category")]


def _decodeItem(details, template):
    """
    Gets a single item from payment request details.
    """
    quantity = int(details[template(key="QTY")])
    amount = details[template(key="AMT")]
    item = api.Item(amount)

    for key, attr in ITEM_KEYS:
        value = details.get(key)
        if value is None:
            continue
        setattr(item, attr, value)

    return item, quantity


def _verifyLastElement(firstEmptyIndex, template, remainingIndices, details):
    for remaining in remainingIndices:
        if template(itemIndex=remaining) in details:
            raise ValueError("Element at index {0} after empty index {1}"
                             .format(remaining, firstEmptyIndex))