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


class LiveState(BackendElement):
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

    def __init__(self, params=None, date_format='%a, %d %b %Y %H:%M:%S %Z', embedded=True):
        # Not that bad ... because __init__ is called from __new__
        # pylint: disable=attribute-defined-outside-init
        """
        Create a livestate (called only once when an object is newly created)
        """
        self._linked_host = 'host'
        self._linked_service = 'service'

        super(LiveState, self).__init__(params, date_format, embedded)

    def __repr__(self):
        return "<Livestate %s, id: %s, name: %s, status: %s>" % (
            self.__class__.get_type(), self.id, self.name, self.status
        )

    @property
    def endpoint(self):
        """
        Get Item endpoint (page url)
        """
        return '/livestate/%s' % (self.id)

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

    @BackendElement.status.setter
    def status(self, status):
        # pylint: disable=function-redefined
        """
        Must redefine status setter here ! Else some errors occur when setting LiveState status
        :rtype: object
        """
        BackendElement.status.fset(self, status)

    def get_html_link(self, prefix=None, title=None):
        """
        Get html link with an optional prefix and an optional title
        """
        if not title and self.host != 'host' and self.service != 'service':
            title = "%s / %s" % (self.host.name, self.service.name)
        return super(LiveState, self).get_html_link(title=title)
