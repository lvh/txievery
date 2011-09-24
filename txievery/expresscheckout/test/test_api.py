"""
Tests for the Express Checkout txievery API.
"""
import decimal
import mock

from twisted.internet import defer
from twisted.trial import unittest

from txievery.expresscheckout import api, interface


emptyPaymentRequest = api.PaymentRequest([])



class ClientTest(unittest.TestCase):
    def setUp(self):
        self.client = api.Client("http://returnuri", "http://canceluri")

        self.deferred = d = defer.Deferred()
        self.client.agent = mock.Mock()
        self.client.agent.makeRequest.return_value = d


    def test_createCheckout(self):
        d = self.client.createCheckout(emptyPaymentRequest)
        @d.addCallback
        def verifyCheckout(checkout):
            self.assertTrue(interface.ICheckout.providedBy(checkout))
            self.assertEqual(checkout.token, "1")

        self.deferred.callback({"TOKEN": "1"})
        return d


    def test_tooManyRequests(self):
        numRequests = self.client.MAX_PAYMENT_REQUESTS + 1
        requests = [emptyPaymentRequest] * numRequests
        self.assertRaises(ValueError, self.client.createCheckout, *requests)



class CheckoutTest(unittest.TestCase):
    def test_getDetails(self):
        client =  mock.Mock()
        expectedToken = "1"
        checkout = api.Checkout(client, expectedToken, [])
        checkout.getDetails()
        token = client.getCheckoutDetails.call_args[0][0]
        self.assertEqual(token, expectedToken)



class ItemTest(unittest.TestCase):
    def setUp(self):
        self.item = api.Item(decimal.Decimal("100.00"), "USD")


    def test_validCategory(self):
        self.assertEqual(self.item.category, interface.PHYSICAL)

        self.item.category = interface.DIGITAL
        self.assertEqual(self.item.category, interface.DIGITAL)

        self.item.category = interface.PHYSICAL
        self.assertEqual(self.item.category, interface.PHYSICAL)


    def test_invalidCategory(self):
        """
        Tries to set the category of an item to a bogus value.
        """
        def assignCategory(value):
            self.item.category = value
        self.assertRaises(ValueError, assignCategory, "BOGUS")



class ItemAmountQuantizationTest(unittest.TestCase):
    """
    Tests that the amount of an item becomes quantized to two decimal places.
    """
    def test_noQuantizationNecessary(self):
        amount = decimal.Decimal("100.00")
        item = api.Item(amount, "USD")
        self.assertEqual(item.amount, amount)


    def test_quantization(self):
        item = api.Item(decimal.Decimal("100.12345"), "USD")
        expected = decimal.Decimal("100.12")
        self.assertEqual(item.amount, expected)


    def test_rounding(self):
        item = api.Item(decimal.Decimal("100.129"), "USD")
        expected = decimal.Decimal("100.13")
        self.assertEqual(item.amount, expected)



class PaymentRequestItemAmountTest(unittest.TestCase):
    def test_empty(self):
        paymentRequest = api.PaymentRequest([])
        self.assertEqual(paymentRequest.itemAmount, decimal.Decimal("0"))


    def test_oneItem(self):
        item = api.Item("100.00", "USD")
        paymentRequest = api.PaymentRequest([(item, 1)])
        self.assertEqual(paymentRequest.itemAmount, decimal.Decimal("100.00"))


    def test_twoItems(self):
        item = api.Item("100.00", "USD")
        paymentRequest = api.PaymentRequest([(item, 2)])
        self.assertEqual(paymentRequest.itemAmount, decimal.Decimal("200.00"))


    def test_combinedItems(self):
        itemOne = api.Item("100.00", "USD")
        itemTwo = api.Item("200.00", "USD")
        paymentRequest = api.PaymentRequest([(itemOne, 1), (itemTwo, 1)])
        self.assertEqual(paymentRequest.itemAmount, decimal.Decimal("300.00"))



class CombinedAmountTest(object):
    amountName = totalAmountName = None

    def setUp(self):
        self.paymentRequest = api.PaymentRequest([])

        self.highAmountItem = api.Item("100.00")
        self.highAmount = decimal.Decimal("100.0")
        setattr(self.highAmountItem, self.amountName, self.highAmount)

        self.lowAmountItem = api.Item("100.00")
        self.lowAmount = decimal.Decimal("10.0")
        setattr(self.lowAmountItem, self.amountName, self.lowAmount)


    def assertAmountEquals(self, expectedAmount):
        amount = getattr(self.paymentRequest, self.totalAmountName)
        self.assertEqual(amount, expectedAmount)


    def test_allZero(self):
        self.assertAmountEquals(decimal.Decimal("0"))


    def test_amountOnRequest(self):
        setattr(self.paymentRequest, self.amountName, self.lowAmount)
        self.assertAmountEquals(self.lowAmount)


    def test_amountOnItem(self):
        items = [(self.lowAmountItem, 1)]
        self.paymentRequest.itemDetails = items
        self.assertAmountEquals(self.lowAmount)


    def test_amountOnItems(self):
        items = [(self.lowAmountItem, 5)]
        self.paymentRequest.itemDetails = items
        # Tax amount is for all items put together, not per item TODO: verify
        self.assertAmountEquals(self.lowAmount)


    def test_amountOnMixedItems(self):
        items = [(self.lowAmountItem, 1), (self.highAmountItem, 1)]
        self.paymentRequest.itemDetails = items
        self.assertAmountEquals(self.lowAmount + self.highAmount)


    def test_amountOnEverything(self):
        setattr(self.paymentRequest, self.amountName, self.lowAmount)
        items = [(self.lowAmountItem, 1), (self.highAmountItem, 10)]
        self.paymentRequest.itemDetails = items
        self.assertAmountEquals(2 * self.lowAmount + self.highAmount)



class HandlingAmountTest(CombinedAmountTest, unittest.TestCase):
    """
    Tests if the handling amount for a payment request is correctly computed.
    """
    amountName = "handlingAmount"
    totalAmountName = "totalHandlingAmount"



class ShippingAmountTest(CombinedAmountTest, unittest.TestCase):
    """
    Tests if the shipping amount for a payment request is correctly computed.
    """
    amountName = "shippingAmount"
    totalAmountName = "totalShippingAmount"



class TaxAmountTest(CombinedAmountTest, unittest.TestCase):
    """
    Tests if the shipping amount for a payment request is correctly computed.
    """
    amountName = "taxAmount"
    totalAmountName = "totalTaxAmount"