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

from bottle import request, response, template

from alignak_webui.utils.plugin import Plugin
from alignak_webui.utils.helper import Helper

# pylint: disable=invalid-name
logger = getLogger(__name__)


class PluginLivestate(Plugin):
    """ Livestate plugin """

    def __init__(self, webui, plugin_dir, cfg_filenames=None):
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
            },
            'get_livestate_widget': {
                'name': 'Livestate widget',
                'route': '/livestate/widget',
                'method': 'POST',
                'view': 'livestate_widget',
                'widgets': [
                    {
                        'id': 'livestate',
                        'for': ['external', 'dashboard'],
                        'name': _('Livestate widget'),
                        'template': 'livestate_widget',
                        'icon': 'heartbeat',
                        'description': _(
                            '<h4>Livestate widget</h4>Displays the live state of '
                            'the monitored system.'
                        ),
                        'picture': 'static/img/livestate_widget.png',
                        'options': {}
                    }
                ]
            }
        }

        super(PluginLivestate, self).__init__(webui, plugin_dir, cfg_filenames)

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

    def get_livestate_widget(self, embedded=False, identifier=None, credentials=None):
        # pylint: disable=too-many-locals
        """Get the livestate widget"""
        user = request.environ['beaker.session']['current_user']
        webui = request.app.config['webui']
        datamgr = webui.datamgr

        panels = datamgr.get_user_preferences(user, 'livestate', {})

        ls = Helper.get_html_livestate(datamgr, panels, int(request.query.get('bi', -1)),
                                       request.query.get('search', {}), actions=user.is_power())

        # Widget options
        widget_id = request.params.get('widget_id', '')
        if widget_id == '':
            return self.webui.response_invalid_parameters(_('Missing widget identifier'))

        widget_place = request.params.get('widget_place', 'dashboard')
        widget_template = request.params.get('widget_template', 'elements_table_widget')
        widget_icon = request.params.get('widget_icon', 'plug')
        logger.debug("Searching a widget %s for: %s (%s)",
                     widget_id, widget_place, widget_template)

        # Search in the application widgets (all plugins widgets)
        options = {}
        for widget in self.webui.get_widgets_for(widget_place):
            logger.debug("Found widget: %s (%s)", widget['name'], widget['id'])
            if widget_id.startswith(widget['id']):
                options = widget['options']
                widget_template = widget['template']
                widget_icon = widget['icon']
                logger.debug("Widget %s found, template: %s, options: %s",
                             widget_id, widget_template, options)
                break
        else:
            logger.warning("Widget identifier not found: %s", widget_id)
            return self.webui.response_invalid_parameters(_('Unknown widget identifier'))

        # Search in the saved dashboard widgets
        saved_widget = None
        saved_widgets = datamgr.get_user_preferences(user, 'dashboard_widgets', [])
        for widget in saved_widgets:
            if widget_id == widget['id']:
                saved_widget = widget
                logger.info("Saved widget found: %s", saved_widget)
                break

        # Widget freshly created
        tmp_options = []
        if not saved_widget or 'options' not in saved_widget:
            for option in options:
                tmp_options.append("%s=%s" % (option, options[option]['value']))
            saved_options = '|'.join(tmp_options)
        else:
            saved_options = saved_widget['options']

        tmp_options = []
        logger.info("Saved widget options: %s", saved_options)
        for option in saved_options.split('|'):
            option = option.split('=')
            logger.info("- saved option: %s", option)
            if len(option) > 1:
                if request.params.get(option[0], option[1]) != option[1]:
                    tmp_options.append("%s=%s" % (option[0], request.params.get(option[0])))
                    options[option[0]]['value'] = request.params.get(option[0])
                else:
                    tmp_options.append("%s=%s" % (option[0], option[1]))
                    options[option[0]]['value'] = option[1]

        new_options = '|'.join(tmp_options)

        if saved_options != new_options:
            logger.info("Widget %s new options: %s", widget_id, new_options)

            # Search for the dashboard widgets
            saved_widgets = datamgr.get_user_preferences(user, 'dashboard_widgets', [])
            for widget in saved_widgets:
                if widget_id.startswith(widget['id']):
                    widget['options'] = new_options
                    datamgr.set_user_preferences(user, 'dashboard_widgets', saved_widgets)
                    logger.info("Widget new options saved!")
                    break
        saved_options = new_options

        title = request.params.get('title', _('Elements'))

        # Use required template to render the widget
        logger.info("Rendering widget %s", widget_id)
        return template('_widget', {
            'widget_id': widget_id,
            'widget_name': widget_template,
            'widget_place': widget_place,
            'widget_template': widget_template,
            'widget_icon': widget_icon,
            'widget_uri': request.urlparts.path,

            'plugin_parameters': self.plugin_parameters,

            'livestate': ls,

            'options': options,
            'title': title,
            'embedded': embedded,
            'identifier': identifier,
            'credentials': credentials
        })
