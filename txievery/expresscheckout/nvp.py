"""
Support for PayPal's NVP API.
"""
import urllib
import urlparse
from OpenSSL import SSL

from twisted.internet import reactor, ssl
from twisted.web import client, http_headers


class PaypalContextFactory(ssl.ClientContextFactory):
    def __init__(self, keyFile):
        self.keyFile = keyFile


    def getContext(self):
        self.method = SSL.SSLv23_METHOD
        ctx = ssl.ClientContextFactory.getContext(self)
        ctx.use_certificate_file(self.keyFile)
        ctx.use_privatekey_file(self.keyFile)
        return ctx



class NVPAgent(object):
    """
    An agent for speaking the NVP API.
    """
    def __init__(self, credentials):
        self.credentials = credentials
        ctxFactory = PaypalContextFactory(credentials.keyFile)
        self._agent = client.Agent(reactor, ctxFactory)


    def makeRequest(self, pairs):
        headers = http_headers.Headers()
        bodyProducer = NVPProducer(pairs)
        apiURL = self.credentials.apiURL
        d = self._agent.request("GET", apiURL, headers, bodyProducer)
        d.addCallback(urlparse.parse_qs)
        return d



class NVPProducer(object):
    """
    A producer for a body consisting of NVP parts.
    """
    def __init__(self, pairs):
        self.content = urllib.urlencode(pairs)
        self.length = len(self.content)


    def startProducing(self, consumer):
        consumer.write(self.content)


    def pauseProducing(self):
        pass


    def stopProducing(self):
        pass
