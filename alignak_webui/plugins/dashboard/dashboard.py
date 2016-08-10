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
        target_user = request.environ['beaker.session']['target_user']
        datamgr = request.environ['beaker.session']['datamanager']

        username = user.get_username()
        if not target_user.is_anonymous():
            username = target_user.get_username()

        # Search for the dashboard widgets
        saved_widgets = datamgr.get_user_preferences(username, 'dashboard_widgets', {'widgets': []})
        if not saved_widgets:
            saved_widgets = {'widgets': []}
            datamgr.set_user_preferences(username, 'dashboard_widgets', saved_widgets)

        widgets = []
        for widget in saved_widgets['widgets']:
            if 'id' not in widget:
                continue

            logger.warning("Dashboard widget, got: %s", widget)

            # Widget data:
            # - for: widget page (default: dashboard)
            # - id: unique identifier
            # - x, y: position (default: 0, 0)
            # - width, height: size (default: 1, 1)
            # - base_url
            # - options_json

            # by default the widget is for /dashboard
            widget['for'] = widget.get('for', 'dashboard')
            if not widget['for'] == 'dashboard':  # pragma: no cover - not testable yet
                # Not a dashboard widget? I don't want it so
                continue

            widget['x'] = widget.get('x', 0)
            widget['y'] = widget.get('x', 0)
            widget['width'] = widget.get('width', 1)
            widget['minWidth'] = widget.get('minWidth', 1)
            widget['maxWidth'] = widget.get('maxWidth', 12)
            widget['height'] = widget.get('height', 1)
            widget['minHeight'] = widget.get('minHeight', 1)
            widget['maxHeight'] = widget.get('maxHeight', 6)

            widget['id'] = widget.get('id', None)
            widget['uri'] = widget.get('uri', '/')
            widget['name'] = widget.get('name', None)
            widget['icon'] = widget.get('icon', 'leaf')
            widget['template'] = widget.get('template', None)

            options = widget.get('options', {})

            widget['options'] = options
            widget['options_json'] = json.dumps(options)
            args = {'id': widget['id']}
            args.update(options)
            widget['options_uri'] = '&'.join('%s=%s' % (k, v) for (k, v) in args.iteritems())
            logger.info("Dashboard widget: %s", widget)
            widgets.append(widget)

        return {
            'widgets_bar': len(self.webui.get_widgets_for('dashboard')) != 0,
            'widgets_place': 'dashboard',
            'dashboard_widgets': widgets,
            'title': request.query.get('title', _('Dashboard'))
        }

    def get_currently(self):
        """
        Display currently page
        """
        user = request.environ['beaker.session']['current_user']
        target_user = request.environ['beaker.session']['target_user']
        datamgr = request.environ['beaker.session']['datamanager']

        username = user.get_username()
        if not target_user.is_anonymous():
            username = target_user.get_username()

        # Get the stored panels
        panels = datamgr.get_user_preferences(username, 'panels', {'panels': {}})

        # Get the stored graphs
        graphs = datamgr.get_user_preferences(username, 'graphs', {'graphs': {}})

        return {
            'panels': panels,
            'graphs': graphs,
            'title': request.query.get('title', _('Dashboard'))
        }
