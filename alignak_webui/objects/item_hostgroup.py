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
# noinspection PyProtectedMember
from alignak_webui import _

from alignak_webui.objects.element import BackendElement


class HostGroup(BackendElement):
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

    def _create(self, params, date_format):
        """
        Create a hostgroup (called only once when an object is newly created)
        """
        self._linked_hostgroups = 'hostgroup'
        self._linked__parent = 'hostgroup'
        self._linked_hosts = 'host'

        super(HostGroup, self)._create(params, date_format)

    @property
    def members(self):
        """ Return linked object """
        return self._linked_hosts

    @property
    def hosts(self):
        """ Return linked object """
        return self._linked_hosts

    @property
    def hostgroups(self):
        """ Return linked object """
        return self._linked_hostgroups

    @property
    def _parent(self):
        """ Return group parent """
        return self._linked__parent

    @property
    def level(self):
        """ Return group level """
        if not hasattr(self, '_level'):
            return -1
        return self._level
