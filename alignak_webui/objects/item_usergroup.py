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
    This module contains the classes used to manage the users groups in the backend.
"""
from alignak_webui.objects.element import BackendElement


class UserGroup(BackendElement):
    """Object representing a users group"""
    _count = 0
    # Next value used for auto generated id
    _next_id = 1
    # _type stands for Backend Object Type
    _type = 'usergroup'
    # _cache is a list of created objects
    _cache = {}

    def __init__(self, params=None, date_format='%a, %d %b %Y %H:%M:%S %Z', embedded=True):
        """Create a usergroup (called only once when an object is newly created)"""
        self._linked_usergroups = 'usergroup'
        self._linked__parent = 'usergroup'
        self._linked_users = 'user'

        super(UserGroup, self).__init__(params, date_format, embedded)

    @property
    def members(self):
        """Return linked object"""
        return self._linked_users

    @property
    def users(self):
        """Return linked object"""
        return self._linked_users

    @property
    def usergroups(self):
        """Return linked object"""
        return self._linked_usergroups

    @property
    def _parent(self):
        """Return group parent"""
        return self._linked__parent

    @property
    def level(self):
        """Return group level"""
        if not hasattr(self, '_level'):
            return -1
        return self._level
