#!/usr/bin/python
# -*- coding: utf-8 -*-

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
    This module is a wrapper to connect with the Glpi Web Services backend
"""
import xmlrpclib

from logging import getLogger

# pylint: disable=invalid-name
logger = getLogger(__name__)

# Define pagination limits according to GLPI's ones!
GLPI_PAGINATION_LIMIT = 50
GLPI_PAGINATION_DEFAULT = GLPI_PAGINATION_LIMIT


class GlpiException(Exception):  # pragma: no cover, not used currently

    """Specific backend exception

    Defined error codes:
    - 1000: general exception, message contains more information
    - 1001: backend access denied
    - 1002: backend connection timeout
    - 1003: backend uncatched HTTPError
    - 1004: backend token not provided on login, user is not yet authorized to log in
    - 1005: If-Match header is required for patching an object
    """

    def __init__(self, code, message, response=None):
        """Call the base class constructor with the parameters it needs"""
        super(GlpiException, self).__init__(message)
        self.code = code
        self.message = message
        self.response = response

    def __str__(self):
        """Exception to String"""
        return "Glpi error code %d: %s" % (self.code, self.message)


class Glpi(object):  # pragma: no cover, not used currently

    """Glpi class to communicate with alignak-backend"""

    def __init__(self, endpoint):
        """Alignak backend

        :param endpoint: root endpoint (API URL)
        :type endpoint: str
        """

        self.connection = None
        self.authenticated = False
        if endpoint.endswith('/'):  # pragma: no cover - test url is complying ...
            self.url_endpoint_root = endpoint[0:-1]
        else:
            self.url_endpoint_root = endpoint
        self.token = None

    def login(self, username, password):

        """Log into the backend and get the token

        if login is:
        - accepted, returns True
        - refused, returns False

        In case of any error, raises a GlpiException

        :param username: login name
        :type username: str
        :param password: password
        :type password: str
        :return: return True if authentication is successfull, otherwise False
        :rtype: bool
        """

        logger.info("request backend authentication for: %s", username)

        if username is None or password is None:
            raise GlpiException(1001, "Missing mandatory parameters")

        self.authenticated = False
        self.token = None

        try:
            logger.info("connecting to %s", self.url_endpoint_root)
            self.connection = xmlrpclib.ServerProxy(self.url_endpoint_root)
        except Exception as exp:  # pragma: no cover - security ...
            self.connection = None
            logger.exception("Glpi connection exception, error: %s / %s", type(exp), exp)
            raise GlpiException(1000, "Glpi exception: %s / %s" % (type(exp), str(exp)))

        try:
            logger.info("authentication in progress...")
            args = {'login_name': username, 'login_password': password, 'iso8859': True}
            method = getattr(self.connection, 'glpi.doLogin')
            resp = method(args)
            self.token = resp['session']
            self.authenticated = True
            logger.info("authenticated, session : %s", str(self.token))
        except xmlrpclib.Fault as err:
            self.connection = None
            logger.error("XMLRPC error: %d / %s", err.faultCode, err.faultString)
            if isinstance(err.faultString, unicode):
                err.faultString = err.faultString.encode('utf-8')
            raise GlpiException(1001, err.faultString)
        except Exception as exp:  # pragma: no cover - security ...
            self.connection = None
            logger.exception("Glpi connection exception, error: %s / %s", type(exp), exp)
            raise GlpiException(1001, "Access denied")

        return self.authenticated

    def logout(self):

        """Logout from the backend

        :return: return True if logout is successfull, otherwise False
        :rtype: bool
        """

        if not self.token or not self.authenticated:
            logger.warning("Unnecessary logout ...")
            return True

        logger.info("request backend logout")

        try:
            logger.info("logout in progress...")
            args = {'session': self.token}
            self.connection.glpi.doLogout(args)
            logger.info("logged out")
        except xmlrpclib.Fault as err:  # pragma: no cover - should not happen
            logger.error("XMLRPC error: %d / %s", err.faultCode, err.faultString)
            if isinstance(err.faultString, unicode):
                err.faultString = err.faultString.encode('utf-8')
            raise GlpiException(1001, err.faultString)
        except Exception as exp:  # pragma: no cover - security ...
            logger.exception("Glpi connection exception, error: %s / %s", type(exp), exp)
            raise GlpiException(1000, "Glpi exception: %s / %s" % (type(exp), str(exp)))

        self.connection = None
        self.authenticated = False
        self.token = None

        return True

    def method_call(self, method_name, parameters=None):

        """Call the XML RPC method

        :param parameters: list of parameters for the backend API
        :param method_name: RPC method name
        :return: list of properties when query item | list of items when get many items
        :rtype: list
        """

        if not self.token:
            logger.error("Authentication is required for getting an object.")
            raise GlpiException(
                1001,
                "Access denied, please login before calling any method."
            )

        logger.info("methodCall: %s", method_name)

        resp = None
        try:
            method = getattr(self.connection, method_name)
            if not parameters:
                parameters = {}
            parameters.update({
                "session": self.token,
                "iso8859": True,
                "id2name": True
            })
            logger.info("methodCall: %s (%s)", method_name, parameters)
            resp = method(parameters)
            logger.debug("methodCall: %s: %s", method_name, resp)
        except xmlrpclib.Fault as err:  # pragma: no cover - should not happen
            logger.error("XMLRPC error: %d / %s", err.faultCode, err.faultString)
            if isinstance(err.faultString, unicode):
                err.faultString = err.faultString.encode('utf-8')
            raise GlpiException(1001, "methodCall: %s: %s" % (method_name, err.faultString))
        except Exception as exp:  # pragma: no cover - security ...
            logger.exception("Glpi connection exception, error: %s / %s", type(exp), exp)
            raise GlpiException(1000, "Glpi exception: %s / %s" % (type(exp), str(exp)))

        return resp
