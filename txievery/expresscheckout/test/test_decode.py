"""
Tests for decoding NVP data to objects.
"""
import decimal

from twisted.trial import unittest

from txievery.expresscheckout import decode


exampleDetails = {'PAYMENTREQUEST_0_AMT': "100.00",
                  'L_PAYMENTREQUEST_0_QTY0': "1",
                  'L_PAYMENTREQUEST_0_AMT0': "100.00",
                  'L_PAYMENTREQUEST_0_ITEMCATEGORY0': "Physical",

                  'PAYMENTREQUEST_1_AMT': '300200.00',
                  'L_PAYMENTREQUEST_1_QTY0': "2",
                  'L_PAYMENTREQUEST_1_AMT0': "100.00",
                  'L_PAYMENTREQUEST_1_ITEMCATEGORY0': "Physical",
                  'L_PAYMENTREQUEST_1_QTY1': "3",
                  'L_PAYMENTREQUEST_1_AMT1': "100000.00",
                  'L_PAYMENTREQUEST_1_ITEMCATEGORY1': "Physical"}
skippedRequestIndexDetails = {'PAYMENTREQUEST_5_AMT': "100.00"}
skippedItemIndexDetails = {'L_PAYMENTREQUEST_1_AMT5': "100.00"}



class DecodeItemDetailsTest(unittest.TestCase):
    """
    Tests for decoding all the item details from payment request details.
    """
    def test_single(self):
        details = decode._decodeItemDetails(exampleDetails, 0)
        self.assertEqual(len(details), 1)


    def test_multiple(self):
        details = decode._decodeItemDetails(exampleDetails, 1)
        self.assertEqual(len(details), 2)



class DecodeItemTest(unittest.TestCase):
    """
    Tests for decoding a single item from payment request details.
    """
    def _decode(self, requestIdx, itemIdx):
        template = "L_PAYMENTREQUEST_%s_{key}%s" % (requestIdx, itemIdx)
        return decode._decodeItem(exampleDetails, template.format)


    def test_single(self):
        item, quantity = self._decode(0, 0)
        self.assertEqual(quantity, 1)
        self.assertEqual(item.amount, decimal.Decimal("100.00"))
        self.assertEqual(item.category, "Physical")


    def test_multiple(self):
        item, quantity = self._decode(1, 0)
        self.assertEqual(quantity, 2)
        self.assertEqual(item.amount, decimal.Decimal("100.00"))
        self.assertEqual(item.category, "Physical")

        item, quantity = self._decode(1, 1)
        self.assertEqual(quantity, 3)
        self.assertEqual(item.amount, decimal.Decimal("100000.00"))
        self.assertEqual(item.category, "Physical")