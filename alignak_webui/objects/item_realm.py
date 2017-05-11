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
from alignak_webui.objects.element import BackendElement


class Realm(BackendElement):
    """Object representing a realm"""
    _count = 0
    # Next value used for auto generated id
    _next_id = 1
    # _type stands for Backend Object Type
    _type = 'realm'
    # _cache is a list of created objects
    _cache = {}

    # Converting real state identifier to text status
    overall_state_to_status = [
        'ok', 'acknowledged', 'in_downtime', 'warning', 'critical', 'nope'
    ]

    def __init__(self, params=None, date_format='%a, %d %b %Y %H:%M:%S %Z', embedded=True):
        """Create a realm (called only once when an object is newly created)"""
        self._linked__parent = 'realm'
        self._linked__children = 'realm'

        super(Realm, self).__init__(params, date_format, embedded)

    @property
    def members(self):
        """Return linked object"""
        return self._linked_hosts

    @property
    def hosts(self):
        """Return linked object"""
        return self._linked_hosts

    @property
    def realms(self):
        """Return linked object"""
        return self._linked__children

    @property
    def _parent(self):
        """Return realm parent"""
        return self._linked__parent

    @property
    def level(self):
        """Return realm level"""
        return self._level
