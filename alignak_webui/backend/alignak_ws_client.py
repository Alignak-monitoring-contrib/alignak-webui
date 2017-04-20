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

        def __init__(self, alignak_endpoint='http://127.0.0.1:8888', authenticated=True):
            if alignak_endpoint.endswith('/'):
                self.alignak_endpoint = alignak_endpoint[0:-1]
            else:
                self.alignak_endpoint = alignak_endpoint
            self.token = None
            self.connected = False
            self.authenticated = authenticated

        def login(self, username, password=None):
            """Log in to the Web Services

            If username and password are provided, use the WS login function to authenticate the
            user

            Else, if password is not provided, store the token that will be used
            in the HTTP authentication
            """

            logger.info("login, connection requested, login: %s", username)
            if not self.authenticated:
                self.connected = True
                logger.warning("Alignak WS, no authentication configured, login: %s", username)
                return True

            self.connected = False

            if not password:
                # Set authentication token (no login request).
                logger.debug("Update Web service token")
                self.token = username
                self.connected = True
                return self.connected

            try:
                # WS login
                logger.info("Requesting Web Service authentication, username: %s", username)
                headers = {'Content-Type': 'application/json'}
                params = {'username': username, 'password': password}
                response = requests.post(urljoin(self.alignak_endpoint, 'login'),
                                         json=params, headers=headers)
                resp = response.json()
                self.token = resp['_result'][0]
            except RequestsConnectionError as exp:
                message = "configured Web service connection failed with " \
                          "provided login information: %s (%s)" % (self.alignak_endpoint, username)
                logger.warning(message)
                logger.debug("Exception: %s", str(exp))
                return False
            except Exception as exp:  # pragma: no cover, should not happen
                logger.exception("WS user login exception: %s", exp)

            logger.info("login result: %s", self.connected)
            return self.connected

        def logout(self):

            """Log out from the WS

            Do nothing except setting 'connected' attribute to False"""

            logger.info("logout")
            self.connected = False
            self.token = None

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

            if self.authenticated and not self.token:
                logger.error("Authentication is required for getting an object.")
                raise AlignakWSException(1001, "Access denied, please login before trying to get")

            auth = requests.auth.HTTPBasicAuth(self.token, '')

            try:
                logger.info("get, endpoint: %s, parameters: %s",
                            urljoin(self.alignak_endpoint, endpoint), params)
                if self.authenticated:
                    response = requests.get(urljoin(self.alignak_endpoint, endpoint),
                                            params=params, auth=auth)
                else:
                    response = requests.get(urljoin(self.alignak_endpoint, endpoint),
                                            params=params)
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

        def post(self, endpoint, params=None):
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

            if self.authenticated and not self.token:
                logger.error("Authentication is required for posting an object.")
                raise AlignakWSException(1001, "Access denied, please login before trying to post")

            headers = {'Content-Type': 'application/json'}
            params = json.dumps(params)
            auth = requests.auth.HTTPBasicAuth(self.token, '')

            try:
                logger.info("post, endpoint: %s, parameters: %s",
                            urljoin(self.alignak_endpoint, endpoint), params)

                if self.authenticated:
                    response = requests.post(urljoin(self.alignak_endpoint, endpoint),
                                             data=params, headers=headers, auth=auth)
                else:
                    response = requests.post(urljoin(self.alignak_endpoint, endpoint),
                                             data=params, headers=headers)
                response.raise_for_status()

                resp = response.json()
                logger.info("post, response: %s", resp)

            except RequestsConnectionError as exp:
                logger.warning("WS connection error, error: %s", str(exp))
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

    def __new__(cls, backend_endpoint, authenticated):
        if not AlignakConnection.instance:
            AlignakConnection.instance = AlignakConnection.__AlignakConnection(backend_endpoint,
                                                                               authenticated)
        return AlignakConnection.instance
