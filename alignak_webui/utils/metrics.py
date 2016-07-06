#!/usr/bin/python
# -*- coding: utf-8 -*-

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
    This module contains functions used to compute values from performance data metrics.

    Those functions are mainly used in the Host view panel.
"""
import os
import sys
import re

from logging import getLogger
from alignak_webui.utils.perfdata import PerfDatas

logger = getLogger(__name__)


# Get plugin's parameters from configuration file
# Define service/perfdata name for each element in graph
class HostMetrics(object):
    """
    Helper functions
    """
    def __init__(self, host, services):
        """ Empty ... """
        self.params = {
            'load': {
                'name': 'load|Load',
                'metrics': 'min(.*)|^load_1|^load_5|^load_15|^load1$|^load5$|^load15$',
                'uom': ''
            },
            'cpu': {
                'name': 'cpu|Cpu|CPU|Linux procstat',
                'metrics': '^percent$|cpu_all_idle|cpu_all_iowait|cpu_all_usr|cpu_all_nice|'
                           'cpu_prct_used|'
                           'cpu_idle|cpu_iowait|cpu_usr|cpu_nice|total 30s|total 1m|total 5m',
                'uom': '%'
            },
            'disk': {
                'name': '^disk|disks|Disks|Partitions$',
                'metrics': 'used_pct|^/(?!dev|sys|proc|run?)(.*)$',
                'uom': '^%|(.?)B$'
            },
            'mem': {
                'name': 'memory|Memory',
                'metrics': '^ram_free|ram_buffered|ram_cached|ram_total$',
                'uom': '^%|(.?)B|$'
            },
            'net': {
                'name': 'network|NET Stat|Network',
                'metrics': 'eth0_rx_by_sec|eth0_tx_by_sec|eth0_rxErrs_by_sec|eth0_txErrs_by_sec|'
                           'eth0_in_Bps|eth0_out_Bps|BytesReceived|BytesSent|eth0_in_prct|'
                           'eth0_out_prct',
                'uom': 'p/s|(.*)'
            }
        }

        self.host = host
        self.services = services

    def _findServiceByName(self, searched):
        """
        Find a service by its name with regex
        """
        for service in self.services:
            if re.search(searched['name'], service.name):
                return service

        return None

    def get_service_metric(self, service):
        """
        Get a specific service state and metrics
        """
        data = {}
        state = 3
        name = 'Unknown'

        logger.critical("metrics, get_service_metric for %s", service)
        s = self._findServiceByName(self.params[service])
        if s:
            logger.critical("metrics, found %s", s.name)
            name = s.name
            state = s.state_id
            if s.acknowledged:
                state = 4
            if s.downtime:
                state = 5

            try:  # pragma: no cover - no livestate data when testing :(
                p = PerfDatas(s.perf_data)
                for m in p:
                    if m.name and m.value is not None:
                        logger.critical(
                            "metrics, metric '%s' = %s, uom: %s", m.name, m.value, m.uom
                        )
                        if re.search(self.params[service]['metrics'], m.name) and \
                           re.match(self.params[service]['uom'], m.uom):
                            logger.critical(
                                "metrics, service: %s, got '%s' = %s", service, m.name, m.value
                            )
                            data[m.name] = m.value
            except Exception, exp:
                logger.warning("metrics get_service_metric, exception: %s", str(exp))

        logger.critical("metrics, get_service_metric %s", data)
        return state, name, data

    def get_services(self):
        """
        Get the host services global state
        """
        data = {}
        state = 0

        # Get host's services list
        for s in self.services:
            s_state = s.state_id
            if s.acknowledged:
                s_state = 4
            if s.downtime:
                s_state = 5

            data[s.name] = s_state
            state = max(state, s_state)

        logger.critical("metrics, get_services %d, %s", state, data)
        return state, data
