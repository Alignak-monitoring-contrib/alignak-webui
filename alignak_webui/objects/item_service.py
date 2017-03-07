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


class Service(BackendElement):
    # Because there are many methods needed :)
    # pylint: disable=too-many-public-methods

    """Object representing a service"""

    _count = 0
    # Next value used for auto generated id
    _next_id = 1
    # _type stands for Backend Object Type
    _type = 'service'
    # _cache is a list of created objects
    _cache = {}

    # Status property
    status_property = 'ls_state'

    # Converting short state character to text status (used for initial_state and freshness_state)
    short_state_to_status = {
        'o': 'Ok',
        'w': 'Warning',
        'c': 'Critical',
        'u': 'Unknown',
        'x': 'Unreachable',
        'r': 'Recovery',
        'f': 'Flapping',
        's': 'Downtime'
    }

    def __init__(self, params=None, date_format='%a, %d %b %Y %H:%M:%S %Z', embedded=True):
        """Create a service (called only once when an object is newly created)"""

        # Converting real state identifier to text status
        self.overall_state_to_status = [
            'ok', 'acknowledged', 'in_downtime', 'warning', 'critical'  # 'unknown', 'unreachable'
        ]
        self.overall_state_to_title = [
            _('Service is ok'),
            _('Service has a problem but is acknowledged'),
            _('Service is in a downtime period'),
            _('Service is warning or state is unknown'),
            _('Service is critical or unreachable')
        ]

        # self._linked__realm = 'realm'
        self._linked__templates = 'service'
        self._linked_host = 'host'
        self._linked_check_command = 'command'
        self._linked_snapshot_command = 'command'
        self._linked_event_handler = 'command'
        self._linked_check_period = 'timeperiod'
        self._linked_notification_period = 'timeperiod'
        self._linked_snapshot_period = 'timeperiod'
        self._linked_maintenance_period = 'timeperiod'
        self._linked_users = 'user'
        self._linked_usergroups = 'usergroup'

        super(Service, self).__init__(params, date_format, embedded)

        if not hasattr(self, 'aggregation'):
            setattr(self, 'aggregation', 'Global')

        if not hasattr(self, '_overall_state'):
            setattr(self, '_overall_state', 0)

    @property
    def endpoint(self):
        """
        Get Item endpoint (page url)
        """
        return '/service/%s' % (self.id)

    # @property
    # def _realm(self):
    #     """ Return concerned realm """
    #     return self._linked__realm

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
    def status(self):
        """
        Return service live state status
        """
        return self.ls_state

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
    def downtimed(self):
        """
        Return host live state downtime
        """
        return self.ls_downtimed

    @property
    def is_problem(self):
        """
        An element is_problem if not ok / unknwown and hard state type
        """
        if self.state_id in [1, 2, 3] and self.state_type == "HARD":
            return True
        return False

    @property
    def level(self):
        """ Return service level (in services aggregation) """
        return self._level

    @property
    def parent(self):
        """ Return service parent (in services aggregation) """
        return self._parent

    def get_initial_state(self):
        """
        Get the element initial state
        """
        return self.short_state_to_status[self.initial_state]

    def get_freshness_state(self):
        """
        Get the element freshness state
        """
        return self.short_state_to_status[self.freshness_state]

    @property
    def overall_state(self):

        """The service overall state is computed by the alignak backend, including:
        - the acknowledged state
        - the downtime state

        The worst state is (prioritized):
        - a service critical or unreachable (4)
        - a service warning or unknown (3)
        - a service downtimed (2)
        - a service acknowledged (1)
        - a service ok (0)

        *Note* that services in unknown state are considered as warning, and unreachable ones
        are considered as critical!
        """
        return self._overall_state_id

    @property
    def overall_status(self):
        """Return real status string from the real state identifier"""
        return self.overall_state_to_status[self.overall_state]

    def get_last_check(self, timestamp=False, fmt=None):
        """
        Get last check date
        """
        if self.last_check == self.__class__._default_date and not timestamp:
            return _('Never checked!')

        if timestamp:
            return self.last_check

        return super(Service, self).get_date(self.last_check, fmt)
