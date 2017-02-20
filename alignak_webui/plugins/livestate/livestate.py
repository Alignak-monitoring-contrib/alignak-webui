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
    Plugin Livestate
"""

from logging import getLogger

from bottle import request

from alignak_webui.utils.plugin import Plugin

# pylint: disable=invalid-name
logger = getLogger(__name__)


class PluginLivestate(Plugin):
    """ Livestate plugin """

    def __init__(self, app, webui, cfg_filenames=None):
        """
        Livestate plugin
        """
        self.name = 'Livestate'
        self.backend_endpoint = None
        _ = app.config['_']

        self.pages = {
            'get_livestate': {
                'name': 'Livestate',
                'route': '/livestate',
                'view': 'livestate'
            }
        }

        super(PluginLivestate, self).__init__(app, webui, cfg_filenames)

    def get_livestate(self):  # pylint:disable=no-self-use
        """
        Display livestate page
        """
        user = request.environ['beaker.session']['current_user']
        webui = request.app.config['webui']
        datamgr = webui.datamgr

        return {
            'panels': datamgr.get_user_preferences(user, 'livestate', {}),
            # 'livestate': livestate['panel_bi'],
            'title': request.query.get('title', _('Livestate'))
        }
