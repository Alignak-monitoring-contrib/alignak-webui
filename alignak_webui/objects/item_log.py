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
    This module contains the classes used to manage the application objects with the data manager.
"""

from logging import getLogger, INFO

# Import the backend interface class
from alignak_webui.objects.element import BackendElement

# pylint: disable=invalid-name
logger = getLogger(__name__)
logger.setLevel(INFO)


class Log(BackendElement):
    """Object representing a log item (host or service)"""
    _count = 0
    # Next value used for auto generated id
    _next_id = 1
    # _type stands for Backend Object Type
    _type = 'logcheckresult'
    # _cache is a list of created objects
    _cache = {}

    # Status property
    status_property = 'state'

    def __init__(self, params=None, date_format='%a, %d %b %Y %H:%M:%S %Z', embedded=True):
        # Not that bad ... because __init__ is called from __new__
        # pylint: disable=attribute-defined-outside-init
        """Create a log (called only once when an object is newly created)"""
        self._linked_host = 'host'
        self._linked_service = 'service'

        super(Log, self).__init__(params, date_format, embedded)

    @property
    def host(self):
        """Return linked object"""
        return self._linked_host

    @property
    def service(self):
        """Return linked object"""
        return self._linked_service

    @property
    def acknowledged(self):
        """Get the inner object propery acknowledged"""
        return self._acknowledged

    @acknowledged.setter
    def acknowledged(self, acknowledged):
        """Set Item property acknowledged"""
        self._acknowledged = acknowledged

    @property
    def downtimed(self):
        """Get the inner object propery downtimed"""
        return self._downtimed

    @downtimed.setter
    def downtimed(self, downtimed):
        """Set Item property downtimed"""
        self._downtimed = downtimed

    def get_check_date(self, timestamp=False, fmt=None, duration=False):
        """Returns a string formatted date"""
        if self.last_check == self.__class__._default_date and not timestamp:
            return _('Never checked!')

        if timestamp:
            return self.last_check

        return super(Log, self).get_date(self.last_check, fmt, duration)
