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

# Import the backend interface class

# Set logger level to INFO, this to allow global application DEBUG logs without being spammed... ;)
from alignak_webui.objects.element import BackendElement

logger = getLogger(__name__)
logger.setLevel(INFO)


class Service(BackendElement):
    """
    Object representing a service
    """
    _count = 0
    # Next value used for auto generated id
    _next_id = 1
    # _type stands for Backend Object Type
    _type = 'service'
    # _cache is a list of created objects
    _cache = {}

    def _create(self, params, date_format):
        """
        Create a service (called only once when an object is newly created)
        """
        self._linked_host = 'host'
        self._linked_check_command = 'command'
        self._linked_event_handler = 'command'
        self._linked_check_period = 'timeperiod'
        self._linked_notification_period = 'timeperiod'
        self._linked_servicegroups = 'servicegroup'
        self._linked_users = 'user'
        self._linked_usergroups = 'usergroup'

        super(Service, self)._create(params, date_format)

    @property
    def check_command(self):
        """ Return linked object """
        return self._linked_check_command

    @property
    def event_handler(self):
        """ Return linked object """
        return self._linked_event_handler

    @property
    def host(self):
        """ Return linked object """
        return self._linked_host

    @property
    def check_period(self):
        """ Return linked object """
        return self._linked_check_period

    @property
    def notification_period(self):
        """ Return linked object """
        return self._linked_notification_period


class ServiceGroup(BackendElement):
    """
    Object representing a servicegroup
    """
    _count = 0
    # Next value used for auto generated id
    _next_id = 1
    # _type stands for Backend Object Type
    _type = 'servicegroup'
    # _cache is a list of created objects
    _cache = {}

    def _create(self, params, date_format):
        """
        Create a servicegroup (called only once when an object is newly created)
        """
        self._linked_servicegroup_members = 'servicegroup'
        self._linked_members = 'service'

        super(ServiceGroup, self)._create(params, date_format)

    @property
    def members(self):
        """ Return linked object """
        return self._linked_members

    @property
    def servicegroup_members(self):
        """ Return linked object """
        return self._linked_servicegroup_members
