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
    Plugin Livestate
"""

from logging import getLogger

from bottle import request, redirect

from alignak_webui import _
from alignak_webui.utils.plugin import Plugin
from alignak_webui.plugins.common.common import get_widget

logger = getLogger(__name__)


class PluginLivestate(Plugin):
    """ Hosts plugin """

    def __init__(self, app, cfg_filenames=None):
        """
        Hosts plugin

        Overload the default get route to declare filters.
        """
        self.name = 'Livestate'
        self.backend_endpoint = 'livestate'

        self.pages = {
            'get_livestate_widget': {
                'name': 'Livestate widget',
                'route': '/livestate/widget',
                'method': 'POST',
                'view': 'livestate_widget',
                'widgets': [
                    {
                        'id': 'livestate_table',
                        'for': ['external', 'dashboard'],
                        'name': _('Livestate table'),
                        'template': 'livestate_table_widget',
                        'icon': 'table',
                        'description': _(
                            '<h4>Livestate table widget</h4>Displays a list of the live state of the'
                            'monitored system hosts and services.<br>'
                            'The number of hosts/services in this list can be defined in the widget '
                            'options. The list of hosts/services can be filtered thanks to regex on the '
                            'host/service name.'
                        ),
                        'picture': 'htdocs/img/livestate_table_widget.png',
                        'options': {
                            'search': {
                                'value': '',
                                'type': 'text',
                                'label': _('Filter (ex. status:up)')
                            },
                            'count': {
                                'value': -1,
                                'type': 'int',
                                'label': _('Number of elements')
                            },
                            'filter': {
                                'value': '',
                                'type': 'hst_srv',
                                'label': _('Host/service name search')
                            }
                        }
                    },
                    {
                        'id': 'livestate_hosts_chart',
                        'for': ['external', 'dashboard'],
                        'name': _('Livestate hosts chart'),
                        'template': 'livestate_hosts_chart_widget',
                        'icon': 'pie-chart',
                        'description': _(
                            '<h4>Hosts livestate chart widget</h4>Displays a pie chart with the monitored'
                            'system hosts states.'
                        ),
                        'picture': 'htdocs/img/livestate_hosts_chart_widget.png',
                        'options': {}
                    },
                    {
                        'id': 'livestate_services_chart',
                        'for': ['external', 'dashboard'],
                        'name': _('Livestate services chart'),
                        'template': 'livestate_services_chart_widget',
                        'icon': 'pie-chart',
                        'description': _(
                            '<h4>Services livestate chart widget</h4>Displays a pie chart with the '
                            'monitored system services states.'
                        ),
                        'picture': 'htdocs/img/livestate_services_chart_widget.png',
                        'options': {}
                    },
                    {
                        'id': 'livestate_hosts_history_chart',
                        'for': ['external', 'dashboard'],
                        'name': _('Livestate hosts history chart'),
                        'template': 'livestate_hosts_history_chart_widget',
                        'icon': 'pie-chart',
                        'description': _(
                            '<h4>Hosts livestate history chart widget</h4>Displays a line chart with '
                            'the monitored system hosts states on a recent period of time.'
                        ),
                        'picture': 'htdocs/img/livestate_hosts_history_chart_widget.png',
                        'options': {}
                    },
                    {
                        'id': 'livestate_services_history_chart',
                        'for': ['external', 'dashboard'],
                        'name': _('Livestate services history chart'),
                        'template': 'livestate_services_history_chart_widget',
                        'icon': 'pie-chart',
                        'description': _(
                            '<h4>Services livestate history chart widget</h4>Displays a line chart with '
                            'the monitored system sevices states on a recent period of time.'
                        ),
                        'picture': 'htdocs/img/livestate_services_history_chart_widget.png',
                        'options': {}
                    },
                    {
                        'id': 'livestate_hosts_counters',
                        'for': ['external', 'dashboard'],
                        'name': _('Livestate hosts counters'),
                        'template': 'livestate_hosts_counters_widget',
                        'icon': 'plus-square',
                        'description': _(
                            '<h4>Hosts livestate counters widget</h4>Displays counters about the '
                            'monitored system hosts states.'
                        ),
                        'picture': 'htdocs/img/livestate_hosts_counters_widget.png',
                        'options': {}
                    },
                    {
                        'id': 'livestate_services_counters',
                        'for': ['external', 'dashboard'],
                        'name': _('Livestate services counters'),
                        'template': 'livestate_services_counters_widget',
                        'icon': 'plus-square',
                        'description': _(
                            '<h4>Services livestate counters widget</h4>Displays counters about the '
                            'monitored system services states.'
                        ),
                        'picture': 'htdocs/img/livestate_services_counters_widget.png',
                        'options': {}
                    },
                    {
                        'id': 'livestate_hosts_sla',
                        'for': ['external', 'dashboard'],
                        'name': _('Livestate hosts SLA'),
                        'template': 'livestate_hosts_sla_widget',
                        'icon': 'life-saver',
                        'description': _(
                            '<h4>Hosts livestate SLA widget</h4>Displays counters and SLA level about the '
                            'monitored system hosts states.'
                        ),
                        'picture': 'htdocs/img/livestate_hosts_sla_widget.png',
                        'options': {}
                    },
                    {
                        'id': 'livestate_services_sla',
                        'for': ['external', 'dashboard'],
                        'name': _('Livestate services SLA'),
                        'template': 'livestate_services_sla_widget',
                        'icon': 'life-saver',
                        'description': _(
                            '<h4>Hosts livestate SLA widget</h4>Displays counters and SLA level about the '
                            'monitored system services states.'
                        ),
                        'picture': 'htdocs/img/livestate_services_sla_widget.png',
                        'options': {}
                    },
                ]
            }
        }

        super(PluginLivestate, self).__init__(app, cfg_filenames)

    def get_one(self, element_id):
        """
        Display the element linked to a livestate item
        """
        datamgr = request.environ['beaker.session']['datamanager']

        livestate = datamgr.get_livestates({'where': {'_id': element_id}})
        if not livestate:
            return self.webui.response_invalid_parameters(_('Livestate element does not exist'))

        livestate = livestate[0]
        if livestate.type == 'host':
            redirect('/host/' + livestate.host.id)
        else:
            redirect('/host/' + livestate.host.id + '#services')


    def get_livestate_widget(self, embedded=False, identifier=None, credentials=None):
        """
        Get the livestate as a widget
        - widget_id: widget identifier

        - start and count for pagination
        - search for specific elements search

        """
        datamgr = request.environ['beaker.session']['datamanager']
        return get_widget(datamgr.get_livestate, 'livestate', embedded, identifier, credentials)
