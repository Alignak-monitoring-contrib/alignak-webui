#!/usr/bin/python
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
    This module contains functions used to compute values from performance data metrics.

    Those functions are mainly used in the Host view panel.
"""
import re
from logging import getLogger

from alignak_webui.utils.perfdata import PerfDatas

# pylint: disable=invalid-name
logger = getLogger(__name__)


# Get plugin's parameters from configuration file
# Define service/perfdata name for each element in graph
class HostMetrics(object):  # pragma: no cover, not with unit tests ...
    """
    Host metrics functions
    """
    def __init__(self, host, services, params, tags=None):
        """Manage host known metrics

        If the plugin parameters contain some information about the host tags, build
        a list of those information to get used for displaying some information graphs.

        An host with the tags: important,linux-nrpe will be searched for plugin parameters
        related with important and linux-nrpe

        If parameters are defined as:

            [linux-nrpe.host_check]
            name=host_check
            type=bar
            metrics=^rta$
            uom=

            [linux-nrpe.load]
            name=Load
            type=horizontalBar
            metrics=^load_1_min|load_5_min|load_15_min$
            uom=

        they will match with the host services to display some graphs.

        """

        logger.debug("HostMetrics, host: %s, services: %s, params: %s, tags: %s",
                     host, services, params, tags)
        # Default values
        self.params = {}
        self.tags = []
        if tags:
            self.tags = tags

        self.services_names = [s.name for s in services]
        for param in params:
            logger.debug("HostMetrics, param: %s", param)
            p = param.split('.')
            if len(p) != 3:
                continue

            if p[0] not in self.tags:
                continue
            if p[1] not in self.services_names:
                continue
            if p[2] not in ['name', 'type', 'metrics', 'uom']:
                continue

            logger.info("metrics, service match: %s=%s", param, params[param])
            if p[1] not in self.params:
                self.params[p[1]] = {}
            self.params[p[1]][p[2]] = params[param]
        logger.debug("metrics, services match configuration: %s", self.params)

        self.host = host
        self.services = services

    def find_service_by_name(self, searched):
        """
        Find a service by its name with regex
        """
        for service in self.services:
            if re.search(searched['name'], service.name):
                return service

        return None

    def get_service_metric(self, service):
        # pylint: disable=too-many-nested-blocks
        """
        Get a specific service state and metrics

        Returns a tuple built with:
        - service state
        - service name
        - metrics common minimum value (all metrics share the same minimum)
        - metrics common maximum value (all metrics share the same maximum)
        - metrics common warning value (all metrics share the same warning)
        - metrics common critical value (all metrics share the same critical)
        - list of metrics dict, including name, value, min, max, warning, critical, and uom)
        """
        data = []
        state = -1
        name = 'Unknown'
        same_min = -1
        same_max = -1
        warning = -1
        critical = -1

        logger.debug("metrics, get_service_metric for %s (%s)", service, self.params[service])
        if self.params[service]['name'] == 'host_check':
            s = self.host
        else:
            s = self.find_service_by_name(self.params[service])

        if not s:
            logger.debug("metrics, get_service_metric, nothing found")
            return state, name, same_min, same_max, warning, critical, data

        logger.debug("metrics, matching service: %s", s.name)
        name = s.name
        state = s.state_id
        if s.acknowledged:
            state = 4
        if s.downtime:
            state = 5

        try:  # pragma: no cover - no existing data when testing :(
            p = PerfDatas(s.perf_data)
            logger.debug("metrics, service perfdata: %s", p.__dict__)
            for m in sorted(p):
                logger.debug("metrics, service perfdata metric: %s", m.__dict__)
                if m.name and m.value is not None:
                    if re.search(self.params[service]['metrics'], m.name) and \
                       re.match(self.params[service]['uom'], m.uom):
                        logger.debug(
                            "metrics, matching metric: '%s' = %s", m.name, m.value
                        )
                        data.append(m)
                        if m.min is not None:
                            if same_min == -1:
                                same_min = m.min
                            if same_min != -1 and same_min != m.min:
                                same_min = -2
                        if m.max is not None:
                            if same_max == -1:
                                same_max = m.max
                            if same_max != -1 and same_max != m.max:
                                same_max = -2
                        if m.warning is not None:
                            if warning == -1:
                                warning = m.warning
                            if warning != -1 and warning != m.warning:
                                warning = -2
                        if m.critical is not None:
                            if critical == -1:
                                critical = m.critical
                            if critical != -1 and critical != m.critical:
                                critical = -2
        except Exception as exp:
            logger.warning("metrics get_service_metric, exception: %s", str(exp))

        logger.debug("metrics, get_service_metric %s", data)
        return state, name, same_min, same_max, warning, critical, data
