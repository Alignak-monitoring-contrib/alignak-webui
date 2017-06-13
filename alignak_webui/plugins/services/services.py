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

    def __init__(self, webui, plugin_dir, cfg_filenames=None):
        """Services plugin"""
        self.name = 'Services'
        self.backend_endpoint = 'service'

        self.pages = {
            'get_service_view': {
                'name': 'service synthesis view widget',
                'route': '/service_view/<element_id>',
                'view': 'service',
                'widgets': [
                    {
                        'id': 'view',
                        'for': ['service'],
                        'order': 1,
                        'name': _('Main view'),
                        'template': 'service_view_widget',
                        'icon': 'server',
                        'read_only': True,
                        'description': _('Service synthesis: displays service synthesis view.'),
                        'options': {}
                    },
                ]
            },
            'get_service_information': {
                'name': 'service information widget',
                'route': '/service_information/<element_id>',
                'view': 'service',
                'widgets': [
                    {
                        'id': 'information',
                        'for': ['service'],
                        'order': 2,
                        'name': _('information'),
                        'template': 'service_information_widget',
                        'icon': 'info',
                        'read_only': True,
                        'description': _('Service information: '
                                         'displays service general information.'),
                        'options': {}
                    },
                ]
            },
            'get_service_configuration': {
                'name': 'service configuration widget',
                'route': '/service_configuration/<element_id>',
                'view': 'service',
                'widgets': [
                    {
                        'id': 'configuration',
                        'for': ['service'],
                        'order': 3,
                        'name': _('Configuration'),
                        'level': 1,
                        'template': 'service_configuration_widget',
                        'icon': 'gear',
                        'read_only': True,
                        'description': _('Service configuration: '
                                         'displays service customs configuration variables.'),
                        'options': {}
                    },
                ]
            },
            'get_service_metrics': {
                'name': 'service metrics widget',
                'route': '/service_metrics/<element_id>',
                'view': 'service',
                'widgets': [
                    {
                        'id': 'metrics',
                        'for': ['service'],
                        'order': 4,
                        'name': _('Metrics'),
                        'level': 1,
                        'template': 'service_metrics_widget',
                        'icon': 'calculator',
                        'read_only': True,
                        'description': _('Service metrics: '
                                         'displays service last received metrics.'),
                        'options': {}
                    },
                ]
            },
            'get_service_timeline': {
                'name': 'service timeline widget',
                'route': '/service_timeline/<element_id>',
                'view': 'service',
                'widgets': [
                    {
                        'id': 'timeline',
                        'for': ['service'],
                        'order': 5,
                        'name': _('Timeline'),
                        'level': 1,
                        'template': 'service_timeline_widget',
                        'icon': 'clock-o',
                        'read_only': True,
                        'description': _('Service timeline: '
                                         'displays service events on a timeline.'),
                        'options': {}
                    },
                ]
            },
            'get_service_grafana': {
                'name': 'service grafana widget',
                'route': '/service_tab_grafana/<element_id>',
                'view': 'service',
                'widgets': [
                    {
                        'id': 'grafana',
                        'for': ['service'],
                        'order': 6,
                        'name': _('Grafana'),
                        'level': 1,
                        'template': 'service_grafana_widget',
                        'icon': 'line-chart',
                        'read_only': True,
                        'description': _(
                            'service metrics: displays service Grafana panel.'
                        ),
                        'options': {}
                    },
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

        super(PluginServices, self).__init__(webui, plugin_dir, cfg_filenames)

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
        """Get the services widget"""
        return self.get_widget(None, 'service', embedded, identifier, credentials)

    def get_one(self, element_id):
        # Because there are many locals needed :)
        # pylint: disable=too-many-locals
        """Display a service"""
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

        # Search filters used for the timeline widget
        events_search_filters = {
            '01': (_('Web UI comments'), 'type:webui.comment'),
            '02': (_('Check results'), 'type:check.'),
            '03': (_('Alerts'), 'type:monitoring.alert'),
            '04': (_('Acknowledges'), 'type:monitoring.ack'),
            '05': (_('Downtimes'), 'type:monitoring.downtime'),
            '06': (_('Notifications'), 'type:monitoring.notification'),
            '07': ('', ''),
        }

        return {
            'plugin': self,
            'plugin_parameters': self.plugin_parameters,

            'search_engine': self.search_engine,
            'search_filters': events_search_filters,

            'host': host,
            'service': service,
            'parents': parents,
            'children': children,
            'title': request.params.get('title', _('Service view: %s/%s'
                                                   % (host.alias, service.alias)))
        }

    def get_service_simple_widget(self, element_id, widget_id=None,
                                  embedded=False, identifier=None, credentials=None):
        """Display a generic service widget"""
        datamgr = request.app.datamgr

        logger.debug("get_service_simple_widget: %s, %s", element_id, widget_id)

        # Get service
        service = datamgr.get_service(element_id)
        if not service:
            return self.webui.response_invalid_parameters(_('Service does not exist'))

        # Get service host
        host = datamgr.get_host(search={'where': {'_id': service.host.id}})

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

        logger.info("get_service_simple_widget: found template: %s", widget_template)

        # Render the widget
        return template('_widget', {
            'widget_id': widget_id,
            'widget_name': widget_template,
            'widget_place': 'user',
            'widget_template': widget_template,
            'widget_uri': request.urlparts.path,
            'options': {},

            'plugin_parameters': self.plugin_parameters,

            'host': host,
            'service': service,

            'title': None,
            'embedded': embedded,
            'identifier': identifier,
            'credentials': credentials
        })

    def get_service_view(self, element_id, widget_id='view',
                         embedded=False, identifier=None, credentials=None):
        # pylint: disable=unused-argument
        """Display a service main view widget"""
        return self.get_service_simple_widget(element_id, widget_id,
                                              embedded, identifier, credentials)

    def get_service_information(self, element_id, widget_id='information',
                                embedded=False, identifier=None, credentials=None):
        # pylint: disable=unused-argument
        """Display a service information widget"""
        return self.get_service_simple_widget(element_id, widget_id,
                                              embedded, identifier, credentials)

    def get_service_configuration(self, element_id, widget_id='configuration',
                                  embedded=False, identifier=None, credentials=None):
        # pylint: disable=unused-argument
        """Display a service configuration widget"""
        return self.get_service_simple_widget(element_id, widget_id,
                                              embedded, identifier, credentials)

    def get_service_metrics(self, element_id, widget_id=None,
                            embedded=False, identifier=None, credentials=None):
        # pylint: disable=unused-argument
        """Display a service metrics widget"""
        return self.get_service_simple_widget(element_id, 'metrics',
                                              embedded, identifier, credentials)

    def get_service_timeline(self, element_id, widget_id='timeline',
                             embedded=False, identifier=None, credentials=None):
        # pylint: disable=unused-argument, too-many-locals
        """Display a service timeline widget"""
        user = request.environ['beaker.session']['current_user']
        datamgr = request.app.datamgr

        # Get service
        service = datamgr.get_service(element_id)
        if not service:
            return self.webui.response_invalid_parameters(_('Service does not exist'))

        # Search the required widget
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

        logger.debug("get_service_timeline: found template: %s", widget_template)

        # Fetch elements per page preference for user, default is 25
        elts_per_page = datamgr.get_user_preferences(user, 'elts_per_page', 25)

        # service history pagination and search parameters
        start = int(request.params.get('start', '0'))
        count = int(request.params.get('count', elts_per_page))
        where = {'service': service.id}

        # Find known history types
        history_plugin = self.webui.find_plugin('Histories')
        if history_plugin:
            decoded_search = Helper.decode_search(request.params.get('search', ''),
                                                  history_plugin.table)
            logger.info("Decoded search: %s", decoded_search)
            if decoded_search:
                where.update(decoded_search)

        search = {
            'page': (start // count) + 1,
            'max_results': count,
            'where': where
        }

        # Get service history
        history = datamgr.get_history(search=search)
        if history is None:
            history = []
        total = 0
        if history:
            total = history[0]['_total']

        # Search filters used for the timeline widget
        events_search_filters = {
            '01': (_('Web UI comments'), 'type:webui.comment'),
            '02': (_('Check results'), 'type:check.'),
            '03': (_('Alerts'), 'type:monitoring.alert'),
            '04': (_('Acknowledges'), 'type:monitoring.ack'),
            '05': (_('Downtimes'), 'type:monitoring.downtime'),
            '06': (_('Notifications'), 'type:monitoring.notification'),
            '07': ('', ''),
        }

        # Render the widget
        return template('_widget', {
            'widget_id': widget_id,
            'widget_name': widget_template,
            'widget_place': 'user',
            'widget_template': widget_template,
            'widget_uri': request.urlparts.path,
            'options': {},

            'plugin_parameters': self.plugin_parameters,
            'search_engine': True,
            'search_filters': events_search_filters,

            'service': service,

            'history': history,
            'pagination': self.webui.helper.get_pagination_control(
                '/service/%s#service_%s' % (service.id, widget_id), total, start, count
            ),

            'title': None,
            'embedded': embedded,
            'identifier': identifier,
            'credentials': credentials
        })

    def get_service_grafana(self, element_id, widget_id='grafana',
                            embedded=False, identifier=None, credentials=None):
        # pylint: disable=unused-argument
        """Display a service grafana widget"""
        return self.get_service_simple_widget(element_id, widget_id,
                                              embedded, identifier, credentials)
