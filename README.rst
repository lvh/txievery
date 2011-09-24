==========
 txievery
==========

txievery (pronounced "thievery") is a library for dealing with Paypal_
using Twisted_.

The first target for txievery will be the `Express Checkout`_ API. This includes `Express Checkout for Digital Goods`_.

txievery only supports the `NVP API`_ (not the `SOAP API`_), and only supports
the `certificate authentication`_ method (not the signature method). Patches
welcome, but nobody sane should be using SOAP or signature authentication.

.. _Paypal: http://www.paypal.com
.. _Twisted: http://www.twistedmatrix.com
.. _`Express Checkout API`: https://www.x.com/community/ppx/ec
.. _`Express Checkout for Digital Goods`: https://cms.paypal.com/us/cgi-bin/?cmd=_render-content&content_ID=developer/e_howto_api_IntroducingExpressCheckoutDG
.. _`NVP API`: https://cms.paypal.com/us/cgi-bin/?cmd=_render-content&content_ID=developer/e_howto_api_nvp_NVPAPIOverview
.. _`SOAP API`: https://cms.paypal.com/us/cgi-bin/?cmd=_render-content&content_ID=developer/e_howto_api_soap_PayPalSOAPAPIArchitecture
.. _`certificate authentication`: https://cms.paypal.com/us/cgi-bin/?cmd=_render-content&content_ID=developer/apicertificates

Reference documents
===================

When first faced with developing using Paypal APIs, many developers
have difficulty finding the relevant pieces of documentation. When you
try to find some of this stuff yourself, it's easy to discover
contradictory information, information on deprecated APIs...

 - `PayPal Express Checkout Integration Guide`_

.. _`PayPal Express Checkout Integration Guide`: https://cms.paypal.com/cms_content/US/en_US/files/developer/PP_ExpressCheckout_IntegrationGuide.pdf

