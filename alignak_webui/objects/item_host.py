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
    # Because there are many methods needed :)
    # pylint: disable=too-many-public-methods
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

    # Status property
    status_property = 'ls_state'

    # Dates fields: list of the attributes to be considered as dates
    _dates = BackendElement._dates + ['ls_last_state_change', 'ls_last_check', 'ls_next_check']

    def _create(self, params, date_format):
        # Not that bad ... because _create is called from __new__
        # pylint: disable=attribute-defined-outside-init
        """
        Create a host (called only once when an object is newly created)
        """
        self._linked__realm = 'realm'
        self._linked__templates = 'host'
        self._linked_check_command = 'command'
        self._linked_snapshot_command = 'command'
        self._linked_event_handler = 'command'
        self._linked_check_period = 'timeperiod'
        self._linked_notification_period = 'timeperiod'
        self._linked_snapshot_period = 'timeperiod'
        self._linked_maintenance_period = 'timeperiod'
        self._linked_users = 'user'
        self._linked_usergroups = 'usergroup'

        super(Host, self)._create(params, date_format)

    @property
    def _realm(self):
        """ Return concerned realm """
        return self._linked__realm

    @property
    def _templates(self):
        """ Return linked object """
        return self._linked__templates

    @property
    def check_command(self):
        """ Return linked object """
        return self._linked_check_command

    @property
    def snapshot_command(self):
        """ Return linked object """
        return self._linked_snapshot_command

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

    # @property
    # def status(self):
        # """
        # Return host live state status
        # """
        # return self.ls_state

    @property
    def state_id(self):
        """
        Return host live state identifier
        """
        return self.ls_state_id

    @property
    def state(self):
        """
        Return host live state
        """
        return self.ls_state

    @property
    def state_type(self):
        """
        Return host live state type
        """
        return self.ls_state_type

    @property
    def last_check(self):
        """
        Return host live state last check
        """
        return self.ls_last_check

    @property
    def execution_time(self):
        """
        Return host live state execution time
        """
        return self.ls_execution_time

    @property
    def latency(self):
        """
        Return host live state latency
        """
        return self.ls_latency

    @property
    def current_attempt(self):
        """
        Return host live state current attempt
        """
        return self.ls_current_attempt

    @property
    def max_attempts(self):
        """
        Return host live state maximum attempts
        """
        return self.ls_max_attempts

    @property
    def next_check(self):
        """
        Return host live state next check
        """
        return self.ls_next_check

    @property
    def last_state_changed(self):
        """
        Return host live state last state changed
        """
        return self.ls_last_state_changed

    @property
    def last_state(self):
        """
        Return host live last_state
        """
        return self.ls_last_state

    @property
    def last_state_type(self):
        """
        Return host live last_state type
        """
        return self.ls_last_state_type

    @property
    def output(self):
        """
        Return host live state output
        """
        return self.ls_output

    @property
    def long_output(self):
        """
        Return host live state long output
        """
        return self.ls_long_output

    @property
    def perf_data(self):
        """
        Return host live state performance data
        """
        return self.ls_perf_data

    @property
    def acknowledged(self):
        """
        Return host live state acknowledged
        """
        return self.ls_acknowledged

    @property
    def downtime(self):
        """
        Return host live state downtime
        """
        return self.ls_downtimed

    @property
    def is_problem(self):
        """
        An element is_problem if not ok / unknwown and hard state type
        """
        if self.state_id in [1, 2] and self.state_type == "HARD":
            return True
        return False

    def get_real_state(self, children):
        """
        Get the host real state, including the services state
        """
        hs = 0

        if self.state == 'DOWN':
            if self.acknowledged:
                hs = 3
            else:
                hs = 2
        elif self.state != 'UP':
            if self.acknowledged:
                hs = 3
            else:
                hs = 1

        for child in children:
            if child.state == 'CRITICAL':
                if hs in ['OK', 'WARNING', 'ACK']:
                    if child.acknowledged:
                        hs = 3
                    else:
                        hs = 2
            elif child.state != 'OK':
                if hs in ['OK', 'ACK']:
                    if child.acknowledged:
                        hs = 3
                    else:
                        hs = 1

        return hs

    def get_last_check(self, timestamp=False, fmt=None):
        """
        Get last check date
        """
        if self.last_check == self.__class__._default_date and not timestamp:
            return _('Never checked!')

        if timestamp:
            return self.last_check

        return super(Host, self).get_date(self.last_check, fmt)
