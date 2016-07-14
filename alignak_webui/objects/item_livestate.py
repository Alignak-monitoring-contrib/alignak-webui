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
from alignak_webui.objects.element import Element

logger = getLogger(__name__)
logger.setLevel(INFO)


class LiveSynthesis(Element):
    """
    Object representing the live synthesis of the system
    """
    _count = 0
    # Next value used for auto generated id
    _next_id = 1
    # _type stands for Backend Object Type
    _type = 'livesynthesis'
    # _cache is a list of created objects
    _cache = {}

    # Status property
    status_property = 'state'

    def __new__(cls, params=None, date_format='%a, %d %b %Y %H:%M:%S %Z'):
        """
        Create a new livesynthesis
        """
        return super(LiveSynthesis, cls).__new__(cls, params, date_format)

    def _create(self, params, date_format):
        """
        Create a livesynthesis (called only once when an object is newly created)
        """
        super(LiveSynthesis, self)._create(params, date_format)

    def _update(self, params=None, date_format='%a, %d %b %Y %H:%M:%S %Z'):
        """
        Update a livesynthesis (called every time an object is updated)
        """
        super(LiveSynthesis, self)._update(params, date_format)

    def __init__(self, params=None):
        """
        Initialize a livesynthesis (called every time an object is invoked)
        """
        super(LiveSynthesis, self).__init__(params)


class LiveState(Element):
    """
    Object representing a livestate item (host or service)
    """
    _count = 0
    # Next value used for auto generated id
    _next_id = 1
    # _type stands for Backend Object Type
    _type = 'livestate'
    # _cache is a list of created objects
    _cache = {}

    # Status property
    status_property = 'state'

    def __new__(cls, params=None, date_format='%a, %d %b %Y %H:%M:%S %Z'):
        """
        Create a new livestate
        """
        return super(LiveState, cls).__new__(cls, params, date_format)

    def _create(self, params, date_format):
        # Not that bad ... because _create is called from __new__
        # pylint: disable=attribute-defined-outside-init
        """
        Create a livestate (called only once when an object is newly created)
        """
        self._linked_host = 'host'
        self._linked_service = 'service'

        super(LiveState, self)._create(params, date_format)

    def _update(self, params=None, date_format='%a, %d %b %Y %H:%M:%S %Z'):
        """
        Update a livestate (called every time an object is updated)
        """
        super(LiveState, self)._update(params, date_format)

    def __init__(self, params=None):
        """
        Initialize a livestate (called every time an object is invoked)
        """
        super(LiveState, self).__init__(params)

    @property
    def host(self):
        """ Return linked object """
        return self._linked_host

    @property
    def service(self):
        """ Return linked object """
        return self._linked_service

    @property
    def is_problem(self):
        """
        An element is_problem if not ok / unknwown and hard state type
        """
        if self.state_id in [1, 2] and self.state_type == "HARD":
            return True
        return False

    @property
    def status(self):
        """
        Get livestate status
        """
        if self.is_problem and self.acknowledged:
            return 'acknowledged'
        if self.is_problem and self.downtime:
            return 'in_downtime'
        return super(LiveState, self).status

    @Element.status.setter
    def status(self, status):
        # pylint: disable=function-redefined
        """
        Must redefine status setter here ! Else some errors occur when setting LiveState status
        :rtype: object
        """
        Element.status.fset(self, status)


