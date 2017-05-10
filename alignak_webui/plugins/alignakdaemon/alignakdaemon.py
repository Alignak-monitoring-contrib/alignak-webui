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
    Plugin Alignak daemon

    This plugin allows to display Alignak overall state information. It uses the Alignak
    Backend to get information about the Alignak running daemons.

    It can also use the Alignak Web services module to get information from the Alignak
    arbiter about all the running daemons.
"""

from logging import getLogger

from bottle import request

from alignak_webui.utils.plugin import Plugin

# pylint: disable=invalid-name
logger = getLogger(__name__)


class PluginAlignakDaemon(Plugin):
    """Alignak plugin"""

    def __init__(self, webui, plugin_dir, cfg_filenames=None):
        """Alignak plugin"""
        self.name = 'AlignakDaemon'
        self.backend_endpoint = 'alignakdaemon'

        self.pages = {
            'alignak_map': {
                'name': 'Alignak map',
                'route': '/alignak_map',
                'view': 'alignak'
            },
            'show_alignak': {
                'name': 'Alignak status',
                'route': '/alignak',
                'view': 'alignak'
            },
            'get_alignak_widget': {
                'name': 'Alignak widget',
                'route': '/alignak/widget',
                'method': 'POST',
                'view': 'alignak_widget',
                'widgets': [
                    {
                        'id': 'alignak_table',
                        'for': ['external', 'dashboard'],
                        'name': _('Alignak state widget'),
                        'template': 'alignak_table_widget',
                        'icon': 'table',
                        'description': _(
                            '<h4>Alignak state widget</h4>Displays a list of the Alignak '
                            'daemons.<br>'
                            'This daemons list displays the state of each daemon as seen by the '
                            'Alignak arbiter.'
                        ),
                        'picture': 'static/img/alignak_widget.png',
                        'options': {}
                    }
                ]
            },
        }

        super(PluginAlignakDaemon, self).__init__(webui, plugin_dir, cfg_filenames)

    def get_alignak_widget(self, embedded=False, identifier=None, credentials=None):
        """Get the Alignak widget"""
        datamgr = request.app.datamgr

        logger.debug("alignakdaemon, get widget")
        return self.get_widget(datamgr.get_alignak_state, 'alignakdaemon',
                               embedded, identifier, credentials)

    def alignak_map(self):
        """Get the Alignak map information from the Alignak WS and build a view from it"""
        datamgr = request.app.datamgr

        # Get Alignak state from the data manager
        alignak_daemons = datamgr.get_alignak_map()
        logger.debug("alignakdaemon, daemons: %s", alignak_daemons)

        # Sort the daemons list by daemon name
        alignak_daemons.sort(key=lambda x: x.name, reverse=False)

        return {
            'title': _('Alignak framework overall status'),
            'pagination': None,
            'params': self.plugin_parameters,
            'alignak_daemons': alignak_daemons
        }

    def show_alignak(self):
        """Get the Alignak map information from the backend and build a view from it"""
        datamgr = request.app.datamgr

        # Get Alignak state from the data manager
        alignak_daemons = datamgr.get_alignak_state()
        logger.debug("alignakdaemon, daemons: %s", alignak_daemons)

        # Sort the daemons list by daemon name
        alignak_daemons.sort(key=lambda x: x.name, reverse=False)

        return {
            'title': _('Alignak framework overall status'),
            'pagination': None,
            'params': self.plugin_parameters,
            'alignak_daemons': alignak_daemons
        }
