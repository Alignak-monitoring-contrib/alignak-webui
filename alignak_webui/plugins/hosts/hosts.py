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

    def __init__(self, webui, plugin_dir, cfg_filenames=None):
        """
        Hosts plugin

        Overload the default get route to declare filters.
        """
        self.name = 'Hosts'
        self.backend_endpoint = 'host'

        self.pages = {
            'get_all_templates': {
                'name': 'All %s templates' % self.name,
                'route': '/%ss/templates' % self.backend_endpoint,
                'view': '%ss_templates' % self.backend_endpoint,
            },
            'get_host_view': {
                'name': 'Host synthesis view widget',
                'route': '/host_view/<element_id>',
                'view': 'host',
                'widgets': [
                    {
                        'id': 'view',
                        'for': ['host'],
                        'order': 1,
                        'name': _('Main view'),
                        'template': 'host_view_widget',
                        'icon': 'server',
                        'read_only': True,
                        'description': _('Host synthesis: displays host synthesis view.'),
                        'options': {}
                    },
                ]
            },
            'get_host_information': {
                'name': 'Host information widget',
                'route': '/host_information/<element_id>',
                'view': 'host',
                'widgets': [
                    {
                        'id': 'information',
                        'for': ['host'],
                        'order': 2,
                        'name': _('information'),
                        'template': 'host_information_widget',
                        'icon': 'info',
                        'read_only': True,
                        'description': _('Host information: displays host general information.'),
                        'options': {}
                    },
                ]
            },
            'get_host_configuration': {
                'name': 'Host configuration widget',
                'route': '/host_configuration/<element_id>',
                'view': 'host',
                'widgets': [
                    {
                        'id': 'configuration',
                        'for': ['host'],
                        'order': 3,
                        'name': _('Configuration'),
                        'level': 1,
                        'template': 'host_configuration_widget',
                        'icon': 'gear',
                        'read_only': True,
                        'description': _('Host configuration: '
                                         'displays host customs configuration variables.'),
                        'options': {}
                    },
                ]
            },
            'get_host_location': {
                'name': 'Host location widget',
                'route': '/host_location/<element_id>',
                'view': 'host',
                'widgets': [
                    {
                        'id': 'location',
                        'for': ['host'],
                        'order': 4,
                        'name': _('Location'),
                        'template': 'host_location_widget',
                        'icon': 'globe',
                        'read_only': True,
                        'description': _('Host location: displays host position on a map.'),
                        'options': {}
                    },
                ]
            },
            'get_host_services': {
                'name': 'Host services widget',
                'route': '/host_services/<element_id>',
                'view': 'host',
                'widgets': [
                    {
                        'id': 'services',
                        'for': ['host'],
                        'order': 5,
                        'name': _('Services'),
                        'level': 1,
                        'template': 'host_services_widget',
                        'icon': 'cubes',
                        'read_only': True,
                        'description': _('Host services: displays host services states.'),
                        'options': {}
                    },
                ]
            },
            'get_host_metrics': {
                'name': 'Host metrics widget',
                'route': '/host_metrics/<element_id>',
                'view': 'host',
                'widgets': [
                    {
                        'id': 'metrics',
                        'for': ['host'],
                        'order': 6,
                        'name': _('Metrics'),
                        'level': 1,
                        'template': 'host_metrics_widget',
                        'icon': 'calculator',
                        'read_only': True,
                        'description': _('Host metrics: displays host (and its services) '
                                         'last received metrics.'),
                        'options': {}
                    },
                ]
            },
            'get_host_timeline': {
                'name': 'Host timeline widget',
                'route': '/host_timeline/<element_id>',
                'view': 'host',
                'widgets': [
                    {
                        'id': 'timeline',
                        'for': ['host'],
                        'order': 7,
                        'name': _('Timeline'),
                        'level': 1,
                        'template': 'host_timeline_widget',
                        'icon': 'clock-o',
                        'read_only': True,
                        'description': _('Host timeline: displays host events on a timeline.'),
                        'options': {}
                    },
                ]
            },
            'get_host_history': {
                'name': 'Host history widget',
                'route': '/host_history/<element_id>',
                'view': 'host',
                'widgets': [
                    {
                        'id': 'history',
                        'for': ['host'],
                        'order': 8,
                        'name': _('History'),
                        'level': 1,
                        'template': 'host_history_widget',
                        'icon': 'history',
                        'read_only': True,
                        'description': _('Host metrics: displays host history.'),
                        'options': {}
                    },
                ]
            },
            'get_host_events': {
                'name': 'Host events widget',
                'route': '/host_events/<element_id>',
                'view': 'host',
                'widgets': [
                    {
                        'id': 'events',
                        'for': ['host'],
                        'order': 9,
                        'name': _('Events'),
                        'level': 1,
                        'template': 'host_events_widget',
                        'icon': 'calendar',
                        'read_only': True,
                        'description': _('Host metrics: displays host events: '
                                         'comments, acknowledges, downtimes,...'),
                        'options': {}
                    },
                ]
            },
            'get_host_grafana': {
                'name': 'Host grafana widget',
                'route': '/host_grafana/<element_id>',
                'view': 'host',
                'widgets': [
                    {
                        'id': 'grafana',
                        'for': ['host'],
                        'order': 9,
                        'name': _('Grafana'),
                        'level': 1,
                        'template': 'host_grafana_widget',
                        'icon': 'line-chart',
                        'read_only': True,
                        'description': _('Host metrics: displays host Grafana panel.'),
                        'options': {}
                    },
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

        super(PluginHosts, self).__init__(webui, plugin_dir, cfg_filenames)

        self.search_engine = True
        self.search_filters = {
            '01': (_('Ok'), 'is:ok'),
            '02': (_('Acknowledged'), 'is:acknowledged'),
            '03': (_('Downtimed'), 'is:in_downtime'),
            '04': (_('Warning'), 'is:warning'),
            '05': (_('Critical'), 'is:critical'),
            '06': ('', ''),
            '07': (_('Up'), 'ls_state:UP'),
            '08': (_('Down'), 'ls_state:DOWN'),
            '09': (_('Unreachable'), 'ls_state:UNREACHABLE'),
        }

    def get_hosts_widget(self, embedded=False, identifier=None, credentials=None):
        """Get the hosts widget"""
        return self.get_widget(None, 'host', embedded, identifier, credentials)

    def get_all_templates(self):
        """Get all the hosts templates"""
        user = request.environ['beaker.session']['current_user']
        edition_mode = request.environ['beaker.session']['edition_mode']
        if not edition_mode:
            self.send_user_message(_("You must activate edition mode to view this page"),
                                   redirected=True)
        if not user.can_edit_configuration():
            logger.warning("Current user '%s' is not authorized to view this page",
                           user.get_username())
            self.send_user_message(_("Not authorized to view this page"), redirected=True)

        return self.get_all(templates=True, all_elements=True)

    def get_one(self, element_id):
        # Because there are many locals needed :)
        # pylint: disable=too-many-locals
        """Display an host"""
        logger.info("Get one host: %s", element_id)
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

        # Get host dependencies
        children = datamgr.get_hostdependencys(search={'where': {'hosts': host.id}})
        parents = datamgr.get_hostdependencys(search={'where': {'dependent_hosts': host.id}})

        return {
            'plugin': self,
            'plugin_parameters': self.plugin_parameters,

            'host': host,
            'services': services,
            'parents': parents,
            'children': children,
            'title': request.params.get('title', _('Host view: %s' % host.alias))
        }

    def get_host_simple_widget(self, element_id, widget_id=None,
                               embedded=False, identifier=None, credentials=None):
        """Display a generic host widget"""
        datamgr = request.app.datamgr

        logger.debug("get_host_simple_widget: %s, %s", element_id, widget_id)

        # Get host
        host = datamgr.get_host(element_id)
        if not host:
            # Test if we got a name instead of an id
            host = datamgr.get_host(search={'max_results': 1, 'where': {'name': element_id}})
            if not host:
                return self.webui.response_invalid_parameters(_('Host does not exist'))

        widget_place = request.params.get('widget_place', 'host')
        widget_template = request.params.get('widget_template', 'host_widget')
        # Search in the application widgets (all plugins widgets)
        for widget in self.webui.get_widgets_for(widget_place):
            if widget_id.startswith(widget['id']):
                widget_template = widget['template']
                logger.debug("Widget found, template: %s", widget_template)
                break
        else:
            logger.info("Widget identifier not found: using default template and no options")

        logger.debug("get_host_simple_widget: found template: %s", widget_template)

        # Render the widget
        return template('_widget', {
            'widget_id': widget_id,
            'widget_name': widget_template,
            'widget_place': 'user',
            'widget_template': widget_template,
            'widget_uri': request.urlparts.path,
            'options': {},

            'plugin': self,
            'plugin_parameters': self.plugin_parameters,

            'host': host,

            'title': None,
            'embedded': embedded,
            'identifier': identifier,
            'credentials': credentials
        })

    def get_host_view(self, element_id, widget_id='view',
                      embedded=False, identifier=None, credentials=None):
        # pylint: disable=unused-argument
        """Display an host main view widget"""
        return self.get_host_simple_widget(element_id, widget_id,
                                           embedded, identifier, credentials)

    def get_host_information(self, element_id, widget_id='information',
                             embedded=False, identifier=None, credentials=None):
        # pylint: disable=unused-argument
        """Display an host information widget"""
        return self.get_host_simple_widget(element_id, widget_id,
                                           embedded, identifier, credentials)

    def get_host_configuration(self, element_id, widget_id='configuration',
                               embedded=False, identifier=None, credentials=None):
        # pylint: disable=unused-argument
        """Display an host configuration widget"""
        return self.get_host_simple_widget(element_id, widget_id,
                                           embedded, identifier, credentials)

    def get_host_location(self, element_id, widget_id='location',
                          embedded=False, identifier=None, credentials=None):
        # pylint: disable=unused-argument
        """Display an host map location widget"""
        return self.get_host_simple_widget(element_id, widget_id,
                                           embedded, identifier, credentials)

    def get_host_services(self, element_id, widget_id='services',
                          embedded=False, identifier=None, credentials=None):
        # pylint: disable=unused-argument
        """Display an host map location widget"""
        return self.get_host_simple_widget(element_id, widget_id,
                                           embedded, identifier, credentials)

    def get_host_metrics(self, element_id, widget_id=None,
                         embedded=False, identifier=None, credentials=None):
        # pylint: disable=unused-argument
        """Display an host metrics widget"""
        return self.get_host_simple_widget(element_id, 'metrics',
                                           embedded, identifier, credentials)

    def get_host_timeline(self, element_id, widget_id='timeline',
                          embedded=False, identifier=None, credentials=None):
        # pylint: disable=unused-argument, too-many-locals
        """Display an host timeline widget"""
        user = request.environ['beaker.session']['current_user']
        datamgr = request.app.datamgr

        # Get the host
        host = datamgr.get_host(element_id)
        if not host:
            # Test if we got a name instead of an id
            host = datamgr.get_host(search={'max_results': 1, 'where': {'name': element_id}})
            if not host:
                return self.webui.response_invalid_parameters(_('Host does not exist'))

        # Search the required widget
        widget_place = request.params.get('widget_place', 'host')
        widget_template = request.params.get('widget_template', 'host_widget')
        # Search in the application widgets (all plugins widgets)
        for widget in self.webui.get_widgets_for(widget_place):
            if widget_id.startswith(widget['id']):
                widget_template = widget['template']
                logger.debug("Widget found, template: %s", widget_template)
                break
        else:
            logger.info("Widget identifier not found: using default template and no options")

        logger.debug("get_host_timeline: found template: %s", widget_template)

        # Fetch elements per page preference for user, default is 25
        elts_per_page = datamgr.get_user_preferences(user, 'elts_per_page', 25)

        # Host history pagination and search parameters
        start = int(request.params.get('start', '0'))
        count = int(request.params.get('count', elts_per_page))
        where = {'host': host.id}

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

        # Get host history
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

            'host': host,

            'history': history,
            'pagination': self.webui.helper.get_pagination_control(
                '/host/%s#host_%s' % (host.id, widget_id), total, start, count
            ),

            'title': None,
            'embedded': embedded,
            'identifier': identifier,
            'credentials': credentials
        })

    # def get_host_events(self, element_id, widget_id='events',
    #                     embedded=False, identifier=None, credentials=None):
    #     # pylint: disable=unused-argument, too-many-locals
    #     """Display an host events widget"""
    #     user = request.environ['beaker.session']['current_user']
    #     datamgr = request.app.datamgr
    #
    #     # Get host
    #     host = datamgr.get_host(element_id)
    #     if not host:
    #         # Test if we got a name instead of an id
    #         host = datamgr.get_host(search={'max_results': 1, 'where': {'name': element_id}})
    #         if not host:
    #             return self.webui.response_invalid_parameters(_('Host does not exist'))
    #
    #     widget_place = request.params.get('widget_place', 'host')
    #     widget_template = request.params.get('widget_template', 'host_widget')
    #     # Search in the application widgets (all plugins widgets)
    #     for widget in self.webui.get_widgets_for(widget_place):
    #         if widget_id.startswith(widget['id']):
    #             widget_template = widget['template']
    #             logger.info("Widget found, template: %s", widget_template)
    #             break
    #     else:
    #         logger.info("Widget identifier not found: using default template and no options")
    #
    #     logger.debug("get_host_events: found template: %s", widget_template)
    #
    #     # Fetch elements per page preference for user, default is 25
    #     elts_per_page = datamgr.get_user_preferences(user, 'elts_per_page', 25)
    #
    #     # Host history pagination and search parameters
    #     start = int(request.params.get('start', '0'))
    #     count = int(request.params.get('count', elts_per_page))
    #     where = Helper.decode_search(request.params.get('search', ''), self.table)
    #     search = {
    #         'page': (start // count) + 1,
    #         'max_results': count,
    #         'where': {'host': host.id}
    #     }
    #
    #     # Find known history types
    #     history_plugin = self.webui.find_plugin('Histories')
    #     history_types = []
    #     if history_plugin and 'type' in history_plugin.table:
    #         logger.debug("History types: %s", history_plugin.table['type'].get('allowed', []))
    #         history_types = history_plugin.table['type'].get('allowed', [])
    #         history_types = history_types.split(',')
    #
    #     # Fetch timeline filters preference for user, default is []
    #     selected_types = datamgr.get_user_preferences(user, 'timeline_filters', [])
    #     # selected_types = selected_types['value']
    #     for selected_type in history_types:
    #         if request.params.get(selected_type) == 'true':
    #             if selected_type not in selected_types:
    #                 selected_types.append(selected_type)
    #         elif request.params.get(selected_type) == 'false':
    #             if selected_type in selected_types:
    #                 selected_types.remove(selected_type)
    #
    #     datamgr.set_user_preferences(user, 'timeline_filters', selected_types)
    #     if selected_types:
    #         search['where'].update({'type': {'$in': selected_types}})
    #     logger.debug("History selected types: %s", selected_types)
    #
    #     # Get host events (all history except the events concerning the checks)
    #     excluded = [t for t in history_types if t.startswith('check.')]
    #     search = {
    #         'page': (start // count) + 1,
    #         'max_results': count,
    #         'where': {'host': host.id, 'type': {'$nin': excluded}}
    #     }
    #
    #     # Get host events
    #     events = datamgr.get_history(search=search)
    #     if events is None:
    #         events = []
    #
    #     # Get last total elements count
    #     total = datamgr.get_objects_count('history', search=where, refresh=True)
    #
    #     # Render the widget
    #     return template('_widget', {
    #         'widget_id': widget_id,
    #         'widget_name': widget_template,
    #         'widget_place': 'user',
    #         'widget_template': widget_template,
    #         'widget_uri': request.urlparts.path,
    #         'options': {},
    #
    #         'plugin_parameters': self.plugin_parameters,
    #
    #         'host': host,
    #
    #         'events': events,
    #         'timeline_pagination': self.webui.helper.get_pagination_control(
    #             '/host/' + host.id, total, start, count
    #         ),
    #         'types': history_types,
    #         'selected_types': selected_types,
    #
    #         'title': None,
    #         'embedded': embedded,
    #         'identifier': identifier,
    #         'credentials': credentials
    #     })
    #
    # def get_host_history(self, element_id, widget_id='history',
    #                      embedded=False, identifier=None, credentials=None):
    #     # pylint: disable=unused-argument, too-many-locals
    #     """Display an host timeline widget"""
    #     user = request.environ['beaker.session']['current_user']
    #     datamgr = request.app.datamgr
    #
    #     # Get host
    #     host = datamgr.get_host(element_id)
    #     if not host:
    #         # Test if we got a name instead of an id
    #         host = datamgr.get_host(search={'max_results': 1, 'where': {'name': element_id}})
    #         if not host:
    #             return self.webui.response_invalid_parameters(_('Host does not exist'))
    #
    #     widget_place = request.params.get('widget_place', 'host')
    #     widget_template = request.params.get('widget_template', 'host_widget')
    #     # Search in the application widgets (all plugins widgets)
    #     for widget in self.webui.get_widgets_for(widget_place):
    #         if widget_id.startswith(widget['id']):
    #             widget_template = widget['template']
    #             logger.info("Widget found, template: %s", widget_template)
    #             break
    #     else:
    #         logger.info("Widget identifier not found: using default template and no options")
    #
    #     logger.debug("get_host_history: found template: %s", widget_template)
    #
    #     # Fetch elements per page preference for user, default is 25
    #     elts_per_page = datamgr.get_user_preferences(user, 'elts_per_page', 25)
    #
    #     # Host history pagination and search parameters
    #     start = int(request.params.get('start', '0'))
    #     count = int(request.params.get('count', elts_per_page))
    #     where = Helper.decode_search(request.params.get('search', ''), self.table)
    #     search = {
    #         'page': (start // count) + 1,
    #         'max_results': count,
    #         'where': {'host': host.id}
    #     }
    #
    #     # Find known history types
    #     history_plugin = self.webui.find_plugin('Histories')
    #     history_types = []
    #     if history_plugin and 'type' in history_plugin.table:
    #         logger.debug("History types: %s", history_plugin.table['type'].get('allowed', []))
    #         history_types = history_plugin.table['type'].get('allowed', [])
    #         history_types = history_types.split(',')
    #
    #     # Fetch timeline filters preference for user, default is []
    #     selected_types = datamgr.get_user_preferences(user, 'timeline_filters', [])
    #     # selected_types = selected_types['value']
    #     for selected_type in history_types:
    #         if request.params.get(selected_type) == 'true':
    #             if selected_type not in selected_types:
    #                 selected_types.append(selected_type)
    #         elif request.params.get(selected_type) == 'false':
    #             if selected_type in selected_types:
    #                 selected_types.remove(selected_type)
    #
    #     datamgr.set_user_preferences(user, 'timeline_filters', selected_types)
    #     if selected_types:
    #         search['where'].update({'type': {'$in': selected_types}})
    #     logger.debug("History selected types: %s", selected_types)
    #
    #     # Get host history
    #     history = datamgr.get_history(search=search)
    #     if history is None:
    #         history = []
    #     total = 0
    #     if history:
    #         total = history[0]['_total']
    #
    #     # Render the widget
    #     return template('_widget', {
    #         'widget_id': widget_id,
    #         'widget_name': widget_template,
    #         'widget_place': 'user',
    #         'widget_template': widget_template,
    #         'widget_uri': request.urlparts.path,
    #         'options': {},
    #
    #         'plugin_parameters': self.plugin_parameters,
    #
    #         'host': host,
    #
    #         'history': history,
    #         'timeline_pagination': self.webui.helper.get_pagination_control(
    #             '/host/' + host.id, total, start, count
    #         ),
    #         'types': history_types,
    #         'selected_types': selected_types,
    #
    #         'title': None,
    #         'embedded': embedded,
    #         'identifier': identifier,
    #         'credentials': credentials
    #     })

    def get_host_grafana(self, element_id, widget_id='grafana',
                         embedded=False, identifier=None, credentials=None):
        # pylint: disable=unused-argument
        """Display an host grafana widget"""
        return self.get_host_simple_widget(element_id, widget_id,
                                           embedded, identifier, credentials)
