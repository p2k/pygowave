
#
# PyGoWave Server
# Copyright (C) 2010 Patrick "p2k" Schneider <patrick.schneider@wavexperts.de>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from twisted.application.service import IService, Service
from twisted.internet.task import LoopingCall
from twisted.internet.interfaces import IProtocolFactory
from twisted.python import components, log
from zope.interface import implements

__all__ = ["IPyGoWaveService", "IStompProtocolFactory", "PyGoWaveService"]

class IStompProtocolFactory(IProtocolFactory):
	"""
	Base class for the client and server protocol factory interfaces
	
	"""
	
	def sendMessagesTo(rkey, messages):
		"""
		Send a list of messages to a message queue with the given
		routing key.
		
		"""

class IPyGoWaveService(IService):
	"""
	Interface for all Services which work with PyGoWave messages.
	
	"""
	
	def process(rkey, message_data):
		"""
		Process one or more messages received by the protocol.
		
		rkey is the routing key for the messages.
		message_data is a list of messages, which are dictionaries.
		
		This function must return a dictionary where the keys are the target
		routing keys and the values are lists of messages to be sent to the
		targets.
		
		"""
	
	def factoryReady():
		"""
		Callback from factory when the connection is up and running.
		
		"""
	
	def messageQueueInfo():
		"""
		This gets called by the Stomp client implementation in order
		to retrieve information about the message queue to subscribe
		to.
		
		It must return a dictionary with the following items:
		"queue_name" - Name of the message queue to subscribe to
		"exchange" - Name of the exchange for messages
		"routing_key" - Routing key (with wildcards) for messages
		"exchange_type" - Type of the exchange (should be "topic")
		
		It may return a list of dictionaries, if you want to
		subscribe to multiple queues.
		
		"""

class PyGoWaveService(Service):
	"""
	Main service for PyGoWave, which processes incoming messages.
	
	"""
	
	implements(IPyGoWaveService)
	
	def factoryReady(self, factory):
		log.msg("=> PyGoWave Server factory ready <=")
	
	def messageQueueInfo(self):
		return [
			{
				"queue_name": "wavelet_server_singlethread",
				"exchange": "wavelet.topic",
				"routing_key": "*.*.clientop",
				"exchange_type": "topic",
			},
			{
				"queue_name": "wavelet_server_singlethread",
				"exchange": "federation.topic",
				"routing_key": "*.*.fedinop",
				"exchange_type": "topic",
			},
		]
	
	def startService(self):
		from message_processor import PyGoWaveMessageProcessor
		self.mp = PyGoWaveMessageProcessor()
		
		self.lc = LoopingCall(self.mp.purge_connections)
		self.lc2 = LoopingCall(self.mp.log_stats)
		self.lc.start(10 * 60) # Purge every 10 minutes
		self.lc2.start(60 * 60, now=False) # Stats every 60 minutes
		
		log.msg("=> PyGoWave Server service ready <=")
	
	def stopService(self):
		if self.lc.running:
			self.lc.stop()
		if self.lc2.running:
			self.lc2.stop()
		
		self.lc = None
		self.lc2 = None
		self.mp = None
	
	def process(self, rkey, message_data):
		return self.mp.process(rkey, message_data)
