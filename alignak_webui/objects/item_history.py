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
    This module contains the classes used to manage the backend history elements
    with the data manager.
"""
# Import the backend interface class
from alignak_webui.objects.element import BackendElement
from alignak_webui.objects.element_state import ElementState


class History(BackendElement):
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

    def __init__(self, params=None, date_format='%a, %d %b %Y %H:%M:%S %Z', embedded=True):
        # Not that bad ... because __init__ is called from __new__
        # pylint: disable=attribute-defined-outside-init
        """
        Create a History (called only once when an object is newly created)
        """
        self._linked_host = 'host'
        self._linked_service = 'service'
        self._linked_user = 'user'
        self._linked_logcheckresult = 'logcheckresult'

        super(History, self).__init__(params, date_format, embedded)

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

    def get_html_state(self, extra='', icon=True, text='',
                       title='', disabled=False, object_type=None, object_item=None,
                       size='', use_status=None):
        # pylint: disable=too-many-arguments
        """
        Uses the ElementState singleton to display HTML state for an item
        """
        if self.type.startswith('check.result') and self.logcheckresult != 'logcheckresult':
            return ElementState().get_html_state('logcheckresult', self.logcheckresult,
                                                 extra, icon, text, title, disabled)

        return super(History, self).get_html_state(object_type=self.get_type(), object_item=self,
                                                   extra=extra, icon=icon, text=text,
                                                   title=title, disabled=disabled, size=size)

    def get_check_date(self, timestamp=False, fmt=None, duration=False):
        """
        Returns a string formatted data
        """
        if self.date == self.__class__._default_date and not timestamp:
            return 'XxX'

        if timestamp:
            return self.date

        return super(History, self).get_date(self.date, fmt, duration)
