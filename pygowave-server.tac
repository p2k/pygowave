
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

# You can run this .tac file directly with:
#    twistd -ny pygowave-server.tac

# This is the PyGoWave Server application used for persistence,
# client-to-server and server-to-server communication
# It can act as a STOMP server or client depending if a message broker is used
# or not.

# Configure the behavior here (choices are "server" and "client":
STOMP_MODE = "server"

# Set STOMP server, port, username and password here; for server mode only
# the port setting is used.
STOMP_USER = "pygowave_server"
STOMP_PASSWORD = "pygowave_server"
STOMP_SERVER = "localhost"
STOMP_PORT = 61613

### Don't edit things below this line, except if you know what you're doing ###

import sys, os

sys.path.append(os.path.dirname(__file__))

from twisted.application.service import Application

from pygowave_server.service import PyGoWaveService

application = Application("PyGoWave Server")

#from twisted.python import log
#def NullLogger(data): pass
#application.setComponent(log.ILogObserver, NullLogger)

service = PyGoWaveService()
service.setServiceParent(application)

if STOMP_MODE == "client":
	from twisted.application.internet import TCPClient
	from pygowave_server.stomp_client import IStompClientProtocolFactory
	scpf = IStompClientProtocolFactory(service)
	scpf.username = STOMP_USER
	scpf.password = STOMP_PASSWORD
	tcpc = TCPClient(
		STOMP_SERVER,
		STOMP_PORT,
		scpf
	)
	tcpc.setServiceParent(application)
elif STOMP_MODE == "server":
	from twisted.application.internet import TCPServer
	from pygowave_server.stomp_server import IStompServerProtocolFactory
	sspf = IStompServerProtocolFactory(service)
	tcps = TCPServer(
		STOMP_PORT,
		sspf
	)
	tcps.setServiceParent(application)
