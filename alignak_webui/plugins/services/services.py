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
    Plugin Services
"""
from logging import getLogger

from bottle import request, template

from alignak_webui.utils.plugin import Plugin
from alignak_webui.utils.helper import Helper

# pylint: disable=invalid-name
logger = getLogger(__name__)


class PluginServices(Plugin):
    """ Services plugin """

    def __init__(self, app, webui, cfg_filenames=None):
        """
        Services plugin
        """
        self.name = 'Services'
        self.backend_endpoint = 'service'

        self.pages = {
            'get_service_widget': {
                'name': 'Service widget',
                'route': '/service_widget/<element_id>/<widget_id>',
                'view': 'service',
                'widgets': [
                    {
                        'id': 'information',
                        'for': ['service'],
                        'name': _('Information'),
                        'template': 'service_information_widget',
                        'icon': 'info',
                        'description': _('Service information: service general information.'),
                        'options': {}
                    },
                    {
                        'id': 'configuration',
                        'for': ['service'],
                        'name': _('Configuration'),
                        'template': 'service_configuration_widget',
                        'icon': 'gear',
                        'read_only': True,
                        'description': _(
                            'Service configuration: service customs configuration variables.'
                        ),
                        'options': {}
                    },
                    {
                        'id': 'metrics',
                        'for': ['service'],
                        'name': _('Metrics'),
                        'template': 'service_metrics_widget',
                        'icon': 'line-chart',
                        'description': _(
                            '<h4>service metrics widget</h4>Displays service (and its services) '
                            'last received metrics.'
                        ),
                        'picture': 'static/img/service_metrics_widget.png',
                        'options': {}
                    },
                    {
                        'id': 'grafana',
                        'for': ['service'],
                        'name': _('Grafana'),
                        'template': 'service_grafana_widget',
                        'icon': 'area-chart',
                        'description': _(
                            '<h4>service grafana widget</h4>Displays service Grafana panel.'
                        ),
                        # Requires Grafana plugin
                        'plugin': 'Grafana',
                        'options': {}
                    }
                ]
            },
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
                        'picture': 'static/img/services_table_widget.png',
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
                        'picture': 'static/img/services_chart_widget.png',
                        'options': {}
                    }
                ]
            },
        }

        super(PluginServices, self).__init__(app, webui, cfg_filenames)

        self.search_engine = True
        self.search_filters = {
            '01': (_('Ok'), 'is:ok'),
            '02': (_('Acknowledged'), 'is:acknowledged'),
            '03': (_('Downtimed'), 'is:in_downtime'),
            '04': (_('Warning'), 'is:warning'),
            '05': (_('Critical'), 'is:warning'),
            '06': ('', ''),
        }

    def get_services_widget(self, embedded=False, identifier=None, credentials=None):
        """
        Get the services widget
        """
        logger.debug("get_services_widget")
        return self.get_widget(None, 'service', embedded, identifier, credentials)

    def get_one(self, element_id):
        # Because there are many locals needed :)
        # pylint: disable=too-many-locals
        """
        Display a service
        """
        user = request.environ['beaker.session']['current_user']
        datamgr = request.app.datamgr

        # Get service
        service = datamgr.get_service(element_id)
        if not service:
            return self.webui.response_invalid_parameters(_('Service does not exist'))

        # Get service host
        host = datamgr.get_host(search={'where': {'_id': service.host.id}})

        # Get service dependencies
        children = datamgr.get_servicedependencys(
            search={'where': {'services': service.id}}
        )
        parents = datamgr.get_servicedependencys(
            search={'where': {'dependent_services': service.id}}
        )

        # Get service history (timeline)
        # Fetch elements per page preference for user, default is 25
        elts_per_page = datamgr.get_user_preferences(user, 'elts_per_page', 25)

        # Service history pagination and search parameters
        start = int(request.params.get('start', '0'))
        count = int(request.params.get('count', elts_per_page))
        where = Helper.decode_search(request.params.get('search', ''), self.table)
        search = {
            'page': (start // count) + 1,
            'max_results': count,
            'where': {'service': element_id}
        }

        # Find known history types
        history_plugin = self.webui.find_plugin('Histories')
        history_types = []
        if history_plugin and 'type' in history_plugin.table:
            logger.warning("History types: %s", history_plugin.table['type'].get('allowed', []))
            history_types = history_plugin.table['type'].get('allowed', [])
            history_types = history_types.split(',')

        # Fetch timeline filters preference for user, default is []
        selected_types = datamgr.get_user_preferences(user, 'timeline_filters', [])
        # selected_types = selected_types['value']
        for selected_type in history_types:
            if request.params.get(selected_type) == 'true':
                if selected_type not in selected_types:
                    selected_types.append(selected_type)
            elif request.params.get(selected_type) == 'false':
                if selected_type in selected_types:
                    selected_types.remove(selected_type)

        datamgr.set_user_preferences(user, 'timeline_filters', selected_types)
        if selected_types:
            search['where'].update({'type': {'$in': selected_types}})
        logger.debug("History selected types: %s", selected_types)

        # Get service history
        history = datamgr.get_history(search=search)
        if history is None:
            history = []
        # Get last total elements count
        total = datamgr.get_objects_count('history', search=where, refresh=True)

        # Get service events (all history except the events concerning the checks)
        excluded = [t for t in history_types if t.startswith('check.')]
        search = {
            'page': (start // count) + 1,
            'max_results': count,
            'where': {'service': element_id, 'type': {'$nin': excluded}}
        }

        # Get service events
        events = datamgr.get_history(search=search)
        if events is None:
            events = []

        return {
            'host': host,
            'service': service,
            'plugin_parameters': self.plugin_parameters,
            'history': history,
            'events': events,
            'parents': parents,
            'children': children,
            'timeline_pagination': self.webui.helper.get_pagination_control(
                '/service/' + element_id, total, start, count
            ),
            'types': history_types,
            'selected_types': selected_types,
            'title': request.params.get('title', _('Service view'))
        }

    def get_service_widget(self, element_id, widget_id,
                           embedded=False, identifier=None, credentials=None):
        # Because there are many locals needed :)
        # pylint: disable=too-many-locals,too-many-arguments
        """
        Display a service widget
        """
        user = request.environ['beaker.session']['current_user']
        datamgr = request.app.datamgr

        logger.warning("get_service_widget: %s, %s", element_id, widget_id)

        # Get service
        service = datamgr.get_service(element_id)
        logger.debug("get_service_widget: service: %s", service)
        if not service:
            # Test if we got a name instead of an id
            service = datamgr.get_service(search={'max_results': 1, 'where': {'name': element_id}})
            if not service:
                return self.webui.response_invalid_parameters(_('Service does not exist'))
        logger.debug("get_service_widget: found service: %s", service.name)

        # Get service host
        host = datamgr.get_host(search={'where': {'_id': service.host.id}})
        logger.debug("get_service_widget: found host: %s", host.name)

        # Get service history (timeline)
        # Fetch elements per page preference for user, default is 25
        elts_per_page = datamgr.get_user_preferences(user, 'elts_per_page', 25)

        # Service history pagination and search parameters
        start = int(request.params.get('start', '0'))
        count = int(request.params.get('count', elts_per_page))
        where = Helper.decode_search(request.params.get('search', ''), self.table)
        search = {
            'page': (start // count) + 1,
            'max_results': count,
            'where': {'service': service.id}
        }

        # Find known history types
        history_plugin = self.webui.find_plugin('Histories')
        history_types = []
        if history_plugin and 'type' in history_plugin.table:
            history_types = history_plugin.table['type'].get('allowed', [])
            history_types = history_types.split(',')

        # Fetch timeline filters preference for user, default is []
        selected_types = datamgr.get_user_preferences(user, 'timeline_filters', [])
        # selected_types = selected_types['value']
        for selected_type in history_types:
            if request.params.get(selected_type) == 'true':
                if selected_type not in selected_types:
                    selected_types.append(selected_type)
            elif request.params.get(selected_type) == 'false':
                if selected_type in selected_types:
                    selected_types.remove(selected_type)

        datamgr.set_user_preferences(user, 'timeline_filters', selected_types)
        if selected_types:
            search['where'].update({'type': {'$in': selected_types}})
        logger.debug("Service widget search: %s", search)

        # Get service history
        history = datamgr.get_history(search=search)
        if history is None:
            history = []

        # Get last total elements count
        total = datamgr.get_objects_count('history', search=where, refresh=True)

        widget_place = request.params.get('widget_place', 'service')
        widget_template = request.params.get('widget_template', 'service_widget')
        # Search in the application widgets (all plugins widgets)
        for widget in self.webui.get_widgets_for(widget_place):
            if widget_id.startswith(widget['id']):
                widget_template = widget['template']
                logger.info("Widget found, template: %s", widget_template)
                break
        else:
            logger.info("Widget identifier not found: using default template and no options")

        title = request.params.get('title', _('Service : %s') % service.name)
        logger.debug("get_service_widget: widget title: %s", title)

        # Use required template to render the widget
        return template('_widget', {
            'widget_id': widget_id,
            'widget_name': widget_template,
            'widget_place': 'host',
            'widget_template': widget_template,
            'widget_uri': request.urlparts.path,
            'options': {},

            'host': host,
            'service': service,
            'history': history,
            'timeline_pagination': self.webui.helper.get_pagination_control(
                '/host/' + service.id, total, start, count
            ),
            'types': history_types,
            'selected_types': selected_types,

            'title': title,
            'embedded': embedded,
            'identifier': identifier,
            'credentials': credentials
        })
