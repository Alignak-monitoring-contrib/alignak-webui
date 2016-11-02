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
    Plugin Alignak

    This plugin allows to display Alignak overall state information. It uses the Alignak
    Web services module to get information from the Alignak arbiter about all the running daemons.
"""

import collections
from logging import getLogger

from bottle import request

from alignak_webui import _
from alignak_webui.utils.plugin import Plugin

logger = getLogger(__name__)


class PluginAlignak(Plugin):
    """ Alignak plugin """

    def __init__(self, app, cfg_filenames=None):
        """
        Alignak plugin
        """
        self.name = 'Alignak'
        self.backend_endpoint = None

        self.pages = {
            'show_alignak': {
                'name': 'Alignak status',
                'route': '/alignak',
                'view': 'alignak'
            }
        }

        super(PluginAlignak, self).__init__(app, cfg_filenames)

    def show_alignak(self):
        """
        Get the Alignak information and build a view from it
        """
        # Yes, but that's how it is made, and it suits ;)
        # pylint: disable=too-many-locals
        user = request.environ['beaker.session']['current_user']
        datamgr = request.app.datamgr

        # Get Alignak state from the data manager
        alignak_state = datamgr.get_alignak_state()

        # Todo: create a realm sorted list of the daemons to display in a tree view ...
        # for daemon_type in alignak_state:
        #     logger.info("Got Alignak state for: %s", daemon_type)
        #     if daemon_type == '_status':
        #         logger.info("Got Alignak state for: %s / %s", daemon_type, alignak_state.get(daemon_type))
        #         continue
        #     daemons = alignak_state.get(daemon_type)
        #     for daemon_name in daemons:
        #         daemon = daemons.get(daemon_name)
        #         logger.info(" - %s: %s", daemon_name, daemon['alive'])

        return {
            'title': _('Alignak framework overall status'),
            'pagination': None,
            'params': self.plugin_parameters,
            'alignak_state': alignak_state
        }
