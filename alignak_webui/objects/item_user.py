#!/usr/bin/env python
# -*- coding: utf-8 -*-
# For _linked_host... too long, I do not know?
# pylint:disable=invalid-name
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
    This module contains the classes used to manage the user in the backend.
"""
from alignak_webui.objects.element import BackendElement


class User(BackendElement):
    """
    Object representing a user
    """
    _count = 0
    # Next value used for auto generated id
    _next_id = 1
    # _type stands for Backend Object Type
    _type = 'user'
    # _cache is a list of created objects
    _cache = {}

    # Displayable strings for the user role
    roles = {
        # "user": _("User"),
        # "power": _("Power user"),
        # "administrator": _("Administrator")
    }

    def __init__(self, params=None, date_format='%a, %d %b %Y %H:%M:%S %Z', embedded=True):
        # Not that bad ... because __init__ is called from __new__
        # pylint: disable=attribute-defined-outside-init
        """
        Create a user (called only once when an object is newly created)
        """
        self._linked__realm = 'realm'
        self._linked__templates = 'user'
        self._linked_host_notification_period = 'timeperiod'
        self._linked_host_notification_commands = 'command'
        self._linked_service_notification_period = 'timeperiod'
        self._linked_service_notification_commands = 'command'

        super(User, self).__init__(params, date_format, embedded)

        self.authenticated = False

        # Is an administrator ?
        if not hasattr(self, 'is_admin'):
            self.is_admin = False

        # Can submit commands
        if not hasattr(self, 'can_submit_commands'):
            self.can_submit_commands = False
            if hasattr(self, 'read_only'):
                if isinstance(self.read_only, bool):
                    self.can_submit_commands = not self.read_only
                else:
                    self.can_submit_commands = getattr(self, 'read_only', '1') == '0'
        if self.is_admin:
            self.can_submit_commands = True

        # Can change dashboard
        if not hasattr(self, 'widgets_allowed'):
            self.widgets_allowed = False
        if self.is_admin:
            self.widgets_allowed = True

        # Has a role ?
        if not hasattr(self, 'role'):
            self.role = self.get_role()

        if not hasattr(self, 'picture'):
            self.picture = '/static/images/user_default.png'
            if self.name == 'anonymous':
                self.picture = '/static/images/user_guest.png'
            else:
                if self.is_admin:
                    self.picture = '/static/images/user_admin.png'

        # User preferences ?
        if not hasattr(self, 'ui_preferences'):
            self.ui_preferences = {}

    def __repr__(self):
        if hasattr(self, 'authenticated') and self.authenticated:
            return "<Authenticated %s, id: %s, name: %s, role: %s>" % (
                self.__class__._type, self.id, self.name, self.get_role()
            )
        return "<%s, id: %s, name: %s, role: %s>" % (
            self.__class__._type, self.id, self.name, self.get_role()
        )

    @property
    def _realm(self):
        """ Return concerned realm """
        return self._linked__realm

    @property
    def _templates(self):
        """ Return linked object """
        return self._linked__templates

    @property
    def host_notification_period(self):
        """ Return linked object """
        return self._linked_host_notification_period

    @property
    def host_notification_commands(self):
        """ Return linked object """
        return self._linked_host_notification_commands

    @property
    def service_notification_period(self):
        """ Return linked object """
        return self._linked_service_notification_period

    @property
    def service_notification_commands(self):
        """ Return linked object """
        return self._linked_service_notification_commands

    @property
    def business_impact(self):
        """ Return minimum business impact """
        return self.min_business_impact

    def get_username(self):
        """
        Get the user username (for login).
        Returns the 'username' field if it exists, else returns  the 'name' field,
        else returns  the 'name' field
        """
        return getattr(self, 'username', self.name)

    def get_role(self, display=False):
        """
        Get the user role.
        If user role is not defined, set the property according to the user attributes:
        - role='administrator' if the user is an administrator
        - role='power' if the user can submit commands
        - role='user' else

        If the display parameter is set, the function returns a displayable string else it
        returns the defined role property
        """
        if self.is_administrator():
            self.role = 'administrator'
        elif self.is_power():
            self.role = 'power'
        else:
            self.role = 'user'

        if display and self.role in self.__class__.roles:
            return self.__class__.roles[self.role]

        return self.role

    def is_anonymous(self):
        """
        An anonymous user is created when no 'name' attribute exists for the user ... 'anonymous'
        is the default value of the Item name property.
        """
        return self.name == 'anonymous'

    def is_super_administrator(self):
        """
        Is user a super administrator?
        """
        if getattr(self, 'back_role_super_admin', None):
            return self.back_role_super_admin

    def is_administrator(self):
        """
        Is user an administrator?
        """
        if self.is_super_administrator():
            return True

        if isinstance(self.is_admin, bool):
            return self.is_admin
        else:
            return getattr(self, 'is_admin', '1') == '1'

    def is_power(self):
        """
        Is allowed to use commands (power user)?
        """
        if self.is_administrator():
            return True

        if isinstance(self.can_submit_commands, bool):
            return self.can_submit_commands
        else:
            return getattr(self, 'can_submit_commands', '1') == '1'

    def can_change_dashboard(self):
        """
        Can the use change dashboard (edit widgets,...)?
        """
        if self.is_power():
            return True

        if isinstance(self.widgets_allowed, bool):
            return self.widgets_allowed
        else:
            return getattr(self, 'widgets_allowed', '1') == '1'

    def get_ui_preference(self, key=None):
        """
        Get a user UI preference
        """
        # Test for old user data model
        if not getattr(self, 'ui_preferences', None):
            return None

        if not key:
            return self.ui_preferences

        if key in self.ui_preferences:
            return self.ui_preferences[key]

        return None

    def set_ui_preference(self, key, value):
        """
        Set a user UI preference

        :param key: preference key
        :type key: string
        :param value: value to store
        :type value: dict
        :return: True / False
        :rtype: boolean
        """
        if not key:
            return None

        self.ui_preferences.update({key: value})
        return True

    def delete_ui_preference(self, key):
        """
        Delete a user UI preference

        :param key: preference key
        :type key: string
        :return: current value of the deleted key
        """
        if not key:
            return None

        return self.ui_preferences.pop(key, None)
