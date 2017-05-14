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
from alignak_webui.objects.item_timeperiod import TimePeriod
from alignak_webui.objects.item_command import Command


class Host(BackendElement):
    # Because there are many methods needed :)
    # pylint: disable=too-many-public-methods
    """Object representing an host"""
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

    # Converting short state character to text status (used for initial_state and freshness_state)
    short_state_to_status = {
        'o': 'Up',
        'd': 'Down',
        'u': 'Unreachable',
        'x': 'Unreachable',
        'r': 'Recovery',
        'f': 'Flapping',
        's': 'Downtime',
    }

    def __init__(self, params=None, date_format='%a, %d %b %Y %H:%M:%S %Z', embedded=True):
        # Not that bad ... because __init__ is called from __new__
        # pylint: disable=attribute-defined-outside-init
        """Create a host (called only once when an object is newly created)"""

        # Converting real state identifier to text status
        self.overall_state_to_status = [
            'ok', 'acknowledged', 'in_downtime', 'warning', 'critical', 'nope'
        ]

        self.overall_state_to_title = [
            _('Host is up and all its services are ok or acknowledged'),
            _('Host or some of its services are problems but acknowledged'),
            _('Host or some of its services are in a downtime period'),
            _('Host or some of its services are warning or state are unknown'),
            _('Host or some of its services are critical'),
            _('Host is not monitored')
        ]

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

        super(Host, self).__init__(params, date_format, embedded)

        if not hasattr(self, '_overall_state'):
            setattr(self, '_overall_state', 0)

    @property
    def members(self):
        """Return list of services"""
        return self.services

    @property
    def _realm(self):
        """Return concerned realm"""
        return self._linked__realm

    @property
    def _templates(self):
        """Return linked objects"""
        return self._linked__templates

    @property
    def _parent(self):
        """Try to find a parent

        If the host is a template and it has some templates, the first template is its parent
        """
        return self._linked__parent

    @property
    def check_command(self):
        """Return linked object"""
        if not isinstance(self._linked_check_command, BackendElement):
            return Command()
        return self._linked_check_command

    @property
    def snapshot_command(self):
        """Return linked object"""
        if not isinstance(self._linked_snapshot_command, BackendElement):
            return Command()
        return self._linked_snapshot_command

    @property
    def event_handler(self):
        """Return linked object"""
        if not isinstance(self._linked_event_handler, BackendElement):
            return Command()
        return self._linked_event_handler

    @property
    def check_period(self):
        """Return linked object"""
        if not isinstance(self._linked_check_period, BackendElement):
            return TimePeriod()
        return self._linked_check_period

    @property
    def notification_period(self):
        """Return linked object"""
        if not isinstance(self._linked_notification_period, BackendElement):
            return TimePeriod()
        return self._linked_notification_period

    @property
    def snapshot_period(self):
        """Return linked object"""
        if not isinstance(self._linked_snapshot_period, BackendElement):
            return TimePeriod()
        return self._linked_snapshot_period

    @property
    def maintenance_period(self):
        """Return linked object"""
        if not isinstance(self._linked_maintenance_period, BackendElement):
            return TimePeriod()
        return self._linked_maintenance_period

    @property
    def usergroups(self):
        """Return linked object"""
        return self._linked_usergroups

    @property
    def users(self):
        """Return linked object"""
        return self._linked_users

    @property
    def position(self):
        """Compute and return host GPS location"""
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

    @property
    def status(self):
        """Return host live state status

        Consider if the host is indeed monitored or not
        """
        if self.monitored:
            return self.ls_state
        if not hasattr(self, self.status_property):
            return None
        return "NOPE"

    @property
    def state_id(self):
        """Return host live state identifier"""
        return self.ls_state_id

    @property
    def state(self):
        """Return host live state"""
        return self.ls_state

    @property
    def state_type(self):
        """Return host live state type"""
        return self.ls_state_type

    @property
    def last_check(self):
        """Return host live state last check"""
        return self.ls_last_check

    @property
    def execution_time(self):
        """Return host live state execution time"""
        return self.ls_execution_time

    @property
    def latency(self):
        """Return host live state latency"""
        return self.ls_latency

    @property
    def current_attempt(self):
        """Return host live state current attempt"""
        return self.ls_current_attempt

    @property
    def max_attempts(self):
        """Return host live state maximum attempts"""
        return self.ls_max_attempts

    @property
    def next_check(self):
        """Return host live state next check"""
        return self.ls_next_check

    @property
    def last_state_changed(self):
        """Return host live state last state changed"""
        return self.ls_last_state_changed

    @property
    def last_state(self):
        """Return host live last_state"""
        return self.ls_last_state

    @property
    def last_state_type(self):
        """Return host live last_state type"""
        return self.ls_last_state_type

    @property
    def output(self):
        """Return host live state output"""
        return self.ls_output

    @property
    def html_output(self):
        """Return HTML formatted host live state output"""
        return "<code>%s</code>" % self.output

    @property
    def long_output(self):
        """Return host live state long output"""
        return self.ls_long_output

    @property
    def html_long_output(self):
        """Return HTML formatted host live state long output"""
        return "<code>%s</code>" % self.long_output.replace('\n', '<br>')

    @property
    def perf_data(self):
        """Return host live state performance data"""
        return self.ls_perf_data

    @property
    def html_perf_data(self):
        """Return HTML formatted host live state performance data"""
        return "<code>%s</code>" % self.perf_data

    @property
    def monitored(self):
        """Return host monitored state

        An host is said as monitored if active checks and/or passive checks are enabled
        for this host. If an host is not monitored the Web UI will exclude the host
        from the views.

        """
        if hasattr(self, 'active_checks_enabled') and self.active_checks_enabled:
            return True
        if hasattr(self, 'passive_checks_enabled') and self.passive_checks_enabled:
            return True
        return False

    @property
    def acknowledged(self):
        """Return host live state acknowledged"""
        return self.ls_acknowledged

    @property
    def downtimed(self):
        """Return host live state downtime"""
        return self.ls_downtimed

    @property
    def is_problem(self):
        """An host is considered as a problem if it is DOWN or UNREACHABLE and in a hard state"""
        if self.status in ['DOWN', 'UNREACHABLE'] and self.state_type == "HARD":
            return True
        return False

    def get_initial_state(self):
        """Get the element initial state"""
        return self.short_state_to_status[self.initial_state]

    def get_freshness_state(self):
        """Get the element freshness state"""
        return self.short_state_to_status[self.freshness_state]

    @property
    def overall_state(self):
        """The host overall state is computed by the alignak backend, including:
        - the acknowledged state
        - the downtime state

        The worst state is (prioritized):
        - an host down (4)
        - an host unreachable (3)
        - an host downtimed (2)
        - an host acknowledged (1)
        - an host up (0)

        If the host overall state is <= 2, then the host overall state is the maximum value
        of the host overall state and all the host services overall states.

        The overall state of an host is:
        - 0 if the host is UP and all its services are OK
        - 1 if the host is DOWN or UNREACHABLE and acknowledged or
            at least one of its services is acknowledged and
            no other services are WARNING or CRITICAL
        - 2 if the host is DOWN or UNREACHABLE and in a scheduled downtime or
            at least one of its services is in a scheduled downtime and no
            other services are WARNING or CRITICAL
        - 3 if the host is UNREACHABLE or
            at least one of its services is WARNING
        - 4 if the host is DOWN or
            at least one of its services is CRITICAL

        """
        if self.monitored:
            return self._overall_state_id
        return 5

    @property
    def variables(self):
        """Get the host custom variables with a nice name formatting:
        - remove the leading and inside underscore
        - lower case the variable name

        Returns a list of dictionaries containing:
        - name: the original variable name
        - alias: the nice name
        - value: the variable value

        The list is ordered with the variables name
        """
        variables = []
        for var in self.customs:
            varname = var[1:]
            varname = varname.replace('_', ' ')
            varname = varname.capitalize()
            variables.append({'name': var, 'alias': varname, 'value': self.customs[var]})
        return sorted(variables, key=lambda k: k['name'])

    @property
    def overall_status(self):
        """Return real status string from the real state identifier"""
        return self.overall_state_to_status[self.overall_state]

    def get_last_check(self, timestamp=False, fmt=None):
        """Get last check date"""
        if self.last_check == self.__class__._default_date and not timestamp:
            return _('Never checked!')

        if timestamp:
            return self.last_check

        return super(Host, self).get_date(self.last_check, fmt)
