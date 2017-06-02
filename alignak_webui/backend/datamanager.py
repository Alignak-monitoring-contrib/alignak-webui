#!/usr/bin/python
# -*- coding: utf-8 -*-

# Yes, but that's how it is made, and it suits ;)
# pylint: disable=too-many-public-methods
# Necessary to import all backend elements objects!
# pylint: disable=wildcard-import,unused-wildcard-import

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
    Application data manager
"""

import time
from datetime import datetime
from copy import deepcopy
import logging

from alignak_backend_client.client import BackendException

# Import the backend interface class
from alignak_webui.backend.backend import BackendConnection
from alignak_webui.backend.alignak_ws_client import AlignakConnection, AlignakWSException

from alignak_webui.utils.dates import get_ts_date
from alignak_webui.utils.helper import Helper

# Import all objects we will need -
# NOTE that all the objects types need to be imported else some errors will raise!
# pylint: disable=unused-import
from alignak_webui.objects.element_state import ElementState
from alignak_webui.objects.element import BackendElement
from alignak_webui.objects.item_realm import Realm
from alignak_webui.objects.item_alignak import Alignak
from alignak_webui.objects.item_daemon import Daemon
from alignak_webui.objects.item_command import Command
from alignak_webui.objects.item_timeperiod import TimePeriod
from alignak_webui.objects.item_user import User
from alignak_webui.objects.item_usergroup import UserGroup
from alignak_webui.objects.item_userrestrictrole import UserRestrictRole
from alignak_webui.objects.item_host import Host
from alignak_webui.objects.item_hostgroup import HostGroup
from alignak_webui.objects.item_hostdependency import HostDependency
from alignak_webui.objects.item_hostescalation import HostEscalation
from alignak_webui.objects.item_service import Service
from alignak_webui.objects.item_servicegroup import ServiceGroup
from alignak_webui.objects.item_servicedependency import ServiceDependency
from alignak_webui.objects.item_serviceescalation import ServiceEscalation
from alignak_webui.objects.item_history import History
from alignak_webui.objects.item_log import Log
from alignak_webui.objects.item_actions import ActionAcknowledge, ActionDowntime, \
    ActionForceCheck
from alignak_webui.objects.item_livesynthesis import LiveSynthesis
from alignak_webui.objects.item_backend_grafana import BackendGrafana
from alignak_webui.objects.item_backend_graphite import BackendGraphite
from alignak_webui.objects.item_backend_statsd import BackendStatsd
from alignak_webui.objects.item_backend_influxdb import BackendInfluxdb


# Set logger level to INFO, this to allow global application DEBUG logs without being spammed... ;)
# pylint:disable=invalid-name
logger = logging.getLogger(__name__)
# logger.setLevel(logging.INFO)


class DataManager(object):

    """Application data manager object"""

    id = 1

    def __init__(self, app, session=None):
        """Initialize a DataManager instance

        The `session` parameter is provided to the data manager when a Web session exists.
        This to avoid getting the session parameters from the backend. the session parameters
        are:
        * the current logged-in user
        * the logged-in user realm
        * the logged-in user live synthesis

        If session is None, then the Data manager calls its load method to get the
        session parameters.

        Args:
            session: session parameters (logged-in user, realm, ...)
            backend_endpoint: Alignak backend URL endpoint
            alignak_endpoint: Alignak Web service URL endpoint
        """
        # Set a unique id for each DM object
        self.__class__.id += 1

        # Associated backend object
        self.backend_endpoint = app.config.get('alignak_backend', 'http://127.0.0.1:5000')
        self.backend = BackendConnection(self.backend_endpoint)

        # Alignak Web services client
        self.alignak_endpoint = app.config.get('alignak_ws', 'http://127.0.0.1:8888')
        self.alignak_authorization = (app.config.get('alignak_ws_authorization', '1') == '1')
        self.alignak_ws = AlignakConnection(self.alignak_endpoint, self.alignak_authorization)
        self.alignak_daemons = {}

        # Get known objects type from the imported modules
        # Search for classes including an _type attribute
        self.known_classes = []
        for k, dummy in globals().items():
            if isinstance(globals()[k], type) and \
               '_type' in globals()[k].__dict__ and \
               globals()[k].get_type() is not None and \
               globals()[k].get_type() != 'item':
                self.known_classes.append(globals()[k])
                # Really too verbose and of not much interest...
                # logger.debug("Known class %s for object type: %s",
                #              globals()[k], globals()[k].get_type())

        self.connected = False
        self.logged_in_user = None
        self.connection_message = None
        self.loading = 0
        self.loaded = False

        self.refresh_required = False
        self.refresh_done = False

        self.updated = datetime.utcnow()

        self.my_realm = None
        self.my_ls = None

        # Restore session parameters
        if session:
            if self.user_login(session['current_user'].token, load=False):
                self.my_realm = session['current_realm']
                self.my_ls = session['current_ls']

    def __repr__(self):
        return "<DM, id: %s, objects count: %d, user: %s, updated: %s>" % (
            self.id,
            self.get_objects_count(),
            self.logged_in_user.get_username() if self.logged_in_user else 'Not logged in',
            self.updated
        )

    ##
    # Connected user
    ##
    def user_login(self, username, password=None, load=True):
        """Set the data manager user

        If password is provided, use the backend login function to authenticate the user

        If no password is provided, the username is assumed to be an authentication token and we
        use the backend connect function."""
        logger.info("user_login, connection requested: %s, load: %s", username, load)

        self.connected = False
        self.connection_message = _('Backend connecting...')
        try:
            # Backend login
            self.connected = self.backend.login(username, password)
            if self.connected:
                self.connection_message = _('Connection successful')

                # Set the backend to use by the data manager objects
                BackendElement.set_backend(self.backend)
                BackendElement.set_known_classes(self.known_classes)

                # Use the same credentials for Alignak Web Service interface
                self.alignak_ws.login(username, password)

                # Fetch the logged-in user
                if password:
                    users = self.backend.get('user',
                                             {'max_results': 1, 'where': {'name': username}})
                else:
                    users = self.backend.get('user',
                                             {'max_results': 1, 'where': {'token': username}})
                self.logged_in_user = User(users[0])
                logger.debug("user_login, user: %s", self.logged_in_user)
                # Tag user as authenticated
                self.logged_in_user.authenticated = True

                # Load data if load required...
                if load:
                    self.load(reset=True)
                self.connection_message = _('Access granted')
            else:
                self.connection_message = _('Access denied! Check your username and password.')
        except BackendException as exp:  # pragma: no cover, should not happen
            logger.exception("configured backend is not available: %s", exp)
            self.connection_message = exp.message
            self.connected = False
        except Exception as exp:  # pragma: no cover, should not happen
            logger.exception("User login exception: %s", exp)
            self.connected = False

        logger.info("user_login, connection message: %s / %s",
                    self.connected, self.connection_message)
        return self.connected

    def user_logout(self):
        """Logout the data manager user. Do not log-out from the backend. Need to reset the
        datamanager to do it."""
        self.logged_in_user = None
        self.connected = False

    ##
    # Find objects and load objects cache
    ##
    def find_object(self, object_type, params=None, all_elements=False, embedded=True):
        """Find an object ...

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

        Returns an array of matching objects"""
        logger.debug("find_object, %s, params: %s, all: %s, embedded: %s",
                     object_type, params, all_elements, embedded)

        if isinstance(params, basestring):
            params = {'where': {'_id': params}}

        if 'embedded' in params and not embedded:
            del params['embedded']

        items = []

        try:
            result = self.backend.get(object_type, params, all_elements)
            logger.debug("find_object, found: %s: %s", object_type, result)
        except BackendException as exp:  # pragma: no cover, simple protection
            logger.exception("find_object, exception: %s", exp)
            raise ValueError(
                '%s, search: %s was not found in the backend' % (object_type, params)
            )

        # Find "Backend object type" classes in file imported modules ...
        object_class = [kc for kc in self.known_classes if kc.get_type() == object_type]
        if not object_class:  # pragma: no cover, should not happen
            logger.warning("find_object, unknown object type: %s", object_type)
            raise ValueError(
                '%s, is not currently managed!' % (object_type)
            )
        object_class = object_class[0]

        for item in result:
            # Create a new object
            # logger.debug("find_object, begin creation: %s", object_class)
            bo_object = object_class(item, embedded=embedded)
            items.append(bo_object)
            self.updated = datetime.utcnow()
            # logger.debug("find_object, created")
            # logger.info("find_object, created: %s.", bo_object.__dict__)

            # Update class _total_count (each item got from backend has an _total field)
            if '_total' in item:
                object_class.set_total_count(item['_total'])

        logger.debug("find_object, %s, found %d items", object_type, len(items))
        return items

    def load(self, reset=False, refresh=False):
        """Load data in the data manager objects

            If reset is set, then all the existing objects are deleted and then created from
            scratch (first load ...). Else, existing objects are updated and new objects are
            created.

            Get all the users (related to current logged-in user)

            :returns: the number of newly created objects"""
        if not self.logged_in_user:
            logger.error("load, must be logged-in before loading")
            return False

        if self.loading > 0:  # pragma: no cover, protection if application shuts down ...
            logger.error("load, already loading: trial: %d", self.loading)
            if self.loading < 3:
                self.loading += 1
                return False
            logger.error("load, already loading: reset counter")
            self.loading = 0

        logger.debug("load, start loading: %s for %s", self, self.logged_in_user)
        logger.debug("load, start as super-administrator: %s",
                     self.logged_in_user.is_super_administrator())
        logger.debug("load, start as administrator: %s",
                     self.logged_in_user.is_administrator())
        start = time.time()

        if reset:
            logger.info("Objects cache reset")
            self.reset(logout=False)

        self.loading += 1
        self.loaded = False

        # Get internal objects count
        objects_count = self.get_objects_count()
        logger.info("Load, start, objects in cache: %d", objects_count)

        # Get the higher level realm for the current logger-in user
        # This realm identifier will be used when it is necessaty to provide a realm
        # (eg. for new objects creation)
        self.my_realm = self.get_realm({'max_results': 1, 'sort': '_level'})
        logger.info("user's default higher level realm: %s", self.my_realm['name'])

        # Get the live synthesis identifier for the user's realm
        # This will allow to request the user's specific realm LS for as the backend
        # to concatenate the sub realms live synthesis
        self.my_ls = self.get_livesynthesis({'concatenation': '1',
                                             'where': {'_realm': self.my_realm.id}})
        logger.info("user's concatenated live synthesis: %s", self.my_ls['_id'])

        # Get internal objects count
        new_objects_count = self.get_objects_count()
        logger.debug("Load, end, objects in cache: %d", new_objects_count)

        logger.info("Data manager load (%s), new objects: %d,  duration: %s",
                    refresh, new_objects_count - objects_count, (time.time() - start))

        if new_objects_count > objects_count:
            self.require_refresh()

        self.loaded = True
        self.loading = 0
        return new_objects_count - objects_count

    def reset(self, logout=False):
        """Reset data in the data manager objects"""
        logger.debug("Data manager reset...")

        # Clean internal objects cache
        for known_class in self.known_classes:
            logger.debug("Cleaning %s cache...", known_class.get_type())
            known_class.clean_cache()

        if logout:
            self.backend.logout()
            self.user_logout()

        self.loaded = False
        self.loading = 0
        self.refresh_required = True

    def require_refresh(self):
        """Require an immediate refresh"""
        self.refresh_required = True
        self.refresh_done = False

    def get_objects_count(self, object_type=None, log=False):
        """Get the count of the objects stored in the data manager cache

        If an object_type is specified, only returns the count for this object type

        If log is set, an information log is made"""
        if object_type:
            for known_class in self.known_classes:
                if object_type == known_class.get_type():
                    return known_class.get_count()
            else:  # pragma: no cover, should not happen
                # pylint: disable=useless-else-on-loop
                logger.warning("count_objects, unknown object type: %s", object_type)
                return 0

        objects_count = 0
        for known_class in self.known_classes:
            if log:
                logger.info("get_objects_count, %s: %d elements",
                            known_class, known_class.get_count())
            objects_count += known_class.get_count()

        if log:
            logger.info("get_objects_count, currently %d elements", objects_count)
        return objects_count

    ##
    # Elements get, add, delete, update, ...
    ##
    def get_objects(self, object_type, search=None, all_elements=False):
        """Get a list of specified objects."""
        if search is None:
            search = {}
        if 'sort' not in search:
            search.update({'sort': '_level'})

        try:
            logger.debug("get_objects, search: %s", search)
            items = self.find_object(object_type, search, all_elements)
            return items
        except ValueError:  # pragma: no cover - should not happen
            logger.debug("get_objects, none found")

        return []

    def get_object(self, object_type, search):
        """Get an object of the specified type by its id."""
        if isinstance(search, basestring):
            search = {'max_results': 1, 'where': {'_id': search}}
        elif 'max_results' not in search:
            search.update({'max_results': 1})

        items = self.get_objects(object_type, search=search)
        return items[0] if items else None

    def count_objects(self, object_type, search=None):
        """Request objects from the backend to pick-up total records count.

        Make a simple request for 1 element and we will get back the total count of elements

        Args:
            object_type: the object type as a backend endpoint (eg. host, realm, ...)
            search: dictionary of key / value to search for

        Returns:

        """
        params = {
            'page': 0, 'max_results': 1
        }
        if search is not None:
            params.update(search)

        return self.backend.count(object_type, params)

    def add_object(self, object_type, data=None, files=None):
        """Add an element"""
        logger.info("add_object, request to add an '%s': %s", object_type, data)

        return self.backend.post(object_type, data=data, files=files)

    def delete_object(self, object_type, element):
        """Delete an element

        - object_type is the element type
        - element may be a string. In this case it is considered to be the element id
        """
        logger.debug("delete_object, request to delete the %s: %s", object_type, element)

        if isinstance(element, basestring):
            object_id = element
        else:
            object_id = element.id

        try:
            if self.backend.delete(object_type, object_id):
                # Find object type class...
                object_class = [kc for kc in self.known_classes if kc.get_type() == object_type][0]

                # Delete existing cache object
                if object_id in object_class.get_cache():
                    del object_class.get_cache()[object_id]

                return True
        except BackendException as exp:  # pragma: no cover, simple protection
            logger.warning("delete_object, exception: %s", exp)

        return False

    def update_object(self, element, data):
        """Update an element"""
        logger.debug("update_object, request to update: %s", element)

        return self.backend.update(element, data)

    ##
    # User's preferences
    # todo: refactor API to use self.logged_in_user if user is None
    ##
    def delete_user_preferences(self, user, preference_key):
        """Delete user's preferences

        *****
        Currently this sets the value None in the preferences dictionary instead of removing
        the attribute, because thebackend does not allow to $unset in a dictionary!
        *****

        :param user: username
        :type user: string
        :param preference_key: preference unique key
        :type preference_key: string
        :return: server's response
        :rtype: dict
        """
        logger.debug("delete_user_preferences, type: %s, for: %s", preference_key, user)

        # Delete user stored value
        if user.delete_ui_preference(preference_key):
            # Should no exist!
            user.set_ui_preference(preference_key, None)
            # {$unset: {preference_key:1}}
            return self.update_object(
                user,
                {'ui_preferences': self.logged_in_user.ui_preferences}
            )

        return False

    def set_user_preferences(self, user, preference_key, value):
        """Set user's preferences

        If an exception occurs, it is raised to the caller.

        This function returns True if the data were stored, else False if a problem was encountered.

        **Note**: When a simple value is stored (value parameter is not a dictionary), it is
        it is stored in a dictionary containing a 'value' property.

        :param user: username
        :type user: string
        :param preference_key: preference unique key
        :type preference_key: string
        :param value: value of the parameter to store
        :type value: dict
        :return: True / False
        :rtype: boolean
        """
        logger.debug("set_user_preferences, key: %s, for: %s", preference_key, user)
        # logger.debug("set_user_preferences, value = %s", value)

        # Get user stored value
        if user.set_ui_preference(preference_key, value):
            return self.update_object(user, {'ui_preferences': user.ui_preferences})

        return False

    def get_user_preferences(self, user, preference_key, default=None):
        # pylint:disable=no-self-use
        """Get user's preferences

        If the data are not found, and no default value is provided, this function returns None. If
        a default value is provided then this function returns the defaut value after having stored
        it in the user's preferendes.

        If preference_key is None then this function returns all the user stored preferences.
        If user is None then all the preferences are returned.

        **Note**: When a simple value is stored with set_user_preferences, it is never returned as
        a simple value but in a dictionary containing a 'value' property.

        :param default:
        :param user: username
        :type user: string
        :param preference_key: preference unique key
        :type preference_key: string
        :return: found data, or None
        :rtype: dict
        """
        logger.debug("get_user_preferences, key: %s, for: %s", preference_key, user)

        # Get user stored value
        result = user.get_ui_preference(preference_key)
        return result if result else default

    ##
    # Alignak
    ##
    def get_alignak_map(self, search=None):  # pylint: disable=unused-argument
        """Get Alignak overall state from the Alignak Web Services module:

            https://github.com/Alignak-monitoring-contrib/alignak-module-ws

            The search parameter is not used but is kept for get method interface compatibility!

            Example response::
            {
                reactionner: {},
                broker: {},
                arbiter: {
                    arbiter-master: {
                        passive: false,
                        realm: "",
                        realm_name: "All",
                        polling_interval: 1,
                        alive: true,
                        manage_arbiters: false,
                        manage_sub_realms: false,
                        is_sent: false,
                        spare: false,
                        check_interval: 60,
                        address: "127.0.0.1",
                        reachable: true,
                        max_check_attempts: 3,
                        last_check: 0,
                        port: 7770
                    }
                },
                scheduler: {
                    scheduler-master: {
                        passive: false,
                        realm: "83596f2b6e254e7ea28467a1fe5627ef",
                        realm_name: "All",
                        polling_interval: 1,
                        alive: true,
                        manage_arbiters: false,
                        manage_sub_realms: false,
                        is_sent: true,
                        spare: false,
                        check_interval: 60,
                        address: "127.0.0.1",
                        reachable: true,
                        max_check_attempts: 3,
                        last_check: 1478064129.016136,
                        port: 7768
                    },
                    scheduler-south: {},
                    scheduler-north: {}
                },
                receiver: {},
                poller: {}
            }

            :return: list of the Alignak daemons
            :rtype: list of Daemon objects"""

        result = []

        try:
            logger.debug("get_alignak_map")
            result = self.alignak_ws.get('alignak_map')
        except AlignakWSException:
            return result

        logger.debug("Alignak status map, %s", result)

        self.alignak_daemons = []
        for daemon_type in result:
            logger.debug("Got Alignak state for: %s", daemon_type)
            daemons = result.get(daemon_type)
            for daemon_name in daemons:
                daemon_data = daemons.get(daemon_name)
                daemon_data['name'] = daemon_name
                daemon = Daemon(daemon_data)
                self.alignak_daemons.append(daemon)
                logger.debug(" - %s: %s", daemon_name, daemon)

        Daemon.set_total_count(len(self.alignak_daemons))
        return self.alignak_daemons

    def get_alignak_state(self, search=None, all_elements=False):
        """Get a list of all alignak daemons states."""
        if search is None:
            search = {}
        if 'sort' not in search:
            search.update({'sort': 'name'})
        if 'embedded' not in search:
            search.update({
                'embedded': {
                    '_realm': 1
                }
            })

        try:
            logger.debug("get_alignak_state, search: %s", search)
            items = self.find_object('alignakdaemon', search, all_elements)
            logger.debug("get_alignak_state, found: %s", items)
            return items
        except ValueError:  # pragma: no cover - should not happen
            logger.debug("get_alignak_state, none found")

        return []

    ##
    # Live synthesis
    ##
    def get_livesynthesis(self, search=None):
        """Get live state synthesis for hosts and services

            Example backend response::

                {
                    '_realm': u'57bd834106fd4b5c26daf040',

                    'services_total': 89,
                    'services_business_impact': 0,
                    'services_ok_hard': 8,
                    'services_ok_soft': 0,
                    'services_warning_hard': 0,
                    'services_warning_soft': 0,
                    'services_critical_hard': 83,
                    'services_critical_soft': 23,
                    'services_unknown_hard': 24,
                    'services_unknown_soft': 0,
                    'services_unreachable_hard': 4,
                    'services_unreachable_soft': 1,
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

                },
                {
                    ... / ...
                }

            The new backend (as of 08/01/2017) introduces a new API, with two parameters:
                * *history=1*: get the history in field *history* with all
                history for the last minutes
                * *concatenation=1*: get the livesynthesis data merged with livesynthesis
                of sub-realm. If you use this parameter with *history* parameter, the
                history will be merged with livesynthesis history of sub-realm.

            This function gets the live synthesis with the concatenation parameter for
            the current realm to let the backend compute the sub realms counters.
            As such if more than one item is received it is because the current user
            can view several realms wich are not in the same realms hierarchy.

            Returns a dictionary containing:
                - livesynthesis backend _id
                - hosts_synthesis dictionary containing:
                    - number of elements
                    - business impact
                    - count for each state (hard and soft)
                    - percentage for each state (hard and soft)
                    - number of problems (down and unreachable, only hard state)
                    - percentage of problems

                - services_synthesis dictionary containing:
                    - number of elements
                    - business impact
                    - count for each state (hard and soft)
                    - percentage for each state (hard and soft)
                    - number of problems (down and unreachable, only hard state)
                    - percentage of problems


            :return: hosts and services live state synthesis in a dictionary
            :rtype: dict
        """

        items = None
        default_ls = {
            '_id': None,
            'hosts_synthesis': {
                'nb_elts': 0,
                'business_impact': 0,

                'warning_threshold': 2.0, 'global_warning_threshold': 2.0,
                'critical_threshold': 5.0, 'global_critical_threshold': 5.0,

                'nb_up': 0, 'pct_up': 0.0,
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

                'nb_ok': 0, 'pct_ok': 0.0,
                'nb_ok_hard': 0, 'nb_ok_soft': 0,
                'nb_warning': 0, 'pct_warning': 0.0,
                'nb_warning_hard': 0, 'nb_warning_soft': 0,
                'nb_critical': 0, 'pct_critical': 0.0,
                'nb_critical_hard': 0, 'nb_critical_soft': 0,
                'nb_unknown': 0, 'pct_unknown': 0.0,
                'nb_unknown_hard': 0, 'nb_unknown_soft': 0,
                'nb_unreachable': 0, 'pct_unreachable': 0.0,
                'nb_unreachable_hard': 0, 'nb_unreachable_soft': 0,

                'nb_problems': 0, 'pct_problems': 0.0,
                'nb_flapping': 0, 'pct_flapping': 0.0,
                'nb_acknowledged': 0, 'pct_acknowledged': 0.0,
                'nb_in_downtime': 0, 'pct_in_downtime': 0.0
            }
        }

        if search is None:
            if not self.my_ls or self.my_ls['_id'] is None:
                return default_ls
            found = False
            error = False
            while not found and not error:
                try:
                    item = self.backend.get('livesynthesis/' + self.my_ls['_id'] +
                                            '?concatenation=1', params=None)
                    items = [item]
                    found = True
                except BackendException as exp:  # pragma: no cover, simple protection
                    logger.exception("get_livesynthesis, exception: %s", exp)
                    if exp.code in [404, 1000, 1003] and not error:
                        error = True
                        self.load(reset=True)
        else:
            try:
                logger.debug("get_livesynthesis, search: %s", search)
                items = self.find_object('livesynthesis', search)
                logger.debug("get_livesynthesis, got: %s", items)
            except ValueError:  # pragma: no cover - should not happen
                logger.debug("get_livesynthesis, none found")
                return default_ls

        if not items:  # pragma: no cover - should not happen
            return default_ls

        synthesis = default_ls
        # Hosts synthesis
        hosts_synthesis = default_ls['hosts_synthesis']
        # Services synthesis
        services_synthesis = default_ls['services_synthesis']

        for livesynthesis in items:
            logger.debug("livesynthesis item: %s", livesynthesis)
            synthesis['_id'] = livesynthesis['_id']

            # Hosts synthesis
            hosts_synthesis.update({
                "nb_elts": hosts_synthesis['nb_elts'] + livesynthesis["hosts_total"]
            })
            hosts_synthesis.update({
                'business_impact': min(hosts_synthesis['business_impact'],
                                       livesynthesis["hosts_business_impact"]),
            })
            for state in 'up', 'down', 'unreachable':
                hosts_synthesis.update({
                    "nb_%s_hard" % state:
                    hosts_synthesis["nb_%s_hard" % state] + livesynthesis["hosts_%s_hard" % state]
                })
                hosts_synthesis.update({
                    "nb_%s_soft" % state:
                    hosts_synthesis["nb_%s_soft" % state] + livesynthesis["hosts_%s_soft" % state]
                })
                hosts_synthesis.update({
                    "nb_" + state:
                    hosts_synthesis["nb_%s_hard" % state] + hosts_synthesis["nb_%s_soft" % state]
                })
            for state in 'acknowledged', 'in_downtime', 'flapping':
                hosts_synthesis.update({
                    "nb_" + state:
                    hosts_synthesis["nb_%s" % state] + livesynthesis["hosts_%s" % state]
                })
            hosts_synthesis.update({
                "nb_problems":
                hosts_synthesis["nb_down_hard"] + hosts_synthesis["nb_unreachable_hard"]
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
            services_synthesis.update({
                "nb_elts": services_synthesis['nb_elts'] + livesynthesis["services_total"]
            })
            services_synthesis.update({
                'business_impact': min(services_synthesis['business_impact'],
                                       livesynthesis["services_business_impact"]),
            })
            for state in 'ok', 'warning', 'critical', 'unknown', 'unreachable':
                services_synthesis.update({
                    "nb_%s_hard" % state:
                    services_synthesis["nb_%s_hard" % state] +
                    livesynthesis["services_%s_hard" % state]
                })
                services_synthesis.update({
                    "nb_%s_soft" % state:
                    services_synthesis["nb_%s_soft" % state] +
                    livesynthesis["services_%s_soft" % state]
                })
                services_synthesis.update({
                    "nb_" + state:
                    services_synthesis["nb_%s_hard" % state] +
                        services_synthesis["nb_%s_soft" % state]
                })
            for state in 'acknowledged', 'in_downtime', 'flapping':
                services_synthesis.update({
                    "nb_" + state:
                        services_synthesis["nb_%s" % state] + livesynthesis["services_%s" % state]
                })
            services_synthesis.update({
                "nb_problems":
                services_synthesis["nb_warning_hard"] + services_synthesis["nb_critical_hard"]
            })
            for state in 'ok', 'warning', 'critical', 'unknown', 'unreachable':
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

        synthesis['hosts_synthesis'] = hosts_synthesis
        synthesis['services_synthesis'] = services_synthesis

        logger.debug("live synthesis, %s", synthesis)
        return synthesis

    def get_livesynthesis_history(self):
        """Get live state synthesis history for hosts and services

            This function gets the live synthesis with the concatenation and history parameters
            for the current realm to let the backend compute the sub realms counters.
            As such if more than one item is received it is because the current user
            can view several realms wich are not in the same realms hierarchy.

            :return: a tuple containing a livesynthesis as get_livesynthesis function and an
            array of livesynthesis for each timestamp
            :rtype: tuple
        """

        item = None
        default_ls = {
            '_created': None,
            'hosts_synthesis': {
                'nb_elts': 0,
                'business_impact': 0,

                'warning_threshold': 2.0, 'global_warning_threshold': 2.0,
                'critical_threshold': 5.0, 'global_critical_threshold': 5.0,

                'nb_up': 0, 'pct_up': 0.0,
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

                'nb_ok': 0, 'pct_ok': 0.0,
                'nb_ok_hard': 0, 'nb_ok_soft': 0,
                'nb_warning': 0, 'pct_warning': 0.0,
                'nb_warning_hard': 0, 'nb_warning_soft': 0,
                'nb_critical': 0, 'pct_critical': 0.0,
                'nb_critical_hard': 0, 'nb_critical_soft': 0,
                'nb_unknown': 0, 'pct_unknown': 0.0,
                'nb_unknown_hard': 0, 'nb_unknown_soft': 0,
                'nb_unreachable': 0, 'pct_unreachable': 0.0,
                'nb_unreachable_hard': 0, 'nb_unreachable_soft': 0,

                'nb_problems': 0, 'pct_problems': 0.0,
                'nb_flapping': 0, 'pct_flapping': 0.0,
                'nb_acknowledged': 0, 'pct_acknowledged': 0.0,
                'nb_in_downtime': 0, 'pct_in_downtime': 0.0
            }
        }

        try:
            logger.debug("get_livesynthesis_history, history...")
            item = self.backend.get('livesynthesis/' + self.my_ls['_id'] +
                                    '?concatenation=1&history=1', params=None)
            logger.debug("get_livesynthesis_history, got: %s", item)
        except ValueError:  # pragma: no cover - should not happen
            logger.debug("get_livesynthesis_history, none found")
            return []

        if not item:  # pragma: no cover - should not happen
            return []

        # Manage global live synthesis
        synthesis = {
            '_id': item['_id']
        }
        hosts_synthesis = default_ls['hosts_synthesis']
        services_synthesis = default_ls['services_synthesis']

        # Hosts synthesis
        hosts_synthesis.update({
            "nb_elts": hosts_synthesis['nb_elts'] + item["hosts_total"]
        })
        hosts_synthesis.update({
            'business_impact': min(hosts_synthesis['business_impact'],
                                   item["hosts_business_impact"]),
        })
        for state in 'up', 'down', 'unreachable':
            hosts_synthesis.update({
                "nb_%s_hard" % state:
                hosts_synthesis["nb_%s_hard" % state] + item["hosts_%s_hard" % state]
            })
            hosts_synthesis.update({
                "nb_%s_soft" % state:
                hosts_synthesis["nb_%s_soft" % state] + item["hosts_%s_soft" % state]
            })
            hosts_synthesis.update({
                "nb_" + state:
                hosts_synthesis["nb_%s_hard" % state] + hosts_synthesis["nb_%s_soft" % state]
            })
        for state in 'acknowledged', 'in_downtime', 'flapping':
            hosts_synthesis.update({
                "nb_" + state:
                hosts_synthesis["nb_%s" % state] + item["hosts_%s" % state]
            })
        hosts_synthesis.update({
            "nb_problems":
            hosts_synthesis["nb_down_hard"] + hosts_synthesis["nb_unreachable_hard"]
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
        services_synthesis.update({
            "nb_elts": services_synthesis['nb_elts'] + item["services_total"]
        })
        services_synthesis.update({
            'business_impact': min(services_synthesis['business_impact'],
                                   item["services_business_impact"]),
        })
        for state in 'ok', 'warning', 'critical', 'unknown', 'unreachable':
            services_synthesis.update({
                "nb_%s_hard" % state:
                services_synthesis["nb_%s_hard" % state] +
                item["services_%s_hard" % state]
            })
            services_synthesis.update({
                "nb_%s_soft" % state:
                services_synthesis["nb_%s_soft" % state] +
                item["services_%s_soft" % state]
            })
            services_synthesis.update({
                "nb_" + state:
                services_synthesis["nb_%s_hard" % state] +
                    services_synthesis["nb_%s_soft" % state]
            })
        for state in 'acknowledged', 'in_downtime', 'flapping':
            services_synthesis.update({
                "nb_" + state:
                    services_synthesis["nb_%s" % state] + item["services_%s" % state]
            })
        services_synthesis.update({
            "nb_problems":
            services_synthesis["nb_warning_hard"] + services_synthesis["nb_critical_hard"]
        })
        for state in 'ok', 'warning', 'critical', 'unknown', 'unreachable':
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

        synthesis['hosts_synthesis'] = hosts_synthesis
        synthesis['services_synthesis'] = services_synthesis

        logger.debug("Global live synthesis, %s", synthesis)

        # Manage livesynthesis history
        history = []
        for livesynthesis in item['history']:  # pragma: no cover - really hard with unit tests...
            logger.info("livesynthesis item: %s", livesynthesis)
            synthesis = deepcopy(default_ls)
            synthesis['_created'] = livesynthesis['_created']
            synthesis['_timestamp'] = get_ts_date(livesynthesis['_created'],
                                                  date_format='%a, %d %b %Y %H:%M:%S %Z')
            # Hosts synthesis
            hs = synthesis['hosts_synthesis']
            # Services synthesis
            ss = synthesis['services_synthesis']

            # Hosts synthesis
            hs.update({"nb_elts": livesynthesis["hosts_total"]})
            hs.update({
                'business_impact': min(hs['business_impact'],
                                       livesynthesis["hosts_business_impact"]),
            })
            for state in 'up', 'down', 'unreachable':
                hs.update({"nb_%s_hard" % state: livesynthesis["hosts_%s_hard" % state]})
                hs.update({"nb_%s_soft" % state: livesynthesis["hosts_%s_soft" % state]})
                hs.update({"nb_" + state: hs["nb_%s_hard" % state] + hs["nb_%s_soft" % state]})
            for state in 'acknowledged', 'in_downtime', 'flapping':
                hs.update({"nb_" + state: livesynthesis["hosts_%s" % state]})
            hs.update({"nb_problems": hs["nb_down_hard"] + hs["nb_unreachable_hard"]})
            for state in 'up', 'down', 'unreachable':
                hs.update({
                    "pct_" + state: round(
                        100.0 * hs['nb_' + state] / hs['nb_elts'], 2
                    ) if hs['nb_elts'] else 0.0
                })
            for state in 'acknowledged', 'in_downtime', 'flapping', 'problems':
                hs.update({
                    "pct_" + state: round(
                        100.0 * hs['nb_' + state] / hs['nb_elts'], 2
                    ) if hs['nb_elts'] else 0.0
                })

            # Services synthesis
            ss.update({"nb_elts": livesynthesis["services_total"]})
            ss.update({
                'business_impact': min(ss['business_impact'],
                                       livesynthesis["services_business_impact"]),
            })
            for state in 'ok', 'warning', 'critical', 'unknown', 'unreachable':
                ss.update({"nb_%s_hard" % state: livesynthesis["services_%s_hard" % state]})
                ss.update({"nb_%s_soft" % state: livesynthesis["services_%s_soft" % state]})
                ss.update({"nb_" + state: ss["nb_%s_hard" % state] + ss["nb_%s_soft" % state]})
            for state in 'acknowledged', 'in_downtime', 'flapping':
                ss.update({
                    "pct_" + state: round(
                        100.0 * ss['nb_' + state] / ss['nb_elts'], 2
                    ) if ss['nb_elts'] else 0.0
                })
            ss.update({
                "nb_problems":
                ss["nb_warning_hard"] + ss["nb_critical_hard"]
            })
            for state in 'ok', 'warning', 'critical', 'unknown', 'unreachable':
                ss.update({
                    "pct_" + state: round(
                        100.0 * ss['nb_' + state] / ss['nb_elts'], 2
                    ) if ss['nb_elts'] else 0.0
                })
            for state in 'acknowledged', 'in_downtime', 'flapping', 'problems':
                ss.update({
                    "pct_" + state: round(
                        100.0 * ss['nb_' + state] / ss['nb_elts'], 2
                    ) if ss['nb_elts'] else 0.0
                })

            # Update history
            history.append(synthesis)
            logger.info("livesynthesis history hosts: %s, %d (%d/%d/%d/%d/%d)",
                        synthesis['_timestamp'],
                        synthesis['hosts_synthesis']['nb_elts'],
                        synthesis['hosts_synthesis']['nb_up'],
                        synthesis['hosts_synthesis']['nb_down'],
                        synthesis['hosts_synthesis']['nb_unreachable'],
                        synthesis['hosts_synthesis']['nb_acknowledged'],
                        synthesis['hosts_synthesis']['nb_in_downtime'])
            logger.info("livesynthesis history service: %s, %d (%d/%d/%d/%d/%d/%d)",
                        synthesis['_timestamp'],
                        synthesis['services_synthesis']['nb_elts'],
                        synthesis['services_synthesis']['nb_ok'],
                        synthesis['services_synthesis']['nb_warning'],
                        synthesis['services_synthesis']['nb_critical'],
                        synthesis['services_synthesis']['nb_unreachable'],
                        synthesis['services_synthesis']['nb_acknowledged'],
                        synthesis['services_synthesis']['nb_in_downtime'])

        return (synthesis, history)

    ##
    # Actions
    ##
    def add_acknowledge(self, data):
        """Request to acknowledge a problem."""
        logger.info("add_acknowledge, request an acknowledge, data: %s", data)
        return self.add_object('actionacknowledge', data)

    def add_recheck(self, data):
        """Request to re-check an host/service."""
        logger.info("add_recheck, request a recheck, data: %s", data)
        return self.add_object('actionforcecheck', data)

    def add_downtime(self, data):
        """Request to schedule a downtime."""
        logger.info("add_downtime, request a downtime, data: %s", data)
        return self.add_object('actiondowntime', data)

    def add_command(self, data):
        """Send an external command to Alignak."""
        logger.info("add_command, send a command, data: %s", data)
        try:
            result = self.alignak_ws.post('command', data)
        except AlignakWSException:
            return None

        return result

    ##
    # Hosts groups
    ##
    def get_hostgroups(self, search=None, all_elements=False):
        """Get a list of all hostgroups."""
        if search is None:
            search = {}
        if 'sort' not in search:
            search.update({'sort': '_level'})
        if 'embedded' not in search:
            search.update({
                'embedded': {
                    '_realm': 1, '_parent': 1, 'hostgroups': 1, 'hosts': 1
                }
            })

        try:
            logger.debug("get_hostgroups, search: %s", search)
            items = self.find_object('hostgroup', search, all_elements)
            return items
        except ValueError:  # pragma: no cover - should not happen
            logger.debug("get_hostgroups, none found")

        return []

    def get_hostgroup(self, search):
        """Get a hostgroup by its id."""
        if isinstance(search, basestring):
            search = {'max_results': 1, 'where': {'_id': search}}
        elif 'max_results' not in search:
            search.update({'max_results': 1})

        items = self.get_hostgroups(search=search)
        return items[0] if items else None

    def get_hostgroup_overall_state(self, hostgroup):
        """Get a hosts group real state (including hosts states).

        Returns a tuple with hostgroup overall state and status
        """
        logger.debug("get_hostgroup_overall_state, group: %s", hostgroup)
        if hostgroup.members == 'host':
            hostgroup.overall_state = 0
            return 0

        overall_state = 0
        for member in hostgroup.members:
            if isinstance(member, basestring):
                continue
            # Ignore hosts that are not monitored
            if member.overall_state < 5:
                overall_state = max(overall_state, member.overall_state)

        # Hosts group real state from group members
        group_members = self.get_hostgroups(
            search={'where': {'_parent': hostgroup.id}}, all_elements=True
        )
        for group in group_members:
            (ov_state, dummy) = self.get_hostgroup_overall_state(group)
            overall_state = max(overall_state, ov_state)

        overall_status = HostGroup.overall_state_to_status[overall_state]
        return (overall_state, overall_status)

    ##
    # Hosts dependencies
    ##
    def get_hostdependencys(self, search=None, all_elements=False):
        """Get a list of all host dependencies."""
        if search is None:
            search = {}
        if 'sort' not in search:
            search.update({'sort': 'name'})
        if 'embedded' not in search:
            search.update({
                'embedded': {
                    '_realm': 1,
                    'hosts': 1, 'hostgroups': 1,
                    'dependent_hosts': 1, 'dependent_hostgroups': 1,
                    'dependency_period': 1
                }
            })

        try:
            logger.debug("get_hostdependencys, search: %s", search)
            items = self.find_object('hostdependency', search, all_elements)
            return items
        except ValueError:  # pragma: no cover - should not happen
            logger.debug("get_hostdependencys, none found")

        return []

    def get_hostdependency(self, search):
        """Get a hostdependency by its id."""
        if isinstance(search, basestring):
            search = {'max_results': 1, 'where': {'_id': search}}
        elif 'max_results' not in search:
            search.update({'max_results': 1})

        items = self.get_hostdependencys(search=search)
        return items[0] if items else None

    ##
    # Hosts escalations
    ##
    def get_hostescalations(self, search=None, all_elements=False):
        """Get a list of all host escalations."""
        if search is None:
            search = {}
        if 'sort' not in search:
            search.update({'sort': 'name'})
        if 'embedded' not in search:
            search.update({
                'embedded': {
                    '_realm': 1,
                    'hosts': 1, 'hostgroups': 1,
                    'users': 1, 'usergroups': 1,
                    'escalation_period': 1
                }
            })

        try:
            logger.debug("get_hostescalations, search: %s", search)
            items = self.find_object('hostescalation', search, all_elements)
            return items
        except ValueError:  # pragma: no cover - should not happen
            logger.debug("get_hostescalations, none found")

        return []

    def get_hostescalation(self, search):
        """Get a hostescalation by its id."""
        if isinstance(search, basestring):
            search = {'max_results': 1, 'where': {'_id': search}}
        elif 'max_results' not in search:
            search.update({'max_results': 1})

        items = self.get_hostescalations(search=search)
        return items[0] if items else None

    ##
    # Hosts
    ##
    def get_hosts(self, search=None, template=False, all_elements=False, embedded=True):
        """Get a list of all hosts."""
        if search is None:
            search = {}
        if 'sort' not in search:
            search.update({'sort': 'name'})
        if 'where' not in search:
            search.update({'where': {'_is_template': template}})
        elif '_is_template' not in search['where']:
            search['where'].update({'_is_template': template})
        if embedded and 'embedded' not in search:
            search.update({
                'embedded': {
                    '_realm': 1, '_templates': 1,
                    'check_command': 1, 'snapshot_command': 1, 'event_handler': 1,
                    'check_period': 1, 'notification_period': 1,
                    'snapshot_period': 1, 'maintenance_period': 1,
                    'parents': 1, 'hostgroups': 1, 'users': 1, 'usergroups': 1
                }
            })

        try:
            logger.debug("get_hosts, search: %s", search)
            items = self.find_object('host', search, all_elements, embedded)
            return items
        except ValueError:  # pragma: no cover - should not happen
            logger.debug("get_hosts, none found")

        return []

    def get_host(self, search, embedded=True):
        """Get a host by its id (default)."""
        if isinstance(search, basestring):
            search = {'max_results': 1, 'where': {'_id': search}}
        elif 'max_results' not in search:
            search.update({'max_results': 1})

        items = self.get_hosts(search=search, embedded=embedded)
        return items[0] if items else None

    def get_host_services(self, host, search=None, embedded=True):
        """Get a host real state (including services states).

        Returns -1 if any problem
        """
        if not isinstance(host, BackendElement):
            host = self.get_host(host)
            if not host:
                return -1

        if search is None:
            search = {'where': {'host': host.id}}
        else:
            if 'where' in search:
                search['where'].update({'host': host.id})
            else:
                search.update({'where': {'host': host.id}})

        # Get host services
        return self.get_services(search=search, embedded=embedded, all_elements=True)

    def get_host_overall_state(self, host):
        # pylint: disable=no-self-use
        """Get a host real state (including services states).

        Returns a tuple with host overall state and status
        """
        return (host.overall_state, host.overall_status)

    ##
    # Services groups
    ##
    def get_servicegroups(self, search=None, all_elements=False):
        """Get a list of all servicegroups."""
        if search is None:
            search = {}
        if 'sort' not in search:
            search.update({'sort': 'name'})
        if 'embedded' not in search:
            search.update({
                'embedded': {
                    '_realm': 1, '_parent': 1, 'hostgroups': 1, 'hosts': 1
                }
            })

        try:
            logger.debug("get_servicegroups, search: %s", search)
            items = self.find_object('servicegroup', search, all_elements)
            return items
        except ValueError:  # pragma: no cover - should not happen
            logger.debug("get_servicegroups, none found")

        return []

    def get_servicegroup(self, search):
        """Get a servicegroup by its id."""
        if isinstance(search, basestring):
            search = {'max_results': 1, 'where': {'_id': search}}
        elif 'max_results' not in search:
            search.update({'max_results': 1})

        items = self.get_servicegroups(search=search)
        return items[0] if items else None

    def get_servicegroup_overall_state(self, servicegroup):
        """Get a services group real state (including services states).

        Returns a tuple with servicegroup overall state and status
        """
        logger.debug("get_servicegroup_overall_state, group: %s", servicegroup)
        if servicegroup.members == 'service':
            servicegroup.overall_state = 0
            return 0

        overall_state = 0
        for member in servicegroup.members:
            if isinstance(member, basestring):
                continue

            overall_state = max(overall_state, member.overall_state)

        # Hosts group real state from group members
        group_members = self.get_servicegroups(
            search={'where': {'_parent': servicegroup.id}}, all_elements=True
        )
        for group in group_members:
            (ov_state, dummy) = self.get_servicegroup_overall_state(group)
            overall_state = max(overall_state, ov_state)

        overall_status = servicegroup.overall_state_to_status[overall_state]
        return (overall_state, overall_status)

    ##
    # Services dependencies
    ##
    def get_servicedependencys(self, search=None, all_elements=False):
        """Get a list of all service dependencies."""
        if search is None:
            search = {}
        if 'sort' not in search:
            search.update({'sort': 'name'})
        if 'embedded' not in search:
            search.update({
                'embedded': {
                    '_realm': 1,
                    'hosts': 1, 'hostgroups': 1,
                    'dependent_hosts': 1, 'dependent_hostgroups': 1,
                    'services': 1, 'dependent_services': 1,
                    'dependency_period': 1
                }
            })

        try:
            logger.debug("get_servicedependencys, search: %s", search)
            items = self.find_object('servicedependency', search, all_elements)
            return items
        except ValueError:  # pragma: no cover - should not happen
            logger.debug("get_servicedependencys, none found")

        return []

    def get_servicedependency(self, search):
        """Get a servicedependency by its id."""
        if isinstance(search, basestring):
            search = {'max_results': 1, 'where': {'_id': search}}
        elif 'max_results' not in search:
            search.update({'max_results': 1})

        items = self.get_servicedependencys(search=search)
        return items[0] if items else None

    ##
    # Services escalations
    ##
    def get_serviceescalations(self, search=None, all_elements=False):
        """Get a list of all service escalations."""
        if search is None:
            search = {}
        if 'sort' not in search:
            search.update({'sort': 'name'})
        if 'embedded' not in search:
            search.update({
                'embedded': {
                    '_realm': 1,
                    'services': 1,
                    'hosts': 1, 'hostgroups': 1,
                    'users': 1, 'usergroups': 1,
                    'escalation_period': 1
                }
            })

        try:
            logger.debug("get_serviceescalations, search: %s", search)
            items = self.find_object('serviceescalation', search, all_elements)
            return items
        except ValueError:  # pragma: no cover - should not happen
            logger.debug("get_serviceescalations, none found")

        return []

    def get_serviceescalation(self, search):
        """Get a serviceescalation by its id."""
        if isinstance(search, basestring):
            search = {'max_results': 1, 'where': {'_id': search}}
        elif 'max_results' not in search:
            search.update({'max_results': 1})

        items = self.get_serviceescalations(search=search)
        return items[0] if items else None

    ##
    # Services
    ##
    def get_services(self, search=None, template=False, all_elements=False, embedded=True):
        """Get a list of all services."""
        if search is None:
            search = {}
        if 'sort' not in search:
            search.update({'sort': 'name'})
        if 'where' not in search:
            search.update({'where': {'_is_template': template}})
        elif '_is_template' not in search['where']:
            search['where'].update({'_is_template': template})
        if embedded and 'embedded' not in search:
            search.update({
                'embedded': {
                    # '_realm': 1,
                    '_templates': 1,
                    'host': 1,
                    'check_command': 1, 'snapshot_command': 1, 'event_handler': 1,
                    'check_period': 1, 'notification_period': 1,
                    'snapshot_period': 1, 'maintenance_period': 1,
                    'service_dependencies': 1, 'servicegroups': 1, 'users': 1, 'usergroups': 1
                }
            })

        try:
            logger.debug("get_services, search: %s", search)
            items = self.find_object('service', search, all_elements, embedded)
            return items
        except ValueError:  # pragma: no cover - should not happen
            logger.error("get_services, none found")

        return []

    def get_service(self, search):
        """Get a service by its id (default)."""
        if isinstance(search, basestring):
            search = {'max_results': 1, 'where': {'_id': search}}
        elif 'max_results' not in search:
            search.update({'max_results': 1})

        items = self.get_services(search=search)
        return items[0] if items else None

    def get_service_overall_state(self, service):
        # pylint: disable=no-self-use
        """Get a service real state (including services states).

        Returns a tuple with service overall state and status
        """
        return (service.overall_state, service.overall_status)

    def get_services_synthesis(self, elts=None):
        """Services synthesis by status"""
        logger.debug("get_services_synthesis, %d elements", len(elts))
        if elts is not None:
            services = [item for item in elts if item.get_type() == 'service']
        else:
            services = self.get_services()
        logger.debug("get_services_synthesis, %d services", len(services))

        synthesis = dict()
        synthesis['nb_elts'] = len(services)
        synthesis['nb_problem'] = 0
        for state in 'ok', 'warning', 'critical', 'unknown', 'acknowledged', 'in_downtime':
            synthesis['nb_' + state] = 0
            synthesis['pct_' + state] = 0

        if services:
            for state in 'ok', 'warning', 'critical', 'unknown', 'acknowledged', 'in_downtime':
                synthesis['nb_' + state] = 0
                for service in services:
                    if service.overall_status == state:
                        synthesis['nb_' + state] += 1
                if synthesis['nb_' + state] > 0:
                    synthesis['pct_' + state] = round(
                        100.0 * synthesis['nb_' + state] / synthesis['nb_elts'], 2
                    )
                else:
                    synthesis['pct_' + state] = 0

        logger.debug("get_services_synthesis: %s", synthesis)
        return synthesis

    def get_services_aggregated(self, elts=None):
        # pylint: disable=protected-access
        """Services by aggregation"""
        if elts:
            services = [item for item in elts if item.get_type() == 'service']
        else:
            services = self.get_services()
        logger.debug("get_services_aggregated, %d services", len(services))

        aggregations = {}
        for service in services:
            service.aggregation = service.aggregation

            if not service.aggregation:
                service.aggregation = _('Global')

            if service.aggregation in aggregations:
                service._level = aggregations[service.aggregation]['level']
                service._parent = service.aggregation
                continue

            if '/' not in service.aggregation:
                aggregations[service.aggregation] = {'level': 1, 'parent': '#'}
                service._level = aggregations[service.aggregation]['level']
                service._parent = service.aggregation
                continue

            splitted = service.aggregation.split('/')
            if len(splitted) > 2:
                logger.warning("Services aggregation only manages two levels. "
                               "Service %s will be aggregated with %s/%s",
                               service.name, splitted[0], splitted[1])

            if splitted[0] not in aggregations:
                aggregations[splitted[0]] = {'level': 1, 'parent': '#'}

            if splitted[1] not in aggregations:
                aggregations[splitted[1]] = {'level': 2, 'parent': splitted[0]}

            service._level = max(len(splitted), 2)
            service._parent = splitted[1]

        # Build tree for aggregations hierarchy
        tree_items = []
        for aggregation in aggregations:
            tree_item = {
                'id': aggregation,
                'parent': aggregations[aggregation]['parent'],
                'text': aggregation.capitalize(),
                'icon': 'fa fa-sitemap',
                'state': {
                    "opened": True,
                    "selected": False,
                    "disabled": False
                },
                'data': {
                    'status': 'none',
                    'name': aggregation,
                    'alias': aggregation,
                    '_level': aggregations[aggregation]['level'],
                    'type': 'node'
                }
            }
            tree_items.append(tree_item)

        # Get element state configuration
        items_states = ElementState()

        for service in services:
            cfg_state = items_states.get_icon_state('service', service.overall_status)
            if not cfg_state:
                cfg_state = {'icon': 'life-ring', 'class': 'unknown'}

            parent = 'host'
            if service._parent:
                parent = service._parent

            tree_item = {
                'id': service.id,
                'parent': parent,
                'text': service.alias,
                'icon': 'fa fa-%s item_%s' % (cfg_state['icon'], cfg_state['class']),
                'state': {
                    "opened": True,
                    "selected": False,
                    "disabled": False
                },
                'data': {
                    'status': service.status,
                    'name': service.name,
                    'alias': service.alias,
                    '_level': service._level,
                    'type': 'service'
                },
                # Attributes for the tree node <a>
                'a_attr': {},
                # Attributes for the tree node <li>
                'li_attr': {
                    'title': "%s - %s (%s)" % (service.status,
                                               Helper.print_duration(service.last_check,
                                                                     duration_only=True, x_elts=0),
                                               service.output),

                }
            }

            tree_items.append(tree_item)

        logger.debug("get_services_aggregated: %s", tree_items)
        return tree_items

    ##
    # Logs
    ##
    def get_logcheckresult(self, search=None):
        """Get log for all elements

            Elements in the log which type is 'host' or 'service'

            :param search: backend request search
            :type search: dic
            :return: list of hosts/services live states
            :rtype: list
            """
        if not search:
            search = {}
        if isinstance(search, basestring):
            search = {'max_results': 1, 'where': {'_id': search}}
        if "where" not in search:
            search.update({'where': {"last_check": {"$ne": 0}}})
        if "sort" not in search:
            search.update({'sort': '-business_impact,-state_id'})
        if 'embedded' not in search:
            search.update({'embedded': {'host': 1, 'service': 1}})

        try:
            logger.debug("get_logcheckresult, search: %s", search)
            items = self.find_object('logcheckresult', search)
            logger.debug("get_logcheckresult, got %s items", len(items))
            return items
        except ValueError:  # pragma: no cover - should not happen
            logger.debug("get_logcheckresult, none found")

    ##
    # History
    ##
    def get_history(self, search=None):
        """Get history

            :param search: backend request search
            :type search: dic
            :return: list of hosts/services live states
            :rtype: list
        """
        if not search:
            search = {}
        if isinstance(search, basestring):
            search = {'max_results': 1, 'where': {'_id': search}}
        if "sort" not in search:
            search.update({'sort': '-_id'})
        if 'embedded' not in search:
            search.update({'embedded': {'logcheckresult': 1}})

        try:
            logger.info("get_history, search: %s", search)
            items = self.find_object('history', search)
            logger.debug("get_history, got %s items", len(items))
            return items
        except ValueError:
            logger.debug("get_history, none found")

    ##
    # Commands
    ##
    def get_commands(self, search=None, all_elements=False):
        """Get a list of all commands."""
        if search is None:
            search = {}
        if 'sort' not in search:
            search.update({'sort': 'name'})
        # if 'embedded' not in search:
        #     search.update({
        #         'embedded': {
        #             '_realm': 1
        #         }
        #     })

        try:
            logger.debug("get_commands, search: %s", search)
            items = self.find_object('command', search, all_elements)
            return items
        except ValueError:  # pragma: no cover - should not happen
            logger.debug("get_commands, none found")

        return []

    def get_command(self, search):
        """Get a command by its id."""
        if isinstance(search, basestring):
            search = {'max_results': 1, 'where': {'_id': search}}
        elif 'max_results' not in search:
            search.update({'max_results': 1})

        items = self.get_commands(search=search)
        return items[0] if items else None

    ##
    # usergroups
    ##
    def get_usergroups(self, search=None, all_elements=False):
        """Get a list of all usergroups."""
        if search is None:
            search = {}
        if 'sort' not in search:
            search.update({'sort': '_level'})
        if 'embedded' not in search:
            search.update({
                'embedded': {
                    # '_realm': 1,
                    '_parent': 1
                }
            })

        try:
            logger.debug("get_usergroups, search: %s", search)
            items = self.find_object('usergroup', search, all_elements)
            return items
        except ValueError:  # pragma: no cover - should not happen
            logger.debug("get_usergroups, none found")

        return []

    def get_usergroup(self, search):
        """Get a usergroup by its id."""
        if isinstance(search, basestring):
            search = {'max_results': 1, 'where': {'_id': search}}
        elif 'max_results' not in search:
            search.update({'max_results': 1})

        items = self.get_usergroups(search=search)
        return items[0] if items else None

    ##
    # Users
    ##
    def get_userrestrictroles(self, search=None, all_elements=False):
        """Get a list of users restriction roles"""
        if search is None:
            search = {}
        if 'sort' not in search:
            search.update({'sort': 'user'})

        try:
            logger.debug("get_userrestrictroles, search: %s", search)
            items = self.find_object('userrestricrole', search, all_elements)
            return items
        except ValueError:  # pragma: no cover - should not happen
            logger.debug("get_userrestrictroles, none found")

        return []

    def get_userrestrictrole(self, search):
        """Get a userrestricrole by its id or a search pattern"""
        if isinstance(search, basestring):
            search = {'max_results': 1, 'where': {'_id': search}}
        elif 'max_results' not in search:
            search.update({'max_results': 1})

        items = self.get_userrestrictroles(search=search)
        return items[0] if items else None

    def get_users(self, search=None, template=False, all_elements=False):
        """Get a list of known users"""
        if not self.logged_in_user.is_super_administrator() \
                and not self.logged_in_user.is_administrator():
            return [self.logged_in_user]

        if search is None:
            search = {}
        if 'where' not in search:
            search.update({'where': {'_is_template': template}})
        elif '_is_template' not in search['where']:
            search['where'].update({'_is_template': template})
        if 'sort' not in search:
            search.update({'sort': 'name'})
        if 'embedded' not in search:
            search.update({
                'embedded': {
                    '_realm': 1, '_templates': 1,
                    'host_notification_period': 1, 'host_notification_commands': 1,
                    'service_notification_period': 1, 'service_notification_commands': 1
                }
            })

        try:
            logger.debug("get_users, search: %s", search)
            items = self.find_object('user', search, all_elements)
            return items
        except ValueError:  # pragma: no cover - should not happen
            logger.debug("get_users, none found")

        return []

    def get_user(self, search):
        """Get a user by its id or a search pattern"""
        if isinstance(search, basestring):
            search = {'max_results': 1, 'where': {'_id': search}}
        elif 'max_results' not in search:
            search.update({'max_results': 1})

        items = self.get_users(search=search)
        return items[0] if items else None

    ##
    # realms
    ##
    def get_realms(self, search=None, all_elements=False):
        """Get a list of all realms."""
        if search is None:
            search = {}
        if 'sort' not in search:
            search.update({'sort': 'name'})
        if 'embedded' not in search:
            search.update({
                'embedded': {
                    '_parent': 1
                }
            })

        try:
            logger.debug("get_realms, search: %s", search)
            items = self.find_object('realm', search, all_elements)
            return items
        except ValueError:  # pragma: no cover - should not happen
            logger.debug("get_realms, none found")

        return []

    def get_realm(self, search):
        """Get a realm by its id."""
        if isinstance(search, basestring):
            search = {'max_results': 1, 'where': {'_id': search}}
        elif 'max_results' not in search:
            search.update({'max_results': 1})

        logger.debug("get_realm, search: %s", search)
        items = self.get_realms(search=search)
        logger.debug("get_realm, got: %s", items)
        return items[0] if items else None

    def get_realm_members(self, realm):
        """Get a realm hosts

        :param realm: realm to get the hosts
        :return: list of hosts
        """
        logger.debug("get_realm_members, realm: %s", realm)

        return self.get_hosts(search={'where': {'_realm': realm.id}}, all_elements=True)

    def get_realm_children(self, realm):
        """Get a realm sub-realms

        :param realm: realm to get the sub-realms
        :return: list of sub-realms
        """
        logger.debug("get_realm_children, realm: %s", realm)

        # Realm sub-realms
        return self.get_realms(search={'sort': '_level',
                                       'where': {'_parent': realm.id}}, all_elements=True)

    def get_realm_overall_state(self, search):
        """Get a realm real state (including realm hosts states).

        Returns -1 if any problem
        """
        logger.debug("get_realm_overall_state, search: %s", search)
        if not isinstance(search, BackendElement):
            realm = self.get_realm(search)
            if not realm:
                return -1
        else:
            realm = search

        overall_state = 0
        # Realm real state from hosts
        hosts = self.get_realm_members(realm)
        for member in hosts:
            logger.debug("get_realm_overall_state, member: %s, state: %s",
                         member.name, member.overall_state)
            # Ignore hosts that are not monitored
            if member.overall_state < 5:
                overall_state = max(overall_state, member.overall_state)

        # Realm real state from sub-realms
        subs = self.get_realm_children(realm)
        for realm in subs:
            (ov_state, dummy) = self.get_realm_overall_state(realm)
            logger.debug("get_realm_overall_state, child: %s, state: %s",
                         realm.name, ov_state)
            overall_state = max(overall_state, ov_state)

        logger.warning("get_realm_overall_state, realm: %s, state: %s", realm.name, overall_state)
        overall_status = Realm.overall_state_to_status[overall_state]
        return (overall_state, overall_status)

    ##
    # timeperiods
    ##
    def get_timeperiods(self, search=None, all_elements=False):
        """Get a list of all timeperiods."""
        if search is None:
            search = {}
        if 'sort' not in search:
            search.update({'sort': 'name'})
        # if 'embedded' not in search:
        #     search.update({
        #         'embedded': {
        #             '_realm': 1
        #         }
        #     })

        try:
            logger.debug("get_timeperiods, search: %s", search)
            items = self.find_object('timeperiod', search, all_elements)
            return items
        except ValueError:
            logger.debug("get_timeperiods, none found")

        return []

    def get_timeperiod(self, search):
        """Get a timeperiod by its id."""
        if isinstance(search, basestring):
            search = {'max_results': 1, 'where': {'_id': search}}
        elif 'max_results' not in search:
            search.update({'max_results': 1})

        items = self.get_timeperiods(search=search)
        return items[0] if items else None
