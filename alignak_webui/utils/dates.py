#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
    This module contains the base class used as time/date utilities
"""

import time

from calendar import timegm
from logging import getLogger, INFO

# Set logger level to INFO, this to allow global application DEBUG logs without being spammed... ;)
# pylint: disable=invalid-name
logger = getLogger(__name__)
logger.setLevel(INFO)


def get_ts_date(param_date, date_format):
    """
        Get date as a timestamp
    """
    if isinstance(param_date, (int, long, float)):
        # Date is received as a float or integer, store as a timestamp ...
        # ... and assume it is UTC
        # ----------------------------------------------------------------
        return param_date
    elif isinstance(param_date, basestring):
        try:
            # Date is supposed to be received as string formatted date
            timestamp = timegm(time.strptime(param_date, date_format))
            return timestamp
        except ValueError:
            logger.warning(
                " parameter: '%s' is not a valid string format: '%s'",
                param_date, date_format
            )
    else:
        try:
            # Date is supposed to be received as a struct time ...
            # ... and assume it is local time!
            # ----------------------------------------------------
            timestamp = timegm(param_date.timetuple())
            return timestamp
        except TypeError:  # pragma: no cover, simple protection
            logger.warning(
                " parameter: %s is not a valid time tuple", param_date
            )
    return None
