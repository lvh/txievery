"""
Support for encoding (serializing) Express Checkout API objects to NVP.
"""
import itertools


REQUEST_KEYS = [("AMT", "totalAmount")]
ITEM_KEYS = [("AMT", "amount"),
             ("ITEMCATEGORY", "category"),
             ("NAME", "name")]


def encodeCheckout(checkout):
    return encodePaymentRequests(*checkout.paymentRequests)


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