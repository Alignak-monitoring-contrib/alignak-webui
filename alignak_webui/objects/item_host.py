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


class Host(BackendElement):
    """
    Object representing an host
    """
    _count = 0
    # Next value used for auto generated id
    _next_id = 1
    # _type stands for Backend Object Type
    _type = 'host'
    # _cache is a list of created objects
    _cache = {}

    # Dates fields: list of the attributes to be considered as dates
    _dates = BackendElement._dates + ['last_state_change', 'last_check', 'next_check']

    def _create(self, params, date_format):
        # Not that bad ... because _create is called from __new__
        # pylint: disable=attribute-defined-outside-init
        """
        Create a host (called only once when an object is newly created)
        """
        self._linked_check_command = 'command'
        self._linked_event_handler = 'command'
        self._linked_check_period = 'timeperiod'
        self._linked_notification_period = 'timeperiod'
        self._linked_snapshot_period = 'timeperiod'
        self._linked_maintenance_period = 'timeperiod'
        self._linked_hostgroups = 'hostgroup'
        self._linked_users = 'user'
        self._linked_usergroups = 'usergroup'

        super(Host, self)._create(params, date_format)

        # Missing in the backend ...
        if not hasattr(self, 'customs'):
            self.customs = []

        # From the livestate
        if not hasattr(self, 'is_impact'):
            self.impact = False
        if not hasattr(self, 'is_problem'):
            self.is_problem = False
        if not hasattr(self, 'problem_has_been_acknowledged'):
            self.problem_has_been_acknowledged = False
        if not hasattr(self, 'last_state_change'):
            self.last_state_change = self._default_date
        if not hasattr(self, 'last_check'):
            self.last_check = self._default_date
        if not hasattr(self, 'output'):
            self.output = self._default_date
        if not hasattr(self, 'long_output'):
            self.long_output = self._default_date
        if not hasattr(self, 'perf_data'):
            self.perf_data = self._default_date
        if not hasattr(self, 'latency'):
            self.latency = self._default_date
        if not hasattr(self, 'execution_time'):
            self.execution_time = self._default_date
        if not hasattr(self, 'attempt'):
            self.attempt = self._default_date
        if not hasattr(self, 'max_check_attempts'):
            self.max_check_attempts = self._default_date
        if not hasattr(self, 'state_type'):
            self.state_type = self._default_date
        if not hasattr(self, 'next_check'):
            self.next_check = self._default_date

        if not hasattr(self, 'comments'):
            self.comments = []

        if not hasattr(self, 'services'):
            self.services = []
        if not hasattr(self, 'downtimes'):
            self.downtimes = []
        if not hasattr(self, 'perfdatas'):
            self.perfdatas = []

    @property
    def check_command(self):
        """ Return linked object """
        return self._linked_check_command

    @property
    def event_handler(self):
        """ Return linked object """
        return self._linked_event_handler

    @property
    def check_period(self):
        """ Return linked object """
        return self._linked_check_period

    @property
    def notification_period(self):
        """ Return linked object """
        return self._linked_notification_period

    @property
    def snapshot_period(self):
        """ Return linked object """
        return self._linked_snapshot_period

    @property
    def maintenance_period(self):
        """ Return linked object """
        return self._linked_maintenance_period

    @property
    def usergroups(self):
        """ Return linked object """
        return self._linked_usergroups

    @property
    def users(self):
        """ Return linked object """
        return self._linked_users

    @property
    def position(self):
        """ Compute and return host GPS location """
        _lat = float(self.customs.get('_LOC_LAT', 999))
        _lng = float(self.customs.get('_LOC_LNG', 999))
        # latitude must be between -90/90 and longitude between -180/180
        if not -90 <= _lat <= 90 or not -180 <= _lng <= 180:
            _lat = float(self.location['coordinates'][0])
            _lng = float(self.location['coordinates'][1])
            # latitude must be between -90/90 and longitude between -180/180
            if not -90 <= _lat <= 90 or not -180 <= _lng <= 180:
                return None

        return {u'type': u'Point', u'coordinates': [_lat, _lng]}

    def get_last_check(self, timestamp=False, fmt=None):
        """
        Get last check date
        """
        if self.last_check == self.__class__._default_date and not timestamp:
            return _('Never checked!')

        if timestamp:
            return self.last_check

        return super(Host, self).get_date(self.last_check, fmt)
