
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
#    twistd -ny pygowave-web-client.tac

# This twisted application script combines PyGoWave's web frontend and Orbited
# under one process. It should be run in conjunction with the PyGoWave Server
# application with or without a message queue in between.

### WORK IN PROGRESS ###

import os, sys, pkg_resources
from twisted.application import service, internet

new_twisted = False

try:
	pkg_resources.require("twisted>=9.0.0")
	new_twisted = True
except pkg_resources.VersionConflict:
	pkg_resources.require("twisted==8.2.0") # Specific workarounds needed

def addOrbitedService(site):
	# Duplicates functionality of orbited's start script
	pkg_resources.require("orbited>=0.7.10")
	
	from orbited import config
	from orbited import logging
	
	class EmptyConfig(object):
		def __init__(self):
			config = None
			version = False
			profile = False
	
	config.setup(options=EmptyConfig())
	logging.setup(config.map)
	
	from twisted.web import static
	import orbited.system
	import orbited.start
	
	orbited.start.logger = logging.get_logger('orbited.start')
	
	root = site.resource
	root.putChild('system', orbited.system.SystemResource())
	
	orbited.start._setup_protocols(root)
	orbited.start._setup_static(root, config.map)

def setupClientService():
	
	from twisted.web import resource, server, static

	index_path = os.path.join("pygowave_client", "tmp", "debug", "build", "static", "pygowave_client", "en", "current", "index.html")
	if not os.path.exists(index_path):
		raise RuntimeError("PyGoWave Client Runtime files not found, make sure you have run sc-build in pygowave_client!")

	root = resource.Resource()
	root.putChild('static', static.File(os.path.join("pygowave_client", "tmp", "debug", "build", "static")))
	root.putChild('', static.File(index_path))
	
	return server.Site(root)

application = service.Application("PyGoWave Web Client")

# attach the service to its parent application
pygo_srv = setupClientService()
addOrbitedService(pygo_srv)

srv = internet.TCPServer(4020, pygo_srv)
srv.setServiceParent(application)
