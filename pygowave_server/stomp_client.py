
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

from twisted.internet.protocol import Protocol, ReconnectingClientFactory
from twisted.python import components
from zope.interface import implements, Attribute

import stomper, simplejson

from service import IPyGoWaveService, IStompProtocolFactory

# This module registers an adapter, please use
# IStompClientProtocolFactory(service) to create a factory from a service
__all__ = ["IStompClientProtocolFactory"]

class IStompClientProtocolFactory(IStompProtocolFactory):
	"""Interface for a stomp client protocol factory"""
	username = Attribute("Username for the Stomp connection")
	password = Attribute("Password for the Stomp connection")

class StompMessageProcessor(stomper.Engine):
	def __init__(self, protocol):
		super(StompMessageProcessor, self).__init__()
		self.proto = protocol
	
	def connect(self):
		"""Generate the STOMP connect command to get a session."""
		return stomper.connect(self.proto.factory.username, self.proto.factory.password)
	
	def connected(self, msg):
		"""Once I've connected I want to subscribe to my the message queue(s)."""
		super(StompMessageProcessor, self).connected(msg)
		
		self.proto.factory.protocolConnected(self.proto)
		
		mqis = self.proto.service.messageQueueInfo()
		
		if not isinstance(mqis, list):
			mqis = [mqis]
		
		out = ""
		for mqi in mqis:
			f = stomper.Frame()
			f.unpack(stomper.subscribe(mqi["queue_name"]))
			f.headers["exchange"] = mqi["exchange"]
			f.headers["routing_key"] = mqi["routing_key"]
			f.headers["exchange_type"] = mqi["exchange_type"]
			out += f.pack()
		return out
	
	def ack(self, message):
		rkey = message["headers"]["destination"]
		message_data = simplejson.loads(message["body"].decode("utf-8"))
		
		msg_dict = self.proto.service.process(rkey, message_data)
		
		out_frames = ""
		for out_rkey, messages in msg_dict.iteritems():
			out_frames += self.send(out_rkey, messages)
		
		return super(StompMessageProcessor, self).ack(message) + out_frames

	def send(self, routing_key, messages):
		"""Convert a routing key and a list of messages into a STOMP frame."""
		f = stomper.Frame()
		f.unpack(stomper.send(routing_key, simplejson.dumps(messages)))
		f.headers["exchange"] = "wavelet.direct"
		f.headers["content-type"] = "application/json"
		return f.pack().encode("utf-8")

class StompClientProtocol(Protocol):
	def __init__(self, service):
		self.service = service
		self.mp = StompMessageProcessor(self)
		self.stompBuffer = stomper.stompbuffer.StompBuffer()
	
	def connectionMade(self):
		"""Register with the stomp server."""
		self.factory.connection = self
		self.transport.write(self.mp.connect())
	
	def connectionLost(self, reason):
		"""Shut down."""
	
	def dataReceived(self, data):
		"""Data received, react to it and respond."""
		self.stompBuffer.appendData(data.replace('\0', '\0\n'))
		
		while True:
			msg = self.stompBuffer.getOneMessage()
			
			if self.stompBuffer.buffer.startswith('\n'):
				self.stompBuffer.buffer = self.stompBuffer.buffer[1:]
			
			if msg is None:
				break
			
			returned = self.mp.react(msg)
			if returned:
				self.transport.write(returned)
	
	def sendMessagesTo(self, rkey, messages):
		"""Convert a routing key and a list of messages into a STOMP frame and send it."""
		self.transport.write(self.mp.send(rkey, messages))

class StompClientFactoryFromService(ReconnectingClientFactory):
	
	implements(IStompClientProtocolFactory)
	
	def __init__(self, service):
		self.service = service
	
	def startedConnecting(self, connector):
		"""Started to connect."""
	
	def clientConnectionLost(self, connector, reason):
		"""Lost connection."""
	
	def buildProtocol(self, addr):
		"""Transport level connected now create the communication protocol."""
		p = StompClientProtocol(self.service)
		p.factory = self
		return p
	
	def protocolConnected(self, protocol):
		self.connected_protocol = protocol
		self.service.factoryReady(self)
	
	def sendMessagesTo(self, rkey, messages):
		# Forwarding to the currently connected protocol object
		if self.connected_protocol == None:
			return
		self.connected_protocol.sendMessagesTo(rkey, messages)
	
	#def clientConnectionFailed(self, connector, reason):
	#	"""Connection failed."""
	#	super(StompClientFactory, self).clientConnectionFailed(connector, reason)
	
	def __repr__(self):
		return "StompClientFactory"

components.registerAdapter(StompClientFactoryFromService, IPyGoWaveService, IStompClientProtocolFactory)
