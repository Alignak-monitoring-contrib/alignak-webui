#!/usr/bin/python
# -*- coding: utf-8 -*-
# Yes, but that's how it is made, and it suits ;)
# pylint: disable=too-many-public-methods

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
    Application data manager
"""

import re
import json
import time
import traceback
from urlparse import urljoin
from datetime import datetime
from logging import getLogger, INFO

from alignak_backend_client.client import BackendException
# from alignak_backend_client.client import BACKEND_PAGINATION_LIMIT, BACKEND_PAGINATION_DEFAULT

# Import the backend interface class
from alignak_webui.objects.backend import BackendConnection

# Import all objects we will need
from alignak_webui.objects.item import Item
from alignak_webui.objects.item import Command, Realm, TimePeriod
from alignak_webui.objects.item import LiveState, LiveSynthesis, Log, History
from alignak_webui.objects.item import UIPref, User, Host, Service
from alignak_webui.objects.item import UserGroup, HostGroup, ServiceGroup
from alignak_webui.objects.item import ActionAcknowledge, ActionDowntime, ActionForceCheck


# Set logger level to INFO, this to allow global application DEBUG logs without being spammed... ;)
logger = getLogger(__name__)
# logger.setLevel(INFO)


class DataManager(object):
    """
    Base class for all data manager objects
    """
    id = 1

    """
        Application data manager object
    """

    def __init__(self, backend_endpoint='http://127.0.0.1:5000'):
        """
        Create an instance
        """
        # Set a unique id for each DM object
        self.__class__.id += 1

        # Associated backend object
        self.backend_endpoint = backend_endpoint
        # self.backend = Backend(backend_endpoint)
        self.backend = BackendConnection(backend_endpoint)

        # Get known objects type from the imported modules
        # Search for classes including an _type attribute
        self.known_classes = []
        for k, dummy in globals().items():
            if isinstance(globals()[k], type) and \
               '_type' in globals()[k].__dict__ and \
               globals()[k].getType() is not None and \
               globals()[k].getType() is not 'item':
                self.known_classes.append(globals()[k])
                logger.debug(
                    "Known class %s for object type: %s",
                    globals()[k], globals()[k].getType()
                )

        self.connected = False
        self.logged_in_user = None
        self.connection_message = None
        self.loading = 0
        self.loaded = False

        self.refresh_required = False
        self.refresh_done = False

        self.updated = datetime.utcnow()

    def __repr__(self):
        return ("<DM, id: %s, objects count: %d, user: %s, updated: %s>") % (
            self.id,
            self.get_objects_count(),
            self.get_logged_user().get_username() if self.get_logged_user() else 'Not logged in',
            self.updated
        )

    ##
    # Connected user
    ##
    def user_login(self, username, password=None, load=True):
        """
        Set the data manager user

        If password is provided, use the backend login function to authenticate the user

        If no password is provided, the username is assumed to be an authentication token and we
        use the backend connect function.
        """
        logger.info("user_login, connection requested: %s, load: %s", username, load)

        self.connected = False
        self.connection_message = _('Backend connecting...')
        try:
            # Backend login
            logger.info("Requesting backend authentication, username: %s", username)
            self.connected = self.backend.login(username, password)
            if self.connected:
                self.connection_message = _('Connection successful')

                # Set the backend to use by the data manager objects
                Item().setBackend(self.backend)
                Item().setKnownClasses(self.known_classes)

                # Fetch the logged-in user
                if password:
                    users = self.backend.get(
                        'user', {'max_results': 1, 'where': {'name': username}}
                    )
                else:
                    users = self.backend.get(
                        'user', {'max_results': 1, 'where': {'token': username}}
                    )
                self.logged_in_user = User(users[0])
                # Tag user as authenticated
                self.logged_in_user.authenticated = True
                logger.info("Logged-in user: %s", self.logged_in_user)

                # Get total objects count from the backend
                self.get_objects_count(refresh=True, log=False)

                # Load data if load required...
                if load:
                    self.load(reset=True)
            else:
                self.connection_message = _('Backend connection refused...')
        except BackendException as e:  # pragma: no cover, should not happen
            logger.warning("configured backend is not available!")
            self.connection_message = e.message
        except Exception as e:  # pragma: no cover, should not happen
            logger.warning("User login exception: %s", str(e))
            logger.error("traceback: %s", traceback.format_exc())

        logger.info("user_login, connection message: %s", self.connection_message)
        return self.connected

    def user_logout(self):
        """
        Logout the data manager user. Do not log-out from the backend. Need to reset the
        datamanager to do it.
        """
        self.logged_in_user = None

    def get_logged_user(self):
        """
        Get the current logged in user
        """
        return self.logged_in_user

    ##
    # Find objects and load objects cache
    ##
    def find_object(self, object_type, params=None, all_elements=False):
        """
        Find an object ...

        Search in internal objects cache for an object matching the required parameters

        If params is a string, it is considered to be an object id and params
        is modified to {'_id': params}.

        Else, params is a dictionary of key/value to find a matching object in the objects cache
        If no objects are found in the cache, params is user to 'get' objects from the backend.

        Default behavior is to search in the backend if objects are not found in the cache. Call
        with backend=False to search only in local cache.

        If the backend search is successful, a new object is created if it exists a class in the
        imported modules (presumably alignak_webui.objects.item) which contains a 'bo_type' property
        and this property is valued as 'object_type'.

        Returns an array of matching objects
        """
        logger.debug("find_object, %s, params: %s", object_type, params)

        if isinstance(params, basestring):
            params = {'where': {'_id': params}}
            logger.debug("find_object, %s, params: %s", object_type, params)

        items = []

        result = self.backend.get(object_type, params, all_elements)
        logger.debug("find_object, found: %s: %s", object_type, result)

        if not result:
            raise ValueError(
                '%s, search: %s was not found in the backend' % (object_type, params)
            )

        for item in result:
            # Find "Backend object type" classes in file imported modules ...
            object_class = [kc for kc in self.known_classes if kc.getType() == object_type][0]

            # Create a new object
            logger.debug("find_object, begin creation")
            bo_object = object_class(item)
            items.append(bo_object)
            self.updated = datetime.utcnow()
            logger.debug("find_object, created: %s", bo_object)

            # Update class _total_count (each item got from backend has an _total field)
            if '_total' in item:
                object_class.setTotalCount(item['_total'])

        return items

    def load(self, reset=False, refresh=False):
        """
            Load data in the data manager objects

            If reset is set, then all the existing objects are deleted and then created from
            scratch (first load ...). Else, existing objects are updated and new objects are
            created.

            Get all the users (related to current logged-in user)

            :returns: the number of newly created objects
        """
        if not self.get_logged_user():
            logger.error("load, must be logged-in before loading")
            return False

        if self.loading > 0:  # pragma: no cover, protection if application shuts down ...
            logger.error("load, already loading: trial: %d", self.loading)
            if self.loading < 3:
                self.loading += 1
                return False
            logger.error("load, already loading: reset counter")
            self.loading = 0

        logger.debug("load, start loading: %s for %s", self, self.get_logged_user())
        logger.debug(
            "load, start as administrator: %s", self.get_logged_user().is_administrator()
        )
        start = time.time()

        if reset:
            logger.warning("Objects cache reset")
            self.reset(logout=False)

        self.loading += 1
        self.loaded = False

        # Get internal objects count
        objects_count = self.get_objects_count()
        logger.debug("Load, start, objects in cache: %d", objects_count)

        # -----------------------------------------------------------------------------------------
        # Get all realms
        # -----------------------------------------------------------------------------------------
        self.get_realms()

        # -----------------------------------------------------------------------------------------
        # Get all users if current user is an administrator
        # -----------------------------------------------------------------------------------------
        self.get_users()

        # -----------------------------------------------------------------------------------------
        # Get all timeperiods
        # -----------------------------------------------------------------------------------------
        self.get_timeperiods()

        # -----------------------------------------------------------------------------------------
        # Get all commands
        # -----------------------------------------------------------------------------------------
        self.get_commands()

        # -----------------------------------------------------------------------------------------
        # Get livestate (livestate which embeds host and services definition)
        # -----------------------------------------------------------------------------------------
        # self.get_livestate()

        # Get internal objects count
        new_objects_count = self.get_objects_count()
        logger.debug("Load, end, objects in cache: %d", new_objects_count)

        logger.warning(
            "Data manager load (%s), new objects: %d,  duration: %s",
            refresh, new_objects_count - objects_count, (time.time() - start)
        )

        if new_objects_count > objects_count:
            self.require_refresh()

        self.loaded = True
        self.loading = 0
        return new_objects_count - objects_count

    def reset(self, logout=False):
        """
        Reset data in the data manager objects
        """
        logger.info("Data manager reset...")

        # Clean internal objects cache
        for known_class in self.known_classes:
            logger.info("Cleaning %s cache...", known_class.getType())
            known_class.cleanCache()

        if logout:
            self.backend.logout()
            self.user_logout()

        self.loaded = False
        self.loading = 0
        self.refresh_required = True

    def require_refresh(self):
        """
        Require an immediate refresh
        """
        self.refresh_required = True
        self.refresh_done = False

    def get_objects_count(self, object_type=None, refresh=False, log=False, search=None):
        """
        Get the count of the objects stored in the data manager cache

        If an object_type is specified, only returns the count for this object type

        If refresh is True, get the total count from the backend. This is only useful if total
        count is required...

        If log is set, an information log is made
        """
        log_function = logger.debug
        if log:
            log_function = logger.info

        if object_type:
            for known_class in self.known_classes:
                if object_type == known_class.getType():
                    objects_count = known_class.getCount()
                    log_function(
                        "get_objects_count, currently %d cached %ss",
                        objects_count, object_type
                    )
                    if refresh:
                        if hasattr(known_class, '_total_count') and \
                           known_class.getTotalCount() != -1:
                            objects_count = known_class.getTotalCount()
                            log_function(
                                "get_objects_count, got _total_count attribute: %d",
                                objects_count
                            )
                        else:
                            objects_count = self.count_objects(object_type, search=search)
                            # _total_count is a property ... should make it a method?
                            # pylint: disable=protected-access
                            known_class._total_count = objects_count

                        log_function(
                            "get_objects_count, currently %d total %ss for %s",
                            objects_count, object_type, search
                        )
                    return objects_count
            else:  # pragma: no cover, should not happen
                # pylint: disable=useless-else-on-loop
                logger.warning("count_objects, unknown object type: %s", object_type)
                return 0

        objects_count = 0
        for known_class in self.known_classes:
            count = known_class.getCount()
            log_function(
                "get_objects_count, currently %d cached %ss",
                count, known_class.getType()
            )
            if refresh:
                count = self.count_objects(known_class.getType(), search=search)
                if search:
                    log_function(
                        "get_objects_count, currently %d total %ss for %s",
                        count, known_class.getType(), search
                    )
                else:
                    log_function(
                        "get_objects_count, currently %d total %ss",
                        count, known_class.getType()
                    )
            objects_count += count

        log_function("get_objects_count, currently %d elements", objects_count)
        return objects_count

    ##
    #
    # Elements add, delete, update, ...
    ##
    def count_objects(self, object_type, search=None):
        """
        Request objects from the backend to pick-up total records count.
        Make a simple request for 1 element and we will get back the total count of elements

        search is a dictionary of key / value to search for
        """
        params = {
            'page': 0, 'max_results': 1
        }
        if search is not None:
            params['where'] = search

        return self.backend.count(object_type, params)

    def add_object(self, object_type, data=None, files=None):
        """ Add an element """
        logger.info("add_object, request to add a %s: data: %s", object_type, data)

        object_id = self.backend.post(object_type, data=data, files=files)
        if object_id:
            items = self.find_object(object_type, object_id)
            return items[0]['_id']
        return None

    def delete_object(self, object_type, element):
        """
        Delete an element
        - object_type is the element type
        - element may be a string. In this case it is considered to be the element id
        """
        logger.info("delete_object, request to delete the %s: %s", object_type, element)

        if isinstance(element, basestring):
            object_id = element
        else:
            object_id = element.id

        if self.backend.delete(object_type, object_id):
            # Find object type class...
            object_class = [kc for kc in self.known_classes if kc.getType() == object_type][0]

            # Delete existing cache object
            if object_id in object_class.getCache():
                del object_class.getCache()[object_id]

        return True

    def update_object(self, object_type, element, data):
        """
        Update an element
        - object_type is the element type
        - element may be a string. In this case it is considered to be the element id
        """
        logger.info("update_object, request to update the %s: %s", object_type, element)

        if isinstance(element, basestring):
            object_id = element
        else:
            object_id = element.id

        if self.backend.update(object_type, object_id, data):
            items = self.find_object(object_type, object_id)
            logger.info("update_object, updated: %s", items[0])
            return True

        return False

    ##
    # User's preferences
    ##
    def delete_user_preferences(self, user, prefs_type):
        """
        Delete user's preferences

        If the data are not found, returns None else return the backend response.

        An exception is raised if an error occurs, else returns the backend response

        :param user: username
        :type user: string
        :param prefs_type: preference type
        :type prefs_type: string
        :return: server's response
        :rtype: dict
        """
        try:
            logger.debug(
                "delete_user_preferences, type: %s, for: %s",
                prefs_type, user
            )

            # Still existing ...
            result = self.backend.get(
                'uipref',
                params={'where': {"type": prefs_type, "user": user}}
            )
            logger.debug("delete_user_preferences, '%s' result: %s", prefs_type, result)
            if result:
                item = result[0]
                logger.debug(
                    "delete_user_preferences, delete an exising record: %s / %s (%s)",
                    prefs_type, user, item['_id']
                )
                # Delete existing record ...
                return self.delete_object('uipref', item['_id'])

            return False
        except Exception as e:  # pragma: no cover - need specific backend tests
            logger.error("delete_user_preferences, exception: %s", str(e))
            logger.error("traceback: %s", traceback.format_exc())
            raise e

        return False

    def set_user_preferences(self, user, prefs_type, value):
        """
        Set user's preferences

        If an exception occurs, it is raised to the caller.

        This function returns True if the data were stored, else False if a problem was encountered.

        **Note**: When a simple value is stored (value parameter is not a dictionary), it is
        it is stored in a dictionary containing a 'value' property.

        :param user: username
        :type user: string
        :param prefs_type: preference type
        :type prefs_type: string
        :param value: value of the parameter to store
        :type value: dict
        :return: True / False
        :rtype: boolean
        """
        try:
            response = None

            logger.debug(
                "set_user_preferences, type: %s, for: %s",
                prefs_type, user
            )

            # Saved parameter must be a dictionary. Create a fake dictionary
            if not isinstance(value, dict):
                value = {'value': value}

            # First, get to check if it exists
            result = self.backend.get(
                'uipref',
                params={'where': {"type": prefs_type, "user": user}}
            )
            if result:
                object_id = result[0]['_id']

                # Update existing record ...
                logger.debug(
                    "set_user_preferences, update existing record: %s / %s (_id=%s)",
                    prefs_type, user, object_id
                )
                data = {
                    "user": user,
                    "type": prefs_type,
                    "data": value
                }
                response = self.backend.update('uipref', object_id, data=data)
            else:
                # Create new record ...
                logger.debug(
                    "set_user_preferences, create new record: %s / %s",
                    prefs_type, user
                )
                data = {
                    "user": user,
                    "type": prefs_type,
                    "data": value
                }
                response = self.backend.post('uipref', data=data)
            logger.debug("set_user_preferences, response: %s", response)
            return response

        except Exception as e:  # pragma: no cover - should not happen
            logger.error("set_user_preferences, exception: %s", str(e))
            logger.error("traceback: %s", traceback.format_exc())
            return False

        return True

    def get_user_preferences(self, user, prefs_type, default=None):
        """
        Get user's preferences

        If the data are not found, and no default value is provided, this function returns None. If
        a default value is provided then this function returns the defaut value after having stored
        it in the user's preferendes.

        If prefs_type is None then this function returns all the user stored preferences.
        If user is None then all the preferences are returned.

        **Note**: When a simple value is stored with set_user_preferences, it is never returned as
        a simple value but in a dictionary containing a 'value' property.

        :param user: username
        :type user: string
        :param prefs_type: preference type
        :type prefs_type: string
        :return: found data, or None
        :rtype: dict
        """
        try:
            logger.debug("get_user_preferences, type: %s, for: %s", prefs_type, user)

            # All the preferences
            if user is None:
                return self.backend.get(
                    'uipref', params={}, all_elements=True
                )

            # All the user preferences
            if prefs_type is None:
                return self.backend.get(
                    'uipref', params={'where': {"user": user}}, all_elements=True
                )

            # Get required preference
            result = self.backend.get(
                'uipref',
                params={'where': {"type": prefs_type, "user": user}}
            )
            # logger.debug("get_user_preferences, '%s' result: %s", prefs_type, result)
            if result:
                # logger.debug("get_user_preferences, found: %s", result)
                return result[0]['data']

        except Exception as e:  # pragma: no cover - should never happen
            logger.error("get_user_preferences, exception: %s", str(e))
            logger.error("traceback: %s", traceback.format_exc())
            return None

        logger.debug("get_user_preferences, not found, default value: %s", default)
        if default is not None and self.set_user_preferences(user, prefs_type, default):
            # No default value...
            return self.get_user_preferences(user, prefs_type)

        return None

    ##
    # Livestate
    ##
    def get_livestate(self, search=None):
        """ Get livestate for all elements

            Elements in the livestate which type is 'host' or 'service'

            :param search: backend request search
            :type search: dic
            :return: list of hosts/services live states
            :rtype: list
        """
        if not search:
            search = {}
        if "sort" not in search:
            search.update({'sort': '-business_impact,-state_id'})
        if 'embedded' not in search:
            search.update({'embedded': {'host': 1, 'service': 1}})

        try:
            logger.info("get_livestate, search: %s", search)
            items = self.find_object('livestate', search)
            logger.info("get_livestate, got: %d elements, %s", len(items), items)
            return items
        except ValueError:
            logger.debug("get_livestate, none found")

    def get_livestate_hosts(self, search=None):
        """ Get livestate for hosts

            Elements in the livestate which type is 'host'

            :param search: backend request search
            :type search: dic
            :param all_elements: get all elements (True) or apply default pagination
            :type all_elements: bool
            :return: list of hosts live states
            :rtype: list
        """
        if not search:
            search = {}
        if "sort" not in search:
            search.update({'sort': '-business_impact,-state_id'})
        if 'embedded' not in search:
            search.update({'embedded': {'host': 1}})
        if 'where' in search:
            search['where'].update({'type': 'host'})

        try:
            logger.info("get_livestate_hosts, search: %s", search)
            items = self.find_object('livestate', search)
            logger.info("get_livestate_hosts, got: %d elements, %s", len(items), items)
            return items
        except ValueError:  # pragma: no cover - should not happen
            logger.debug("get_livestate_hosts, none found")

    def get_livestate_host(self, search):
        """ Get a host livestate """

        if isinstance(search, basestring):
            search = {'max_results': 1, 'where': {'_id': search}}
        elif 'max_results' not in search:
            search.update({'max_results': 1})

        items = self.get_livestate_hosts(search=search)
        return items[0] if items else None

    def get_livestate_services(self, search=None):
        """ Get livestate for services

            Elements in the livestat which service is not null (eg. services)

            :param search: backend request search
            :type search: dic
            :param all_elements: get all elements (True) or apply default pagination
            :type all_elements: bool
            :return: list of services live states
            :rtype: list
        """
        if not search:
            search = {}
        if "sort" not in search:
            search.update({'sort': '-business_impact,-state_id'})
        if 'embedded' not in search:
            search.update({'embedded': {'service': 1}})
        if 'where' in search:
            search['where'].update({'type': 'service'})

        try:
            logger.info("get_livestate_services, search: %s", search)
            items = self.find_object('livestate', search)
            logger.info("get_livestate_services, got: %d elements, %s", len(items), items)
            return items
        except ValueError:
            logger.debug("get_livestate_services, none found")

    def get_livestate_service(self, search):
        """ Get a service livestate """

        if isinstance(search, basestring):
            search = {'max_results': 1, 'where': {'_id': search}}
        elif 'max_results' not in search:
            search.update({'max_results': 1})

        items = self.get_livestate_services(search=search)
        return items[0] if items else None

    def get_livesynthesis(self, search=None):
        """ Get livestate synthesis for hosts and services

            Example backend response::

                {
                    'services_total': 89,
                    'services_business_impact': 0,
                    'services_ok_hard': 8,
                    'services_ok_soft': 0,
                    'services_warning_hard': 0,
                    'services_warning_soft': 0,
                    'services_critical_hard': 83,
                    'services_critical_soft': -23,
                    'services_unknown_hard': 24,
                    'services_unknown_soft': -3,
                    'services_acknowledged': 0,
                    'services_flapping': 0,
                    'services_in_downtime': 0,

                    'hosts_total': 13,
                    'hosts_business_impact': 0,
                    'hosts_up_hard': 3,
                    'hosts_up_soft': 0,
                    'hosts_down_hard': 14,
                    'hosts_down_soft': -4,
                    'hosts_unreachable_hard': 0,
                    'hosts_unreachable_soft': 0,
                    'hosts_acknowledged': 0,
                    'hosts_flapping': 0,
                    'hosts_in_downtime': 0,

                    ... / ...
                }

            Returns an hosts_synthesis dictionary containing:
            - number of elements
            - business impact
            - count for each state (hard and soft)
            - percentage for each state (hard and soft)
            - number of problems (down and unreachable, only hard state)
            - percentage of problems

            Returns a services_synthesis dictionary containing:
            - number of elements
            - business impact
            - count for each state (hard and soft)
            - percentage for each state (hard and soft)
            - number of problems (down and unreachable, only hard state)
            - percentage of problems

            :return: hosts and services live state synthesis in a dictionary
            :rtype: dict
        """
        if not search:
            search = {}

        default_ls = {
            'hosts_synthesis': {
                'nb_elts': 0,
                'business_impact': 0,

                'warning_threshold': 2.0, 'global_warning_threshold': 2.0,
                'critical_threshold': 5.0, 'global_critical_threshold': 5.0,

                'nb_up': 0, 'pct_up': 100.0,
                'nb_up_hard': 0, 'nb_up_soft': 0,
                'nb_down': 0, 'pct_down': 0.0,
                'nb_down_hard': 0, 'nb_down_soft': 0,
                'nb_unreachable': 0, 'pct_unreachable': 0.0,
                'nb_unreachable_hard': 0, 'nb_unreachable_soft': 0,

                'nb_problems': 0, 'pct_problems': 0.0,
                'nb_flapping': 0, 'pct_flapping': 0.0,
                'nb_acknowledged': 0, 'pct_acknowledged': 0.0,
                'nb_in_downtime': 0, 'pct_in_downtime': 0.0,
            },
            'services_synthesis': {
                'nb_elts': 0,
                'business_impact': 0,

                'warning_threshold': 2.0, 'global_warning_threshold': 2.0,
                'critical_threshold': 5.0, 'global_critical_threshold': 5.0,

                'nb_ok': 0, 'pct_ok': 100.0,
                'nb_ok_hard': 0, 'nb_ok_soft': 0,
                'nb_warning': 0, 'pct_warning': 0.0,
                'nb_warning_hard': 0, 'nb_warning_soft': 0,
                'nb_critical': 0, 'pct_critical': 0.0,
                'nb_critical_hard': 0, 'nb_critical_soft': 0,
                'nb_unknown': 0, 'pct_unknown': 0.0,
                'nb_unknown_hard': 0, 'nb_unknown_soft': 0,

                'nb_problems': 0, 'pct_problems': 0.0,
                'nb_flapping': 0, 'pct_flapping': 0.0,
                'nb_acknowledged': 0, 'pct_acknowledged': 0.0,
                'nb_in_downtime': 0, 'pct_in_downtime': 0.0
            }
        }

        try:
            logger.debug("get_livesynthesis, search: %s", search)
            items = self.find_object('livesynthesis', search)
            logger.debug("get_livesynthesis, got: %d elements, %s", len(items), items)
        except ValueError:  # pragma: no cover - should not happen
            logger.debug("get_livesynthesis, none found")
            return default_ls

        if not items:
            return default_ls
        ls = items[0]

        # Services synthesis
        hosts_synthesis = {
            'nb_elts': ls["hosts_total"],
            'business_impact': ls["hosts_business_impact"],
            'critical_threshold': 5.0,
            'warning_threshold': 2.0,
            'global_critical_threshold': 5.0,
            'global_warning_threshold': 2.0,
        }
        for state in 'up', 'down', 'unreachable':
            hosts_synthesis.update({
                "nb_%s_hard" % state: ls["hosts_%s_hard" % state]
            })
            hosts_synthesis.update({
                "nb_%s_soft" % state: ls["hosts_%s_soft" % state]
            })
            hosts_synthesis.update({
                "nb_" + state: ls["hosts_%s_hard" % state] + ls["hosts_%s_soft" % state]
            })
        for state in 'acknowledged', 'in_downtime', 'flapping':
            hosts_synthesis.update({
                "nb_" + state: ls["hosts_%s" % state]
            })
        hosts_synthesis.update({
            "nb_problems": ls["hosts_down_hard"] + ls["hosts_unreachable_hard"]
        })
        for state in 'up', 'down', 'unreachable':
            hosts_synthesis.update({
                "pct_" + state: round(
                    100.0 * hosts_synthesis['nb_' + state] / hosts_synthesis['nb_elts'], 2
                ) if hosts_synthesis['nb_elts'] else 0.0
            })
        for state in 'acknowledged', 'in_downtime', 'flapping', 'problems':
            hosts_synthesis.update({
                "pct_" + state: round(
                    100.0 * hosts_synthesis['nb_' + state] / hosts_synthesis['nb_elts'], 2
                ) if hosts_synthesis['nb_elts'] else 0.0
            })

        # Services synthesis
        services_synthesis = {
            'nb_elts': ls["services_total"],
            'business_impact': ls["services_business_impact"],
            'critical_threshold': 5.0,
            'warning_threshold': 2.0,
            'global_critical_threshold': 5.0,
            'global_warning_threshold': 2.0,
        }
        for state in 'ok', 'warning', 'critical', 'unknown':
            services_synthesis.update({
                "nb_%s_hard" % state: ls["services_%s_hard" % state]
            })
            services_synthesis.update({
                "nb_%s_soft" % state: ls["services_%s_soft" % state]
            })
            services_synthesis.update({
                "nb_" + state: ls["services_%s_hard" % state] + ls["services_%s_soft" % state]
            })
        for state in 'acknowledged', 'in_downtime', 'flapping':
            services_synthesis.update({
                "nb_" + state: ls["services_%s" % state]
            })
        services_synthesis.update({
            "nb_problems": ls["services_warning_hard"] + ls["services_critical_hard"]
        })
        for state in 'ok', 'warning', 'critical', 'unknown':
            services_synthesis.update({
                "pct_" + state: round(
                    100.0 * services_synthesis['nb_' + state] / services_synthesis['nb_elts'], 2
                ) if services_synthesis['nb_elts'] else 0.0
            })
        for state in 'acknowledged', 'in_downtime', 'flapping', 'problems':
            services_synthesis.update({
                "pct_" + state: round(
                    100.0 * services_synthesis['nb_' + state] / services_synthesis['nb_elts'], 2
                ) if services_synthesis['nb_elts'] else 0.0
            })

        synthesis = {
            'hosts_synthesis': hosts_synthesis,
            'services_synthesis': services_synthesis
        }
        logger.debug("live synthesis, %s", synthesis)
        return synthesis

    ##
    # Actions
    ##
    def add_acknowledge(self, data):
        """ Request to acknowledge a problem. """

        logger.info("add_acknowledge, request an acknowledge, data: %s", data)
        return self.add_object('actionacknowledge', data)

    def add_recheck(self, data):
        """ Request to re-check an host/service. """

        logger.info("add_recheck, request a recheck, data: %s", data)
        return self.add_object('actionforcecheck', data)

    def add_downtime(self, data):
        """ Request to schedule a downtime. """

        logger.info("add_downtime, request a downtime, data: %s", data)
        return self.add_object('actiondowntime', data)

    ##
    # hostgroups
    ##
    def get_hostgroups(self, search=None, all_elements=False):
        """ Get a list of all hostgroups. """
        if search is None:
            search = {}
        if 'sort' not in search:
            search.update({'sort': 'name'})

        try:
            logger.info("get_hostgroups, search: %s", search)
            items = self.find_object('hostgroup', search, all_elements)
            return items
        except ValueError:  # pragma: no cover - should not happen
            logger.debug("get_hostgroups, none found")

        return []

    def get_hostgroup(self, search):
        """ Get a hostgroup by its id. """

        if isinstance(search, basestring):
            search = {'max_results': 1, 'where': {'_id': search}}
        elif 'max_results' not in search:
            search.update({'max_results': 1})

        items = self.get_hostgroups(search=search)
        return items[0] if items else None

    ##
    # Hosts
    ##
    def get_hosts(self, search=None, template=False, all_elements=False):
        """ Get a list of all hosts. """
        if search is None:
            search = {}
        if 'sort' not in search:
            search.update({'sort': 'name'})
        if 'where' not in search:
            search.update({'where': {'_is_template': template}})
        elif '_is_template' not in search['where']:
            search['where'].update({'_is_template': template})
        if 'embedded' not in search:
            search.update({
                'embedded': {
                    'check_command': 1, 'snapshot_command': 1, 'event_handler': 1,
                    'check_period': 1, 'notification_period': 1,
                    'snapshot_period': 1, 'maintenance_period': 1,
                    'parents': 1, 'hostgroups': 1, 'users': 1, 'usergroups': 1
                }
            })

        try:
            logger.info("get_hosts, search: %s", search)
            items = self.find_object('host', search, all_elements)
            logger.info("get_hosts, got: %d elements, %s", len(items), items)
            return items
        except ValueError:  # pragma: no cover - should not happen
            logger.debug("get_hosts, none found")

        return []

    def get_host(self, search):
        """ Get a host by its id (default). """

        if isinstance(search, basestring):
            search = {'max_results': 1, 'where': {'_id': search}}
        elif 'max_results' not in search:
            search.update({'max_results': 1})

        items = self.get_hosts(search=search)
        return items[0] if items else None

    ##
    # servicegroups
    ##
    def get_servicegroups(self, search=None, all_elements=False):
        """ Get a list of all servicegroups. """
        if search is None:
            search = {}
        if 'sort' not in search:
            search.update({'sort': 'name'})

        try:
            logger.info("get_servicegroups, search: %s", search)
            items = self.find_object('servicegroup', search, all_elements)
            return items
        except ValueError:  # pragma: no cover - should not happen
            logger.debug("get_servicegroups, none found")

        return []

    def get_servicegroup(self, search):
        """ Get a servicegroup by its id. """

        if isinstance(search, basestring):
            search = {'max_results': 1, 'where': {'_id': search}}
        elif 'max_results' not in search:
            search.update({'max_results': 1})

        items = self.get_servicegroups(search=search)
        return items[0] if items else None

    ##
    # Services
    ##
    def get_services(self, search=None, template=False, all_elements=False):
        """ Get a list of all services. """
        if search is None:
            search = {}
        if 'sort' not in search:
            search.update({'sort': 'name'})
        if 'where' not in search:
            search.update({'where': {'_is_template': template}})
        elif '_is_template' not in search['where']:
            search['where'].update({'_is_template': template})
        if 'embedded' not in search:
            search.update({
                'embedded': {
                    'host': 1,
                    'check_command': 1, 'snapshot_command': 1, 'event_handler': 1,
                    'check_period': 1, 'notification_period': 1,
                    'snapshot_period': 1, 'maintenance_period': 1,
                    'service_dependencies': 1, 'servicegroups': 1, 'users': 1, 'usergroups': 1
                }
            })

        try:
            logger.info("get_services, search: %s", search)
            items = self.find_object('service', search, all_elements)
            logger.info("get_services, got: %d elements, %s", len(items), items)
            return items
        except ValueError:  # pragma: no cover - should not happen
            logger.debug("get_services, none found")

        return []

    def get_service(self, search):
        """ Get a service by its id (default). """

        if isinstance(search, basestring):
            search = {'max_results': 1, 'where': {'_id': search}}
        elif 'max_results' not in search:
            search.update({'max_results': 1})

        items = self.get_services(search=search)
        return items[0] if items else None

    def get_services_synthesis(self, elts=None):
        """
        Services synthesis by status
        """
        if elts:
            services = [item for item in elts if item.getType() == 'service']
        else:
            services = self.get_services()
        logger.debug("get_services_synthesis, %d services", len(services))

        synthesis = dict()
        synthesis['nb_elts'] = len(services)
        synthesis['nb_problem'] = 0
        if services:
            for state in 'ok', 'warning', 'critical', 'unknown', 'ack', 'downtime':
                synthesis['nb_' + state] = sum(
                    1 for service in services if service.status.lower() == state
                )
                synthesis['pct_' + state] = round(
                    100.0 * synthesis['nb_' + state] / synthesis['nb_elts'], 2
                )
        else:
            for state in 'ok', 'warning', 'critical', 'unknown', 'ack', 'downtime':
                synthesis['nb_' + state] = 0
                synthesis['pct_' + state] = 0

        logger.debug("get_services_synthesis: %s", synthesis)
        return synthesis

    ##
    # Logs
    ##
    def get_logcheckresult(self, search=None):
        """ Get log for all elements

            Elements in the log which type is 'host' or 'service'

            :param search: backend request search
            :type search: dic
            :return: list of hosts/services live states
            :rtype: list
        """
        if not search:
            search = {}
        if "sort" not in search:
            search.update({'sort': '-business_impact,-state_id'})
        if 'embedded' not in search:
            search.update({'embedded': {'host': 1, 'service': 1}})

        try:
            logger.info("get_logcheckresult, search: %s", search)
            items = self.find_object('logcheckresult', search)
            logger.info("get_logcheckresult, got: %d elements, %s", len(items), items)
            return items
        except ValueError:  # pragma: no cover - should not happen
            logger.debug("get_logcheckresult, none found")

    ##
    # History
    ##
    def get_history(self, search=None):
        """ Get history

            :param search: backend request search
            :type search: dic
            :return: list of hosts/services live states
            :rtype: list
        """
        if not search:
            search = {}
        if "sort" not in search:
            search.update({'sort': '-_id'})
        if 'embedded' not in search:
            search.update({'embedded': {'host': 1, 'service': 1, 'logcheckresult': 1}})

        try:
            logger.info("get_history, search: %s", search)
            items = self.find_object('history', search)
            # logger.info("get_history, got: %d elements, %s", len(items), items)
            return items
        except ValueError:
            logger.debug("get_history, none found")

    ##
    # Commands
    ##
    def get_commands(self, search=None, all_elements=False):
        """ Get a list of all commands. """
        if search is None:
            search = {}
        if 'sort' not in search:
            search.update({'sort': 'name'})

        try:
            logger.info("get_commands, search: %s", search)
            items = self.find_object('command', search, all_elements)
            return items
        except ValueError:  # pragma: no cover - should not happen
            logger.debug("get_commands, none found")

        return []

    def get_command(self, search):
        """ Get a command by its id. """

        if isinstance(search, basestring):
            search = {'max_results': 1, 'where': {'_id': search}}
        elif 'max_results' not in search:
            search.update({'max_results': 1})

        items = self.get_commands(search=search)
        return items[0] if items else None

    ##
    # Users
    ##
    def get_users(self, search=None, all_elements=False):
        """ Get a list of known users """
        if not self.get_logged_user().is_administrator():
            return [self.get_logged_user()]

        if search is None:
            search = {}
        if 'sort' not in search:
            search.update({'sort': 'name'})

        try:
            logger.info("get_users, search: %s", search)
            items = self.find_object('user', search, all_elements)
            # logger.info("get_users, got: %d elements, %s", len(items), items)
            return items
        except ValueError:  # pragma: no cover - should not happen
            logger.debug("get_users, none found")

        return []

    def get_user(self, search):
        """
        Get a user by its id or a search pattern
        """
        if isinstance(search, basestring):
            search = {'max_results': 1, 'where': {'_id': search}}
        elif 'max_results' not in search:
            search.update({'max_results': 1})

        items = self.get_users(search=search)
        return items[0] if items else None

    def add_user(self, data):
        """ Add a user. """

        return self.add_object('user', data)

    def delete_user(self, user):
        """ Delete a user.

        Cannot delete the currently logged in user ...

        If user is a string it is assumed to be the User object id to be searched in
        the objects cache.

        :param user: User object instance
        :type user: User (or string)

        Returns True/False depending if user has been deleted
        """
        logger.info("delete_user, request to delete the user: %s", user)

        if isinstance(user, basestring):
            user = self.get_user(user)
            if not user:
                return False

        user_id = user.id
        if user_id == self.get_logged_user().id:
            logger.warning(
                "unauthorized request to delete the current logged-in user: %s",
                user_id
            )
            return False

        return self.delete_object('user', user)

    ##
    # realms
    ##
    def get_realms(self, search=None, all_elements=False):
        """ Get a list of all realms. """
        if search is None:
            search = {}
        if 'sort' not in search:
            search.update({'sort': 'name'})

        try:
            logger.info("get_realms, search: %s", search)
            items = self.find_object('realm', search, all_elements)
            # logger.info("get_realms, got: %d elements, %s", len(items), items)
            return items
        except ValueError:  # pragma: no cover - should not happen
            logger.debug("get_realms, none found")

        return []

    def get_realm(self, search):
        """ Get a realm by its id. """

        if isinstance(search, basestring):
            search = {'max_results': 1, 'where': {'_id': search}}
        elif 'max_results' not in search:
            search.update({'max_results': 1})

        items = self.get_realms(search=search)
        return items[0] if items else None

    ##
    # timeperiods
    ##
    def get_timeperiods(self, search=None, all_elements=False):
        """ Get a list of all timeperiods. """
        if search is None:
            search = {}
        if 'sort' not in search:
            search.update({'sort': 'name'})

        try:
            logger.info("get_timeperiods, search: %s", search)
            items = self.find_object('timeperiod', search, all_elements)
            # logger.info("get_timeperiods, got: %d elements, %s", len(items), items)
            return items
        except ValueError:
            logger.debug("get_timeperiods, none found")

        return []

    def get_timeperiod(self, search):
        """ Get a timeperiod by its id. """

        if isinstance(search, basestring):
            search = {'max_results': 1, 'where': {'_id': search}}
        elif 'max_results' not in search:
            search.update({'max_results': 1})

        items = self.get_timeperiods(search=search)
        return items[0] if items else None
