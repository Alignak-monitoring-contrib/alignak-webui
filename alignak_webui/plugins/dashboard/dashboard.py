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
    Plugin Dashboard
"""

import json
from logging import getLogger

from bottle import request

from alignak_webui import _
from alignak_webui.utils.plugin import Plugin
from alignak_webui.objects.datamanager import DataManager

logger = getLogger(__name__)


class PluginDashboard(Plugin):
    """ Dashboard plugin """

    def __init__(self, app, cfg_filenames=None):
        """
        Dashboard plugin
        """
        self.name = 'Dashboard'
        self.backend_endpoint = None

        self.pages = {
            'get_page': {
                'name': 'Dashboard',
                'route': '/dashboard',
                'view': 'dashboard'
            },
            'get_currently': {
                'name': 'Currently',
                'route': '/currently',
                'view': 'currently'
            }
        }

        super(PluginDashboard, self).__init__(app, cfg_filenames)

    def get_page(self):
        """
        Display dashboard page
        """
        user = request.environ['beaker.session']['current_user']
        datamgr = request.app.datamgr

        # Search for the dashboard widgets
        saved_widgets = datamgr.get_user_preferences(user, 'dashboard_widgets', [])
        if not saved_widgets:
            datamgr.set_user_preferences(user, 'dashboard_widgets', [])

        widgets = []
        for widget in saved_widgets:
            logger.info("Dashboard widget, got: %s", widget)

            # if 'id' not in widget:
                # logger.warning("Widget ignored: %s", widget)
                # continue

            # Widget saved data are missing some fields when widget got created:
            # - for: widget page (default: dashboard)
            # - id: unique identifier
            # - x, y: position (default: 0, 0)
            # - width, height: size (default: 1, 1)
            # - base_url
            # - options_json

            # by default the widget is for /dashboard
            # if 'for' not in wiget:
                # widget['for'] = 'dashboard'

            # widget['uri'] = widget.get('uri', '/')
            # if 'icon' not in wiget:
                # widget['icon'] = widget.get('icon', 'leaf')

            # options = widget.get('options', {})
            # args = {'id': widget['id']}
            # widget['options_uri'] = '&'.join('%s=%s' % (k, v) for (k, v) in args.iteritems())
            # for option in options:
                # widget['options_uri'] += '&%s=%s' % (option, options[option]['value'])
            # logger.warning("Dashboard widget: %s", widget)
            # widgets.append(widget)

        message = None
        session = request.environ['beaker.session']
        if 'user_message' in session and session['user_message']:
            message = session['user_message']
            session['user_message'] = None

        return {
            'widgets_bar': len(self.webui.get_widgets_for('dashboard')) != 0,
            'widgets_place': 'dashboard',
            'dashboard_widgets': saved_widgets,
            'title': request.query.get('title', _('Dashboard')),
            'message': message
        }

    def get_currently(self):
        """
        Display currently page
        """
        user = request.environ['beaker.session']['current_user']
        datamgr = request.app.datamgr

        # Get the stored panels
        panels = datamgr.get_user_preferences(user, 'currently_panels', None)

        # Get the stored graphs
        graphs = datamgr.get_user_preferences(user, 'currently_graphs', None)

        # Live state stored queuers
        hosts_states_queue = datamgr.get_user_preferences(user, 'hosts_states_queue', [])
        services_states_queue = datamgr.get_user_preferences(user, 'services_states_queue', [])

        return {
            'panels': panels,
            'graphs': graphs,
            'hosts_states_queue': hosts_states_queue,
            'services_states_queue': services_states_queue,
            'title': request.query.get('title', _('Keep an eye'))
        }
