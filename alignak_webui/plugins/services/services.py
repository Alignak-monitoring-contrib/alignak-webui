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
    Plugin Services
"""
from logging import getLogger

from bottle import request, template, response

from alignak_webui import _
from alignak_webui.utils.plugin import Plugin

logger = getLogger(__name__)


class PluginServices(Plugin):
    """ Services plugin """

    def __init__(self, app, cfg_filenames=None):
        """
        Services plugin
        """
        self.name = 'Services'
        self.backend_endpoint = 'service'

        self.pages = {
            'get_services_widget': {
                'routes': [
                    ('/services/widget', 'Services widget')
                ],
                'method': 'POST',
                'view': 'services_widget',
                'widgets': [
                    {
                        'id': 'services_table',
                        'for': ['external', 'dashboard'],
                        'name': _('Services table widget'),
                        'template': 'services_table_widget',
                        'icon': 'table',
                        'description': _(
                            '<h4>Services table widget</h4>Displays a list of the monitored system '
                            'services.<br>The number of services in this list can be defined in '
                            'the widget options. The list of services can be filtered thanks to '
                            'regex on the service name'
                        ),
                        'picture': 'htdocs/img/services/table_widget.png',
                        'options': {
                            'search': {
                                'value': '',
                                'type': 'text',
                                'label': _('Filter (ex. status:ok)')
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
                        'id': 'services_chart',
                        'for': ['external', 'dashboard'],
                        'name': _('Services chart widget'),
                        'template': 'services_chart_widget',
                        'icon': 'pie-chart',
                        'description': _(
                            '<h4>Services chart widget</h4>Displays a pie chart with the system '
                            'services states.'
                        ),
                        'picture': 'htdocs/img/services_chart_widget.png',
                        'options': {}
                    }
                ]
            },
        }

        super(PluginServices, self).__init__(app, cfg_filenames)

    def get_services_widget(self, embedded=False, identifier=None, credentials=None):
        # Because there are many locals needed :)
        # pylint: disable=too-many-locals
        """
        Get the hosts list as a widget
        - widget_id: widget identifier

        - start and count for pagination
        - search for specific elements search

        """
        user = request.environ['beaker.session']['current_user']
        datamgr = request.app.datamgr

        # Fetch elements per page preference for user, default is 25
        elts_per_page = datamgr.get_user_preferences(user, 'elts_per_page', 25)

        # Pagination and search
        start = int(request.params.get('start', '0'))
        count = int(request.params.get('count', elts_per_page))
        where = self.webui.helper.decode_search(request.params.get('search', ''))
        search = {
            'page': start // (count + 1),
            'max_results': count,
            'where': where
        }
        name_filter = request.params.get('filter', '')
        if name_filter:
            search['where'].update({
                '$or': [
                    {'name': {'$regex': ".*%s.*" % name_filter}},
                    {'alias': {'$regex': ".*%s.*" % name_filter}}
                ]
            })
        logger.info("Search parameters: %s", search)

        # Get elements from the data manager
        services = datamgr.get_services(search)
        # Get last total elements count
        total = datamgr.get_objects_count('service', search=where, refresh=True)
        count = min(count, total)

        # Widget options
        widget_id = request.params.get('widget_id', '')
        if widget_id == '':
            return self.webui.response_invalid_parameters(_('Missing widget identifier'))

        widget_place = request.params.get('widget_place', 'dashboard')
        widget_template = request.params.get('widget_template', 'services/table_widget')
        widget_icon = request.params.get('widget_icon', 'plug')
        # Search in the application widgets (all plugins widgets)
        options = {}
        for widget in self.webui.get_widgets_for(widget_place):
            if widget_id.startswith(widget['id']):
                options = widget['options']
                widget_template = widget['template']
                widget_icon = widget['icon']
                logger.info("Widget found, template: %s, options: %s", widget_template, options)
                break
        else:
            logger.warning("Widget identifier not found: %s", widget_id)
            return self.webui.response_invalid_parameters(_('Unknown widget identifier'))

        if options:
            options['search']['value'] = request.params.get('search', '')
            options['count']['value'] = count
            options['filter']['value'] = name_filter
        logger.info("Widget options: %s", options)

        title = request.params.get('title', _('Services'))
        if name_filter:
            title = _('%s (%s)') % (title, name_filter)

        # Use required template to render the widget
        return template('_widget', {
            'widget_id': widget_id,
            'widget_name': widget_template,
            'widget_place': widget_place,
            'widget_template': widget_template,
            'widget_icon': widget_icon,
            'widget_uri': request.urlparts.path,
            'services': services,
            'options': options,
            'title': title,
            'embedded': embedded,
            'identifier': identifier,
            'credentials': credentials
        })
