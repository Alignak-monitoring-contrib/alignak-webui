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
    Plugin Hosts
"""
from logging import getLogger

from copy import deepcopy

from bottle import request, template, response

from alignak_webui import _
from alignak_webui.utils.plugin import Plugin

logger = getLogger(__name__)


class PluginHosts(Plugin):
    """ Hosts plugin """

    def __init__(self, app, cfg_filenames=None):
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
                        'picture': 'htdocs/img/host_metrics_widget.png',
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
                        'picture': 'htdocs/img/host_timeline_widget.png',
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
                        'picture': 'htdocs/img/hosts_table_widget.png',
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
                        'picture': 'htdocs/img/hosts_chart_widget.png',
                        'options': {}
                    }
                ]
            },
        }

        super(PluginHosts, self).__init__(app, cfg_filenames)

    def get_hosts_widget(self, embedded=False, identifier=None, credentials=None):
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
        if count < 1:
            count = elts_per_page
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
        logger.debug("Widget search parameters: %s", search)

        # Get elements from the data manager
        hosts = datamgr.get_hosts(search)
        # Get last total elements count
        total = datamgr.get_objects_count('host', search=where, refresh=True)
        count = min(count, total)

        # Widget options
        widget_id = request.params.get('widget_id', '')
        if widget_id == '':
            return self.webui.response_invalid_parameters(_('Missing widget identifier'))

        widget_place = request.params.get('widget_place', 'dashboard')
        widget_template = request.params.get('widget_template', 'hosts/table_widget')
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

        new_options = deepcopy(options)
        logger.info("Widget options: %s", options)
        if options:
            new_options['search']['value'] = request.params.get('search', '')
            new_options['count']['value'] = request.params.get('count', elts_per_page)
            new_options['filter']['value'] = request.params.get('filter', '')
        if options != new_options:
            logger.info("Widget new options: %s", new_options)

            # Search for the dashboard widgets
            saved_widgets = datamgr.get_user_preferences(user, 'dashboard_widgets', [])
            for widget in saved_widgets:
                if widget_id.startswith(widget['id']):
                    widget['options'] = new_options
                    datamgr.set_user_preferences(user, 'dashboard_widgets', saved_widgets)
                    logger.info("Widget new options saved!")
                    break

        title = request.params.get('title', _('Hosts'))
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
            'hosts': hosts,
            'options': options,
            'save_options': options != new_options,
            'title': title,
            'embedded': embedded,
            'identifier': identifier,
            'credentials': credentials
        })

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
        services = datamgr.get_services(search={'where': {'host': host.id}})

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
        where = self.webui.helper.decode_search(request.params.get('search', ''))
        search = {
            'page': start // (count + 1),
            'max_results': count,
            'where': {'host': element_id}
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
        logger.warning("History selected types: %s", selected_types)

        # Get host history
        history = datamgr.get_history(search=search)
        if history is None:
            history = []
        # Get last total elements count
        total = datamgr.get_objects_count('history', search=where, refresh=True)

        # Get host events (all history except the events concerning the checks)
        excluded = [t for t in history_types if t.startswith('check.')]
        search = {
            'page': start // (count + 1),
            'max_results': count,
            'where': {'host': element_id, 'type': {'$nin': excluded}}
        }

        # Get host events
        events = datamgr.get_history(search=search)
        if events is None:
            events = []

        return {
            'host': host,
            'plugin_parameters': self.plugin_parameters,
            'services': services,
            # 'livestate': livestate,
            # 'livestate_services': livestate_services,
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
        Display an host
        """
        user = request.environ['beaker.session']['current_user']
        datamgr = request.app.datamgr

        # Get host
        host = datamgr.get_host(element_id)
        if not host:  # pragma: no cover, should not happen
            return self.webui.response_invalid_parameters(_('Host does not exist'))

        # Get host services
        services = datamgr.get_services(search={'where': {'host': element_id}})

        # Fetch elements per page preference for user, default is 25
        elts_per_page = datamgr.get_user_preferences(user, 'elts_per_page', 25)

        # Host history pagination and search parameters
        start = int(request.params.get('start', '0'))
        count = int(request.params.get('count', elts_per_page))
        where = self.webui.helper.decode_search(request.params.get('search', ''))
        search = {
            'where': {'host': element_id}
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

        if selected_types:
            datamgr.set_user_preferences(user, 'timeline_filters', selected_types)
            search['where'].update({'type': {'$in': selected_types}})
        logger.warning("History selected types: %s", selected_types)

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
                '/host/' + element_id, total, start, count
            ),
            'types': history_types,
            'selected_types': selected_types,

            'title': title,
            'embedded': embedded,
            'identifier': identifier,
            'credentials': credentials
        })
