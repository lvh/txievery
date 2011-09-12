"""
Tests for the Express Checkout API.
"""
from urlparse import parse_qsl

from twisted.trial import unittest

from txievery.expresscheckout import api


def grouper(it, n):
    return zip(*[iter(it)]*n)



class EncodePaymentRequestTest(unittest.TestCase):
    """
    Tests for encoding payment requests.
    """
    def _test_encode(self, requests):
        suffixes = [k for _, k in api._ENCODE_ATTRKEYS]

        encoded = "".join(api.encodePaymentRequests(*requests))
        parsed = parse_qsl(encoded)
        parsedPerRequest = grouper(parsed, len(suffixes))
        self.assertEqual(len(parsedPerRequest), len(requests))

        for index, requestData in enumerate(zip(requests, parsedPerRequest)):
            request, parsedEntries = requestData

            for expectedSuffix, entry in zip(suffixes, parsedEntries):
                key, value = entry
                prefix, entryIndex, suffix = key.split("_", 2)

                self.assertEqual(prefix, "PAYMENTREQUEST")
                self.assertEqual(entryIndex, str(index))
                self.assertEqual(suffix, expectedSuffix)


    def test_empty(self):
        """
        Tests encoding an empty payment request.
        """
        self._test_encode([])


    def test_one(self):
        """
        Tests encoding a payment request with one entry.
        """
        data = [("0.01", "USD")]
        self._test_encode([api.PaymentRequest(a, c) for a, c in data])


    def test_multiple(self):
        """
        Tests encoding a payment request with multiple entries.
        """
        data = [("0.01", "USD"), ("0.01", "EUR"), ("0.01", "HKD")]
        self._test_encode([api.PaymentRequest(a, c) for a, c in data])

