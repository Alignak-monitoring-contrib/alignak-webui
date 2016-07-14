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
    This module contains the classes used to manage the user preferences in the backend
"""

from logging import getLogger, INFO

from alignak_webui.objects.element import BackendElement

# Set logger level to INFO, this to allow global application DEBUG logs without being spammed... ;)
logger = getLogger(__name__)
logger.setLevel(INFO)


class UIPref(BackendElement):
    """
    Object representing a UIPref
    """
    _count = 0
    # Next value used for auto generated id
    _next_id = 1
    # _type stands for Backend Object Type
    _type = 'uipref'
    # _cache is a list of created objects
    _cache = {}

    def __new__(cls, params=None, date_format='%a, %d %b %Y %H:%M:%S %Z'):
        """
        Create a new UIPref
        """
        return super(UIPref, cls).__new__(cls, params, date_format)

    def _create(self, params, date_format):
        # Not that bad ... because _create is called from __new__
        # pylint: disable=attribute-defined-outside-init
        """
        Create a UIPref (called only once when an object is newly created)
        """
        super(UIPref, self)._create(params, date_format)

    def _update(self, params=None, date_format='%a, %d %b %Y %H:%M:%S %Z'):
        """
        Update a UIPref (called every time an object is updated)
        """
        super(UIPref, self)._update(params, date_format)

    def __init__(self, params=None):
        """
        Initialize a UIPref (called every time an object is invoked)
        """
        super(UIPref, self).__init__(params)
