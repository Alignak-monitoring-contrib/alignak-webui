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

import json
from logging import getLogger

from bottle import request, response

from alignak_webui.utils.plugin import Plugin
from alignak_webui.utils.helper import Helper

# pylint: disable=invalid-name
logger = getLogger(__name__)


class PluginLivestate(Plugin):
    """ Livestate plugin """

    def __init__(self, app, webui, cfg_filenames=None):
        """Livestate plugin"""
        self.name = 'Livestate'
        self.backend_endpoint = None

        self.pages = {
            'bi_livestate': {
                'name': 'Livestate json',
                'route': '/bi-livestate',
                'view': ''
            },
            'get_livestate': {
                'name': 'Livestate',
                'route': '/livestate',
                'view': 'livestate'
            }
        }

        super(PluginLivestate, self).__init__(app, webui, cfg_filenames)

    def bi_livestate(self):  # pylint:disable=no-self-use
        """Returns the livestate for a specific business impact level

        Used by the view to update the live state page content
        """
        user = request.environ['beaker.session']['current_user']
        webui = request.app.config['webui']
        datamgr = webui.datamgr

        panels = datamgr.get_user_preferences(user, 'livestate', {})

        ls = Helper.get_html_livestate(datamgr, panels, int(request.query.get('bi', -1)),
                                       request.query.get('search', {}), actions=user.is_power())

        response.status = 200
        response.content_type = 'application/json'
        return json.dumps({'livestate': ls})

    def get_livestate(self):  # pylint:disable=no-self-use
        """Display livestate page"""
        user = request.environ['beaker.session']['current_user']
        webui = request.app.config['webui']
        datamgr = webui.datamgr

        return {
            'panels': datamgr.get_user_preferences(user, 'livestate', {}),
            'layout': request.app.config.get('livestate_layout', 'table'),
            'title': request.query.get('title', _('Livestate'))
        }
