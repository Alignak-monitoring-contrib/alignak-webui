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

from alignak_webui import _
from alignak_webui.utils.plugin import Plugin

# pylint: disable=invalid-name
logger = getLogger(__name__)


class PluginCurrently(Plugin):
    """ Currently plugin """

    def __init__(self, app, cfg_filenames=None):
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
            }
        }

        super(PluginCurrently, self).__init__(app, cfg_filenames)

    def get_currently(self):  # pylint:disable=no-self-use
        """
        Display currently page
        """
        user = request.environ['beaker.session']['current_user']
        datamgr = request.app.datamgr

        # Get the stored panels
        currently_panels = datamgr.get_user_preferences(user, 'currently_panels', None)

        # Get the stored graphs
        currently_graphs = datamgr.get_user_preferences(user, 'currently_graphs', None)

        # Live state global and history
        (livesynthesis, ls_history) = datamgr.get_livesynthesis_history()
        ls_history = sorted(ls_history, key=lambda x: x['_timestamp'], reverse=False)

        return {
            'currently_panels': currently_panels,
            'currently_graphs': currently_graphs,
            'history': ls_history,
            'hs': livesynthesis['hosts_synthesis'],
            'ss': livesynthesis['services_synthesis'],
            'title': request.query.get('title', _('Keep an eye'))
        }
