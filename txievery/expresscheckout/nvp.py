"""
Support for PayPal's NVP API.
"""
import urllib
import urlparse

from twisted.internet import reactor
from twisted.web import client, http_headers


class NVPAgent(object):
    """
    An agent for speaking the NVP API.
    """
    def __init__(self, apiURL):
        self.apiURL = apiURL
        self._agent = client.Agent(reactor)


    def makeRequest(self, pairs):
        headers = http_headers.Headers()
        bodyProducer = NVPProducer(pairs)
        d = self._agent.request("GET", self.apiURL, headers, bodyProducer)
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
