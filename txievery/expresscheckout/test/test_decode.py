"""
Tests for decoding NVP data to objects.
"""
from twisted.trial import unittest


EXAMPLE_PAIRS = [
    ('PAYMENTREQUEST_0_AMT', decimal.Decimal('100.00')),
    ('L_PAYMENTREQUEST_0_QTY0', 1),
    ('L_PAYMENTREQUEST_0_ITEMCATEGORY0', categories[0][0]),

    ('PAYMENTREQUEST_1_AMT', '300200.00'),
    ('L_PAYMENTREQUEST_1_QTY0', 2),
    ('L_PAYMENTREQUEST_1_QTY1', 3)]

class DecodeItemTest(unittest.TestCase):
    """
    Tests for decoding a single item from payment request details.
    """