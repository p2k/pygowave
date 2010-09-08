
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

class PyGoWaveMessageProcessor(object):
	def purge_connections(self):
		pass
	
	def log_stats(self):
		pass
	
	def process(self, rkey, message_data):
		return {}
