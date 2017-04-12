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


class ServiceEscalation(BackendElement):
    """Object representing a serviceescalation"""
    _count = 0
    # Next value used for auto generated id
    _next_id = 1
    # _type stands for Backend Object Type
    _type = 'serviceescalation'
    # _cache is a list of created objects
    _cache = {}

    def __init__(self, params=None, date_format='%a, %d %b %Y %H:%M:%S %Z', embedded=True):
        """Create a serviceescalation (called only once when an object is newly created)"""
        self._linked__realm = 'realm'
        self._linked_services = 'service'
        self._linked_hosts = 'host'
        self._linked_hostgroups = 'hostgroup'
        self._linked_escalation_period = 'timeperiod'
        self._linked_users = 'user'
        self._linked_usergroups = 'usergroup'

        super(ServiceEscalation, self).__init__(params, date_format, embedded)

    @property
    def _realm(self):
        """Return concerned realm"""
        return self._linked__realm

    @property
    def services(self):
        """Return concerned services"""
        return self._linked_services

    @property
    def hosts(self):
        """Return concerned hosts"""
        return self._linked_hosts

    @property
    def hostgroups(self):
        """Return concerned hosts groups"""
        return self._linked_hostgroups

    @property
    def escalation_period(self):
        """Return concerned dependency timeperiod"""
        return self._linked_escalation_period

    @property
    def users(self):
        """Return linked users"""
        return self._linked_users

    @property
    def usergroups(self):
        """Return linked users groups"""
        return self._linked_usergroups
