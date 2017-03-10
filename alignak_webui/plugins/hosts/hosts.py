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
    Plugin Hosts
"""
from logging import getLogger

from bottle import request, template

from alignak_webui.utils.plugin import Plugin
from alignak_webui.utils.helper import Helper

# pylint: disable=invalid-name
logger = getLogger(__name__)


class PluginHosts(Plugin):
    """ Hosts plugin """

    def __init__(self, app, webui, cfg_filenames=None):
        """
        Hosts plugin

        Overload the default get route to declare filters.
        """
        self.name = 'Hosts'
        self.backend_endpoint = 'host'

        self.pages = {
            'get_host_widget': {
                'name': 'Host widget',
                'route': '/host_widget/<element_id>/<widget_id>',
                'view': 'host',
                'widgets': [
                    {
                        'id': 'information',
                        'for': ['host'],
                        'name': _('Information'),
                        'template': 'host_information_widget',
                        'icon': 'info',
                        'description': _(
                            'Host information: displays host general information.'
                        ),
                        'options': {}
                    },
                    {
                        'id': 'configuration',
                        'for': ['host'],
                        'name': _('Configuration'),
                        'template': 'host_configuration_widget',
                        'icon': 'gear',
                        'read_only': True,
                        'description': _(
                            'Host configuration: displays host customs configuration variables.'
                        ),
                        'options': {}
                    },
                    {
                        'id': 'location',
                        'for': ['host'],
                        'name': _('Location'),
                        'template': 'host_location_widget',
                        'icon': 'globe',
                        'read_only': True,
                        'description': _(
                            'Host location: displays host position on a map.'
                        ),
                        # Requires Worldmap plugin
                        'plugin': 'Worldmap',
                        'options': {}
                    },
                    {
                        'id': 'services',
                        'for': ['host'],
                        'name': _('Services'),
                        'template': 'host_services_widget',
                        'icon': 'cubes',
                        'description': _(
                            '<h4>Host service widget</h4>Displays host services.'
                        ),
                        'options': {}
                    },
                    {
                        'id': 'metrics',
                        'for': ['host'],
                        'name': _('Metrics'),
                        'template': 'host_metrics_widget',
                        'icon': 'line-chart',
                        'description': _(
                            '<h4>Host metrics widget</h4>Displays host (and its services) last '
                            'received metrics.'
                        ),
                        'picture': 'static/img/host_metrics_widget.png',
                        'options': {}
                    },
                    {
                        'id': 'timeline',
                        'for': ['host'],
                        'name': _('Timeline'),
                        'template': 'host_timeline_widget',
                        'icon': 'clock-o',
                        'description': _(
                            '<h4>Host timeline widget</h4>Displays host timeline.'
                        ),
                        'picture': 'static/img/host_timeline_widget.png',
                        'options': {}
                    },
                    {
                        'id': 'history',
                        'for': ['host'],
                        'name': _('History'),
                        'template': 'host_history_widget',
                        'icon': 'history',
                        'description': _(
                            '<h4>Host history widget</h4>Displays host history.'
                        ),
                        'options': {}
                    },
                    {
                        'id': 'events',
                        'for': ['host'],
                        'name': _('Events'),
                        'template': 'host_events_widget',
                        'icon': 'history',
                        'description': _(
                            '<h4>Host events widget</h4>Displays host events: '
                            'comments, acknowledges, downtimes,...'
                        ),
                        'options': {}
                    },
                    {
                        'id': 'grafana',
                        'for': ['host'],
                        'name': _('Grafana'),
                        'template': 'host_grafana_widget',
                        'icon': 'area-chart',
                        'description': _(
                            '<h4>Host grafana widget</h4>Displays host Grafana panel.'
                        ),
                        # Requires Grafana plugin
                        'plugin': 'Grafana',
                        'options': {}
                    }
                ]
            },
            'get_hosts_widget': {
                'name': 'Hosts widget',
                'route': '/hosts/widget',
                'method': 'POST',
                'view': 'hosts_widget',
                'widgets': [
                    {
                        'id': 'hosts_table',
                        'for': ['external', 'dashboard'],
                        'name': _('Hosts table widget'),
                        'template': 'hosts_table_widget',
                        'icon': 'table',
                        'description': _(
                            '<h4>Hosts table widget</h4>Displays a list of the monitored system '
                            'hosts.<br>'
                            'The number of hosts in this list can be defined in the widget options.'
                            'The list of hosts can be filtered thanks to regex on the host name'
                        ),
                        'picture': 'static/img/hosts_table_widget.png',
                        'options': {
                            'search': {
                                'value': '',
                                'type': 'text',
                                'label': _('Filter (ex. status:up)')
                            },
                            'count': {
                                'value': -1,
                                'type': 'int',
                                'label': _('Number of elements')
                            },
                            'filter': {
                                'value': '',
                                'type': 'hst_srv',
                                'label': _('Host name search')
                            }
                        }
                    },
                    {
                        'id': 'hosts_chart',
                        'for': ['external', 'dashboard'],
                        'name': _('Hosts chart widget'),
                        'template': 'hosts_chart_widget',
                        'icon': 'pie-chart',
                        'description': _(
                            '<h4>Hosts chart widget</h4>Displays a pie chart with the system '
                            'hosts states.'
                        ),
                        'picture': 'static/img/hosts_chart_widget.png',
                        'options': {}
                    }
                ]
            },
        }

        super(PluginHosts, self).__init__(app, webui, cfg_filenames)

        self.search_engine = True
        self.search_filters = {
            '01': (_('Ok'), 'is:ok'),
            '02': (_('Acknowledged'), 'is:acknowledged'),
            '03': (_('Downtimed'), 'is:in_downtime'),
            '04': (_('Warning'), 'is:warning'),
            '05': (_('Critical'), 'is:warning'),
            '06': ('', ''),
        }

    def get_hosts_widget(self, embedded=False, identifier=None, credentials=None):
        """
        Get the hosts widget
        """
        return self.get_widget(None, 'host', embedded, identifier, credentials)

    def get_one(self, element_id):
        # Because there are many locals needed :)
        # pylint: disable=too-many-locals
        """
        Display an host
        """
        user = request.environ['beaker.session']['current_user']
        datamgr = request.app.datamgr

        # Get host
        host = datamgr.get_host(element_id)
        if not host:
            # Test if we got a name instead of an id
            host = datamgr.get_host(search={'max_results': 1, 'where': {'name': element_id}})
            if not host:
                return self.webui.response_invalid_parameters(_('Host does not exist'))

        # Get host services
        services = datamgr.get_host_services(host)

        # Aggregate host services in a tree
        tree_items = datamgr.get_services_aggregated(services)

        # Get host dependencies
        children = datamgr.get_hostdependencys(
            search={'where': {'hosts': host.id}}
        )
        parents = datamgr.get_hostdependencys(
            search={'where': {'dependent_hosts': host.id}}
        )

        # Fetch elements per page preference for user, default is 25
        elts_per_page = datamgr.get_user_preferences(user, 'elts_per_page', 25)

        # Host history pagination and search parameters
        start = int(request.params.get('start', '0'))
        count = int(request.params.get('count', elts_per_page))
        where = Helper.decode_search(request.params.get('search', ''), self.table)
        search = {
            'page': (start // count) + 1,
            'max_results': count,
            'where': {'host': host.id}
        }

        # Find known history types
        history_plugin = self.webui.find_plugin('Histories')
        history_types = []
        if history_plugin and 'type' in history_plugin.table:
            logger.debug("History types: %s", history_plugin.table['type'].get('allowed', []))
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

        # Get host history
        history = datamgr.get_history(search=search)
        if history is None:
            history = []
        # Get last total elements count
        total = datamgr.get_objects_count('history', search=where, refresh=True)

        # Get host events (all history except the events concerning the checks)
        excluded = [t for t in history_types if t.startswith('check.')]
        search = {
            'page': (start // count) + 1,
            'max_results': count,
            'where': {'host': host.id, 'type': {'$nin': excluded}}
        }

        # Get host events
        events = datamgr.get_history(search=search)
        if events is None:
            events = []

        return {
            'host': host,
            'plugin_parameters': self.plugin_parameters,
            'services': services,
            'tree_items': tree_items,
            'history': history,
            'events': events,
            'parents': parents,
            'children': children,
            'timeline_pagination': self.webui.helper.get_pagination_control(
                '/host/' + element_id, total, start, count
            ),
            'types': history_types,
            'selected_types': selected_types,
            'title': request.params.get('title', _('Host view'))
        }

    def get_host_widget(self, element_id, widget_id,
                        embedded=False, identifier=None, credentials=None):
        # Because there are many locals needed :)
        # pylint: disable=too-many-locals,too-many-arguments
        """
        Display an host widget
        """
        user = request.environ['beaker.session']['current_user']
        datamgr = request.app.datamgr

        logger.debug("get_host_widget: %s, %s", element_id, widget_id)

        # Get host
        host = datamgr.get_host(element_id)
        if not host:
            # Test if we got a name instead of an id
            host = datamgr.get_host(search={'max_results': 1, 'where': {'name': element_id}})
            if not host:
                return self.webui.response_invalid_parameters(_('Host does not exist'))

        # Get host services
        services = datamgr.get_services(search={'where': {'host': host.id}})

        # Fetch elements per page preference for user, default is 25
        elts_per_page = datamgr.get_user_preferences(user, 'elts_per_page', 25)

        # Host history pagination and search parameters
        start = int(request.params.get('start', '0'))
        count = int(request.params.get('count', elts_per_page))
        where = Helper.decode_search(request.params.get('search', ''), self.table)
        search = {
            'where': {'host': host.id}
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

        if selected_types:
            datamgr.set_user_preferences(user, 'timeline_filters', selected_types)
            search['where'].update({'type': {'$in': selected_types}})
        logger.debug("Host widget search: %s", search)

        history = datamgr.get_history(search=search)
        if history is None:
            history = []

        # Get last total elements count
        total = datamgr.get_objects_count('history', search=where, refresh=True)

        widget_place = request.params.get('widget_place', 'host')
        widget_template = request.params.get('widget_template', 'host_widget')
        # Search in the application widgets (all plugins widgets)
        for widget in self.webui.get_widgets_for(widget_place):
            if widget_id.startswith(widget['id']):
                widget_template = widget['template']
                logger.info("Widget found, template: %s", widget_template)
                break
        else:
            logger.info("Widget identifier not found: using default template and no options")

        title = request.params.get('title', _('Host: %s') % host.name)

        # Use required template to render the widget
        return template('_widget', {
            'widget_id': widget_id,
            'widget_name': widget_template,
            'widget_place': 'host',
            'widget_template': widget_template,
            'widget_uri': request.urlparts.path,
            'options': {},

            'host': host,
            'services': services,
            'history': history,
            'timeline_pagination': self.webui.helper.get_pagination_control(
                '/host/' + host.id, total, start, count
            ),
            'types': history_types,
            'selected_types': selected_types,

            'title': title,
            'embedded': embedded,
            'identifier': identifier,
            'credentials': credentials
        })
