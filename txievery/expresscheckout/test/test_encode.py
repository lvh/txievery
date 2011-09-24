"""
Tests for encoding Express Checkout API objects to NVP.
"""
import decimal

from twisted.trial import unittest

from txievery.expresscheckout import api
from txievery.expresscheckout.encode import encodePaymentRequests, _encodeItem


CHEAP_ITEM = api.Item("100.00")
EXPENSIVE_ITEM = api.Item("100000.00")


def categories(itemDetails):
    return [item.category for item, qty in itemDetails]



class RequestEncodingTest(unittest.TestCase):
    items = [CHEAP_ITEM, EXPENSIVE_ITEM]

    def setUp(self):
        itemDetails = [(self.items[0], 1)]
        self.singleItemRequest = api.PaymentRequest(itemDetails)
        self.singleItemRequest.categories = categories(itemDetails)

        itemDetails = [(self.items[0], 2), (self.items[1], 3)]
        self.multipleItemRequest = api.PaymentRequest(itemDetails)
        self.multipleItemRequest.categories = categories(itemDetails)


    def test_oneItem(self):
        """
        Tests a single payment request with a single item.
        """
        request = self.singleItemRequest
        encoded = encodePaymentRequests(request)
        categories = request.categories
        expected = [('PAYMENTREQUEST_0_AMT', decimal.Decimal('100.00')),
                    ('L_PAYMENTREQUEST_0_QTY0', 1),
                    ('L_PAYMENTREQUEST_0_ITEMCATEGORY0', categories[0])]
        self.assertEqual(list(encoded), expected)


    def test_manyItems(self):
        """
        Tests a single payment request with more than one item.
        """
        request = self.multipleItemRequest
        encoded = encodePaymentRequests(request)
        categories = request.categories
        expected = [('PAYMENTREQUEST_0_AMT', decimal.Decimal('300200.00')),
                    ('L_PAYMENTREQUEST_0_QTY0', 2),
                    ('L_PAYMENTREQUEST_0_ITEMCATEGORY0', categories[0]),
                    ('L_PAYMENTREQUEST_0_QTY1', 3),
                    ('L_PAYMENTREQUEST_0_ITEMCATEGORY1', categories[1])]
        self.assertEqual(list(encoded), expected)


    def test_several(self):
        """
        Test several payment requests with variable amounts of items.
        """
        requests = self.singleItemRequest, self.multipleItemRequest
        encoded = encodePaymentRequests(*requests)
        categories = [r.categories for r in requests]
        expected = [('PAYMENTREQUEST_0_AMT', decimal.Decimal('100.00')),
                    ('L_PAYMENTREQUEST_0_QTY0', 1),
                    ('L_PAYMENTREQUEST_0_ITEMCATEGORY0', categories[0][0]),
                    ('PAYMENTREQUEST_1_AMT', decimal.Decimal('300200.00')),
                    ('L_PAYMENTREQUEST_1_QTY0', 2),
                    ('L_PAYMENTREQUEST_1_ITEMCATEGORY0', categories[1][0]),
                    ('L_PAYMENTREQUEST_1_QTY1', 3),
                    ('L_PAYMENTREQUEST_1_ITEMCATEGORY1', categories[1][1])]
        self.assertEqual(list(encoded), expected)


        
class ItemEncodingTest(unittest.TestCase):
    items = [CHEAP_ITEM, EXPENSIVE_ITEM]

    def _testEncode(self, index, item, qty, expected):
        encoded = _encodeItem("PAYMENTREQUEST_0_{0}", index, item, qty)
        self.assertEqual(list(encoded), expected)

        
    def test_one(self):
        """
        Tests encoding a single item.
        """
        expectedCategory = self.items[0].category
        expected = [('L_PAYMENTREQUEST_0_QTY0', 1),
                    ('L_PAYMENTREQUEST_0_ITEMCATEGORY0', expectedCategory)]
        self._testEncode(0, self.items[0], 1, expected)


    def test_many(self):
        """
        Tests encoding a single item with a quantity larger than 1.
        """
        expectedCategory = self.items[0].category
        expected = [('L_PAYMENTREQUEST_0_QTY0', 10),
                    ('L_PAYMENTREQUEST_0_ITEMCATEGORY0', expectedCategory)]
        self._testEncode(0, self.items[0], 10, expected)