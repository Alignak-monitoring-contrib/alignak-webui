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


class HostDependency(BackendElement):
    """
    Object representing a hostdependency
    """
    _count = 0
    # Next value used for auto generated id
    _next_id = 1
    # _type stands for Backend Object Type
    _type = 'hostdependency'
    # _cache is a list of created objects
    _cache = {}

    def _create(self, params, date_format):
        """
        Create a hostdependency (called only once when an object is newly created)
        """
        self._linked__realm = 'realm'
        self._linked_dependent_hosts = 'host'
        self._linked_dependent_hostgroups = 'hostgroup'
        self._linked_hosts = 'host'
        self._linked_hostgroups = 'hostgroup'

        super(HostDependency, self)._create(params, date_format)

    @property
    def _realm(self):
        """ Return concerned realm """
        return self._linked__realm

    @property
    def hosts(self):
        """ Return concerned hosts """
        return self._linked_hosts

    @property
    def hostgroups(self):
        """ Return concerned hosts groups """
        return self._linked_hostgroups

    @property
    def dependent_hosts(self):
        """ Return dependent hosts """
        return self._linked_dependent_hosts

    @property
    def dependent_hostgroups(self):
        """ Return concerned dependent hosts groups """
        return self._linked_dependent_hostgroups
