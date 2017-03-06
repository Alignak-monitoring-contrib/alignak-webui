#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Many functions need to use protected members of a base class
# pylint: disable=protected-access
# Attributes need to be defined in constructor before initialization
# pylint: disable=attribute-defined-outside-init

# Copyright (c) 2015-2017:
#   Frederic Mohier, frederic.mohier@alignak.net
#
# This file is part of (WebUI).
#
# (WebUI) is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# (WebUI) is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with (WebUI).  If not, see <http://www.gnu.org/licenses/>.

"""
    This module contains an Alignek Web services interface class
"""

import json
import logging

import requests
from requests import HTTPError
from requests import ConnectionError as RequestsConnectionError

from future.moves.urllib.parse import urljoin

# Set logger level to INFO, this to allow global application DEBUG logs without being spammed... ;)
# pylint: disable=invalid-name
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class AlignakWSException(Exception):  # pragma: no cover, not used currently

    """Specific exception class.
    This exception provides an error code, an error message and the WS response.

    Defined error codes:

    - 1000: general exception, message contains more information
    - 1001: WS access denied
    - 1002: WS connection timeout
    - 1003: WS uncatched HTTPError
    """

    def __init__(self, code, message, response=None):
        # Call the base class constructor with the parameters it needs
        super(AlignakWSException, self).__init__(message)

        self.code = code
        self.message = message
        self.response = response

    def __str__(self):

        """Exception to String"""

        return "Alignak WS error code %d: %s" % (self.code, self.message)


# pylint: disable=too-few-public-methods
class AlignakConnection(object):  # pragma: no cover, not used currently

    """Singleton design pattern ..."""

    class __AlignakConnection(object):

        """Base class for Alignak Web Services connection"""

        def __init__(self, alignak_endpoint='http://127.0.0.1:8888'):
            if alignak_endpoint.endswith('/'):
                self.alignak_endpoint = alignak_endpoint[0:-1]
            else:
                self.alignak_endpoint = alignak_endpoint
            self.token = None
            self.connected = False

        def login(self, username, password=None):

            """Log in to the Web Services

            # Todo: not yet implemented in the Alignak WS module
            If username and password are provided, use the WS login function to authenticate the
            user"""

            logger.info("login, connection requested, login: %s", username)

            self.connected = False

            if not password:  # pragma: no cover, should not happen
                # Set backend token (no login request).
                logger.debug("Update backend token")
                self.token = username
                self.connected = True
                return self.connected

            try:
                # WS login
                logger.info("Requesting backend authentication, username: %s", username)
                self.connected = self.backend.login(username, password)
            except AlignakWSException:  # pragma: no cover, should not happen
                logger.warning("configured backend is not available!")
            except Exception as exp:  # pragma: no cover, should not happen
                logger.exception("User login exception: %s", exp)

            logger.info("login result: %s", self.connected)
            return self.connected

        def logout(self):

            """Log out from the WS

            Do nothing except setting 'connected' attribute to False"""

            logger.info("logout")
            self.connected = False

        def get(self, endpoint, params=None):

            """Get information from an Alignak WS

            If an error occurs, an AlignakWSException is raised.

            This method builds a response that always contains: _items and _status::

                {
                    u'_items': [
                        ...
                    ],
                    u'_status': u'OK'
                }

            :param endpoint: WS endpoint
            :type endpoint: str
            :param params: list of parameters for the WS
            :type params: list
            :return: list of properties when query item | list of items when get many items
            :rtype: list"""

            if not self.connected:
                self.login('no_login', None)

            if not self.token:
                logger.error("Authentication is required for getting an object.")
                raise AlignakWSException(1001, "Access denied, please login before trying to get")

            try:
                logger.info("get, endpoint: %s, parameters: %s",
                            urljoin(self.alignak_endpoint, endpoint), params)
                response = requests.get(urljoin(self.alignak_endpoint, endpoint), params=params)
                logger.debug("get, response: %s", response)
                response.raise_for_status()

            except RequestsConnectionError as exp:
                logger.exception("Backend connection error, error: %s", exp)
                raise AlignakWSException(1000, "Alignak Web Services connection error")

            except HTTPError as exp:  # pragma: no cover - need specific backend tests
                if exp.response.status_code == 404:
                    raise AlignakWSException(404, 'Not found')

                logger.exception("Backend HTTP error, error: %s", exp)
                raise AlignakWSException(1003, "Backend HTTPError: %s / %s" % (type(exp), str(exp)))

            return response.json()

        def post(self, endpoint, params=None, files=None):

            """Post information to an Alignak WS endpoint

            If an error occurs, an AlignakWSException is raised.

            This method builds a response that always contains: _items and _status::

                {
                    u'_items': [
                        ...
                    ],
                    u'_status': u'OK'
                }

            :param endpoint: WS endpoint
            :type endpoint: str
            :param params: list of parameters for the WS
            :type params: list
            :return: list of properties when query item | list of items when get many items
            :rtype: list"""

            if not self.connected:
                self.login('no_login', None)

            if not self.token:
                logger.error("Authentication is required for posting an object.")
                raise AlignakWSException(1001, "Access denied, please login before trying to post")

            headers = {'Content-Type': 'application/json'}
            if isinstance(params, dict):
                params = json.dumps(params)
            if files:
                logger.info("post, request to post a %s with files: %s", endpoint, files)
                # Set header to disable client default behavior
                headers = {'Content-type': 'multipart/form-data'}

            try:
                logger.info("post, endpoint: %s, parameters: %s",
                            urljoin(self.alignak_endpoint, endpoint), params)

                if not files:
                    response = requests.post(
                        urljoin(self.alignak_endpoint, endpoint),
                        data=params,
                        files=files,
                        headers=headers
                    )
                    resp = response.json()
                else:
                    # Posting files is not yet used, but reserved for future use...
                    response = requests.post(
                        urljoin(self.alignak_endpoint, endpoint),
                        data=params,
                        files=files
                    )
                    resp = json.loads(response.content)
                logger.info("post, response: %s", resp)

                response.raise_for_status()

            except RequestsConnectionError as exp:
                logger.exception("WS connection error, error: %s", exp)
                raise AlignakWSException(1000, "Alignak Web Services connection error")

            except HTTPError as exp:  # pragma: no cover - need specific backend tests
                if exp.response.status_code == 404:
                    raise AlignakWSException(404, 'Not found')

                logger.exception("WS HTTP error, error: %s", exp)
                raise AlignakWSException(1003, "Backend HTTPError: %s / %s" % (type(exp), str(exp)))

            except Exception as exp:
                logger.exception("WS exception, error: %s", exp)
                raise AlignakWSException(1000, "Alignak Web Services connection error")

            return response.json()

    instance = None

    def __new__(cls, backend_endpoint):
        if not AlignakConnection.instance:
            AlignakConnection.instance = AlignakConnection.__AlignakConnection(backend_endpoint)
        return AlignakConnection.instance
