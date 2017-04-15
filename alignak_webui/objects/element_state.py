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
    This module contains the base class used to manage the application objects configuration:
    - representation,
    - date
    -...
"""
from __future__ import print_function

from logging import getLogger, INFO

from dateutil import tz

from alignak_webui import get_app_config

# Set logger level to INFO, this to allow global application DEBUG logs without being spammed... ;)
# pylint: disable=invalid-name
logger = getLogger(__name__)
logger.setLevel(INFO)


# pylint: disable=too-few-public-methods
class ElementState(object):
    """
    Singleton design pattern ...
    """
    class __ElementState(object):
        """
        Base class for all objects state management (displayed icon, ...)
        """

        def __init__(self):
            self.states = {}

            # Get global configuration
            app_config = get_app_config()
            if not app_config:  # pragma: no cover, should not happen
                print("No application configuration!")
                assert False

            self.object_types_states = {}
            self.default_states = {}
            for s in app_config:
                s = s.split('.')
                if s[0] not in ['items']:
                    continue

                logger.debug("ElementState, item configuration element: %s", s)
                if s[1] == 'item':
                    if s[2] not in self.default_states:
                        self.default_states[s[2]] = []
                    continue

                if s[1] not in ['content', 'back', 'front', 'badge']:
                    if s[1] not in self.object_types_states:
                        self.object_types_states[s[1]] = []

                    if s[2] and s[2] not in self.object_types_states[s[1]]:
                        self.object_types_states[s[1]].append(s[2])

            logger.debug("ElementState, object types and states: %s", self.object_types_states)
            logger.debug("ElementState, default states: %s", self.default_states)

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
                            app_config.get("items.%s" % prop)

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

            status = status.lower()

            if status not in self.get_icon_states(object_type):
                return None

            for s in self.get_icon_states(object_type):
                if status == s:
                    return self.get_icon_states(object_type)[s]

            return None

        def get_html_state(self, object_type, object_item, extra='', icon=True, text='',
                           title='', disabled=False, size='', use_status=None):
            # pylint: disable=too-many-arguments
            # Yes, but it is needed ;)
            # pylint: disable=too-many-locals, too-many-return-statements
            # Yes, but else it will be quite difficult :/

            """Returns an item status as HTML text and icon if needed

            If parameters are not valid, returns 'n/a'

            If disabled is True, the class does not depend upon object status and is always
            text-muted

            If a title is specified, it will be used instead of the default built-in text.

            If object status contains '.' characters they are replaced with '_'

            Text and icon are defined in the application configuration file.

            :param size:
            :param disabled:
            :param title:
            :param object_type: element type
            :type object_type: string
            :param object_item: element
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
            if use_status:
                status = use_status
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

            # If item is acknowledged or downtimed...
            opacity = False
            if getattr(object_item, 'acknowledged', False):
                opacity = True
            if getattr(object_item, 'downtimed', False):
                opacity = True

            # Text
            res_icon_state = cfg_state['icon']
            res_icon_text = cfg_state['text']
            res_icon_class = 'item_' + cfg_state['class']
            res_text = res_icon_text

            if not icon:
                if text == '':
                    return res_text
                return text

            # Icon
            res_icon_global = cfg_state_view['content']
            res_icon_back = cfg_state_view['back']
            res_icon_front = cfg_state_view['front']

            res_extra = ""
            if extra:
                res_extra = extra
            res_opacity = ""
            if opacity:
                res_opacity = 'style="opacity: 0.5"'

            # Assembling ...
            item_id = object_item.id
            res_icon = res_icon_global
            res_icon = res_icon.replace("##type##", object_type)
            res_icon = res_icon.replace("##id##", item_id)
            res_icon = res_icon.replace("##name##", object_item.json_alias)
            res_icon = res_icon.replace("##state##", object_item.get_state())
            res_icon = res_icon.replace("##back##", res_icon_back)
            res_icon = res_icon.replace("##front##", res_icon_front)
            res_icon = res_icon.replace("##status##", status.lower())
            res_icon = res_icon.replace("##size##", size)
            if not disabled:
                res_icon = res_icon.replace("##class##", res_icon_class)
            else:
                res_icon = res_icon.replace("##class##", "text-muted")

            res_icon = res_icon.replace("##icon##", res_icon_state)
            res_icon = res_icon.replace("##extra##", res_extra)
            res_icon = res_icon.replace("##opacity##", res_opacity)

            if not title:
                title = res_extra

            if text is None:
                res_text = ''
            elif text != '':
                res_text = text
                if extra:
                    res_text += extra

            res_icon = res_icon.replace("##title##", title)
            res_icon = res_icon.replace("##text##", res_text)

            logger.debug("get_html_state, res_icon: %s", res_icon)
            res_icon = res_icon.replace("\n", "")
            res_icon = res_icon.replace("\r", "")
            return res_icon

    instance = None

    def __new__(cls):
        if not ElementState.instance:
            ElementState.instance = ElementState.__ElementState()
        return ElementState.instance

    def get_html_state(self, object_type, object_item, extra='', icon=True, text='',
                       title='', disabled=False, size='', use_status=None):
        # pylint: disable=too-many-arguments
        """
        Base function used by Item objects
        """
        return self.instance.get_html_state(object_type, object_item,
                                            extra, icon, text, title, disabled, size,
                                            use_status)
