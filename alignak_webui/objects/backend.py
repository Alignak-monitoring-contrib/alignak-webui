#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Many functions need to use protected members of a base class
# pylint: disable=protected-access
# Attributes need to be defined in constructor before initialization
# pylint: disable=attribute-defined-outside-init

# Copyright (c) 2015-2016:
#   Frederic Mohier, frederic.mohier@gmail.com
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
    This module contains the classes used to manage the objects backend.
"""

import json
import traceback
from logging import getLogger, DEBUG, INFO

from alignak_backend_client.client import Backend, BackendException
from alignak_backend_client.client import BACKEND_PAGINATION_LIMIT, BACKEND_PAGINATION_DEFAULT

# Set logger level to INFO, this to allow global application DEBUG logs without being spammed... ;)
logger = getLogger(__name__)
logger.setLevel(INFO)


class BackendConnection(object):    # pylint: disable=too-few-public-methods
    """
    Singleton design pattern ...
    """
    class __BackendConnection(object):
        """
        Base class for all objects state management (displayed icon, ...)
        """

        def __init__(self, backend_endpoint='http://127.0.0.1:5002'):
            self.backend_endpoint = backend_endpoint
            self.backend = Backend(backend_endpoint)
            self.connected = False

        def login(self, username, password=None):
            """
            Log into the backend

            If password is provided, use the backend login function to authenticate the user

            If no password is provided, the username is assumed to be an authentication token and we
            use the backend connect function.
            """
            logger.info("login, connection requested: %s", username)

            self.connected = False

            if not password:
                # Set backend token (no login request).
                logger.debug("Update backend token")
                self.backend.token = username
                self.connected = True
                return self.connected

            try:
                # Backend real login
                logger.info("Requesting backend authentication, username: %s", username)
                self.connected = self.backend.login(username, password)
            except BackendException as e:  # pragma: no cover, should not happen
                logger.warning("configured backend is not available!")
            except Exception as e:  # pragma: no cover, should not happen
                logger.warning("User login exception: %s", str(e))
                logger.error("traceback: %s", traceback.format_exc())

            logger.info("login result: %s", self.connected)
            return self.connected

        def logout(self):
            """
            Log out from the backend

            Do nothing except setting 'connected' attribute to False
            """
            logger.info("logout")

            self.connected = False

        def count(self, object_type, params=None):
            """
            params is used to 'get' objects from the backend.
            """
            logger.debug("count, %s, params: %s", object_type, params)

            # Update backend search parameters
            if params is None:
                params = {'page': 0, 'max_results': 1}
            if 'where' in params:
                params['where'] = json.dumps(params['where'])
            if 'max_results' not in params:
                params['max_results'] = 1
            logger.debug(
                "count, search in the backend for %s: parameters=%s", object_type, params
            )

            try:
                result = self.backend.get(object_type, params=params)
            except BackendException as e:  # pragma: no cover, simple protection
                logger.warning("get, backend exception: %s", str(e))
                return 0

            logger.debug("count, search result for %s: result=%s", object_type, result)
            if result['_status'] != 'OK':  # pragma: no cover, should not happen
                error = []
                if "content" in result:
                    error.append(result["content"])
                if "_issues" in result:
                    error.append(result["_issues"])
                logger.warning("count, %s: %s, not found: %s", object_type, params, error)
                return 0

            # If more than one element is found, we get an _items list
            if '_items' in result:
                logger.debug("count, found in the backend: %s: %s", object_type, result['_items'])
                return result['_meta']['total']

            logger.debug("count, found one element: %s: %s", object_type, result)
            return 1

        def get(self, object_type, params=None, all_elements=False):
            """
            If params is a string, it is considered to be an object id and params
            is modified to {'_id': params}.

            Else, params is used to 'get' objects from the backend.

            Returns an object or an array of matching objects. All extra attributes
            (_links, _status, _meta, ...) are not returned.

            If all_elements is True, it calls the get_all function of the backend client to
            get all the elements without any pagination activated.
            """
            logger.debug("get, %s, params: %s", object_type, params)

            if isinstance(params, basestring):
                params = {'where': {'_id': params}}
                logger.debug("get, %s, params: %s", object_type, params)

            items = []

            # Update backend search parameters
            if params is None:
                params = {'page': 0, 'max_results': BACKEND_PAGINATION_LIMIT}
            if 'where' in params:
                params['where'] = json.dumps(params['where'])
            if 'embedded' in params:
                params['embedded'] = json.dumps(params['embedded'])
            if 'where' not in params:
                params['where'] = {}
            if 'page' not in params:
                params['page'] = 0
            if 'max_results' not in params:
                params['max_results'] = BACKEND_PAGINATION_LIMIT
            logger.debug(
                "get, search in the backend for %s: parameters=%s", object_type, params
            )

            try:
                if all_elements:
                    result = self.backend.get_all(object_type, params=params)
                else:
                    result = self.backend.get(object_type, params=params)
            except BackendException as e:  # pragma: no cover, simple protection
                logger.warning("get, backend exception: %s", str(e))
                return items

            logger.debug(
                "search, search result for %s: result=%s", object_type, result
            )
            if result['_status'] != 'OK':  # pragma: no cover, should not happen
                error = []
                if "content" in result:
                    error.append(result["content"])
                if "_issues" in result:
                    error.append(result["_issues"])
                logger.warning("get, %s: %s, not found: %s", object_type, params, error)
                raise ValueError(
                    '%s, search: %s was not found in the backend, error: %s' % (
                        object_type, params, error
                    )
                )

            # If more than one element is found, we get an _items list
            if '_items' in result:
                logger.debug("get, found in the backend: %s: %s", object_type, result['_items'])
                return result['_items']

            logger.debug("get, found one in the backend: %s: %s", object_type, result)
            return result

        def post(self, object_type, data=None, files=None):
            """ Add an element """
            logger.info("post, request to add a %s: data: %s", object_type, data)

            # Do not set header to use the client default behavior:
            # - set headers as {'Content-Type': 'application/json'}
            # - encode provided data to JSON
            headers = None
            if files:
                logger.info("post, request to add a %s with files: %s", object_type, files)
                # Set header to disable client default behavior
                headers = {'Content-type': 'multipart/form-data'}

            try:
                result = self.backend.post(object_type, data=data, files=files, headers=headers)
                logger.debug("post, response: %s", result)
                if result['_status'] != 'OK':
                    logger.warning("post, error: %s", result)
                    return None
            except BackendException as e:
                logger.error("post, backend exception: %s", str(e))
                if "response" in e and "_issues" in e.response:
                    logger.error("- issues: %s", e.response['_issues'])
                return None
            except ValueError as e:  # pragma: no cover, should never happen
                logger.warning("post, error: %s", str(e))
                return None

            return result['_id']

        def delete(self, object_type, object_id):
            """
            Delete an element
            - object_type is the element type
            - object_id is the element identifier
            """
            logger.info("delete, request to delete the %s: %s", object_type, object_id)

            try:
                # Get most recent version of the element
                items = self.find_object(object_type, object_id)
                element = items[0]
            except ValueError:  # pragma: no cover, should never happen
                logger.warning("delete, object %s, _id=%s not found", object_type, object_id)
                return False

            try:
                # Request deletion
                headers = {'If-Match': element['_etag']}
                endpoint = '/'.join([object_type, object_id])
                logger.info("delete, endpoint: %s", endpoint)
                result = self.backend.delete(endpoint, headers)
                logger.debug("delete, response: %s", result)
                if result['_status'] != 'OK':  # pragma: no cover, should never happen
                    error = []
                    if "content" in result:
                        error.append(result["content"])
                    if "_issues" in result:
                        error.append(result["_issues"])
                        for issue in result["_issues"]:
                            error.append(result["_issues"][issue])
                    logger.warning("delete, error: %s", error)
                    return False
            except BackendException as e:  # pragma: no cover, should never happen
                logger.error("delete, backend exception: %s", str(e))
                return False
            except ValueError as e:  # pragma: no cover, should never happen
                logger.warning("delete, not found %s: %s", object_type, element)
                return False

            try:
                # Try to get most recent version of the element
                items = self.find_object(object_type, object_id)
            except ValueError:
                logger.info("delete, object deleted: %s, _id=%s", object_type, object_id)
                # Object deletion
                # _delete is the deletion method name... yes, it sounds like a protected member :/
                # pylint: disable=protected-access
                element._delete()

            return True

        def update(self, object_type, object_id, data):
            """
            Update an element
            - object_type is the element type
            - object_id is the element identifier
            """
            logger.info("update, request to update the %s: %s", object_type, object_id)

            try:
                # Get most recent version of the element
                element = self.get('/'.join([object_type, object_id]))
                logger.warning("update, element: %s", element)
            except ValueError:
                logger.warning("update, object %s, _id=%s not found", object_type, object_id)
                return False

            try:
                # Request update
                headers = {'If-Match': element['_etag']}
                endpoint = '/'.join([object_type, object_id])
                logger.info("update, endpoint: %s, data: %s", endpoint, data)
                result = self.backend.patch(endpoint, data, headers)
                logger.debug("update, response: %s", result)
                if result['_status'] != 'OK':  # pragma: no cover, should never happen
                    error = []
                    if "content" in result:
                        error.append(result["content"])
                    if "_issues" in result:
                        error.append(result["_issues"])
                        for issue in result["_issues"]:
                            error.append(result["_issues"][issue])
                    logger.warning("update, error: %s", error)
                    return False
            except BackendException as e:  # pragma: no cover, should never happen
                logger.error("update, backend exception: %s", str(e))
                return False
            except ValueError:  # pragma: no cover, should never happen
                logger.warning("update, not found %s: %s", object_type, element)
                return False

            return True

    instance = None

    def __new__(cls, backend_endpoint):
        if not BackendConnection.instance:
            BackendConnection.instance = BackendConnection.__BackendConnection(backend_endpoint)
        return BackendConnection.instance