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

from logging import getLogger, INFO

# noinspection PyProtectedMember
from alignak_webui import _
# Import the backend interface class

# Set logger level to INFO, this to allow global application DEBUG logs without being spammed... ;)
from alignak_webui.objects.element import BackendElement

logger = getLogger(__name__)
logger.setLevel(INFO)


class Log(BackendElement):
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

    def _create(self, params, date_format):
        # Not that bad ... because _create is called from __new__
        # pylint: disable=attribute-defined-outside-init
        """
        Create a log (called only once when an object is newly created)
        """
        self._linked_host = 'host'
        self._linked_service = 'service'

        super(Log, self)._create(params, date_format)

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
