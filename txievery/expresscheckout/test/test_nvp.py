"""
Tests for NVP support.
"""
import mock
import StringIO

from twisted.trial import unittest

from txievery.expresscheckout import nvp


class NVPAgentTest(unittest.TestCase):
    def test_agent(self):
        expectedURL = "http://apiurl"
        credentials = mock.Mock()
        credentials.apiURL = expectedURL
        agent = nvp.NVPAgent(credentials)
        agent._agent = mock.Mock()

        pairs = [("a", "b")]
        agent.makeRequest(pairs)

        method, apiURL, headers, producer = agent._agent.request.call_args[0]
        self.assertEqual(method, "GET")
        self.assertEqual(apiURL, expectedURL)
        self.assertEqual(list(headers.getAllRawHeaders()), [])
        self.assertEqual(producer.content, "a=b")



class NVPProducerTest(unittest.TestCase):
    def test_producer(self):
        pairs = [("a", "b")]
        producer = nvp.NVPProducer(pairs)
        self.assertEqual(producer.length, len(producer.content))
        consumer = StringIO.StringIO()
        producer.startProducing(consumer)
        self.assertEqual(consumer.getvalue(), "a=b")


    def test_pauseOrStopProducing(self):
        """
        Tests that ``pauseProducing`` and ``stopProducing`` are no-ops.
        """
        producer = nvp.NVPProducer([])
        producer.pauseProducing()
        producer.stopProducing()
