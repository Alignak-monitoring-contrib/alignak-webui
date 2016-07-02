#!/usr/bin/python

# -*- coding: utf-8 -*-

# Copyright (C) 2009-2012:
#    Gabes Jean, naparuba@gmail.com
#    Gerhard Lausser, Gerhard.Lausser@consol.de
#    Gregory Starck, g.starck@gmail.com
#    Hartmut Goebel, h.goebel@goebel-consult.de
#    Frederic Mohier, frederic.mohier@gmail.com
#
# This file is part of Shinken.
#
# Shinken is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Shinken is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Shinken.  If not, see <http://www.gnu.org/licenses/>.

import os
import sys
import re

from alignak_webui.utils.perfdata import PerfDatas
from logging import getLogger

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
                'name': 'cpu|CPU|Linux procstat',
                'metrics': '^percent$|cpu_all_idle|cpu_all_iowait|cpu_all_usr|cpu_all_nice|cpu_idle|cpu_iowait|cpu_usr|cpu_nice|total 30s|total 1m|total 5m',
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
                'metrics': 'eth0_rx_by_sec|eth0_tx_by_sec|eth0_rxErrs_by_sec|eth0_txErrs_by_sec|eth0_in_Bps|eth0_out_Bps|BytesReceived|BytesSent|eth0_in_prct|eth0_out_prct',
                'uom': 'p/s|(.*)'
            }
        }

        self.host = host
        self.services = services

    def _findServiceByName(self, searched):
        for service in self.services:
            if re.search(searched['name'], service.name):
                return service

        return None

    def get_service_metric(self, service):
        all = {}
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

            try:
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
                            all[m.name] = m.value
            except Exception, exp:
                logger.warning("metrics get_service_metric, exception: %s", str(exp))

        logger.critical("metrics, get_service_metric %s", all)
        return state, name, all

    def get_services(self):
        # all = []
        all = {}
        state = 0

        # Get host's services list
        for s in self.services:
            s_state = s.state_id
            if s.acknowledged:
                s_state = 4
            if s.downtime:
                s_state = 5

            all[s.name] = s_state
            state = max(state, s_state)

        logger.critical("metrics, get_services %d, %s", state, all)
        return state, all

    def compute_worst_state(self, all_states):
        _ref = {'OK':0, 'UP':0, 'DOWN':3, 'UNREACHABLE':1, 'UNKNOWN':1, 'CRITICAL':3, 'WARNING':2, 'PENDING' :1, 'ACK' :1, 'DOWNTIME' :1}
        cur_level = 0
        for (k,v) in all_states.iteritems():
            logger.critical("metrics, self.compute_worst_state: %s/%s", k, v)
            # level = _ref[v]
            cur_level = max(cur_level, v)
        return cur_level
