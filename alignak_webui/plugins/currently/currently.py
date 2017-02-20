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
    Plugin Currently
"""

from logging import getLogger

from bottle import request

from alignak_webui.utils.plugin import Plugin
from alignak_webui.utils.helper import Helper

# pylint: disable=invalid-name
logger = getLogger(__name__)


class PluginCurrently(Plugin):
    """ Currently plugin """

    def __init__(self, app, webui, cfg_filenames=None):
        """
        Currently plugin
        """
        self.name = 'Currently'
        self.backend_endpoint = None

        self.pages = {
            'get_currently': {
                'name': 'Currently',
                'route': '/currently',
                'view': 'currently'
            },
            'get_currently_old': {
                'name': 'Currently old',
                'route': '/currently_old',
                'view': 'currently_old'
            }
        }

        super(PluginCurrently, self).__init__(app, webui, cfg_filenames)

    def get_currently_old(self):  # pylint:disable=no-self-use
        """
        Display currently page
        """
        user = request.environ['beaker.session']['current_user']
        datamgr = request.app.datamgr

        # Get the stored panels
        panels = datamgr.get_user_preferences(user, 'panels', None)

        # Get the stored graphs
        currently_graphs = datamgr.get_user_preferences(user, 'currently_graphs', None)

        # Live state global and history
        (livesynthesis, ls_history) = datamgr.get_livesynthesis_history()
        ls_history = sorted(ls_history, key=lambda x: x['_timestamp'], reverse=False)

        return {
            'panels': panels,
            'currently_graphs': currently_graphs,
            'history': ls_history,
            'hs': livesynthesis['hosts_synthesis'],
            'ss': livesynthesis['services_synthesis'],
            'title': request.query.get('title', _('Keep an eye'))
        }

    def get_currently(self):  # pylint:disable=no-self-use, too-many-locals
        """
        Display currently page
        """
        user = request.environ['beaker.session']['current_user']
        webui = request.app.config['webui']
        datamgr = webui.datamgr

        # Default states
        hosts_states = ['up', 'down', 'unreachable']
        services_states = ['ok', 'warning', 'critical', 'unreachable', 'unknown']

        # Get the stored panels in user's preferences
        panels = datamgr.get_user_preferences(user, 'panels', None)
        if not panels:
            panels = {
                'panel_counters_hosts': {'collapsed': False},
                'panel_counters_services': {'collapsed': False},
                'panel_percentage_hosts': {'collapsed': False},
                'panel_percentage_services': {'collapsed': False},
                'panel_pie_graph_hosts': {'collapsed': False},
                'panel_pie_graph_services': {'collapsed': False},
                'panel_line_graph_hosts': {'collapsed': False},
                'panel_line_graph_services': {'collapsed': False}
            }

        # Get the stored graphs
        currently_graphs = datamgr.get_user_preferences(user, 'currently_graphs', None)
        if not currently_graphs:
            currently_graphs = {
                'pie_graph_hosts': {'legend': True, 'title': True, 'states': hosts_states},
                'pie_graph_services': {'legend': True, 'title': True, 'states': services_states},
                'line_graph_hosts': {'legend': True, 'title': True, 'states': hosts_states},
                'line_graph_services': {'legend': True, 'title': True, 'states': services_states}
            }

        # Live state global and history
        (livesynthesis, ls_history) = datamgr.get_livesynthesis_history()
        hs = livesynthesis['hosts_synthesis']
        ss = livesynthesis['services_synthesis']
        ls_history = sorted(ls_history, key=lambda x: x['_timestamp'], reverse=False)

        collapsed = False
        if 'panel_counters_hosts' in panels:
            collapsed = panels['panel_counters_hosts']['collapsed']
        pc_h = Helper.get_html_hosts_count_panel(hs, self.webui.get_url('Hosts table'),
                                                 collapsed=collapsed, percentage=False)

        collapsed = False
        if 'panel_percentage_hosts' in panels:
            collapsed = panels['panel_percentage_hosts']['collapsed']
        pp_h = Helper.get_html_hosts_count_panel(hs, self.webui.get_url('Hosts table'),
                                                 collapsed=collapsed, percentage=True)

        collapsed = False
        if 'panel_counters_services' in panels:
            collapsed = panels['panel_counters_services']['collapsed']
        pc_s = Helper.get_html_services_count_panel(ss, self.webui.get_url('Services table'),
                                                    collapsed=collapsed, percentage=False)

        collapsed = False
        if 'panel_percentage_services' in panels:
            collapsed = panels['panel_percentage_services']['collapsed']
        pp_s = Helper.get_html_services_count_panel(ss, self.webui.get_url('Services table'),
                                                    collapsed=collapsed, percentage=True)

        collapsed = False
        if 'panel_ls_history_hosts' in panels:
            collapsed = panels['panel_ls_history_hosts']['collapsed']
        lsh = Helper.get_html_hosts_ls_history(hs, ls_history, collapsed=collapsed)

        collapsed = False
        if 'panel_ls_history_services' in panels:
            collapsed = panels['panel_ls_history_services']['collapsed']
        ssh = Helper.get_html_services_ls_history(ss, ls_history, collapsed=collapsed)

        return {
            'panels': panels,
            'panel_counters_hosts': pc_h,
            'panel_percentage_hosts': pp_h,
            'panel_ls_history_hosts': lsh,
            'panel_counters_services': pc_s,
            'panel_percentage_services': pp_s,
            'panel_ls_history_services': ssh,
            'title': request.query.get('title', _('Keep an eye'))
        }
