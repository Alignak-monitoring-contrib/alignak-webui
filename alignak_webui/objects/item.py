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
    This module contains the classes used to manage the application objects with the data manager.
"""

import time
from datetime import datetime

import locale

import traceback
from logging import getLogger, INFO

from calendar import timegm
from dateutil import tz

from alignak_webui import get_app_config, _

# Import the backend interface class
from alignak_webui.objects.backend import BackendConnection
from alignak_backend_client.client import BackendException

from alignak_webui.utils.helper import Helper

# Set logger level to INFO, this to allow global application DEBUG logs without being spammed... ;)
logger = getLogger(__name__)
logger.setLevel(INFO)


class ItemState(object):    # pylint: disable=too-few-public-methods
    """
    Singleton design pattern ...
    """
    class __ItemState(object):
        """
        Base class for all objects state management (displayed icon, ...)
        """

        def __init__(self):
            self.states = None

            # Get global configuration
            app_config = get_app_config()
            if not app_config:  # pragma: no cover, should not happen
                return

            self.object_types_states = {}
            self.default_states = {}
            for s in app_config:
                s = s.split('.')
                if s[0] not in ['items']:
                    continue

                logger.debug("ItemState, item configuration element: %s", s)
                if s[1] == 'item':
                    if s[2] not in self.default_states:
                        self.default_states[s[2]] = []
                    continue

                if s[1] not in ['content', 'back', 'front', 'badge']:
                    if s[1] not in self.object_types_states:
                        self.object_types_states[s[1]] = []

                    if s[2] and s[2] not in self.object_types_states[s[1]]:
                        self.object_types_states[s[1]].append(s[2])

            logger.debug("ItemState, object types and states: %s", self.object_types_states)
            # print "Objects types: ", self.object_types_states
            logger.debug("ItemState, default states: %s", self.default_states)

            # Application locales, timezone, ...
            # Set timezones
            self.tz_from = tz.gettz('UTC')
            logger.debug(
                "Set default time zone: %s",
                app_config.get("timezone", 'Europe/Paris')
            )
            self.tz_to = tz.gettz(app_config.get("timezone", 'Europe/Paris'))

            # Set class date format
            logger.debug(
                "Set default time format string: %s",
                app_config.get("timeformat", '%Y-%m-%d %H:%M:%S')
            )
            self.date_format = app_config.get("timeformat", '%Y-%m-%d %H:%M:%S')

            # For each defined object type and object type state ...
            self.states = {}
            for object_type in self.object_types_states:
                self.states[object_type] = {}
                for state in self.object_types_states[object_type]:
                    self.states[object_type][state] = {}
                    for prop in ['text', 'icon', 'class']:
                        search = "items.%s.%s.%s" % (object_type, state, prop)
                        if "items.%s.%s.%s" % (object_type, state, prop) in app_config:
                            self.states[object_type][state][prop] = app_config.get(search)
                        else:  # pragma: no cover, should not happen
                            self.states[object_type][state][prop] = \
                                app_config.get("items.%s.%s" % (state, prop), '')

                # If no states is defined for element type, define default states ...
                # if not self.states:
                for state in self.default_states:
                    if state not in self.states[object_type]:
                        self.states[object_type][state] = {}
                        for prop in ['text', 'icon', 'class']:
                            self.states[object_type][state][prop] = \
                                app_config.get("items.item.%s.%s" % (state, prop), '')

                # Build a self state view with content, back and front templates
                self.states[object_type]['state_view'] = {}
                for prop in ['content', 'back', 'front', 'badge']:
                    search = "items.%s.%s" % (object_type, prop)
                    if "items.%s.%s" % (object_type, prop) in app_config:  # pragma: no cover
                        self.states[object_type]['state_view'][prop] = \
                            app_config.get(search)
                    else:
                        self.states[object_type]['state_view'][prop] = \
                            app_config.get("items.%s" % (prop))

                logger.debug(
                    " --- class configuration: %s: %s",
                    object_type, self.states[object_type]
                )

        def get_objects_types(self):
            """
                Return all the configured objects types

                All other object type will use the default 'item' configuration
            """
            return [s for s in self.states]

        def get_icon_states(self, object_type=None):
            """ Return all the configured states for an object type """
            if not object_type:
                return self.states
            if object_type in self.states:
                return self.states[object_type]
            return []

        def get_default_states(self):
            """ Return all the configured states for a generic item """
            return [s for s in self.default_states]

        def get_icon_state(self, object_type, status):
            """ Return the configured state for an object type """
            if not object_type or not status:
                return None

            if status not in self.get_icon_states(object_type):
                return None

            for s in self.get_icon_states(object_type):
                if status == s:
                    return self.get_icon_states(object_type)[s]

        def get_html_state(self, object_type, object_item, extra='', icon=True, text='',
                           title='', disabled=False):
            # pylint: disable=too-many-arguments
            # Yes, but it is needed ;)
            # pylint: disable=too-many-locals, too-many-return-statements
            # Yes, but else it will be quite difficult :/
            """
            Returns an item status as HTML text and icon if needed

            If parameters are not valid, returns 'n/a'

            If disabled is True, the class does not depend upon object status and is always
            font-greyed

            If a title is specified, it will be used instead of the default built-in text.

            If object status contains '.' characters they are replaced with '_'

            Text and icon are defined in the application configuration file.

            :param object_type: element type
            :type object_type: string
            :param object_item: element
            :type object: Item class based object

            :param extra: extra string replacing ##extra##, and set opacity to 0.5
            :type extra: string

            :param text: include text in the response
            :type text: string
            :param icon: include icon in the response
            :type icon: boolean
            :return: formatted status HTML string
            :rtype: string
            """
            if not object_type:  # pragma: no cover, should not happen
                return 'n/a - element'

            if not object_item:  # pragma: no cover, should not happen
                return 'n/a - object'

            if not icon and not text:
                return 'n/a - icon/text'

            status = object_item.status
            status = status.replace('.', '_').lower()
            if object_type in self.get_objects_types():
                if status not in self.get_icon_states(object_type):
                    return 'n/a - status: ' + status
            else:
                if status not in self.get_default_states():  # pragma: no cover, should not happen
                    return 'n/a - default status: ' + status

            cfg_state = self.get_icon_state(object_type, status)
            if object_type not in self.get_objects_types() and status in self.get_default_states():
                cfg_state = self.get_icon_state("user", status)
            logger.debug("get_html_state, states: %s", cfg_state)

            cfg_state_view = self.get_icon_state(object_type, 'state_view')
            if object_type not in self.get_objects_types():
                cfg_state_view = self.get_icon_state("user", 'state_view')
            if not cfg_state_view:  # pragma: no cover, should not happen
                return 'n/a - cfg_state_view'
            # logger.debug("get_html_state, states view: %s", cfg_state_view)

            # Text
            res_icon_state = cfg_state['icon']
            res_icon_text = cfg_state['text']
            res_icon_class = 'item_' + cfg_state['class']
            res_text = res_icon_text

            if not icon:
                if text == '':
                    return res_text
                else:
                    return text

            # Icon
            res_icon_global = cfg_state_view['content']
            res_icon_back = cfg_state_view['back']
            res_icon_front = cfg_state_view['front']

            res_extra = "fa-inverse"
            if extra:
                res_extra = extra
            res_opacity = ""
            if extra:
                res_opacity = 'style="opacity: 0.5"'

            # Assembling ...
            item_id = object_item.id
            res_icon = res_icon_global
            res_icon = res_icon.replace("##type##", object_type)
            res_icon = res_icon.replace("##id##", item_id)
            res_icon = res_icon.replace("##name##", object_item.name)
            res_icon = res_icon.replace("##state##", object_item.get_state())
            res_icon = res_icon.replace("##back##", res_icon_back)
            res_icon = res_icon.replace("##front##", res_icon_front)
            res_icon = res_icon.replace("##status##", status.lower())
            if not disabled:
                res_icon = res_icon.replace("##class##", res_icon_class)
            else:
                res_icon = res_icon.replace("##class##", "font-greyed")

            res_icon = res_icon.replace("##icon##", res_icon_state)
            res_icon = res_icon.replace("##extra##", res_extra)
            res_icon = res_icon.replace("##opacity##", res_opacity)

            if not title:
                title = res_text

            if text is None:
                res_text = ''
            elif text != '':
                res_text = text

            res_icon = res_icon.replace("##title##", title)
            res_icon = res_icon.replace("##text##", res_text)

            logger.debug("get_html_state, res_icon: %s", res_icon)
            res_icon = res_icon.replace("\n", "")
            res_icon = res_icon.replace("\r", "")
            return res_icon

    instance = None

    def __new__(cls):
        if not ItemState.instance:
            ItemState.instance = ItemState.__ItemState()
        return ItemState.instance

    def get_html_state(self, extra='', icon=True, text='',
                       title='', disabled=False,
                       object_type='', object_item=None):  # pragma: no cover
        # pylint: disable=too-many-arguments
        """
        Base function used by Item objects
        """
        return self.instance.get_html_state(object_type, object_item,
                                            extra, icon, text, title, disabled)


class Item(object):
    # Yes, but it is the base object and it needs those pubic methods!
    # pylint: disable=too-many-public-methods
    """
    Base class for all the data manager objects

    An Item is created from a dictionary with some specific features:
    - an item has an identifier, a name, an alias and a comment (notes)
    - some specific treatments are applied on some specific fields (see _create method doc)
    - all objects are cached internally to avoid creating several instances for the same element

    If no identifier attribute exists in the provided data an automatic identifier is assigned.

    Manages links between Item objects base upon some specific fields.

    !!!!! TO BE COMPLETED !!!!!
    """
    _count = 0
    _total_count = -1

    _backend = None
    _known_classes = None

    # Next value used for auto generated id
    _next_id = 1
    # _type stands for Backend Object Type
    _type = 'item'
    # _cache is a list of created objects
    _cache = {}

    # Default date used for bad formatted string dates
    _default_date = 0

    # Dates fields: list of the attributes to be considered as dates
    _dates = ['_created', '_updated']

    # Items states
    items_states = [
        # Ok
        "ok",
        # Warning
        "warning",
        # Critical
        "critical",
        # Unknown
        "unknown",
        # Not executed
        "not_executed"
    ]

    @classmethod
    def getKnownClasses(cls):
        """ Get protected member """
        return cls._known_classes

    @classmethod
    def setKnownClasses(cls, known_classes):
        """ Set protected member _known_classes """
        cls._known_classes = known_classes

    @classmethod
    def getBackend(cls):
        """ Get protected member """
        return cls._backend

    @classmethod
    def setBackend(cls, backend):
        """ Set protected member _backend """
        cls._backend = backend

    @classmethod
    def getType(cls):
        """ Get protected member """
        return cls._type

    @classmethod
    def getCount(cls):
        """ Get protected member """
        return cls._count

    @classmethod
    def getTotalCount(cls):
        """ Get protected member """
        return cls._total_count

    @classmethod
    def getCache(cls):
        """ Get protected member """
        return cls._cache

    @classmethod
    def cleanCache(cls):
        """
        Clean internal objects cache and reset the internal counters
        """
        cls._next_id = 1
        cls._count = 0
        cls._total_count = -1
        cls._cache = {}

    def __new__(cls, params=None, date_format='%a, %d %b %Y %H:%M:%S %Z'):
        """
        Create a new object

        If the provided arguments have a params dictionary that include an _id field,
        this field will be used as an unique object identifier. else, an auto generated
        _id field will be used to identify uniquely an object. If no parameters are provided
        a dummy _id==0 object will be created and used for each non parameters call.

        As of it, each new declaration without any parameter do not always create a new object!

        To reuse the dummy _id=0 object, specify '_id': '0' in the parameters.

        A newly created object is included in the global class _cache list that maintain a
        unique objects list for each class. If the new object identifier still exists in the
        unique objects list, no new object is created and the existing object is returned.

        Note: the _id attribute is always a string. If not, it is forced to be ...

        This function raises a ValueError exception if the first parameter is not a dictionary.
        """
        id_property = getattr(cls, 'id_property', '_id')
        # print "Class %s, id_property: %s, params: %s" % (cls, id_property, params)

        if not cls.getBackend():
            # Get global configuration
            app_config = get_app_config()
            if not app_config:  # pragma: no cover, should not happen
                return

            cls._backend = BackendConnection(
                app_config.get('alignak_backend', 'http://127.0.0.1:5000')
            )
            # print "Class backend: %s" % (cls.getBackend())

        _id = '0'
        if params:
            if not isinstance(params, dict):
                print "Class %s, id_property: %s, params: %s" % (cls, id_property, params)
                raise ValueError(
                    '%s.__new__: object parameters must be a dictionary!' % (
                        cls._type
                    )
                )

            if id_property in params:
                if not isinstance(params[id_property], basestring):
                    params[id_property] = str(params[id_property])
                _id = params[id_property]
            else:
                _id = '%s_%d' % (cls.getType(), cls._next_id)
                params[id_property] = _id
                cls._next_id += 1

        if _id == '0':
            if not params:
                params = {}
            # Force _id in the parameters
            params.update({id_property: '%s_0' % (cls.getType())})

        if _id not in cls._cache:
            # print "Create a new %s (%s)" % (cls.getType(), _id)
            cls._cache[_id] = super(Item, cls).__new__(cls, params, date_format)
            cls._cache[_id]._type = cls.getType()
            cls._cache[_id]._default_date = cls._default_date
            # print " ... new: %s" % cls._cache[_id]

            # Call the new object create function
            cls._cache[_id]._create(params, date_format)
            # print " ... created: %s" % cls._cache[_id]
            cls._count += 1
        else:
            if params != cls._cache[_id].__dict__:
                # print "Update existing instance for: ", cls._cache[_id]
                cls._cache[_id]._update(params, date_format)

        return cls._cache[_id]

    def __del__(self):
        """
        Delete an object (called only when no more reference exists for an object)
        """
        logger.debug(" --- deleting a %s (%s)", self.__class__, self._id)

    def _delete(self):
        """
        Delete an object

        If the object exists in the cache, its reference is removed from the internal cache.
        """
        logger.debug(" --- deleting a %s (%s)", self.__class__, self._id)
        cls = self.__class__
        if self._id in cls._cache:
            logger.debug("Removing from cache...")
            del cls._cache[self._id]
            cls._count -= 1
            logger.debug(
                "Removed. Remaining in cache: %d / %d",
                cls.getCount(), len(cls.getCache())
            )

    def _create(self, params, date_format):
        """
        Create an object (called only once when an object is newly created)

        Some specificities:
        1/ dates
            Parameters which name ends with date are considered as dates.
            _created and _updated parameters also.

            Accept dates as:
             - float (time.now()) as timestamp
             - formatted string as '%a, %d %b %Y %H:%M:%S %Z' (Tue, 01 Mar 2016 14:15:38 GMT)
             - else use date_format parameter to specify date string format

            If date can not be converted, parameter is set to a default date defined in the class

        2/ dicts
            If the object has declared some '_linked_XXX' prefixed attributes and the paramaters
            contain an 'XXX' field, this function creates a new object in the '_linked_XXX'
            attribute. The initial '_linked_XXX' attribute must contain the new object type!

            If the attribute is a simple dictionary, the new attribute contains the dictionary.

            This feature allows to create links between embedded objects of the backend.
        """
        id_property = getattr(self.__class__, 'id_property', '_id')
        if id_property not in params:  # pragma: no cover, should never happen
            raise ValueError('No %s attribute in the provided parameters' % id_property)
        logger.debug(
            " --- creating a %s (%s - %s)",
            self.getType(), params[id_property], params['name'] if 'name' in params else ''
        )

        for key in params:  # pylint: disable=too-many-nested-blocks
            logger.debug(" parameter: %s (%s) = %s", key, params[key].__class__, params[key])
            # print(" parameter: %s (%s) = %s", key, params[key].__class__, params[key])
            # Object must have declared a _linked_ attribute ...
            if hasattr(self, '_linked_' + key) and self.getKnownClasses():
                logger.debug(
                    " link parameter: %s (%s) = %s", key, params[key].__class__, params[key]
                )
                # Linked resource type
                object_type = getattr(self, '_linked_' + key, None)
                if object_type not in [kc.getType() for kc in self.getKnownClasses()]:
                    logger.error("_create, unknown %s for %s", object_type, params[key])
                    continue

                object_class = [kc for kc in self.getKnownClasses()
                                if kc.getType() == object_type][0]

                # Dictionary - linked object attributes (backend embedded object)
                if isinstance(params[key], dict):
                    linked_object = object_class(params[key])
                    setattr(self, '_linked_' + key, linked_object)
                    logger.debug("_create, linked with %s (%s)", key, linked_object['_id'])
                    continue

                # String - object id
                if isinstance(params[key], basestring) and self.getBackend():
                    # we need to load the object from the backend
                    result = self.getBackend().get(object_type + '/' + params[key])
                    if not result:
                        logger.error(
                            "_create, item not found for %s, %s", object_type, params[key]
                        )
                        continue

                    # Create a new object
                    linked_object = object_class(result)
                    setattr(self, '_linked_' + key, linked_object)
                    logger.debug("_create, linked with %s (%s)", key, linked_object['_id'])
                    continue

                # List - list of objects id
                if isinstance(params[key], list):
                    objects_list = []
                    for element in params[key]:
                        if isinstance(element, basestring) and self.getBackend():
                            # we need to load the object from the backend
                            result = self.getBackend().get(object_type + '/' + element)
                            if not result:
                                logger.error(
                                    "_create, item not found for %s, %s", object_type, params[key]
                                )
                                continue

                            # Create a new object
                            objects_list.append(object_class(result))
                        else:
                            logger.critical(
                                "_create, list element %s is not a string: %s", key, element
                            )

                    setattr(self, '_linked_' + key, objects_list)
                    logger.debug("_create, linked with %s (%s)", key, [o for o in objects_list])
                    continue

                logger.warning(
                    "Parameter: %s for %s is not a dict or a list or an object id "
                    "as it should be, instead of being: %s",
                    key, self.getType(), params[key]
                )
                continue

            # If the property is a known date, make it a timestamp...
            if key.endswith('date') or key in self.__class__._dates:
                if params[key]:
                    if isinstance(params[key], (int, long, float)):
                        # Date is received as a float or integer, store as a timestamp ...
                        # ... and assume it is UTC
                        # ----------------------------------------------------------------
                        setattr(self, key, params[key])
                    elif isinstance(params[key], basestring):
                        try:
                            # Date is supposed to be received as string formatted date
                            timestamp = timegm(time.strptime(params[key], date_format))
                            setattr(self, key, timestamp)
                        except ValueError:
                            logger.warning(
                                " parameter: %s = '%s' is not a valid string format: '%s'",
                                key, params[key], date_format
                            )
                            setattr(self, key, self.__class__._default_date)
                    else:
                        try:
                            # Date is supposed to be received as a struct time ...
                            # ... and assume it is local time!
                            # ----------------------------------------------------
                            timestamp = timegm(params[key].timetuple())
                            setattr(self, key, timestamp)
                        except TypeError:  # pragma: no cover, simple protection
                            logger.warning(
                                " parameter: %s is not a valid time tuple: '%s'",
                                key, params[key]
                            )
                            setattr(self, key, self.__class__._default_date)
                else:
                    setattr(self, key, self.__class__._default_date)
                continue

            try:
                setattr(self, key, params[key])
            except Exception:
                logger.critical(" parameter TypeError: %s = %s", key, params[key])

        # Object name
        if not hasattr(self, 'name'):
            setattr(self, 'name', 'anonymous')

        # Object alias
        if not hasattr(self, 'alias'):
            setattr(self, 'alias', '')

        # Object notes
        if not hasattr(self, 'notes'):
            setattr(self, 'notes', '')

        # Object status
        if not hasattr(self, 'status'):
            setattr(self, 'status', 'unknown')

        logger.debug(" --- created %s (%s): %s", self.__class__, self[id_property], self.__dict__)

    def _update(self, params, date_format='%a, %d %b %Y %H:%M:%S %Z'):
        # pylint: disable=too-many-nested-blocks
        id_property = getattr(self.__class__, 'id_property', '_id')

        logger.debug(" --- updating a %s (%s)", self.object_type, self[id_property])

        if not isinstance(params, dict):
            if self.__class__ == params.__class__:
                params = params.__dict__
            elif self.getKnownClasses() and params.__class__ in self.getKnownClasses():
                params = params.__dict__
            else:
                logger.critical(
                    "_update, cannot update an object with: %s (%s)", params, params.__class__
                )
                return

        for key in params:
            logger.debug(" --- parameter %s = %s", key, params[key])
            if hasattr(self, '_linked_' + key):
                logger.debug(
                    "link parameter: %s (%s) = %s", key, params[key].__class__, params[key]
                )
                object_type = getattr(self, '_linked_' + key, None)
                if not isinstance(object_type, basestring):
                    # Already contains an object, so update object ...
                    logger.debug("_update, update object: %s = %s", key, params[key])
                    # object_type._update(params[key])
                    continue

                # Linked resource type
                logger.debug(
                    "_update, must create link for %s/%s with %s ",
                    self.object_type, key, params[key]
                )
                # No object yet linked...
                if object_type not in [kc.getType() for kc in self.getKnownClasses()]:
                    logger.error("_update, unknown %s for %s", object_type, params[key])
                    continue

                object_class = [kc for kc in self.getKnownClasses()
                                if kc.getType() == object_type][0]

                # String - object id
                if isinstance(params[key], basestring) and self.getBackend():
                    # Object link is a string, so it contains the object type
                    object_type = getattr(self, '_linked_' + key, None)
                    if object_type not in [kc.getType() for kc in self.getKnownClasses()]:
                        logger.error("_update, unknown %s for %s", object_type, params[key])
                        continue

                    object_class = [kc for kc in self.getKnownClasses()
                                    if kc.getType() == object_type][0]

                    # Object link is a string, so we need to load the object from the backend
                    result = self.getBackend().get(object_type + '/' + params[key])
                    if not result:
                        logger.error(
                            "_update, item not found for %s, %s", object_type, params[key]
                        )
                        continue

                    # Create a new object
                    linked_object = object_class(result)
                    setattr(self, '_linked_' + key, linked_object)
                    logger.warning("_update, linked with %s (%s)", key, linked_object['_id'])
                    continue

                # List - list of objects id
                if isinstance(params[key], list):
                    objects_list = []
                    for element in params[key]:
                        if isinstance(element, basestring) and self.getBackend():
                            # we need to load the object from the backend
                            result = self.getBackend().get(object_type + '/' + element)
                            if not result:
                                logger.error(
                                    "_update, item not found for %s, %s", object_type, params[key]
                                )
                                continue

                            # Create a new object
                            objects_list.append(object_class(result))
                        elif isinstance(element, dict):
                            objects_list.append(object_class(element))
                        else:
                            logger.critical(
                                "_update, list element %s is not a string nor a dict: %s",
                                key, element
                            )

                    setattr(self, '_linked_' + key, objects_list)
                    logger.info("_update, linked with %s (%s)", key, [o for o in objects_list])
                    continue

                continue

            # If the property is a date, make it a timestamp...
            if key.endswith('date') or key in self.__class__._dates:
                if params[key]:
                    if isinstance(params[key], (int, long, float)):
                        # Date is received as a float or integer, store as a timestamp ...
                        # ... and assume it is UTC
                        # ----------------------------------------------------------------
                        setattr(self, key, params[key])
                    elif isinstance(params[key], basestring):
                        try:
                            # Date is supposed to be received as string formatted date
                            timestamp = timegm(time.strptime(params[key], date_format))
                            setattr(self, key, timestamp)
                        except ValueError:
                            logger.warning(
                                " parameter: %s = '%s' is not a valid string format: '%s'",
                                key, params[key], date_format
                            )
                            setattr(self, key, self.__class__._default_date)
                    else:
                        try:
                            # Date is supposed to be received as a struct time ...
                            # ... and assume it is local time!
                            # ----------------------------------------------------
                            timestamp = timegm(params[key].timetuple())
                            setattr(self, key, timestamp)
                        except TypeError:  # pragma: no cover, simple protection
                            logger.warning(
                                " parameter: %s is not a valid time tuple: '%s'",
                                key, params[key]
                            )
                            setattr(self, key, self.__class__._default_date)
                else:
                    setattr(self, key, self.__class__._default_date)
                continue

            try:
                setattr(self, key, params[key])
            except TypeError:  # pragma: no cover, should not happen
                logger.critical(" parameter TypeError: %s = %s", key, params[key])

    def __init__(self, params=None, date_format='%a, %d %b %Y %H:%M:%S %Z'):
        """
        Initialize an object

        Beware: always called, even if the object is not newly created! Use _create function for
        initializing newly created objects.
        """
        id_property = getattr(self.__class__, 'id_property', '_id')

        logger.debug(" --- initializing a %s (%s)", self._type, self[id_property])
        logger.debug(" --- initializing with %s and %s", params, date_format)

    def __repr__(self):
        return ("<%s, id: %s, name: %s, status: %s>") % (
            self.__class__._type, self.id, self.name, self.status
        )

    def __getitem__(self, key):
        return getattr(self, key, None)

    @property
    def object_type(self):
        """
        Get Item object type
        """
        return self._type

    @property
    def id(self):
        """
        Get Item object identifier
        A class inheriting from an Item can define its own `id_property`
        """
        if hasattr(self.__class__, 'id_property'):
            return getattr(self, self.__class__.id_property, None)
        return self._id

    @property
    def name(self):
        """
        Get Item object name
        A class inheriting from an Item can define its own `name_property`
        """
        if hasattr(self.__class__, 'name_property'):
            return getattr(self, self.__class__.name_property, None)
        return self._name

    @property
    def endpoint(self):
        """
        Get Item endpoint (page url)
        """
        return '/%s/%s' % (self.object_type, self.id)

    @property
    def html_link(self):
        """
        Get Item html link
        """
        return '<a href="%s">%s</a>' % (self.endpoint, self.alias)

    @property
    def html_state_link(self):
        """
        Get Item html link
        """
        return '<a href="%s">%s</a>' % (self.endpoint, self.get_html_state(
            text=self.alias, title=self.alias
        ))

    @name.setter
    def name(self, name):
        """
        Set Item object name
        """
        if hasattr(self.__class__, 'name_property'):
            setattr(self, self.__class__.name_property, name)
        else:
            self._name = name

    @property
    def alias(self):
        """
        Get Item object alias
        A class inheriting from an Item can define its own `name_property`
        """
        if hasattr(self, 'alias') and getattr(self, '_alias', None):
            return getattr(self, '_alias', None)
        return getattr(self, 'name', '')

    @alias.setter
    def alias(self, alias):
        """
        Set Item object alias
        """
        self._alias = alias

    @property
    def notes(self):
        """
        Get Item object notes
        A class inheriting from an Item can define its own `comment_property`
        """
        if hasattr(self.__class__, 'comment_property'):
            return getattr(self, self.__class__.comment_property, None)
        return self._comment

    @notes.setter
    def notes(self, notes):
        """
        Get Item object notes
        A class inheriting from an Item can define its own `comment_property`
        """
        if hasattr(self.__class__, 'comment_property'):
            setattr(self, self.__class__.comment_property, notes)
        else:
            self._comment = notes

    @property
    def status(self):
        """
        Get Item object status
        A class inheriting from an Item can define its own `status_property`
        """
        if hasattr(self.__class__, 'status_property'):
            return getattr(self, self.__class__.status_property, None)
        return self._status

    @status.setter
    def status(self, status):
        """
        Get Item object status
        A class inheriting from an Item can define its own `status_property`
        """
        if hasattr(self.__class__, 'status_property'):
            setattr(self, self.__class__.status_property, status)
        else:
            self._status = status

    def get_state(self):
        """
        Get Item object state
        A class inheriting from an Item can define its own `state_property`

        !!!!! TO BE COMPLETED !!!!
        """
        state = getattr(self, 'state', 99)
        if isinstance(state, int):
            try:
                return self.__class__.items_states[state]
            except IndexError:
                return ''
        return state

    def get_icon_states(self):
        """
        Uses the ItemState singleton to get configured states for an item
        """
        item_state = ItemState()
        return item_state.get_icon_states()

    def get_html_state(self, extra='', icon=True, text='',
                       title='', disabled=False, object_type=None, object_item=None):
        # pylint: disable=too-many-arguments
        """
        Uses the ItemState singleton to display HTML state for an item
        """
        if not object_type:
            object_type = self.object_type

        if not object_item:
            object_item = self

        return ItemState().get_html_state(object_type, object_item,
                                          extra, icon, text, title, disabled)

    def get_date(self, _date, fmt=None, duration=False):
        """
        Format the provided `_date` as a string according to the specified format.

        If no date format is specified, it uses the one defined in the ItemState object that is
        the date format defined in the application configuration.

        If duration is True, the date is displayed as a pretty date: 1 day 12 minutes ago ...
        """
        if _date == self.__class__._default_date:
            return _('Never dated!')

        if duration:
            return Helper.print_duration(_date, duration_only=False, x_elts=0)

        if not fmt:
            item_state = ItemState()
            if item_state.date_format:
                fmt = item_state.date_format

        # Make timestamp to datetime
        _date = datetime.utcfromtimestamp(_date)
        # Tell the datetime object that it's in UTC time zone since
        # datetime objects are 'naive' by default
        _date = _date.replace(tzinfo=item_state.tz_from)
        # Convert to required time zone
        _date = _date.astimezone(item_state.tz_to)

        if fmt:
            return _date.strftime(fmt)

        return _date.isoformat(' ')


class Realm(Item):
    """
    Object representing a realm
    """
    _count = 0
    # Next value used for auto generated id
    _next_id = 1
    # _type stands for Backend Object Type
    _type = 'realm'
    # _cache is a list of created objects
    _cache = {}

    def __new__(cls, params=None, date_format='%a, %d %b %Y %H:%M:%S %Z'):
        """
        Constructor
        """
        return super(Realm, cls).__new__(cls, params, date_format)

    def _create(self, params, date_format):
        """
        Create a realm (called only once when an object is newly created)
        """
        super(Realm, self)._create(params, date_format)

    def _update(self, params=None, date_format='%a, %d %b %Y %H:%M:%S %Z'):
        """
        Update a realm (called every time an object is updated)
        """
        super(Realm, self)._update(params, date_format)

    def __init__(self, params=None):
        """
        Initialize a realm (called every time an object is invoked)
        """
        super(Realm, self).__init__(params)


class User(Item):
    """
    Object representing a user
    """
    _count = 0
    # Next value used for auto generated id
    _next_id = 1
    # _type stands for Backend Object Type
    _type = 'user'
    # _cache is a list of created objects
    _cache = {}

    # Displayable strings for the user role
    roles = {
        "user": _("User"),
        "power": _("Power user"),
        "administrator": _("Administrator")
    }

    def __new__(cls, params=None, date_format='%a, %d %b %Y %H:%M:%S %Z'):
        """
        Create a new user
        """
        return super(User, cls).__new__(cls, params, date_format)

    def _create(self, params, date_format):
        # Not that bad ... because _create is called from __new__
        # pylint: disable=attribute-defined-outside-init
        """
        Create a user (called only once when an object is newly created)
        """
        if params and 'can_submit_commands' in params:
            params['read_only'] = False
            params.pop('can_submit_commands', None)

        super(User, self)._create(params, date_format)

        self.authenticated = False

        # Is an administrator ?
        if not hasattr(self, 'is_admin'):
            self.is_admin = False

        # Can submit commands
        if not hasattr(self, 'read_only'):
            self.read_only = True

        # Can change dashboard
        if not hasattr(self, 'widgets_allowed'):
            self.widgets_allowed = False

        # Has a role ?
        if not hasattr(self, 'role'):
            self.role = self.get_role()

        if not hasattr(self, 'picture'):
            self.picture = '/static/images/user_default.png'
            if self.name == 'anonymous':
                self.picture = '/static/images/user_guest.png'
            else:
                if self.is_admin:
                    self.picture = '/static/images/user_admin.png'

    def _update(self, params=None, date_format='%a, %d %b %Y %H:%M:%S %Z'):
        """
        Update a user (called every time an object is updated)
        """
        if params and 'can_submit_commands' in params:
            params['read_only'] = False
            params.pop('can_submit_commands', None)

        super(User, self)._update(params, date_format)

    def __init__(self, params=None):
        """
        Initialize a user (called every time an object is invoked)
        """
        self.role = None
        super(User, self).__init__(params)

    def __repr__(self):
        if hasattr(self, 'authenticated') and self.authenticated:
            return ("<Authenticated %s, id: %s, name: %s, role: %s>") % (
                self.__class__._type, self.id, self.name, self.get_role()
            )
        return ("<%s, id: %s, name: %s, role: %s>") % (
            self.__class__._type, self.id, self.name, self.get_role()
        )

    @property
    def endpoint(self):
        """
        Overload default property. Link to the main objects page with an anchor.
        """
        return '/%ss#%s' % (self.object_type, self.id)

    def get_username(self):
        """
        Get the user username (for login).
        Returns the 'username' field if it exisrs, else returns  the 'name' field,
        else returns  the 'name' field
        """
        return getattr(self, 'username', self.name)

    def get_role(self, display=False):
        """
        Get the user role.
        If user role is not defined, set the property according to the user attributes:
        - role='administrator' if the user is an administrator
        - role='power' if the user can submit commands
        - role='user' else

        If the display parameter is set, the function returns a displayable string else it
        returns the defined role property
        """
        if not getattr(self, 'role', None):
            if self.is_administrator():
                self.role = 'administrator'
            elif self.can_submit_commands():
                self.role = 'power'
            else:
                self.role = 'user'

        if display and self.role in self.__class__.roles:
            return self.__class__.roles[self.role]

        return self.role

    def is_anonymous(self):
        """
        An anonymous user is created when no 'name' attribute exists for the user ... 'anonymous'
        is the default value of the Item name property.
        """
        return self.name == 'anonymous'

    def is_administrator(self):
        """
        Is user an administrator?
        """
        if getattr(self, 'back_role_super_admin', None):
            return self.back_role_super_admin
        return self.is_admin

    def can_submit_commands(self):
        """
        Is allowed to use commands?
        """
        if self.is_administrator():
            return True

        if isinstance(self.read_only, bool):
            return not self.read_only
        else:
            return not getattr(self, 'read_only', '0') == '1'

    def can_change_dashboard(self):
        """
        Can the use change dashboard (edit widgets,...)?
        """
        if self.is_administrator():
            return True

        if hasattr(self, 'widgets_allowed'):
            if isinstance(self.widgets_allowed, bool):
                return self.widgets_allowed
            else:
                return getattr(self, 'widgets_allowed', '0') == '1'

        return False


class UserGroup(Item):
    """
    Object representing a user group
    """
    _count = 0
    # Next value used for auto generated id
    _next_id = 1
    # _type stands for Backend Object Type
    _type = 'usergroup'
    # _cache is a list of created objects
    _cache = {}

    def __new__(cls, params=None, date_format='%a, %d %b %Y %H:%M:%S %Z'):
        """
        Create a new contactgroup
        """
        return super(UserGroup, cls).__new__(cls, params, date_format)

    def _create(self, params, date_format):
        """
        Create a contactgroup (called only once when an object is newly created)
        """
        self._linked_contactgroup_members = 'contactgroup'
        self._linked_members = 'contact'

        super(UserGroup, self)._create(params, date_format)

    def _update(self, params=None, date_format='%a, %d %b %Y %H:%M:%S %Z'):
        """
        Update a contactgroup (called every time an object is updated)
        """
        super(UserGroup, self)._update(params, date_format)

    def __init__(self, params=None):
        """
        Initialize a contactgroup (called every time an object is invoked)
        """
        super(UserGroup, self).__init__(params)

    @property
    def members(self):
        """ Return linked object """
        return self._linked_members

    @property
    def contactgroup_members(self):
        """ Return linked object """
        return self._linked_contactgroup_members


class LiveSynthesis(Item):
    """
    Object representing the live synthesis of the system
    """
    _count = 0
    # Next value used for auto generated id
    _next_id = 1
    # _type stands for Backend Object Type
    _type = 'livesynthesis'
    # _cache is a list of created objects
    _cache = {}

    # Status property
    status_property = 'state'

    def __new__(cls, params=None, date_format='%a, %d %b %Y %H:%M:%S %Z'):
        """
        Create a new livesynthesis
        """
        return super(LiveSynthesis, cls).__new__(cls, params, date_format)

    def _create(self, params, date_format):
        """
        Create a livesynthesis (called only once when an object is newly created)
        """
        super(LiveSynthesis, self)._create(params, date_format)

    def _update(self, params=None, date_format='%a, %d %b %Y %H:%M:%S %Z'):
        """
        Update a livesynthesis (called every time an object is updated)
        """
        super(LiveSynthesis, self)._update(params, date_format)

    def __init__(self, params=None):
        """
        Initialize a livesynthesis (called every time an object is invoked)
        """
        super(LiveSynthesis, self).__init__(params)


class LiveState(Item):
    """
    Object representing a livestate item (host or service)
    """
    _count = 0
    # Next value used for auto generated id
    _next_id = 1
    # _type stands for Backend Object Type
    _type = 'livestate'
    # _cache is a list of created objects
    _cache = {}

    # Status property
    status_property = 'state'

    def __new__(cls, params=None, date_format='%a, %d %b %Y %H:%M:%S %Z'):
        """
        Create a new livestate
        """
        return super(LiveState, cls).__new__(cls, params, date_format)

    def _create(self, params, date_format):
        # Not that bad ... because _create is called from __new__
        # pylint: disable=attribute-defined-outside-init
        """
        Create a livestate (called only once when an object is newly created)
        """
        self._linked_host = 'host'
        self._linked_service = 'service'

        super(LiveState, self)._create(params, date_format)

    def _update(self, params=None, date_format='%a, %d %b %Y %H:%M:%S %Z'):
        """
        Update a livestate (called every time an object is updated)
        """
        super(LiveState, self)._update(params, date_format)

    def __init__(self, params=None):
        """
        Initialize a livestate (called every time an object is invoked)
        """
        super(LiveState, self).__init__(params)

    @property
    def host(self):
        """ Return linked object """
        return self._linked_host

    @property
    def service(self):
        """ Return linked object """
        return self._linked_service


class Host(Item):
    """
    Object representing an host
    """
    _count = 0
    # Next value used for auto generated id
    _next_id = 1
    # _type stands for Backend Object Type
    _type = 'host'
    # _cache is a list of created objects
    _cache = {}

    # Dates fields: list of the attributes to be considered as dates
    _dates = Item._dates + ['last_state_change', 'last_check', 'next_check']

    def __new__(cls, params=None, date_format='%a, %d %b %Y %H:%M:%S %Z'):
        """
        Create a new host
        """
        return super(Host, cls).__new__(cls, params, date_format)

    def _create(self, params, date_format):
        # Not that bad ... because _create is called from __new__
        # pylint: disable=attribute-defined-outside-init
        """
        Create a host (called only once when an object is newly created)
        """
        self._linked_check_command = 'command'
        self._linked_event_handler = 'command'
        self._linked_check_period = 'timeperiod'
        self._linked_notification_period = 'timeperiod'
        self._linked_snapshot_period = 'timeperiod'
        self._linked_maintenance_period = 'timeperiod'
        self._linked_hostgroups = 'hostgroup'
        self._linked_users = 'user'
        self._linked_usergroups = 'usergroup'

        super(Host, self)._create(params, date_format)

        # Missing in the backend ...
        if not hasattr(self, 'customs'):
            self.customs = []

        # From the livestate
        if not hasattr(self, 'is_impact'):
            self.impact = False
        if not hasattr(self, 'is_problem'):
            self.is_problem = False
        if not hasattr(self, 'problem_has_been_acknowledged'):
            self.problem_has_been_acknowledged = False
        if not hasattr(self, 'last_state_change'):
            self.last_state_change = self._default_date
        if not hasattr(self, 'last_check'):
            self.last_check = self._default_date
        if not hasattr(self, 'output'):
            self.output = self._default_date
        if not hasattr(self, 'long_output'):
            self.long_output = self._default_date
        if not hasattr(self, 'perf_data'):
            self.perf_data = self._default_date
        if not hasattr(self, 'latency'):
            self.latency = self._default_date
        if not hasattr(self, 'execution_time'):
            self.execution_time = self._default_date
        if not hasattr(self, 'attempt'):
            self.attempt = self._default_date
        if not hasattr(self, 'max_check_attempts'):
            self.max_check_attempts = self._default_date
        if not hasattr(self, 'state_type'):
            self.state_type = self._default_date
        if not hasattr(self, 'next_check'):
            self.next_check = self._default_date

        if not hasattr(self, 'comments'):
            self.comments = []

        if not hasattr(self, 'services'):
            self.services = []
        if not hasattr(self, 'downtimes'):
            self.downtimes = []
        if not hasattr(self, 'perfdatas'):
            self.perfdatas = []

    def _update(self, params=None, date_format='%a, %d %b %Y %H:%M:%S %Z'):
        """
        Update a host (called every time an object is updated)
        """
        super(Host, self)._update(params, date_format)

    def __init__(self, params=None):
        """
        Initialize a host (called every time an object is invoked)
        """
        super(Host, self).__init__(params)

    @property
    def check_command(self):
        """ Return linked object """
        return self._linked_check_command

    @property
    def event_handler(self):
        """ Return linked object """
        return self._linked_event_handler

    @property
    def check_period(self):
        """ Return linked object """
        return self._linked_check_period

    @property
    def notification_period(self):
        """ Return linked object """
        return self._linked_notification_period

    @property
    def snapshot_period(self):
        """ Return linked object """
        return self._linked_snapshot_period

    @property
    def maintenance_period(self):
        """ Return linked object """
        return self._linked_maintenance_period

    def get_last_check(self, timestamp=False, fmt=None):
        """
        Get last check date
        """
        if self.last_check == self.__class__._default_date and not timestamp:
            return _('Never checked!')

        if timestamp:
            return self.last_check

        return super(Host, self).get_date(self.last_check, fmt)


class HostGroup(Item):
    """
    Object representing a hostgroup
    """
    _count = 0
    # Next value used for auto generated id
    _next_id = 1
    # _type stands for Backend Object Type
    _type = 'hostgroup'
    # _cache is a list of created objects
    _cache = {}

    def __new__(cls, params=None, date_format='%a, %d %b %Y %H:%M:%S %Z'):
        """
        Constructor
        """
        return super(HostGroup, cls).__new__(cls, params, date_format)

    def _create(self, params, date_format):
        """
        Create a hostgroup (called only once when an object is newly created)
        """
        self._linked_hostgroups = 'hostgroup'
        self._linked_hosts = 'host'

        super(HostGroup, self)._create(params, date_format)

    def _update(self, params=None, date_format='%a, %d %b %Y %H:%M:%S %Z'):
        """
        Update a hostgroup (called every time an object is updated)
        """
        super(HostGroup, self)._update(params, date_format)

    def __init__(self, params=None):
        """
        Initialize a hostgroup (called every time an object is invoked)
        """
        super(HostGroup, self).__init__(params)

    @property
    def hosts(self):
        """ Return linked object """
        return self._linked_hosts

    @property
    def hostgroups(self):
        """ Return linked object """
        return self._linked_hostgroups


class Service(Item):
    """
    Object representing a service
    """
    _count = 0
    # Next value used for auto generated id
    _next_id = 1
    # _type stands for Backend Object Type
    _type = 'service'
    # _cache is a list of created objects
    _cache = {}

    def __new__(cls, params=None, date_format='%a, %d %b %Y %H:%M:%S %Z'):
        """
        Create a new user
        """
        return super(Service, cls).__new__(cls, params, date_format)

    def _create(self, params, date_format):
        """
        Create a service (called only once when an object is newly created)
        """
        self._linked_host = 'host'
        self._linked_check_command = 'command'
        self._linked_event_handler = 'command'
        self._linked_check_period = 'timeperiod'
        self._linked_notification_period = 'timeperiod'
        self._linked_servicegroups = 'servicegroup'
        self._linked_users = 'user'
        self._linked_usergroups = 'usergroup'

        super(Service, self)._create(params, date_format)

    def _update(self, params=None, date_format='%a, %d %b %Y %H:%M:%S %Z'):
        """
        Update a service (called every time an object is updated)
        """
        super(Service, self)._update(params, date_format)

    def __init__(self, params=None):
        """
        Initialize a service (called every time an object is invoked)
        """
        super(Service, self).__init__(params)

    @property
    def check_command(self):
        """ Return linked object """
        return self._linked_check_command

    @property
    def event_handler(self):
        """ Return linked object """
        return self._linked_event_handler

    @property
    def host(self):
        """ Return linked object """
        return self._linked_host

    @property
    def check_period(self):
        """ Return linked object """
        return self._linked_check_period

    @property
    def notification_period(self):
        """ Return linked object """
        return self._linked_notification_period


class ServiceGroup(Item):
    """
    Object representing a servicegroup
    """
    _count = 0
    # Next value used for auto generated id
    _next_id = 1
    # _type stands for Backend Object Type
    _type = 'servicegroup'
    # _cache is a list of created objects
    _cache = {}

    def __new__(cls, params=None, date_format='%a, %d %b %Y %H:%M:%S %Z'):
        """
        Create a new servicegroup
        """
        return super(ServiceGroup, cls).__new__(cls, params, date_format)

    def _create(self, params, date_format):
        """
        Create a servicegroup (called only once when an object is newly created)
        """
        self._linked_servicegroup_members = 'servicegroup'
        self._linked_members = 'service'

        super(ServiceGroup, self)._create(params, date_format)

    def _update(self, params=None, date_format='%a, %d %b %Y %H:%M:%S %Z'):
        """
        Update a servicegroup (called every time an object is updated)
        """
        super(ServiceGroup, self)._update(params, date_format)

    def __init__(self, params=None):
        """
        Initialize a servicegroup (called every time an object is invoked)
        """
        super(ServiceGroup, self).__init__(params)

    @property
    def members(self):
        """ Return linked object """
        return self._linked_members

    @property
    def servicegroup_members(self):
        """ Return linked object """
        return self._linked_servicegroup_members


class Log(Item):
    """
    Object representing a log item (host or service)
    """
    _count = 0
    # Next value used for auto generated id
    _next_id = 1
    # _type stands for Backend Object Type
    _type = 'logcheckresult'
    # _cache is a list of created objects
    _cache = {}

    # Status property
    status_property = 'state'

    def __new__(cls, params=None, date_format='%a, %d %b %Y %H:%M:%S %Z'):
        """
        Create a new log
        """
        return super(Log, cls).__new__(cls, params, date_format)

    def _create(self, params, date_format):
        # Not that bad ... because _create is called from __new__
        # pylint: disable=attribute-defined-outside-init
        """
        Create a log (called only once when an object is newly created)
        """
        self._linked_host = 'host'
        self._linked_service = 'service'

        super(Log, self)._create(params, date_format)

    def _update(self, params=None, date_format='%a, %d %b %Y %H:%M:%S %Z'):
        """
        Update a log (called every time an object is updated)
        """
        super(Log, self)._update(params, date_format)

    def __init__(self, params=None):
        """
        Initialize a log (called every time an object is invoked)
        """
        super(Log, self).__init__(params)

    @property
    def host(self):
        """ Return linked object """
        return self._linked_host

    @property
    def service(self):
        """ Return linked object """
        return self._linked_service

    def get_check_date(self, timestamp=False, fmt=None, duration=False):
        """
        Returns a string formatted data
        """
        if self.last_check == self.__class__._default_date and not timestamp:
            return _('Never checked!')

        if timestamp:
            return self.last_check

        return super(Log, self).get_date(self.last_check, fmt, duration)


class History(Item):
    """
    Object representing a History item (host or service)
    """
    _count = 0
    # Next value used for auto generated id
    _next_id = 1
    # _type stands for Backend Object Type
    _type = 'history'
    # _cache is a list of created objects
    _cache = {}

    # Status property
    status_property = 'type'

    def __new__(cls, params=None, date_format='%a, %d %b %Y %H:%M:%S %Z'):
        """
        Create a new History
        """
        return super(History, cls).__new__(cls, params, date_format)

    def _create(self, params, date_format):
        # Not that bad ... because _create is called from __new__
        # pylint: disable=attribute-defined-outside-init
        """
        Create a History (called only once when an object is newly created)
        """
        self._linked_host = 'host'
        self._linked_service = 'service'
        self._linked_user = 'user'
        self._linked_logcheckresult = 'logcheckresult'

        super(History, self)._create(params, date_format)

    def _update(self, params=None, date_format='%a, %d %b %Y %H:%M:%S %Z'):
        """
        Update a History (called every time an object is updated)
        """
        super(History, self)._update(params, date_format)

    def __init__(self, params=None):
        """
        Initialize a History (called every time an object is invoked)
        """
        super(History, self).__init__(params)

    @property
    def date(self):
        """ Return linked object """
        return self._created

    @property
    def host(self):
        """ Return linked object """
        return self._linked_host

    @property
    def service(self):
        """ Return linked object """
        return self._linked_service

    @property
    def user(self):
        """ Return linked object """
        return self._linked_user

    @property
    def logcheckresult(self):
        """ Return linked object """
        return self._linked_logcheckresult

    def get_check_date(self, timestamp=False, fmt=None, duration=False):
        """
        Returns a string formatted data
        """
        if self.date == self.__class__._default_date and not timestamp:
            return _('Never dated!')

        if timestamp:
            return self.date

        return super(History, self).get_date(self.date, fmt, duration)


class Command(Item):
    """
    Object representing a command
    """
    _count = 0
    # Next value used for auto generated id
    _next_id = 1
    # _type stands for Backend Object Type
    _type = 'command'
    # _cache is a list of created objects
    _cache = {}

    def __new__(cls, params=None, date_format='%a, %d %b %Y %H:%M:%S %Z'):
        """
        Create a new command
        """
        return super(Command, cls).__new__(cls, params, date_format)

    def _create(self, params, date_format):
        """
        Create a command (called only once when an object is newly created)
        """
        super(Command, self)._create(params, date_format)

    def _update(self, params=None, date_format='%a, %d %b %Y %H:%M:%S %Z'):
        """
        Update a command (called every time an object is updated)
        """
        super(Command, self)._update(params, date_format)

    def __init__(self, params=None):
        """
        Initialize a command (called every time an object is invoked)
        """
        super(Command, self).__init__(params)

    @property
    def endpoint(self):
        """
        Overload default property. Link to the main objects page with an anchor.
        """
        return '/%ss#%s' % (self.object_type, self.id)


class TimePeriod(Item):
    """
    Object representing a timeperiod
    """
    _count = 0
    # Next value used for auto generated id
    _next_id = 1
    # _type stands for Backend Object Type
    _type = 'timeperiod'
    # _cache is a list of created objects
    _cache = {}

    def __new__(cls, params=None, date_format='%a, %d %b %Y %H:%M:%S %Z'):
        """
        Create a new user
        """
        return super(TimePeriod, cls).__new__(cls, params, date_format)

    def _create(self, params, date_format):
        """
        Create a timeperiod (called only once when an object is newly created)
        """
        super(TimePeriod, self)._create(params, date_format)

    def _update(self, params=None, date_format='%a, %d %b %Y %H:%M:%S %Z'):
        """
        Update a timeperiod (called every time an object is updated)
        """
        super(TimePeriod, self)._update(params, date_format)

    def __init__(self, params=None):
        """
        Initialize a timeperiod (called every time an object is invoked)
        """
        super(TimePeriod, self).__init__(params)

    @property
    def endpoint(self):
        """
        Overload default property. Link to the main objects page with an anchor.
        """
        return '/%ss#%s' % (self.object_type, self.id)


# Sort methods
# -----------------------------------------------------
def sort_items_most_recent_first(s1, s2):
    """
    Sort elemnts by descending date
    """
    if s1.get_date() > s2.get_date():
        return -1
    if s1.get_date() < s2.get_date():
        return 1
    return 0


def sort_items_least_recent_first(s1, s2):
    """
    Sort elements by ascending date
    """
    if s1.get_date() < s2.get_date():
        return -1
    if s1.get_date() > s2.get_date():
        return 1
    return 0
