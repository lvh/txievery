"""
Tests for the Express Checkout API.
"""
from twisted.trial import unittest

from txievery.expresscheckout import api, interfaces


class EncodePaymentRequestTest(unittest.TestCase):
    def _test_encode(self, requests):
        encoded = api.encodePaymentRequests(requests)


    def test_empty(self):
        self._test_encode([])


    def test_one(self):
        pr = api.PaymentRequest("0.01", "USD")
        self._test_encode([pr])


    def test_brokenInput(self):
        """
        Tests that data in the template gets quoted correctly.

        Note that this is a fairly unrealistic 
        """


class InterspersionTest(object):
    """
    Tests for ways to intersperse an iterable with a delimiter.
    """
    delimiter = "\x00"

    def buildInterspersed(self, iterable, delimiter):
        """
        Return an iterable of strings that, when joined, is the output
        of the original iterator, interspersed with ``delimiter``.
        """
        return NotImplementedError("Override this method")


    def _test_intersperse(self, iterable):
        """
        Tests interspersion using the ``_intersperse`` function
        directly.
        """
        got = "".join(self.buildInterspersed(iterable, self.delimiter))
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
    @staticmethod
    def buildInterspersed(iterable, delimiter):
        return api._intersperse(iterable, delimiter)



class InterspersedTest(InterspersionTest):
    """
    Tests for the ``interspersed`` decorator.
    """
    @staticmethod
    def buildInterspersed(iterable, delimiter):
        @api.interspersed(delimiter)
        def generatorFunction():
            return iterable

        return generatorFunction()
