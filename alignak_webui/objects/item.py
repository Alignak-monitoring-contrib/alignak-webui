#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring, fixme,too-many-arguments, too-many-public-methods
# pylint: disable=too-many-nested-blocks, too-many-locals, too-many-return-statements
# pylint: disable=attribute-defined-outside-init, protected-access

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
from datetime import datetime, timedelta

import locale

import traceback
from logging import getLogger, INFO

from calendar import timegm
from dateutil import tz

from alignak_webui import get_app_config, _

# Set logger level to INFO, this to allow global application DEBUG logs without being spammed... ;)
logger = getLogger(__name__)
logger.setLevel(INFO)


class ItemState(object):
    '''
    Singleton design pattern ...
    '''
    class __ItemState(object):
        '''
        Base class for all objects state management (displayed icon, ...)
        '''

        def __init__(self):
            '''
            Create
            '''
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
            '''
                Return all the configured objects types

                All other object type will use the default 'item' configuration
            '''
            return [s for s in self.states]

        def get_icon_states(self, object_type=None):
            ''' Return all the configured states for an object type '''
            if not object_type:
                return self.states
            if object_type in self.states:
                return self.states[object_type]
            return []

        def get_default_states(self):
            ''' Return all the configured states for a generic item '''
            return [s for s in self.default_states]

        def get_icon_state(self, object_type, status):
            ''' Return the configured state for an object type '''
            if not object_type or not status:
                return None

            if status not in self.get_icon_states(object_type):
                return None

            for s in self.get_icon_states(object_type):
                if status == s:
                    return self.get_icon_states(object_type)[s]

        def get_html_state(self, object_type, object_item, extra='', icon=True, text=False,
                           label='', disabled=False):
            """
            Returns an item status as HTML text and icon if needed

            If parameters are not valid, returns 'n/a'

            If disabled is True, the class does not depend upon object status and is always
            font-greyed

            If a label is specified, text must be True, and the label will be used instead
            of the built text.

            If object status contains '.' characters they are replaced with '_'

            Text and icon are defined in the application configuration file.

            :param object_type: element type
            :type object_type: string
            :param object_item: element
            :type object: Item class based object

            :param extra: extra string replacing ##extra##, and set opacity to 0.5
            :type extra: string

            :param text: include text in the response
            :type text: boolean
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

            status = object_item.get_status()
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
            logger.debug("get_html_state, states view: %s", cfg_state_view)

            # Text
            res_icon_state = cfg_state['icon']
            res_icon_text = cfg_state['text']
            res_icon_class = 'item_' + cfg_state['class']
            res_text = res_icon_text

            if text and not icon:
                return res_text

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
            item_id = object_item.get_id()
            res_icon = res_icon_global
            res_icon = res_icon.replace("##type##", object_type)
            res_icon = res_icon.replace("##id##", item_id)
            res_icon = res_icon.replace("##name##", object_item.get_name())
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
            res_icon = res_icon.replace("##title##", res_text)
            res_icon = res_icon.replace("##opacity##", res_opacity)
            if label:
                res_icon = res_icon.replace("##text##", label)
            elif text:
                res_icon = res_icon.replace("##text##", res_text)
            else:
                res_icon = res_icon.replace("##text##", "")

            logger.debug("get_html_state, res_icon: %s", res_icon)
            return res_icon

        def get_html_badge(self, object_type, object_item, label='', disabled=False):
            """
            Returns an item status as HTML text and icon if needed

            If parameters are not valid, returns 'n/a'

            If disabled is True, the class does not depend upon status and is always font-greyed

            If a label is specified, text must be True, and the label will be used instead
            of the built text.

            Text and icon are defined in the application configuration file.

            :param element: force element type (to get generic element type view)
            :type element: string
            :param object_item: element
            :type object: Item class based object

            :param text: include text in the response
            :type text: boolean
            :param icon: include icon in the response
            :type icon: boolean
            :return: formatted status HTML string
            :rtype: string
            """
            if not object_type:  # pragma: no cover, should not happen
                return 'n/a - element'

            if not object_item:  # pragma: no cover, should not happen
                return 'n/a - object'

            status = object_item.get_status()
            status = status.replace('.', '_').lower()
            if object_type in self.get_objects_types():
                if status not in self.get_icon_states(object_type):
                    return 'n/a - status: ' + status
            else:  # pragma: no cover, not tested
                if status not in self.get_default_states():
                    return 'n/a - default status: ' + status

            cfg_state = self.get_icon_state(object_type, status)
            if object_type not in self.get_objects_types() and status in self.get_default_states():
                cfg_state = self.get_icon_state("user", status)
            logger.debug("get_html_badge, states: %s", cfg_state)

            cfg_state_view = self.get_icon_state(object_type, 'state_view')
            if object_type not in self.get_objects_types():
                cfg_state_view = self.get_icon_state("user", 'state_view')
            if not cfg_state_view:  # pragma: no cover, should not happen
                return 'n/a - cfg_state_view'
            logger.debug("get_html_badge, states view: %s", cfg_state_view)

            # Text
            res_icon_state = cfg_state['icon']
            res_icon_text = cfg_state['text']
            res_icon_class = 'item_' + cfg_state['class']
            res_text = res_icon_text

            # Icon
            res_icon_badge = cfg_state_view['badge']
            if not res_icon_badge:  # pragma: no cover, should not happen
                return 'n/a - res_icon_badge'

            res_extra = "fa-inverse"
            res_opacity = ""

            # Assembling ...
            item_id = object_item.get_id()
            res_icon = res_icon_badge
            res_icon = res_icon.replace("##type##", object_type)
            res_icon = res_icon.replace("##id##", item_id)
            res_icon = res_icon.replace("##name##", object_item.get_name())
            res_icon = res_icon.replace("##state##", object_item.get_state())
            res_icon = res_icon.replace("##status##", status.lower())
            if not disabled:
                res_icon = res_icon.replace("##class##", res_icon_class)
            else:
                res_icon = res_icon.replace("##class##", "font-greyed")

            res_icon = res_icon.replace("##icon##", res_icon_state)
            res_icon = res_icon.replace("##extra##", res_extra)
            res_icon = res_icon.replace("##title##", res_text)
            res_icon = res_icon.replace("##opacity##", res_opacity)
            if label:
                res_icon = res_icon.replace("##text##", label)
            else:
                res_icon = res_icon.replace("##text##", "")

            logger.debug("get_html_badge, res_icon: %s", res_icon)
            return res_icon

    instance = None

    def __new__(cls):
        if not ItemState.instance:
            ItemState.instance = ItemState.__ItemState()
        return ItemState.instance

    def get_html_state(self, extra='', icon=True, text=False,
                       label='', disabled=False,
                       object_type='', object_item=None):  # pragma: no cover
        return self.instance.get_html_state(object_type, object_item,
                                            extra, icon, text, label, disabled)

    def get_html_badge(self,
                       label='', disabled=False,
                       object_type='', object_item=None):  # pragma: no cover
        return self.instance.get_html_badge(object_type, object_item,
                                            label, disabled)


class Item(object):
    '''
    Base class for all objects
    '''
    _count = 0

    # Next value used for auto generated id
    _next_id = 1
    # _type stands for Backend Object Type
    _type = 'item'
    # _cache is a list of created objects
    _cache = {}

    # Default date used for bad formatted string dates
    _default_date = 0

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

    """ Manage cached objects """
    @classmethod
    def getType(cls):
        return cls._type

    @classmethod
    def getCount(cls):
        return cls._count

    @classmethod
    def getTotalCount(cls):
        return cls._total_count

    @classmethod
    def getCache(cls):
        return cls._cache

    @classmethod
    def cleanCache(cls):
        cls._next_id = 1
        cls._count = 0
        cls._cache = {}

    def __new__(cls, params=None, date_format='%a, %d %b %Y %H:%M:%S %Z'):
        '''
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
        '''
        id_property = getattr(cls, 'id_property', '_id')
        # print "Class %s, id_property: %s, params: %s" % (cls, id_property, params)

        _id = '0'
        if params:
            if not isinstance(params, dict):
                raise ValueError('Object parameters must be a dictionary!')

            if id_property in params:
                if not isinstance(params[id_property], basestring):
                    params[id_property] = str(params[id_property])
                _id = params[id_property]
            else:
                # TODO: change this ... always create type_0 object!
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

            # Call the new object create function
            cls._cache[_id]._create(params, date_format)
            cls._count += 1
        else:
            if params != cls._cache[_id].__dict__:
                # print "Update existing instance for: ", _id, params
                cls._cache[_id]._update(params, date_format)

        # print "Return existing instance for: ", _id, params
        return cls._cache[_id]

    def __del__(self):
        '''
        Delete an object (called only when no more reference exists for an object)
        '''
        logger.debug(" --- deleting a %s (%s)", self.__class__, self._id)
        # print "Delete a %s (%s)" % (self.getType(), self._id)

    def _delete(self):
        '''
        Delete an object

        If the object exists in the cache, its reference is removed from the internal cache.
        '''
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
        '''
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
            If the object has declared some 'linked_XXX' prefixed attributes and the paramaters
            contain an 'XXX' field, this function creates a new object in the 'linked_XXX'
            attribute. The initial 'linked_XXX' attribute must contain the new object type!

            If the attribute is a simple dictionary, the new attribute contains the dictionary.

            This feature allows to create links between embedded objects of the backend.
        '''
        id_property = getattr(self.__class__, 'id_property', '_id')

        if id_property not in params:  # pragma: no cover, should never happen
            raise ValueError('No %s attribute in the provided parameters' % id_property)
        logger.debug(
            " --- creating a %s (%s - %s)",
            self.getType(), params[id_property], params['name'] if 'name' in params else ''
        )

        for key in params:
            logger.debug(" parameter: %s (%s) = %s", key, params[key].__class__, params[key])
            # Object must have declared a linked_ attribute ...
            if isinstance(params[key], dict) and hasattr(self, 'linked_' + key):
                logger.debug(" parameter: %s is a linked object", key)
                # Linked resource type
                object_type = getattr(self, 'linked_' + key, None)
                if object_type is None:  # pragma: no cover, should never happen
                    setattr(self, key, params[key])
                    continue

                for k in globals().keys():
                    if isinstance(globals()[k], type) and \
                       '_type' in globals()[k].__dict__ and \
                       globals()[k]._type == object_type:
                        linked_object = globals()[k](params[key])
                        setattr(self, 'linked_' + key, linked_object)
                        setattr(self, key, linked_object['_id'])
                        logger.debug("Linked with %s (%s)", key, linked_object['_id'])
                        break
                continue

            # If the property is a date, make it a timestamp...
            if key.endswith('date') or key in ['_created', '_updated']:
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
                logger.warning(" parameter TypeError: %s = %s", key, params[key])

        # Object name
        if not hasattr(self, 'name'):
            setattr(self, 'name', 'anonymous')

        # Object state
        if not hasattr(self, 'status'):
            setattr(self, 'status', 'unknown')

        logger.debug(" --- created %s (%s): %s", self.__class__, self[id_property], self.__dict__)

    def _update(self, params, date_format='%a, %d %b %Y %H:%M:%S %Z'):
        id_property = getattr(self.__class__, 'id_property', '_id')

        logger.debug(" --- updating a %s (%s)", self.__class__, self[id_property])

        if not isinstance(params, dict):
            params = params.__dict__
        for key in params:
            logger.debug(" --- parameter %s = %s", key, params[key])
            if isinstance(params[key], dict) and hasattr(self, 'linked_' + key):
                if not isinstance(getattr(self, 'linked_' + key, None), basestring):
                    # Does not contain a string, so update object ...
                    logger.debug(" Update object: %s = %s", key, params[key])
                    getattr(self, 'linked_' + key)._update(params[key])
                else:
                    # Else, create new linked object
                    object_type = getattr(self, 'linked_' + key, None)
                    if object_type is None:  # pragma: no cover, should never happen
                        setattr(self, key, params[key])
                        continue

                    for k in globals().keys():
                        if isinstance(globals()[k], type) and \
                           '_type' in globals()[k].__dict__ and \
                           globals()[k]._type == object_type:
                            linked_object = globals()[k](params[key])
                            setattr(self, 'linked_' + key, linked_object)
                            setattr(self, key, linked_object['_id'])
                            logger.debug(
                                "Linked: %s (%s) with %s (%s)",
                                self._type, self[id_property], key, linked_object.get_id()
                            )
                            break
                    continue
                continue

            # If the property is a date, make it a timestamp...
            if key.endswith('date') or key in ['_created', '_updated']:
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
                logger.warning(" parameter TypeError: %s = %s", key, params[key])

    def __init__(self, params=None, date_format='%a, %d %b %Y %H:%M:%S %Z'):
        '''
        Initialize an object

        Beware: always called, even if the object is not newly created! Use _create function for
        initializing newly created objects.
        '''
        id_property = getattr(self.__class__, 'id_property', '_id')

        logger.debug(" --- initializing a %s (%s)", self._type, self[id_property])
        logger.debug(" --- initializing with %s and %s", params, date_format)

    def __repr__(self):
        return ("<%s, id: %s, name: %s, status: %s>") % (
            self.__class__._type, self.get_id(), self.get_name(), self.get_status()
        )

    def __getitem__(self, key):
        return getattr(self, key, None)

    def get_id(self):
        if hasattr(self.__class__, 'id_property'):
            return getattr(self, self.__class__.id_property, None)
        return getattr(self, '_id', None)

    def get_name(self):
        if hasattr(self.__class__, 'name_property'):
            return getattr(self, self.__class__.name_property, None)
        return getattr(self, 'name', None)

    def get_description(self):
        if hasattr(self.__class__, 'description_property'):
            return getattr(self, self.__class__.description_property, None)
        if hasattr(self, 'description'):
            return self.description
        return self.get_name()

    def get_status(self):
        if hasattr(self.__class__, 'status_property'):
            return getattr(self, self.__class__.status_property, None)
        return getattr(self, 'status', 'unknown')

    def get_state(self):
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

    def get_html_state(self, extra='', icon=True, text=False,
                       label='', disabled=False, object_type=None, object_item=None):
        """
        Uses the ItemState singleton to display HTML state for an item
        """
        if not object_type:
            object_type = self.__class__._type

        if not object_item:
            object_item = self

        return ItemState().get_html_state(object_type, object_item,
                                          extra, icon, text, label, disabled)

    def get_html_badge(self, label='', disabled=False, object_type='', object_item=None):
        """
        Uses the ItemState singleton to display HTML badge for an item
        """
        if not object_type:
            object_type = self.__class__._type

        if not object_item:
            object_item = self

        return ItemState().get_html_badge(object_type, object_item,
                                          label, disabled)

    def get_date(self, _date=None, fmt=None):
        if _date == self.__class__._default_date:
            return _('Never dated!')

        item_state = ItemState()
        if not fmt and item_state.date_format:
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


class User(Item):
    _count = 0
    # Next value used for auto generated id
    _next_id = 1
    # _type stands for Backend Object Type
    _type = 'contact'
    # _cache is a list of created objects
    _cache = {}

    roles = {
        "user": _("User"),
        "power": _("Power user"),
        "administrator": _("Administrator")
    }

    def __new__(cls, params=None, date_format='%a, %d %b %Y %H:%M:%S %Z'):
        '''
        Create a new user
        '''
        return super(User, cls).__new__(cls, params, date_format)

    def _create(self, params, date_format):
        '''
        Create a user (called only once when an object is newly created)
        '''
        self.linked_userservices = []
        self.linked_userservice_sessions = []

        if params and 'can_submit_commands' in params:
            params['read_only'] = False
            params.pop('can_submit_commands', None)

        super(User, self)._create(params, date_format)

        self.authenticated = False

        if not hasattr(self, 'email'):
            self.email = None

        if not hasattr(self, 'lync'):
            self.lync = None

        # Has a session token ?
        if not hasattr(self, 'token'):
            self.token = None

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
            self.picture = '/static/photos/user_default'
            if self.name == 'anonymous':
                self.picture = '/static/photos/user_guest'
            else:
                if self.is_admin:
                    self.picture = '/static/photos/user_admin'

    def _update(self, params=None, date_format='%a, %d %b %Y %H:%M:%S %Z'):
        '''
        Update a user (called every time an object is updated)
        '''
        if params and 'can_submit_commands' in params:
            params['read_only'] = False
            params.pop('can_submit_commands', None)

        super(User, self)._update(params, date_format)

    def __init__(self, params=None):
        '''
        Initialize a user (called every time an object is invoked)
        '''
        super(User, self).__init__(params)

    def __repr__(self):
        if self.authenticated:
            return ("<Authenticated %s, id: %s, name: %s, role: %s>") % (
                self.__class__._type, self.get_id(), self.get_name(), self.get_role()
            )
        return ("<%s, id: %s, name: %s, role: %s>") % (
            self.__class__._type, self.get_id(), self.get_name(), self.get_role()
        )

    def get_friendly_name(self):
        return getattr(self, 'friendly_name', self.get_name())

    def get_token(self):
        return self.token

    def get_picture(self):
        return self.picture

    def get_username(self):
        if getattr(self, 'username', None):
            return self.username
        if getattr(self, 'contact_name', None):
            return self.contact_name
        return self.name

    def get_name(self):
        name = self.get_username()
        if getattr(self, 'friendly_name', None):
            return self.friendly_name
        elif getattr(self, 'realname', None):
            return "%s %s" % (getattr(self, 'firstname'), getattr(self, 'realname'))
        elif getattr(self, 'alias', None) and getattr(self, 'alias', None) != 'none':
            return getattr(self, 'alias', name)
        return name

    def get_email(self):
        return self.email

    def get_lync(self):
        return self.lync

    def get_role(self, display=False):
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
        Is user anonymous?
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

    def is_related_to(self, item):  # pragma: no cover, RFU!
        """ Is the item (host, service, group,...) related to the user?

            In other words, can the user see this item in the WebUI?

            :returns: True or False
        """
        # TODO : to be managed ...
        if item:
            return True

        return False

    def set_userservice(self, item):
        '''
        Link with a new user service. Maintain an internal services list.
        '''
        if not isinstance(item, UserService):
            logger.critical("User, set_userservice, not a UserService: %s", item)
            return None

        if item in self.linked_userservices:
            return item.get_id()

        self.linked_userservices.append(item)
        return item.get_id()

    def get_userservices(self):
        return self.linked_userservices

    def set_session(self, item):
        '''
        Link with a new session. Maintain an internal sessions list.
        '''
        if not isinstance(item, Session):
            logger.critical("User, set_session, not a Session: %s", item)
            return None

        if item in self.linked_userservice_sessions:
            return item.get_id()

        self.linked_userservice_sessions.append(item)
        return item.get_id()

    def get_sessions(self):
        return self.linked_userservice_sessions


class Kiosk(Item):
    _count = 0
    # Next value used for auto generated id
    _next_id = 1
    # _type stands for Backend Object Type
    _type = 'kiosk'
    # _cache is a list of created objects
    _cache = {}

    # Store total count for object in the backend
    _total_count = 0

    # Override default identifier property
    id_property = 'id'
    # name_property = 'name'
    # status_property = 'state'
    # description_property = 'comment'

    def __new__(cls, params=None, date_format='%a, %d %b %Y %H:%M:%S %Z'):
        '''
        Create a new kiosk
        '''
        return super(Kiosk, cls).__new__(cls, params, date_format)

    def _create(self, params, date_format):
        '''
        Create a kiosk (called only once when an object is newly created)
        '''
        if params and '_id' in params:
            params['_id'] = '#%s' % params['_id']
            params.pop('id', None)

        super(Kiosk, self)._create(params, date_format)

    def _update(self, params=None, date_format='%a, %d %b %Y %H:%M:%S %Z'):
        '''
        Update a kiosk (called every time an object is updated)
        '''
        if params and '_id' in params:
            params['_id'] = '#%s' % params['_id']
            params.pop('id', None)

        super(Kiosk, self)._update(params, date_format)

    def __init__(self, params=None):
        '''
        Initialize a kiosk (called every time an object is invoked)
        '''
        super(Kiosk, self).__init__(params)

        if not hasattr(self, 'state'):
            self.state = self.status

        if not hasattr(self, 'comment'):
            self.comment = self.name


class Service(Item):  # pragma: no cover, RFU!
    id = 1
    _type = 'service'
    name_property = 'service_description'


class UserServiceUser(Item):
    _count = 0
    # Next value used for auto generated id
    _next_id = 1
    # _type stands for Backend Object Type
    _type = 'userservice_user'
    # _cache is a list of created objects
    _cache = {}

    def __new__(cls, params=None, date_format='%a, %d %b %Y %H:%M:%S %Z'):
        '''
        Create a new service / user relation
        '''
        return super(UserServiceUser, cls).__new__(cls, params, date_format)

    def _create(self, params, date_format):
        '''
        Create a relation (called only once when an object is newly created)
        '''
        self.linked_userservice = 'userservice'
        self.linked_user = 'user'

        super(UserServiceUser, self)._create(params, date_format)
        print "Created USU:", self._id

    def _update(self, params=None, date_format='%a, %d %b %Y %H:%M:%S %Z'):
        '''
        Update a relation (called every time an object is updated)
        '''
        super(UserServiceUser, self)._update(params, date_format)
        print "Updated USU:", self._id

    def __init__(self, params=None):
        '''
        Initialize a relation
        '''
        super(UserServiceUser, self).__init__(params)
        print "Init USU:", self._id, self.__dict__

        # Search if we already have User linked objects...
        if not self.get_user():
            for dummy, user in User.getCache().items():
                if self.user and user._id == self.user:
                    self.set_user(user)

        # Search if we already have UserService linked objects...
        if not self.get_userservice():
            for dummy, us in UserService.getCache().items():
                if self.get_userservice() and us.get_id() == self.get_userservice():
                    self.set_userservice(us)

        if self.get_user() and self.get_userservice():
            self.get_userservice().set_user(self.get_user())
            self.get_user().set_userservice(self.get_userservice())

    def __repr__(self):
        return ("<%s, id: %s, service: %s, user: %s>") % (
            self.__class__._type, self.get_id(),
            self.get_userservice().get_name() if self.get_userservice() else 'unknown',
            self.get_user().get_name() if self.get_user() else 'unknown'
        )

    def set_userservice(self, item):
        if not isinstance(item, UserService):
            logger.critical("UserServiceUser, set_userservice, not a UserService: %s", item)
            return None

        self.linked_userservice = item
        return self.linked_userservice.get_id()

    def get_userservice(self):
        if self.linked_userservice != 'userservice':
            return self.linked_userservice

        return None

    def set_user(self, item):
        if not isinstance(item, User):
            logger.critical("UserServiceUser, set_user, not a User: %s", item)
            return None

        self.linked_user = item
        return self.linked_user.get_id()

    def get_user(self):
        if self.linked_user != 'user':
            return self.linked_user

        return None


class UserService(Item):
    _count = 0
    # Next value used for auto generated id
    _next_id = 1
    # _type stands for Backend Object Type
    _type = 'userservice'
    # _cache is a list of created objects
    _cache = {}

    def __new__(cls, params=None, date_format='%a, %d %b %Y %H:%M:%S %Z'):
        '''
        Create a new user service
        '''
        return super(UserService, cls).__new__(cls, params, date_format)

    def _create(self, params, date_format):
        '''
        Create a user service (called only once when an object is newly created)
        '''
        # Default is active
        self.status = 'active'

        self.linked_cdr = 'userservice_cdr'
        self.linked_users = []
        self.linked_userservice_sessions = []

        super(UserService, self)._create(params, date_format)
        print "Created US:", self._id

    def _update(self, params=None, date_format='%a, %d %b %Y %H:%M:%S %Z'):
        '''
        Update a user service (called every time an object is updated)
        '''
        super(UserService, self)._update(params, date_format)
        print "Updated US:", self._id

    def __init__(self, params=None):
        '''
        Initialize a user service (called every time an object is invoked)
        '''
        super(UserService, self).__init__(params)
        print "Init US:", self._id

        # Search if we already have UserServiceUser linked objects...
        for dummy, usu in UserServiceUser.getCache().items():
            if usu['userservice'] and usu['userservice'] == self._id:
                # Link service user / service
                if usu.get_userservice():
                    usu.get_userservice().set_user(usu.get_user())
                if usu.get_user():
                    usu.get_user().set_userservice(usu.get_userservice())

        # Search if we already have Session linked objects...
        for dummy, ses in Session.getCache().items():
            if ses['userservice'] and ses['userservice'] == self._id:
                # Link service / session
                self.set_session(ses)

        # Search if we already have UserServiceCdr linked objects...
        for dummy, usc in UserServiceCdr.getCache().items():
            if usc['userservice'] and usc['userservice'] == self._id:
                # link service / cdr
                self.set_cdr(usc)
                usc.set_userservice(self)

    def is_active(self):
        return self.get_status() == 'active'

    def set_session(self, item):
        if not isinstance(item, Session):
            logger.critical("UserService, set_session, not a session: %s", item)
            return None

        if item in self.get_sessions():
            return item.get_id()

        self.linked_userservice_sessions.append(item)
        return item.get_id()

    def get_sessions(self):
        return self.linked_userservice_sessions

    def set_cdr(self, item):
        if not isinstance(item, UserServiceCdr):
            logger.critical("UserService, set_cdr, not a UserServiceCdr: %s", item)
            return None

        self.linked_cdr = item
        return self.linked_cdr.get_id()

    def get_cdr(self):
        if self.linked_cdr != 'userservice_cdr':
            return self.linked_cdr
        return None

    def set_user(self, item):
        '''
        Link with a new user. Maintain an internal users list.
        '''
        if not isinstance(item, User):
            logger.critical("UserService, set_user, not a User: %s", item)
            return None

        if item in self.linked_users:
            return item.get_id()

        self.linked_users.append(item)
        return item.get_id()

    def get_users(self):
        return self.linked_users

    def get_relation_id(self, user):
        for user in self.get_users():
            if user.get_id() == user.get_id():
                return user.get_id()
        return -1

    def is_related(self, user):
        return self.get_relation_id(user) != -1

    def has_opened_session(self):
        for session in self.get_sessions():
            if session.is_opened():
                return True
        return False


class UserServiceCdr(Item):
    _count = 0
    # Next value used for auto generated id
    _next_id = 1
    # _type stands for Backend Object Type
    _type = 'userservice_cdr'
    # _cache is a list of created objects
    _cache = {}

    def __new__(cls, params=None, date_format='%a, %d %b %Y %H:%M:%S %Z'):
        '''
        Create a new service CDR
        '''
        return super(UserServiceCdr, cls).__new__(cls, params, date_format)

    def _create(self, params, date_format):
        '''
        Create a service CDR (called only once when an object is newly created)
        '''
        self.linked_userservice_session = 'userservice_session'
        self.linked_userservice = 'userservice'
        self.linked_user_creator = 'user'
        self.linked_user_participant = 'user'

        super(UserServiceCdr, self)._create(params, date_format)

    def _update(self, params=None, date_format='%a, %d %b %Y %H:%M:%S %Z'):
        '''
        Update a service CDR (called every time an object is updated)
        '''
        super(UserServiceCdr, self)._update(params, date_format)

    def __init__(self, params=None):
        '''
        Initialize a service CDR (called every time an object is invoked)
        '''
        super(UserServiceCdr, self).__init__(params)

        if not hasattr(self, 'opening_date'):
            self.opening_date = self.__class__._default_date

        if not hasattr(self, 'closing_date'):
            self.closing_date = self.__class__._default_date

    def __repr__(self):
        return ("<%s, id: %s, service: %s, session: %s>") % (
            self.__class__._type, self.get_id(),
            self.get_userservice().get_name() if self.get_userservice() else 'unknown',
            self.get_session().get_id() if self.get_session() else 'unknown'
        )

    def get_userservice(self):
        if self.linked_userservice != 'userservice':
            return self.linked_userservice

        return None

    def get_session(self):
        if self.linked_userservice_session != 'userservice_session':
            return self.linked_userservice_session

        return None

    def is_opened(self):
        return self.get_status() == 'open'

    def is_closed(self):
        return self.get_status() == 'close'

    def get_date(self, timestamp=False, fmt=None):
        return self.get_opening_date(timestamp=timestamp, fmt=fmt)

    def get_opening_date(self, timestamp=False, fmt=None):
        if self.opening_date == self.__class__._default_date and not timestamp:
            return _('Never opened!')

        if timestamp:
            return self.opening_date

        return super(UserServiceCdr, self).get_date(self.opening_date, fmt)

    def get_closing_date(self, timestamp=False, fmt=None):
        if self.closing_date == self.__class__._default_date and not timestamp:
            return _('Never closed!')

        if timestamp:
            return self.closing_date

        return super(UserServiceCdr, self).get_date(self.closing_date, fmt)

    def get_duration(self):
        if self.is_closed():
            return self.closing_date - self.opening_date
        else:
            now = datetime.utcnow()
            now = timegm(now.utctimetuple())
            return now - self.opening_date

    def get_nb_users(self):
        return getattr(self, 'nb_users', 0)

    def get_user_creator(self):
        if self.linked_user_creator != 'user':
            return self.linked_user_creator
        return None

    def get_user_participant(self):
        if self.linked_user_participant != 'user':
            return self.linked_user_participant
        return None

    def get_nb_documents(self):
        return getattr(self, 'nb_documents', 0)

    def get_videoconference(self):
        return getattr(self, 'videoconference', None)

    def set_session(self, item):
        if not isinstance(item, Session):
            logger.critical("UserServiceCdr, set_session, not a Session: %s", item)
            return None

        self.linked_userservice_session = item
        return self.linked_userservice_session.get_id()

    def set_userservice(self, item):
        if not isinstance(item, UserService):
            logger.critical("UserServiceCdr, set_userservice, not a UserService: %s", item)
            return None

        self.linked_userservice = item
        return self.linked_userservice.get_id()


class Session(Item):
    _count = 0
    # Next value used for auto generated id
    _next_id = 1
    # _type stands for Backend Object Type
    _type = 'userservice_session'
    # _cache is a list of created objects
    _cache = {}

    def __new__(cls, params=None, date_format='%a, %d %b %Y %H:%M:%S %Z'):
        '''
        Create a new session
        '''
        return super(Session, cls).__new__(cls, params, date_format)

    def _create(self, params, date_format):
        '''
        Create a user (called only once when an object is newly created)
        '''
        # Set name to 'session'
        self.name = 'session'

        self.linked_userservice = 'userservice'
        self.linked_users = []
        self.linked_events = []
        self.session_users = []

        super(Session, self)._create(params, date_format)

        if not hasattr(self, 'opening_date'):
            self.opening_date = self.__class__._default_date

        if not hasattr(self, 'closing_date'):
            self.closing_date = self.__class__._default_date

    def _update(self, params=None, date_format='%a, %d %b %Y %H:%M:%S %Z'):
        '''
        Update a session (called every time an object is updated)
        '''
        super(Session, self)._update(params, date_format)

    def __init__(self, params=None):
        '''
        Initialize a session (called every time an object is invoked)
        '''
        super(Session, self).__init__(params)

        # Search if we already have UserService linked objects...
        for dummy, us in UserService.getCache().items():
            if self.get_userservice() and us.get_id() == self.get_userservice().get_id():
                # Link service / session
                assert self.set_userservice(us)
                assert us.set_session(self)

        # Search if we already have SessionUser linked objects...
        for dummy, su in SessionUser.getCache().items():
            if su['userservice_session'] and su['userservice_session'] == self._id:
                # Link session user / session
                su.set_session(self)
                self.set_session_user(su)
                if su.get_user():
                    # Link user / session
                    su.get_user().set_session(self)
                    self.set_user(su.get_user())

    def __repr__(self):
        return ("<%s, id: %s, name: %s, service: %s, status: %s>") % (
            self.__class__._type, self.get_id(),
            self.get_name(),
            self.get_userservice().get_name() if self.get_userservice() else 'unknown',
            self.get_status()
        )

    def get_userservice(self):
        if self.linked_userservice != 'userservice':
            return self.linked_userservice

        return None

    def get_userservice_name(self):
        if self.service_name:
            return self.service_name

        return None

    def is_opened(self):
        return self.get_status() == 'open'

    def is_closed(self):
        return self.get_status() == 'close'

    def get_date(self, timestamp=False, fmt=None):
        return self.get_opening_date(timestamp=timestamp, fmt=fmt)

    def get_opening_date(self, timestamp=False, fmt=None):
        if self.opening_date == self.__class__._default_date and not timestamp:
            return _('Never opened!')

        if timestamp:
            return self.opening_date

        return super(Session, self).get_date(self.opening_date, fmt)

    def get_closing_date(self, timestamp=False, fmt=None):
        if self.closing_date == self.__class__._default_date and not timestamp:
            return _('Never closed!')

        if timestamp:
            return self.closing_date

        return super(Session, self).get_date(self.closing_date, fmt)

    def get_duration(self):
        if self.is_closed():
            return self.closing_date - self.opening_date
        else:
            now = datetime.utcnow()
            now = timegm(now.utctimetuple())
            return now - self.opening_date

    def get_nb_users(self):
        return getattr(self, 'nb_users', 0)

    def set_userservice(self, item):
        if not isinstance(item, UserService):
            logger.critical("Session, set_userservice, not a UserService: %s", item)
            return None

        self.linked_userservice = item
        return self.linked_userservice.get_id()

    def set_user(self, item):
        if not isinstance(item, User):
            logger.critical("Session, set_user, not a User: %s", item)
            return None

        if item in self.linked_users:
            return item.get_id()

        self.linked_users.append(item)
        return item.get_id()

    def get_users(self):
        return self.linked_users

    def set_session_user(self, item):
        if not isinstance(item, SessionUser):
            logger.critical("Session, set_session_user, not a SessionUser: %s", item)
            return None

        if item in self.session_users:
            return item.get_id()

        self.session_users.append(item)
        return item.get_id()

    def get_session_users(self):
        return self.session_users

    def set_event(self, item):
        if not isinstance(item, SessionEvent):
            logger.critical("Session, set_event, not a SessionEvent: %s", item)
            return None

        if item in self.linked_events:
            return item.get_id()

        self.linked_events.append(item)
        return item.get_id()

    def get_events(self):
        return self.linked_events

    def has_joined(self, user=None, but_left=False):
        '''
        If the User (or SessionUser) in the parameter joined the session, returns True else False

        When called with no parameter, it returns True if any user joined the session.
        '''
        if user and isinstance(user, User):
            for session_user in self.get_session_users():
                if user.get_id() == session_user.get_user().get_id():
                    user = session_user
                    break

        if user and isinstance(user, SessionUser) and user in self.get_session_users():
            return user.get_status() == 'open' if not but_left else True

        if not user and (self.linked_users or self.session_users):
            return True

        return False


class SessionUser(Item):
    _count = 0
    # Next value used for auto generated id
    _next_id = 1
    # _type stands for Backend Object Type
    _type = 'userservice_session_user'
    # _cache is a list of created objects
    _cache = {}

    def __new__(cls, params=None, date_format='%a, %d %b %Y %H:%M:%S %Z'):
        '''
        Create a new session user
        '''
        return super(SessionUser, cls).__new__(cls, params, date_format)

    def _create(self, params, date_format):
        '''
        Create a session user (called only once when an object is newly created)
        '''
        self.linked_userservice_session = 'userservice_session'
        self.linked_user = 'user'

        super(SessionUser, self)._create(params, date_format)

    def _update(self, params=None, date_format='%a, %d %b %Y %H:%M:%S %Z'):
        '''
        Update a session user (called every time an object is updated)
        '''
        super(SessionUser, self)._update(params, date_format)
        logger.debug(" --- SessionUser: %s, update: %s", self._id, self.__dict__)

    def __init__(self, params=None):
        '''
        Initialize a session user (called every time an object is invoked)
        '''
        super(SessionUser, self).__init__(params)

        # Search if we already have User linked objects...
        for dummy, user in User.getCache().items():
            if hasattr(self, 'user') and user._id == self.user:
                self.set_user(user)

        # Link our own objects...
        logger.debug(" --- SessionUser: %s, back links: %s", self._id, self.__dict__)
        if self.get_user() and self.get_session():
            logger.debug(" --- SessionUser, link back session to user")
            self.get_session().set_user(self.get_user())
            self.get_session().set_session_user(self)
            logger.debug(" --- SessionUser, link back user to session")
            self.get_user().set_session(self.get_session())

    def __repr__(self):
        return ("<%s, id: %s, user: %s, session: %s, status: %s>") % (
            self.__class__._type, self.get_id(),
            self.get_user().get_name() if self.get_user() else 'unknown',
            self.get_session().get_id() if self.get_session() else 'unknown',
            self.get_status()
        )

    def get_session(self):
        if self.linked_userservice_session != 'userservice_session':
            return self.linked_userservice_session

        return None

    def get_user(self):
        if self.linked_user != 'user':
            return self.linked_user

        return None

    def set_user(self, item):
        if not isinstance(item, User):
            logger.critical("SessionUser, set_user, not a User: %s", item)
            return None

        self.linked_user = item
        return self.linked_user.get_id()

    def set_session(self, item):
        if not isinstance(item, Session):
            logger.critical("SessionUser, set_session, not a Session: %s", item)
            return None

        self.linked_userservice_session = item
        return self.linked_userservice_session.get_id()

    def get_date(self, timestamp=False, fmt=None):
        return self.get_join_date(timestamp=timestamp, fmt=fmt)

    def get_join_date(self, timestamp=False, fmt=None):
        '''
        TODO: Get the date in the related session events
        '''
        if self._created == self.__class__._default_date and not timestamp:
            return _('Never joined!')

        if timestamp:
            return self._created

        return super(SessionUser, self).get_date(self._created, fmt)

    def get_leave_date(self, timestamp=False, fmt=None):
        '''
        TODO: Get the date in the related session events
        '''
        if self._updated == self.__class__._default_date and not timestamp:
            return _('Never joined!')

        if timestamp:
            return self._updated

        return super(SessionUser, self).get_date(self._updated, fmt)


class SessionEvent(Item):
    _count = 0
    # Next value used for auto generated id
    _next_id = 1
    # _type stands for Backend Object Type
    _type = 'event'
    # _cache is a list of created objects
    _cache = {}

    # Session events messages
    message_ids = {
        "network_unavailable": _("No network connection"),
        "service_unavailable": _("Service unavailable."),
        "session_unavailable": _("Session opening unavailable."),
        "connect_ok": _("Connection established"),
        "connect_failed": _("Connection failed."),
        "auth_processing": _("Authenticating..."),

        "call_processing": _("Calling..."),
        "call_processing_details": _("An advisor will answer soon."),
        "please_wait": _("Hold on"),
        "in_conversation": _("In a call"),
        "in_conversation_details": _("Your advisor is answering."),
        "error_occured": _("An error occured."),
        "command_failed": _("Command failed."),
        "call_failed": _("Call failed."),
        "call_rejected": _("Call rejected."),
        "call_rejected_details": _("All our advisors are busy."),

        "print_processing": _("Printing..."),
        "print_ok": _("Printing finished."),
        "print_ok_details": _("Document printed succesfullly."),
        "print_ko": _("Printing failed."),
        "print_ko_details": _("Document printing failed."),

        "scan_processing": _("Scanning...."),
        "scan_ok": _("Scanning finished."),
        "scan_ok_details": _("Document scanned succesfully."),
        "scan_ko": _("Scanning failed."),
        "scan_ko_details": _("Document scanning failed.")
    }

    # Session events allowed types
    allowed_types = [
        # Session management events
        "session.opened",
        "session.joined",
        "session.left",
        "session.status",
        "session.closed",

        # Information posted from WebUI
        "info.webui",
        # Instant messaging
        "info.chat",

        # Command requested
        "command.print",
        "command.scan",
        "command.close",

        # Videoconferencing
        "video.launched",
        "video.notified",
        "video.rejected",
        "video.connected",
        "video.disconnected",

        # Attached a document
        "attachment.document",
        # Attached a counter
        "attachment.counter",
        # Monitoring event (kiosk and peripheral status)
        "attachment.status"
    ]

    # Session events types to display in the session timeline view
    timeline_types = [
        # Session management events
        "session.opened",
        "session.joined",
        "session.left",
        # "session.status", # Hide session status in the timeline
        "session.closed",

        # Information posted from WebUI
        "info.webui",
        # Instant messaging
        "info.chat",

        # Command requested
        "command.print",
        "command.scan",
        "command.close",

        # Videoconferencing
        "video.launched",
        "video.notified",
        "video.rejected",
        "video.connected",
        "video.disconnected",

        # Attached a document
        "attachment.document",
        # Attached a counter
        "attachment.counter",
        # Monitoring event (kiosk and peripheral status)
        "attachment.status"
    ]

    def __new__(cls, params=None, date_format='%a, %d %b %Y %H:%M:%S %Z'):
        '''
        Create a new event
        '''
        return super(SessionEvent, cls).__new__(cls, params, date_format)

    def _create(self, params, date_format):
        '''
        Create an event (called only once when an object is newly created)
        '''
        self.type = None

        self.linked_userservice_session = 'userservice_session'
        self.linked_user = 'user'
        self.linked_command = 'command'
        self.linked_document = 'host'

        if params and 'result' in params:
            if 'ack' in params['result']:
                params['command_ack'] = params['result']['ack']
            if 'status' in params['result']:
                params['command_status'] = params['result']['status']

            params.pop('result', None)

        super(SessionEvent, self)._create(params, date_format)

    def _update(self, params, date_format='%a, %d %b %Y %H:%M:%S %Z'):
        '''
        Update an event (called every time an object is updated)
        '''
        if 'result' in params:
            if 'ack' in params['result']:
                params['command_ack'] = params['result']['ack']
            if 'status' in params['result']:
                params['command_status'] = params['result']['status']

            params.pop('result', None)

        super(SessionEvent, self)._update(params, date_format)

        # State is based on command status if event is a command
        if hasattr(self, 'command_status'):
            self.state = getattr(self, 'command_status', 99)

    def __init__(self, params=None):
        '''
        Initialize an event (called every time an object is invoked)
        '''
        super(SessionEvent, self).__init__(params)

        # Event type must exist in the allowed types
        if not hasattr(self, 'type'):
            self.type = 'info.webui'

        if self.type not in self.__class__.allowed_types:
            logger.warning("SessionEvent: type is not in the allowed types list: %s", self.type)
            self.type = 'info.webui'

        # State is based on command status if event is a command
        if hasattr(self, 'command_status'):
            self.state = getattr(self, 'command_status', 99)

        logger.debug(" --- SessionEvent: %s, back links", self._id)
        if self.get_session():
            logger.debug(" --- SessionEvent, link back session to event")
            self.get_session().set_event(self)
        if self.get_document():
            logger.debug(" --- SessionEvent, link back host to event")
            self.get_document().set_event(self)
        if self.get_command():
            logger.debug(" --- SessionEvent, link back command to event")
            self.get_command().set_event(self)

    def get_status(self):
        """
        For an event, status is the event type
        """
        return self.type

    def get_state(self):
        # State is based on command status if event is a command
        if hasattr(self, 'command_status'):
            self.state = getattr(self, 'command_status', 99)

        return super(SessionEvent, self).get_state()

    def get_session(self):
        if self.linked_userservice_session != 'userservice_session':
            return self.linked_userservice_session

        return None

    def get_user(self):
        if self.linked_user != 'user':
            return self.linked_user

        return None

    def get_document(self):
        """ Used to test if the event concerns a host """
        if self.linked_document != 'host':
            return self.linked_document

        return None

    def get_command(self):
        """ Used to test if the event concerns a command """
        if self.linked_command != 'command':
            return self.linked_command

        return None

    def get_date(self, timestamp=False, fmt=None):
        if self.date == self.__class__._default_date and not timestamp:
            return _('Never dated!')

        if timestamp:
            return self.date

        return super(SessionEvent, self).get_date(self.date, fmt)

    def get_type(self):
        return getattr(self, 'type', '')

    def get_name(self):
        ''' Name of an event is its type '''
        return getattr(self, 'type', '')

    def get_message(self):
        if getattr(self, 'message', '') in self.__class__.message_ids:
            return self.__class__.message_ids[getattr(self, 'message', '')]

        return getattr(self, 'message', '')

    def set_user(self, item):
        if not isinstance(item, User):
            logger.critical("SessionEvent, set_user, not a User: %s", item)
            return None

        self.linked_user = item
        return self.linked_user.get_id()

    def set_session(self, item):
        if not isinstance(item, Session):
            logger.critical("SessionEvent, set_session, not a Session: %s", item)
            return None

        self.linked_userservice_session = item
        return self.linked_userservice_session.get_id()

    def set_document(self, item):
        if not isinstance(item, Host):
            logger.critical("SessionEvent, set_document, not a Host: %s", item)
            return None

        self.linked_document = item
        return self.linked_document.get_id()

    def set_command(self, item):
        if not isinstance(item, Command):
            logger.critical("SessionEvent, set_command, not a Command: %s", item)
            return None

        self.linked_command = item
        return self.linked_command.get_id()


class Host(Item):
    _count = 0
    # Next value used for auto generated id
    _next_id = 1
    # _type stands for Backend Object Type
    _type = 'host'
    # _cache is a list of created objects
    _cache = {}

    def __new__(cls, params=None, date_format='%a, %d %b %Y %H:%M:%S %Z'):
        '''
        Create a new user
        '''
        return super(Host, cls).__new__(cls, params, date_format)

    def _create(self, params, date_format):
        '''
        Create a host (called only once when an object is newly created)
        '''
        self.linked_userservice_session = 'userservice_session'
        self.linked_event = 'event'

        super(Host, self)._create(params, date_format)

    def _update(self, params=None, date_format='%a, %d %b %Y %H:%M:%S %Z'):
        '''
        Update a host (called every time an object is updated)
        '''
        super(Host, self)._update(params, date_format)

    def __init__(self, params=None):
        '''
        Initialize a host (called every time an object is invoked)
        '''
        super(Host, self).__init__(params)

    def has_attachment(self):
        return self.attachment

    def get_date(self, timestamp=False, fmt=None):
        if self.date == self.__class__._default_date and not timestamp:
            return _('Never dated!')

        if timestamp:
            return self.date

        return super(Host, self).get_date(self.date, fmt)

    def get_filename(self):
        if not self.has_attachment():
            return ''
        return getattr(self, 'filename', 'unknown')

    def get_document_type(self):
        if not self.has_attachment():
            return ''
        doc_type = self.get_content_type()
        if 'image' in doc_type:
            return _('Image host')
        if 'pdf' in doc_type:
            return _('PDF host')
        if 'txt' in doc_type or 'text' in doc_type:
            return _('Text host')

        return doc_type

    def get_content_type(self):
        if not self.has_attachment():
            return ''
        return getattr(self, 'content_type', '')

    def get_length(self):
        if not self.has_attachment():
            return 0
        return getattr(self, 'length', 0)

    def get_content(self):
        if not self.has_attachment():
            return ''
        return getattr(self, 'file', None)

    def get_download_link(self, complete=True):
        if not self.get_filename():
            return ''

        if complete:
            return (
                '<a href="%s?id=%s">'
                '<span class="fa-stack">'
                '<i class="fa fa-circle fa-stack-2x font-greyed"></i>'
                '<i class="fa fa-close fa-stack-1x fa-download"></i>'
                '</span>'
                '<span>'
                '&nbsp;'
                '<small>%s</small>'
                '</span>'
                '<span class="hidden-xs">'
                '&nbsp;'
                '<small><em>(%s bytes)</em></small>'
                '</span>'
                '</a>'
            ) % ('/host', self.get_id(), self.get_filename(), self.get_length())
        else:
            return (
                '<a href="%s?id=%s">'
                '<span class="fa-stack">'
                '<i class="fa fa-circle fa-stack-2x font-greyed"></i>'
                '<i class="fa fa-close fa-stack-1x fa-download"></i>'
                '</span>'
                '</a>'
            ) % ('/host', self.get_id())

    def set_event(self, item):
        if not isinstance(item, SessionEvent):
            logger.critical("Host, set_event, not a SessionEvent: %s", item)
            return None

        self.linked_event = item
        return self.linked_event.get_id()


class Command(Item):
    _count = 0
    # Next value used for auto generated id
    _next_id = 1
    # _type stands for Backend Object Type
    _type = 'command'
    # _cache is a list of created objects
    _cache = {}

    def __new__(cls, params=None, date_format='%a, %d %b %Y %H:%M:%S %Z'):
        '''
        Create a new command
        '''
        return super(Command, cls).__new__(cls, params, date_format)

    def _create(self, params, date_format):
        '''
        Create a command (called only once when an object is newly created)
        '''
        self.linked_userservice_session = 'userservice_session'
        self.linked_event = 'event'

        super(Command, self)._create(params, date_format)

    def _update(self, params=None, date_format='%a, %d %b %Y %H:%M:%S %Z'):
        '''
        Update a command (called every time an object is updated)
        '''
        super(Command, self)._update(params, date_format)

    def __init__(self, params=None):
        '''
        Initialize a command (called every time an object is invoked)
        '''
        super(Command, self).__init__(params)


# Sort methods
# -----------------------------------------------------
# Sort elements by descending date
def sort_items_most_recent_first(s1, s2):  # pragma: no cover, hard to test ...
    if s1.get_date() > s2.get_date():
        return -1
    if s1.get_date() < s2.get_date():
        return 1
    return 0


# Sort elements by ascending date
def sort_items_least_recent_first(s1, s2):  # pragma: no cover, hard to test ...
    if s1.get_date() < s2.get_date():
        return -1
    if s1.get_date() > s2.get_date():
        return 1
    return 0
