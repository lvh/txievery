"""
Interfaces for the Express Checkout API.
"""
from zope.interface import Interface, Attribute


class ICheckout(Interface):
    token = Attribute(
        """
        The token for this checkout.
        """)

    def getDetails():
        """
        Gets the details for this checkout.
        """

    def complete(amount=UNCHANGED, currency=UNCHANGED):
        pass


class IPaymentRequest(Interface):
    amount = Attribute(
        """
        The amount in this payment request.

        This should be a ``Decimal`` object, and will always be
        rounded to two places.
        """)

    currency = Attribute(
        """
        The currency code for the currency in which the amount is
        expressed.
        """)
