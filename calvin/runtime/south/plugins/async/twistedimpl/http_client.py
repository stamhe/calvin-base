# -*- coding: utf-8 -*-

# Copyright (c) 2015 Ericsson AB
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

# from twisted.internet.task import react
from twisted.internet import reactor
from twisted.web.client import Agent, readBody
from twisted.web.http_headers import Headers
from twisted.internet.ssl import ClientContextFactory

from urllib import urlencode

# from calvin.utilities.calvinlogger import get_logger
from calvin.utilities.calvin_callback import CalvinCBClass

# _log = get_logger(__name__)


class HTTPRequest(object):
    def __init__(self, handle):
        self._response = {}
        self._handle = handle

    def parse_headers(self, response):
        self._response = {}
        self._response['version'] = "%s/%d.%d" % (response.version)
        self._response['status'] = response.code
        self._response['phrase'] = response.phrase
        self._response['headers'] = {}
        for hdr, val in response.headers.getAllRawHeaders():
            self._response['headers'][hdr.lower()] = val[0] if isinstance(val, list) and len(val) > 0 else val

    def parse_body(self, body):
        self._response['body'] = body

    def body(self):
        return self._response.get('body', None)

    def headers(self):
        return self._response.get('headers', None)

    def status(self):
        return self._response.get('status', None)

    def version(self):
        return self._response.get('version', None)

    def phrase(self):
        return self._response.get('phrase', None)

    def handle(self):
        return self._handle


class HTTPClient(CalvinCBClass):

    class WebClientContextFactory(ClientContextFactory):
        """TODO: enable certificate verification, hostname checking"""
        def getContext(self, hostname, port):
            return ClientContextFactory.getContext(self)

    def __init__(self, callbacks=None):
        super(HTTPClient, self).__init__(callbacks)
        self._agent = Agent(reactor, self.WebClientContextFactory())

    def _receive_headers(self, response, request):
        request.parse_headers(response)
        self._callback_execute('receive-headers', request)
        deferred = readBody(response)
        deferred.addCallback(self._receive_body, request)

    def _receive_body(self, response, request):
        request.parse_body(response)
        self._callback_execute('receive-body', request)

    def get(self, url, params=None, headers=None, handle=None):
        if params:
            params = "?" + urlencode(params)
        else:
            params = ""
        url += params

        twisted_headers = Headers()
        for k, v in headers.items():
            key = k.encode('ascii', 'ignore')
            val = v.encode('ascii', 'ignore')
            twisted_headers.addRawHeader(key, val)

        deferred = self._agent.request('GET', url, twisted_headers)
        request = HTTPRequest(handle)
        deferred.addCallback(self._receive_headers, request)
        return request
