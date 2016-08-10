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
    The plugin class is the base class of all the Web UI plugins.

    It provides base features for the application plugins:
    - register views and routes for the application
    - create lists for plugin widgets, tables, and lists
    - create a route endpoint for the plugin configuration
"""
import os
import json
from collections import OrderedDict

from logging import getLogger
from bottle import request, response, template, route, view
import bottle

from alignak_webui import _
from alignak_webui.utils.helper import Helper
from alignak_webui.utils.datatable import Datatable

# Settings
from alignak_webui.utils.settings import Settings

logger = getLogger(__name__)

# Will be populated by the UI with it's own value
webui = None


class Plugin(object):
    """ WebUI base plugin """

    def __init__(self, app, cfg_filenames=None):
        """
        Create a new plugin:
        """
        self.webui = app
        if not hasattr(self, 'name'):
            self.name = 'Unknown'
        if not hasattr(self, 'backend_endpoint'):
            self.backend_endpoint = None
        self.plugin_filenames = cfg_filenames
        self.plugin_parameters = None
        self.table = None

        # Store all the widgets, tables and lists declared by the plugin
        self.widgets = {}
        self.tables = {}
        self.lists = {}

        self.load_routes(bottle.app())

        if cfg_filenames:
            self.load_config()

    def load_routes(self, app):
        """
        Load and create plugin routes

        This function declares a config route if it is not yet declared.

        If the plugin manages a backend endpoint, this function declares routes for elements
        view, elements table, list and templates if they are not yet declared.

        Then, it creates the views and routes for the plugin in the main application, and store the
        widgets, tables and lists declared by the plugin.
        """
        if 'load_config' not in self.pages:
            self.pages.update({
                'load_config': {
                    'name': '%s plugin config' % self.name,
                    'route': '/%ss/config' % self.backend_endpoint
                }
            })

        if self.backend_endpoint:
            if 'get_one' not in self.pages:
                self.pages.update({
                    'get_one': {
                        'name': '%s' % self.name,
                        'route': '/%s/<element_id>' % self.backend_endpoint,
                        'view': '%s' % self.backend_endpoint,
                    }
                })

            if 'get_all' not in self.pages:
                self.pages.update({
                    'get_all': {
                        'name': 'All %s' % self.name,
                        'route': '/%ss' % self.backend_endpoint,
                        'view': '%ss' % self.backend_endpoint,
                    }
                })

            if 'get_tree' not in self.pages:
                self.pages.update({
                    'get_tree': {
                        'name': '%s tree' % self.name,
                        'route': '/%ss/tree' % self.backend_endpoint,
                        'view': '_tree',
                    }
                })

            if 'get_form' not in self.pages:
                self.pages.update({
                    'get_form': {
                        'name': '%s form' % self.name,
                        'route': '/%s/form/<element_id>' % self.backend_endpoint,
                        'view': '_form',
                    }
                })

            if 'get_table' not in self.pages:
                self.pages.update({
                    'get_table': {
                        'name': '%s table' % self.name,
                        'route': '/%ss/table' % self.backend_endpoint,
                        'view': '_table',
                        'tables': [
                            {
                                'id': '%ss_table' % self.backend_endpoint,
                                'for': ['external'],
                                'name': _('%s table' % self.name),
                                'template': '_table',
                                'icon': 'table',
                                'description': _(
                                    '<h4>%s table</h4>Displays a data table for the '
                                    'system %ss.<br>' % (
                                        self.name, self.backend_endpoint
                                    )
                                ),
                                'actions': {
                                    '%ss/table_data' % self.backend_endpoint: 'get_table_data'
                                }
                            }
                        ]
                    }
                })

            if 'get_table_data' not in self.pages:
                self.pages.update({
                    'get_table_data': {
                        'name': '%s table data' % self.name,
                        'route': '/%ss/table_data' % self.backend_endpoint,
                        'method': 'POST'
                    }
                })

            if 'get_list' not in self.pages:
                self.pages.update({
                    'get_list': {
                        'name': '%s list' % self.name,
                        'route': '/%ss/list' % self.backend_endpoint
                    }
                })

            if 'get_templates' not in self.pages:
                self.pages.update({
                    'get_templates': {
                        'name': '%s templates' % self.name,
                        'route': '/%ss/templates' % self.backend_endpoint
                    }
                })

        for (f_name, entry) in self.pages.items():
            logger.debug("page entry: %s -> %s", entry, f_name)
            f = getattr(self, f_name, None)
            if not callable(f):
                logger.error("Callable method: %s does not exist!", f_name)
                continue

            # Important: always apply the view before the route!
            if entry.get('view', None):
                f = view(entry.get('view'))(f)

            page_route = entry.get('route', None)
            if not page_route:
                page_route = entry.get('routes', None)
            page_name = entry.get('name', None)
            if not page_route:
                # Maybe there is no route to link, so pass
                continue

            methods = entry.get('method', 'GET')

            # Routes are an array of tuples [(route, name), ...]
            route_url = ''
            if not isinstance(page_route, list):
                page_route = [(page_route, page_name)]

            for route_url, name in page_route:
                f = app.route(
                    route_url, callback=f, method=methods, name=name,
                    search_engine=entry.get('search_engine', False),
                    search_prefix=entry.get('search_prefix', ''),
                    search_filters=entry.get('search_filters', {})
                )

                # Register plugin element list route
                if route_url == ('/%ss_list' % self.backend_endpoint):
                    self.lists['%ss_list' % self.backend_endpoint] = {
                        'id': self.backend_endpoint,
                        'base_uri': route_url,
                        'function': f
                    }
                    logger.info(
                        "Found list '%s' for %s", route_url, self.backend_endpoint
                    )

            if 'widgets' in entry:
                for widget in entry.get('widgets'):
                    # It's a valid widget entry if it got all data, and at least one route
                    if 'id' not in widget or 'for' not in widget:
                        continue
                    if 'name' not in widget or 'description' not in widget:
                        continue
                    if 'template' not in widget or not page_route:
                        continue

                    for place in widget['for']:
                        if place not in self.widgets:
                            self.widgets[place] = []
                        self.widgets[place].append({
                            'id': widget['id'],
                            'name': widget['name'],
                            'description': widget['description'],
                            'template': widget['template'],
                            'icon': widget.get('icon', 'leaf'),
                            'read_only': widget.get('read_only', False),
                            'options': widget.get('options', None),
                            'picture': os.path.join(
                                os.path.join('/static/plugins/', self.name.lower()),
                                widget.get('picture', '')
                            ),
                            'base_uri': route_url,
                            'function': f
                        })
                        logger.info(
                            "Found widget '%s' for %s", widget['id'], place
                        )

            if 'tables' in entry:
                for table in entry.get('tables'):
                    # It's a valid table entry if it got all data, and at least one route
                    if 'id' not in table or 'for' not in table:
                        continue
                    if 'name' not in table or 'description' not in table:
                        continue
                    if 'template' not in table or not page_route:
                        continue

                    for place in table['for']:
                        if place not in self.tables:
                            self.tables[place] = []
                        table_dict = {
                            'id': table['id'],
                            'name': table['name'],
                            'description': table['description'],
                            'template': table['template'],
                            'icon': table.get('icon', 'leaf'),
                            'base_uri': page_route,
                            'function': f,
                            'actions': {}
                        }
                        for action, f_name in table.get('actions', {}).items():
                            f = getattr(self, f_name, None)
                            if not callable(f):
                                logger.error("Table action method: %s does not exist!", f_name)
                                continue

                            table_dict['actions'].update({
                                action: f
                            })
                        self.tables[place].append(table_dict)
                        logger.info(
                            "Found table '%s' for %s", table['id'], place
                        )

    def load_config(self, cfg_filenames=None):
        """
        Load plugin configuration

        The list of files to search for is provided in the `cfg_filenames` parameter. If this
        parameter is None, then the list stored in the `plugin_filenames` attribute is used.

        All the content of the configuration files found is stored in the `plugin_parameters`
        attribute.

        The `table` attribute  is initialized with the content of the [table] and [table.field]
        variables.
        """
        if not cfg_filenames:
            cfg_filenames = self.plugin_filenames
        else:
            self.plugin_filenames = cfg_filenames

        logger.info("Read plugin configuration file: %s", cfg_filenames)

        # Read configuration file
        self.plugin_parameters = Settings(cfg_filenames)
        config_file = self.plugin_parameters.read('hosts')
        logger.info("Plugin configuration read from: %s", config_file)
        if not self.plugin_parameters:
            response.status = 204
            response.content_type = 'application/json'
            return json.dumps({'error': 'No configuration found'})

        self.table = OrderedDict()
        for param in self.plugin_parameters:
            p = param.split('.')
            if p[0] not in ['table']:
                continue
            if len(p) < 3:
                # Table global configuration [self.table]
                logger.debug(
                    "table global configuration: %s = %s",
                    param, self.plugin_parameters[param]
                )
                if '_table' not in self.table:
                    self.table['_table'] = {}
                self.table['_table'][p[1]] = self.plugin_parameters[param]
                continue

            # Table field configuration [self.table.field]
            if p[1] not in self.table:
                self.table[p[1]] = {}
            self.table[p[1]][p[2]] = self.plugin_parameters[param]
            logger.debug(
                "self.table field configuration: %s = %s", param, self.plugin_parameters[param]
            )

        response.status = 200
        response.content_type = 'application/json'
        return json.dumps(self.plugin_parameters)

    def get_one(self):
        """
            Show one element
        """
        datamgr = request.environ['beaker.session']['datamanager']

        # Get elements from the data manager
        f = getattr(datamgr, 'get_%s' % self.backend_endpoint)
        if not f:
            response.status = 204
            response.content_type = 'application/json'
            return json.dumps(
                {'error': 'No method available to get a %s element' % self.backend_endpoint}
            )

        element = f(element_id)
        if not element:
            element = f(search={'max_results': 1, 'where': {'name': element_id}})
            if not element:
                return webui.response_invalid_parameters(_('Element does not exist: %s')
                                                         % element_id)

        # Build table structure and data model
        dt = Datatable(self.backend_endpoint, datamgr, self.table)

        return {
            'object_type': self.backend_endpoint,
            'dt': dt,
            'element': element
        }

    def get_all(self):
        """
            Show all elements on one page
        """
        user = request.environ['beaker.session']['current_user']
        target_user = request.environ['beaker.session']['target_user']
        datamgr = request.environ['beaker.session']['datamanager']

        username = user.get_username()
        if not target_user.is_anonymous():
            username = target_user.get_username()

        # Fetch elements per page preference for user, default is 25
        elts_per_page = datamgr.get_user_preferences(username, 'elts_per_page', 25)
        # elts_per_page = elts_per_page['value']

        # Pagination and search
        start = int(request.query.get('start', '0'))
        count = int(request.query.get('count', elts_per_page))
        where = Helper.decode_search(request.query.get('search', ''))
        search = {
            'page': start // (count + 1),
            'max_results': count,
            'where': where
        }

        # Get elements from the data manager
        f = getattr(datamgr, 'get_%ss' % self.backend_endpoint)
        if not f:
            response.status = 204
            response.content_type = 'application/json'
            return json.dumps(
                {'error': 'No method available to get %s elements' % self.backend_endpoint}
            )

        elts = f(search, all_elements=True)

        # Get last total elements count
        total = datamgr.get_objects_count(
            self.backend_endpoint, search=where, refresh=True
        )
        count = min(count, total)

        return {
            'elts': elts,
            'pagination': Helper.get_pagination_control(
                '/%ss' % self.backend_endpoint, total, start, count
            ),
            'title': request.query.get('title', _('All %ss') % self.backend_endpoint)
        }

    def get_tree(self):
        """
            Show list of elements
        """
        user = request.environ['beaker.session']['current_user']
        target_user = request.environ['beaker.session']['target_user']
        datamgr = request.environ['beaker.session']['datamanager']

        username = user.get_username()
        if not target_user.is_anonymous():
            username = target_user.get_username()

        # Fetch elements per page preference for user, default is 25
        elts_per_page = datamgr.get_user_preferences(username, 'elts_per_page', 25)
        # elts_per_page = elts_per_page['value']

        # Pagination and search
        start = int(request.query.get('start', '0'))
        count = int(request.query.get('count', elts_per_page))
        where = Helper.decode_search(request.query.get('search', ''))
        search = {
            'page': start // (count + 1),
            'max_results': count,
            'where': where
        }

        # Get elements from the data manager
        f = getattr(datamgr, 'get_%ss' % self.backend_endpoint)
        if not f:
            response.status = 204
            response.content_type = 'application/json'
            return json.dumps(
                {'error': 'No method available to get %s elements' % self.backend_endpoint}
            )

        elts = f(search, all_elements=True)

        # Get last total elements count
        total = datamgr.get_objects_count(
            self.backend_endpoint, search=where, refresh=True
        )
        count = min(count, total)

        # Define contextual menu
        context_menu = {
            'actions': {
                'action1': {
                    "label": _('Fake action 1'),
                    "icon": "ion-monitor",
                    "separator_before": False,
                    "separator_after": True,
                    "action": '''
                        function (obj) {
                            console.log('Fake action 1');
                        }
                    '''
                },
                'action2': {
                    "label": _('Fake action 2!'),
                    "icon": "ion-monitor",
                    "separator_before": False,
                    "separator_after": False,
                    "action": '''function (obj) {
                       console.log('Fake action 2');
                    }'''
                }
            }
        }

        return {
            'tree_type': self.backend_endpoint,
            'elts': elts,
            'context_menu': context_menu,
            'pagination': Helper.get_pagination_control(
                '/%ss' % self.backend_endpoint, total, start, count
            ),
            'title': request.query.get('title', _('All %ss') % self.backend_endpoint)
        }

    def get_form(self, element_id):
        """
        Build the object_type table and get data to populate the table
        """
        datamgr = request.environ['beaker.session']['datamanager']

        # Get elements from the data manager
        f = getattr(datamgr, 'get_%s' % self.backend_endpoint)
        if not f:
            response.status = 204
            response.content_type = 'application/json'
            return json.dumps(
                {'error': 'No method available to get a %s element' % self.backend_endpoint}
            )

        element = f(element_id)
        if not element:
            element = f(search={'max_results': 1, 'where': {'name': element_id}})
            if not element:
                return webui.response_invalid_parameters(_('Element does not exist: %s')
                                                         % element_id)

        # Build table structure and data model
        dt = Datatable(self.backend_endpoint, datamgr, self.table)

        return {
            'object_type': self.backend_endpoint,
            'dt': dt,
            'element': element
        }

    def get_table(self, embedded=False, identifier=None, credentials=None):
        """
        Build the object_type table and get data to populate the table
        """
        datamgr = request.environ['beaker.session']['datamanager']

        # Table filtering: default is to restore the table saved filters
        where = {'saved_filters': True}
        if request.query.get('search') is not None:
            where = Helper.decode_search(request.query.get('search', ''))

        # Get total elements count
        # total = datamgr.get_objects_count(object_type, search=where, refresh=True)

        # Build table structure
        dt = Datatable(self.backend_endpoint, datamgr, self.table)

        # Build page title
        title = dt.title
        if '%d' in title:
            title = title % dt.records_total

        return {
            'object_type': self.backend_endpoint,
            'dt': dt,
            'where': where,
            'title': request.query.get('title', title),
            'embedded': embedded,
            'identifier': identifier,
            'credentials': credentials
        }

    def get_table_data(self):
        """
        Get the table data (requested from the table)
        """
        datamgr = request.environ['beaker.session']['datamanager']
        dt = Datatable(self.backend_endpoint, datamgr, self.table)

        response.status = 200
        response.content_type = 'application/json'
        return dt.table_data()

    def get_templates(self, embedded=False):
        # pylint: disable=unused-argument
        """
        Get the elements templates list

        Returns a JSON list containing, for each template, its id, name and alias
        """
        return self.get_list(templates=True, embedded=embedded)

    def get_list(self, templates=None, embedded=False):
        # pylint: disable=unused-argument
        """
        Get the elements list

        Returns a JSON list containing, for each item, its id, name and alias
        """
        datamgr = request.environ['beaker.session']['datamanager']

        # Get elements from the data manager
        f = getattr(datamgr, 'get_%ss' % self.backend_endpoint)
        if not f:
            response.status = 204
            response.content_type = 'application/json'
            return json.dumps(
                {'error': 'No method available to get %s elements' % self.backend_endpoint}
            )

        search = {
            'projection': json.dumps({"_id": 1, "name": 1, "alias": 1})
        }
        if templates is not None:
            search['where'] = {'_is_template': templates}
        elts = f(search, all_elements=True)

        items = []
        for elt in elts:
            items.append({'id': elt.id, 'name': elt.name, 'alias': elt.alias})

        response.status = 200
        response.content_type = 'application/json'
        return json.dumps(items)

    def get_widget(self, get_method, object_type,
                   embedded=False, identifier=None, credentials=None):
        # Because there are many locals needed :)
        # pylint: disable=too-many-locals, too-many-arguments
        """
        Get a widget...
        - get_methode is the datamanager method to call to get elements
        - object_type is the elements type

        - widget_id: widget identifier

        - start and count for pagination
        - search for specific elements search

        """
        user = request.environ['beaker.session']['current_user']
        datamgr = request.environ['beaker.session']['datamanager']
        target_user = request.environ['beaker.session']['target_user']

        username = user.get_username()
        if not target_user.is_anonymous():
            username = target_user.get_username()

        # Fetch elements per page preference for user, default is 25
        elts_per_page = datamgr.get_user_preferences(username, 'elts_per_page', 25)
        # elts_per_page = elts_per_page['value']

        # Pagination and search
        start = int(request.params.get('start', '0'))
        count = int(request.params.get('count', elts_per_page))
        where = webui.helper.decode_search(request.params.get('search', ''))
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
        elements = get_method(search)
        # Get last total elements count
        total = datamgr.get_objects_count(object_type, search=where, refresh=True)
        count = min(count, total)

        # Widget options
        widget_id = request.params.get('widget_id', '')
        if widget_id == '':
            return webui.response_invalid_parameters(_('Missing widget identifier'))

        widget_place = request.params.get('widget_place', 'dashboard')
        widget_template = request.params.get('widget_template', 'elements_table_widget')
        widget_icon = request.params.get('widget_icon', 'plug')
        # Search in the application widgets (all plugins widgets)
        options = {}
        for widget in webui.widgets[widget_place]:
            if widget_id.startswith(widget['id']):
                options = widget['options']
                widget_template = widget['template']
                widget_icon = widget['icon']
                logger.info("Widget found, template: %s, options: %s", widget_template, options)
                break
        else:
            logger.warning("Widget identifier not found: %s", widget_id)
            return webui.response_invalid_parameters(_('Unknown widget identifier'))

        if options:
            options['search']['value'] = request.params.get('search', '')
            options['count']['value'] = count
            options['filter']['value'] = name_filter
        logger.info("Widget options: %s", options)

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
            'elements': elements,
            'options': options,
            'title': title,
            'embedded': embedded,
            'identifier': identifier,
            'credentials': credentials
        })
