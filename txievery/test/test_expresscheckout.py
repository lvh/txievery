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



class InterspersionTest(object):
    """
    Tests for ways to intersperse an iterable with a delimiter.
    """
    delimiter = "\x00"

    def buildInterspersed(self, iterable):
        """
        Return an iterable of strings that, when joined, is the output
        of the original iterator, interspersed with ``self.delimiter``.
        """
        return NotImplementedError("Override this method")


    def _test_intersperse(self, iterable):
        """
        Tests interspersion using the ``_intersperse`` function
        directly.
        """
        got = "".join(self.buildInterspersed(iterable))
        expected = self.delimiter.join(iterable)
        self.assertEqual(got, expected)


    def test_empty(self):
        """
        Tests that an empty iterable results in an empty string.
        """
        self._test_intersperse("")


    def test_single(self):
        """
        Tests that a single element results in that single element.
        """
        self._test_intersperse("a")


    def test_multiple(self):
        """
        Tests that multiple elements result in those elements
        interspersed with the delimiter.
        """
        self._test_intersperse("abc")



class IntersperseTest(InterspersionTest, unittest.TestCase):
    """
    Tests for the ``_intersperse`` function.
    """
    def buildInterspersed(self, iterable):
        return api._intersperse(iterable, self.delimiter)



class InterspersedTest(InterspersionTest):
    """
    Tests for the ``interspersed`` decorator.
    """
    def buildInterspersed(self, iterable):
        @api.interspersed(self.delimiter)
        def generatorFunction():
            return iterable

        return generatorFunction()
