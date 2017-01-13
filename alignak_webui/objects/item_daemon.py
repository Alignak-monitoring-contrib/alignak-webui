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


class Daemon(BackendElement):
    """
    Object representing an Alignak daemon
    """
    _count = 0
    # Next value used for auto generated id
    _next_id = 1
    # _type stands for Backend Object Type
    _type = 'daemon'
    # _cache is a list of created objects
    _cache = {}

    def __init__(self, params=None, date_format='%a, %d %b %Y %H:%M:%S %Z', embedded=True):
        # Not that bad ... because __init__ is called from __new__
        # pylint: disable=attribute-defined-outside-init
        """
        Create a History (called only once when an object is newly created)
        """
        self._linked__realm = 'realm'

        super(Daemon, self).__init__(params, date_format, embedded)

        if not hasattr(self, 'address'):
            self.address = "unknown"

        if not hasattr(self, 'port'):
            self.port = 0

        if not hasattr(self, 'reachable'):
            self.reachable = False

        if not hasattr(self, 'spare'):
            self.spare = False

        if not hasattr(self, 'alive'):
            self.alive = False

    @property
    def _realm(self):
        """ Return concerned realm """
        return self._linked__realm

    @property
    def state(self):
        """
        Get daemon state
        """
        return self.status

    @property
    def status(self):
        """
        Get daemon status
        """
        if not self.reachable:
            return 'UNREACHABLE'
        if self.alive:
            return 'UP'
        else:
            return 'DOWN'

    @property
    def endpoint(self):
        """
        Overload default property. Returns None, there is no linkable page
        """
        return None
