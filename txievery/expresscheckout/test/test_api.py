"""
Tests for the Express Checkout txievery API.
"""
import decimal

from twisted.trial import unittest

from txievery.expresscheckout import api, interface


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
        self.assertRaises(TypeError, assignCategory, "BOGUS")


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



class PaymentRequestTest(unittest.TestCase):
    pass

