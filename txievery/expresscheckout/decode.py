"""
Support for decoding NVP API to Express Checkout API objects.
"""
from txievery.expresscheckout import api


def decodeCheckout(details):
    paymentRequests = _decodePaymentRequests(details)
    return api.Checkout(paymentRequests)


def _verifyLastElement(firstEmptyIndex, template, remainingIndices, details):
    for remaining in remainingIndices:
        if template.format(remaining) in details:
            raise ValueError("Element at index {0} after empty index {1}"
                             .format(remaining, firstEmptyIndex))


def _decodePaymentRequests(details):
    requests = []
    firstEmpty = 0
    idxs = xrange(10)

    for idx in idxs:
        template = "PAYMENTREQUEST_{0}_{{0}}".format(idx)
        if template.format("AMT") not in details:
            firstEmpty = idx
            break

        itemDetails = _decodeItemDetails(details, idx)
        request = api.PaymentRequest(itemDetails)
        requests.append(request)

    _verifyLastElement(firstEmpty, "PAYMENTREQUEST_{0}_AMT", idxs, details)

    return requests


def _decodeItemDetails(details, paymentRequestIndex):
    """
    Gets the item details from payment request details.

    Since the payment request details may contain multiple payment requests,
    you must specify the index of the payment request you want to get the
    items from.
    """
    itemDetails = []
    template = "L_PAYMENTREQUEST_{0}_{{{0}}}{{0}}".format(paymentRequestIndex)
    firstEmpty = 0
    idxs = xrange(10)

    for idx in idxs:
        itemTemplate = template.format(idx)
        if template.format("AMT") not in details:
            firstEmpty = idx
            break

        item, qty = _decodeItem(details, itemTemplate)
        itemDetails.append((item, qty))

    verifyTemplate = "L_PAYMENTREQUEST_{0}_AMT{{0}})".format(paymentRequestIndex)
    _verifyLastElement(firstEmpty, verifyTemplate, idxs, details)

    return itemDetails


ITEM_KEYS = [("ITEMCATEGORY", "category")]


def _decodeItem(details, template):
    """
    Gets a single item from payment request details.
    """
    amount = details[template.format("AMT")]
    item = api.Item(amount)

    for key, attr in ITEM_KEYS:
        value = details.get(key)
        if value is None:
            continue
        setattr(item, attr, value)

    return item
