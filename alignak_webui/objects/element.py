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
    This module contains the base class used to manage the application objects
    with the data manager.
"""

import time

from copy import deepcopy

from datetime import datetime
from logging import getLogger, INFO

from alignak_webui import get_app_config
# Import the backend interface class
from alignak_webui.backend.backend import BackendConnection
from alignak_webui.objects.element_state import ElementState
from alignak_webui.utils.helper import Helper
from alignak_webui.utils.dates import get_ts_date

# Set logger level to INFO, this to allow global application DEBUG logs without being spammed... ;)
# pylint: disable=invalid-name
logger = getLogger(__name__)
logger.setLevel(INFO)


class BackendElement(object):
    # Yes, but it is the base object and it needs those pubic methods!
    # pylint: disable=too-many-public-methods
    """
    Base class for all the data manager objects

    An Item is created from a dictionary with some specific features:
    - an item has an identifier, a name, an alias and a comment (notes)
    - some specific treatments are applied on some specific fields (see __init__ method doc)
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

    # Default elements common fields
    _name = 'anonymous'
    _status = 'unknown'
    _alias = ''
    _notes = ''

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
    def get_known_classes(cls):
        """Get protected member"""
        return cls._known_classes

    @classmethod
    def set_known_classes(cls, known_classes):
        """ Set protected member _known_classes """
        cls._known_classes = known_classes

    @classmethod
    def get_backend(cls):
        """Get protected member"""
        return cls._backend

    @classmethod
    def set_backend(cls, backend):
        """Set protected member _backend"""
        cls._backend = backend

    @classmethod
    def get_type(cls):
        """Get protected member"""
        return cls._type

    @classmethod
    def get_count(cls):
        """Get protected member"""
        return cls._count

    @classmethod
    def get_total_count(cls):
        """Get protected member"""
        return cls._total_count

    @classmethod
    def set_total_count(cls, count):
        """Set protected member _total_count"""
        cls._total_count = count

    @classmethod
    def get_cache(cls):
        """Get protected member"""
        return cls._cache

    @classmethod
    def clean_cache(cls):
        """
        Clean internal objects cache and reset the internal counters
        """
        cls._next_id = 1
        cls._count = 0
        cls._total_count = -1
        cls._cache = {}

    def __new__(cls, params=None, date_format='%a, %d %b %Y %H:%M:%S %Z', embedded=True):
        """Create a new object

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

        if not cls.get_backend():
            # Get global configuration
            app_config = get_app_config()
            if not app_config:  # pragma: no cover, should not happen
                return

            cls._backend = BackendConnection(
                app_config.get('alignak_backend', 'http://127.0.0.1:5000')
            )

        _id = '0'
        if params:
            if not isinstance(params, dict):
                logger.warning("__new__ Class %s, id_property: %s, type: %s, invalid params: %s",
                               cls, id_property, type(params), params)
                if isinstance(params, BackendElement):  # pragma: no cover, not tested!
                    # params = params.__dict__
                    # Do not copy, build a new object...
                    if params.id in cls._cache:
                        logger.warning(
                            "New %s, id: %s, cache copy of an object", cls, cls._cache[params.id]
                        )
                        return cls._cache[params.id]
                    logger.info("New %s, id: %s, copy an object", cls, params)
                    return deepcopy(params)
                else:
                    logger.critical("Class %s, id_property: %s, invalid params: %s",
                                    cls, id_property, params)
                    raise ValueError(
                        '%s.__new__: object parameters must be a dictionary!' % (cls._type)
                    )

            if id_property in params:
                if not isinstance(params[id_property], basestring):
                    params[id_property] = str(params[id_property])
                _id = params[id_property]
            else:
                _id = '%s_%d' % (cls.get_type(), cls._next_id)
                params[id_property] = _id
                cls._next_id += 1

        if _id == '0':
            if not params:
                params = {}
            now = int(time.time())
            # Force _id in the parameters
            params.update({
                id_property: '%s_0' % (cls.get_type()),
                '_created': now, '_updated': now
            })

        try:
            logger.debug("New %s, id: %s, params: %s", cls, id_property, params['name'])
        except Exception:
            logger.debug("New %s, id: %s, params: %s (%s)", cls,
                         id_property, params.__class__, params)

        if _id not in cls._cache:
            # print "Create a new %s (%s)" % (cls.get_type(), _id)
            logger.debug("New create an object")
            cls._cache[_id] = super(BackendElement, cls).__new__(cls, params, date_format)
            cls._cache[_id]._type = cls.get_type()
            cls._cache[_id]._default_date = cls._default_date
            # print " ... new: %s" % cls._cache[_id]

            # Call the new object create function
            cls._cache[_id].__init__(params, date_format, embedded)
            cls._count += 1
        else:
            logger.debug("New %s, id: %s, object exists in cache", cls, cls._cache[_id])

        try:
            logger.debug("New end, object: %s", cls._cache[_id]['name'])
        except Exception:  # pragma: no cover, should not happen
            logger.debug("New end, object: %s", cls._cache[_id].__dict__)
        return cls._cache[_id]

    def _delete(self):
        """Delete an object

        If the object exists in the cache, its reference is removed from the internal cache.
        """
        logger.debug(" --- deleting a %s (%s)", self.__class__, self._id)
        cls = self.__class__
        if self._id in cls._cache:
            logger.debug("Removing from cache...")
            del cls._cache[self._id]
            cls._count -= 1
            logger.debug("Removed. Remaining in cache: %d / %d",
                         cls.get_count(), len(cls.get_cache()))

    def __init__(self, params=None, date_format='%a, %d %b %Y %H:%M:%S %Z', embedded=True):
        # Yes, but we need those locals!
        # pylint: disable=too-many-locals
        # pylint:disable=too-many-nested-blocks
        # Yes, but it is the base object and it needs those arguments!
        # pylint: disable=unused-argument
        """
        Initialize an object

        Beware: always called, even if the object is not newly created! Use __init__ function for
        initializing newly created objects.
        """
        logger.debug(" --- __init__ %s", self.__class__)
        if params is None:
            logger.debug("__init__, cannot update an object (%s) with no parameters.", self)
            return

        if not isinstance(params, dict):  # pragma: no cover, should not happen
            if self.__class__ == params.__class__:
                params = params.__dict__
            elif self.get_known_classes() and params.__class__ in self.get_known_classes():
                params = params.__dict__
            else:
                logger.warning("__init__, cannot update an object (%s) with: %s (%s). "
                               "Updated object is a second level object, else "
                               "you should try to embed this object from the backend",
                               self.__class__, params, params.__class__)
                return

        for key, value in sorted(params.items()):
            if hasattr(self, '_linked_' + key):
                # Not yet the linked objects...
                continue
            # logger.debug(" --- parameter %s = %s", key, params[key])

            # If the property is a date, make it a timestamp...
            if key.endswith('date') or key in self.__class__._dates:
                if params[key]:
                    # Convert date to timestamp
                    new_date = get_ts_date(params[key], date_format)
                    if new_date:
                        setattr(self, key, new_date)
                        continue

                setattr(self, key, self.__class__._default_date)
                continue

            try:
                setattr(self, key, params[key])
            except Exception as exp:
                logger.critical("__init__ parameter exception: %s, %s = %s",
                                self.__class__, key, params[key])
                logger.exception("exception: %s", exp)

        if embedded:
            for key, value in sorted(params.items()):
                if not hasattr(self, '_linked_' + key):
                    # Only the linked objects...
                    continue
                logger.debug(" --- linked parameter %s = %s", key, params[key])

                # Object must have declared a _linked_ attribute ...
                if value is not None and self.get_known_classes():
                    logger.debug("__init__, link parameter: %s (%s) = %s",
                                 key, params[key].__class__, value)

                    object_type = getattr(self, '_linked_' + key, None)
                    if object_type is None:  # pragma: no cover, should not happen
                        logger.error("__init__, object_type is None, key %s for %s, as %s for %s",
                                     key, self.get_type(), object_type, params[key])
                        continue

                    # Already contains an object, so update object ...
                    # Currently, DO NOTHING!
                    if isinstance(object_type, BackendElement):
                        logger.debug("__init__, already linked with an object, %s/%s: %s",
                                     self.get_type(), key, object_type)
                        continue
                    elif isinstance(object_type, list):
                        if object_type and object_type[0] \
                                and isinstance(object_type[0], BackendElement):
                            logger.debug("__init__, already linked with an object list, %s/%s: %s",
                                         self.get_type(), key, object_type)
                        continue
                    elif not isinstance(object_type, dict) and \
                            object_type not in [kc.get_type() for kc
                                                in self.get_known_classes()]:
                        logger.error("__init__, unknown %s for %s, as %s for %s",
                                     key, self.get_type(), object_type, params[key])
                        continue

                    object_class = [kc for kc in self.get_known_classes()
                                    if kc.get_type() == object_type][0]

                    # Linked resource type
                    logger.debug("__init__, must create a link for %s -> %s with %s ",
                                 self.object_type, key, value)

                    # Dictionary from a backend embedded object
                    if isinstance(params[key], dict):
                        if '_id' in params[key] and params[key]['_id'] not in object_class._cache:
                            linked_object = object_class(params[key])
                            setattr(self, '_linked_' + key, linked_object)
                        else:
                            logger.debug("__init__ %s: %s, object exists in cache",
                                         key, object_class._cache[params[key]['_id']])
                            setattr(self, '_linked_' + key, object_class._cache[params[key]['_id']])
                            logger.debug("__init__, linked with %s (%s)",
                                         key, object_class._cache[params[key]['_id']])
                        continue

                    # String - object id
                    if isinstance(params[key], basestring) and params[key] and self.get_backend():
                        if params[key] not in object_class._cache:
                            try:
                                # Object link is a string, so we load the object from the backend
                                result = self.get_backend().get(object_type + '/' + params[key])
                                if not result:  # pragma: no cover, should not happen
                                    logger.error("__init__, item not found for %s, %s",
                                                 object_type, value)
                                    continue
                            except:  # pragma: no cover, should not happen
                                logger.error("__init__, item not existing for %s, %s",
                                             object_type, value)
                                continue

                            # Create a new object
                            linked_object = object_class(result)
                            setattr(self, '_linked_' + key, linked_object)
                            logger.debug("__init__, linked with %s (%s)", key, linked_object['_id'])
                        else:
                            logger.debug("__init__ %s: %s, object exists in cache",
                                         key, object_class._cache[params[key]])
                            setattr(self, '_linked_' + key, object_class._cache[params[key]])
                            logger.debug("__init__, linked with %s (%s)",
                                         key, object_class._cache[params[key]])
                        continue

                    # List - list of objects id
                    if isinstance(params[key], list):
                        objects_list = []
                        for element in params[key]:
                            if isinstance(element, basestring) and self.get_backend():
                                if element not in object_class._cache:
                                    try:
                                        # we need to load the object from the backend
                                        result = self.get_backend().get(object_type + '/' + element)
                                        if not result:  # pragma: no cover, should not happen
                                            logger.error("__init__, item not found for %s, %s",
                                                         object_type, value)
                                            continue
                                    except:  # pragma: no cover, should not happen
                                        logger.error("__init__, item not existing for %s, %s",
                                                     object_type, value)
                                        continue

                                    # Create a new object
                                    objects_list.append(object_class(result))
                                else:
                                    logger.debug("__init__ %s: %s, object exists in cache",
                                                 key, object_class._cache[element])
                                    objects_list.append(object_class._cache[element])
                            elif isinstance(element, dict):
                                # Create a new object from a dict
                                objects_list.append(object_class(element))
                            else:  # pragma: no cover, should not happen
                                logger.critical("__init__, list element %s is not a string "
                                                "nor a dict: %s", key, element)
                                continue

                        setattr(self, '_linked_' + key, objects_list)
                        logger.debug("__init__, linked with %s (%s)",
                                     key, [o for o in objects_list])
                        continue
                else:
                    logger.debug("__init__, no value for link parameter: %s (%s), "
                                 "for: %s, %s, value: %s",
                                 key, params[key].__class__, self.get_type(),
                                 params['name'] if 'name' in params else params['_id'], value)

        logger.debug(" --- __init__ end")

    def __repr__(self):
        return "<%s, id: %s, name: %s, status: %s>" \
               % (self.__class__.get_type(), self.id, self.name, self.status)

    def __getitem__(self, key):
        return getattr(self, key, None)

    @property
    def object_type(self):
        """Get Item object type"""
        return self._type

    @property
    def id(self):
        """Get Item object identifier

        A class inheriting from an Item can define its own `id_property`
        """
        if hasattr(self.__class__, 'id_property'):
            return getattr(self, self.__class__.id_property, None)
        return self._id

    @property
    def updated(self):
        """Get Item update date as a timestamp"""
        return self._updated

    @property
    def created(self):
        """Get Item creation date as a timestamp"""
        return self._created

    @property
    def name(self):
        """Get Item object name

        A class inheriting from an Item can define its own `name_property`
        """
        if hasattr(self.__class__, 'name_property'):
            return getattr(self, self.__class__.name_property, None)
        return self._name

    @property
    def endpoint(self):
        """Get Item endpoint (page url)"""
        return '/%s/%s' % (self.object_type, self.name)

    @property
    def html_link(self):
        """Get Item html link"""
        return '<a href="%s" title="%s">%s</a>' % (self.endpoint, self.name, self.json_alias)

    def get_html_link(self, prefix=None, title=None):
        """Get Item html link with an optional prefix and an optional title"""
        if prefix is not None:
            return '<a href="%s%s">%s</a>' % (
                prefix, self.endpoint, self.alias if not title else title
            )
        if title:
            return '<a href="%s">%s</a>' % (self.endpoint, title)
        return self.html_link

    @property
    def html_state_link(self):
        """Get Item html link with state"""
        return '<a href="%s">%s</a>' \
               % (self.endpoint, self.get_html_state(text=self.json_alias, title=self.json_alias))

    def get_html_state_link(self, prefix=None, title=None):
        """Get Item html link with state and an optional prefix"""
        if prefix is not None:
            return '<a href="%s%s">%s</a>' \
                   % (prefix, self.endpoint,
                      self.get_html_state(text=self.json_alias,
                                          title=self.json_alias if not title else title))
        if title:
            return '<a href="%s" title="%s">%s</a>' \
                   % (self.endpoint, title, self.get_html_state(text=self.alias, title=title))

        return self.html_state_link

    @name.setter
    def name(self, name):
        """Set Item object name"""
        if hasattr(self.__class__, 'name_property'):
            setattr(self, self.__class__.name_property, name)
        else:
            self._name = name

    @property
    def alias(self):
        """Get Item object alias - raw form"""
        if hasattr(self, '_alias') and getattr(self, '_alias', None):
            return getattr(self, '_alias', self.name)
        return getattr(self, 'name', '')

    @property
    def json_alias(self):
        """Get Item object alias - JSON encoded alias

        Single or double quotes are properly escaped for HTML pages
        """
        if hasattr(self, '_alias') and getattr(self, '_alias', None):
            # Sanitize string to make it usable in Javascript
            json_alias = getattr(self, '_alias', self.name)
            json_alias = json_alias.replace("'", "\\'")
            json_alias = json_alias.replace('"', '\\"')
            return json_alias
        return getattr(self, 'name', '')

    @alias.setter
    def alias(self, alias):
        """Set Item object alias"""
        self._alias = alias

    @property
    def notes(self):
        """Get Item object notes

        A class inheriting from an Item can define its own `comment_property`
        """
        if hasattr(self.__class__, 'comment_property'):
            return getattr(self, self.__class__.comment_property, None)
        return self._notes

    @notes.setter
    def notes(self, notes):
        """Get Item object notes

        A class inheriting from an Item can define its own `comment_property`
        """
        if hasattr(self.__class__, 'comment_property'):
            setattr(self, self.__class__.comment_property, notes)
        else:
            self._notes = notes

    @property
    def status(self):
        """Get Item object status

        A class inheriting from an Item can define its own `status_property`
        """
        if hasattr(self.__class__, 'status_property'):
            return getattr(self, self.__class__.status_property, None)
        return self._status

    @status.setter
    def status(self, status):
        """Get Item object status

        A class inheriting from an Item can define its own `status_property`
        """
        if hasattr(self.__class__, 'status_property'):
            setattr(self, self.__class__.status_property, status)
        else:
            self._status = status

    @property
    def total_count(self):
        """Get Item total count

        BackendElement has an _total set by the BackendConnection get method...
        """
        if hasattr(self, '_total'):
            return self._total
        return 0

    @property
    def is_problem(self):
        """An element is never a problem except if it overloads this method"""
        return False

    @property
    def acknowledged(self):
        """An element is never acknowledged except if it overloads this method"""
        return False

    @property
    def downtimed(self):
        """An element is never in a downtime except if it overloads this method"""
        return False

    def get_state(self):
        """Get Item object state

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

    def get_html_state(self, extra='', icon=True, text='',
                       title='', disabled=False, object_type=None, object_item=None,
                       size='', use_status=None):
        # pylint: disable=too-many-arguments
        """Uses the ElementState singleton to display HTML state for an item"""
        if not object_type:
            object_type = self.object_type

        if not object_item:
            object_item = self

        return ElementState().get_html_state(object_type, object_item,
                                             extra, icon, text, title, disabled, size,
                                             use_status)

    def get_date(self, _date, fmt=None, duration=False):
        """Format the provided `_date` as a string according to the specified format.

        If no date format is specified, it uses the one defined in the ElementState object that is
        the date format defined in the application configuration.

        If duration is True, the date is displayed as a pretty date: 1 day 12 minutes ago ...
        """
        if _date == self.__class__._default_date:
            return _('Never dated!')

        if duration:
            return Helper.print_duration(_date, duration_only=False, x_elts=0)

        item_state = ElementState()
        if not fmt:
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
