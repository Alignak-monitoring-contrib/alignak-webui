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
from bottle import request, response, template, view, redirect
import bottle

from alignak_webui import _
from alignak_webui.objects.element import BackendElement
from alignak_webui.objects.element_state import ElementState
from alignak_webui.utils.helper import Helper
from alignak_webui.utils.datatable import Datatable

# Settings
from alignak_webui.utils.settings import Settings

logger = getLogger(__name__)


class Plugin(object):
    """ WebUI base plugin """

    def __init__(self, app, cfg_filenames):
        """
        Create a new plugin:
        """
        self.webui = app
        if not hasattr(self, 'name'):  # pragma: no cover - plugin should declare
            self.name = 'Unknown'
        if not hasattr(self, 'backend_endpoint'):  # pragma: no cover - plugin should declare
            self.backend_endpoint = None
        self.plugin_filenames = cfg_filenames
        self.plugin_parameters = None
        self.table = None

        # Store all the widgets, tables and lists declared by the plugin
        self.widgets = {}
        self.tables = {}
        self.lists = {}

        self.configuration_loaded = self.load_config(initialization=True)
        if self.configuration_loaded and self.plugin_parameters.get('enabled', 'True') != 'True':
            logger.warning("Plugin %s is installed but disabled.", self.name)
            return

        self.load_routes(bottle.app())
        logger.info("Plugin %s is installed and enabled.", self.name)

    def send_user_message(self, message, status='ko'):
        """
        Send a user message:
        - store a message in the current session
        - redirects to the application home page
        """
        session = request.environ['beaker.session']
        session['user_message'] = {
            'status': status,
            'message': message
        }
        redirect('/')

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

            if 'update_form' not in self.pages:
                self.pages.update({
                    'update_form': {
                        'name': '%s form post' % self.name,
                        'route': '/%s/form/<element_id>' % self.backend_endpoint,
                        'method': 'POST'
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
            if not callable(f):  # pragma: no cover - method should exist
                logger.error("Callable method: %s does not exist!", f_name)
                continue

            # Important: always apply the view before the route!
            if entry.get('view', None):
                f = view(entry.get('view'))(f)

            page_route = entry.get('route', None)
            if not page_route:
                page_route = entry.get('routes', None)
            page_name = entry.get('name', None)
            if not page_route:  # pragma: no cover
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
                if route_url == ('/%ss/list' % self.backend_endpoint):
                    self.lists['%ss/list' % self.backend_endpoint] = {
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
                    if 'id' not in widget or 'for' not in widget:  # pragma: no cover
                        continue
                    if 'name' not in widget or 'description' not in widget:  # pragma: no cover
                        continue
                    if 'template' not in widget or not page_route:  # pragma: no cover
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
                    if 'id' not in table or 'for' not in table:  # pragma: no cover
                        continue
                    if 'name' not in table or 'description' not in table:  # pragma: no cover
                        continue
                    if 'template' not in table or not page_route:  # pragma: no cover
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
                            if not callable(f):  # pragma: no cover
                                logger.error("Table action method: %s does not exist!", f_name)
                                continue

                            table_dict['actions'].update({
                                action: f
                            })
                        self.tables[place].append(table_dict)
                        logger.info(
                            "Found table '%s' for %s", table['id'], place
                        )

    def load_config(self, cfg_filenames=None, initialization=False):
        """
        Load plugin configuration

        The list of files to search for is provided in the `cfg_filenames` parameter. If this
        parameter is None, then the list stored in the `plugin_filenames` attribute is used.

        All the content of the configuration files found is stored in the `plugin_parameters`
        attribute.

        The `table` attribute  is initialized with the content of the [table] and [table.field]
        variables.

        When the initialization parameter is set, the function returns True / False instead of a
        JSON formatted response.
        """
        if not cfg_filenames:
            cfg_filenames = self.plugin_filenames
        else:
            self.plugin_filenames = cfg_filenames

        logger.debug("Read plugin configuration file: %s", cfg_filenames)

        # Read configuration file
        self.plugin_parameters = Settings(cfg_filenames)
        config_file = self.plugin_parameters.read(self.name)
        logger.debug("Plugin configuration read from: %s", config_file)
        if not self.plugin_parameters:
            if initialization:
                return False
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
                "table field configuration: %s = %s", param, self.plugin_parameters[param]
            )

        if initialization:
            return True
        response.status = 200
        response.content_type = 'application/json'
        return json.dumps(self.plugin_parameters)

    def get_one(self, element_id):
        """
            Show one element
        """
        datamgr = request.app.datamgr

        # Get elements from the data manager
        f = getattr(datamgr, 'get_%s' % self.backend_endpoint)
        if not f:
            self.send_user_message(_("No method to get a %s element") % self.backend_endpoint)

        logger.debug("get_one, search: %s", element_id)
        element = f(element_id)
        if not element:
            element = f(search={'max_results': 1, 'where': {'name': element_id}})
            if not element:
                self.send_user_message(_("%s '%s' not found") % (self.backend_endpoint, element_id))
        logger.debug("get_one, found: %s - %s", element, element.__dict__)

        return {
            'object_type': self.backend_endpoint,
            'element': element
        }

    def get_all(self):
        """
            Show all elements on one page
        """
        user = request.environ['beaker.session']['current_user']
        datamgr = request.app.datamgr

        # Get elements get method from the data manager
        f = getattr(datamgr, 'get_%ss' % self.backend_endpoint)
        if not f:
            self.send_user_message(_("No method to get a %s element") % self.backend_endpoint)

        # Fetch elements per page preference for user, default is 25
        elts_per_page = datamgr.get_user_preferences(user, 'elts_per_page', 25)

        # Pagination and search
        start = int(request.query.get('start', '0'))
        count = int(request.query.get('count', elts_per_page))
        where = Helper.decode_search(request.query.get('search', ''))
        search = {
            'page': (start // count) + 1,
            'max_results': count,
            'where': where
        }

        logger.debug("get_all, search: %s", search)
        elts = f(search, all_elements=False)

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
        # Because the fields are named as _parent and _level ...
        # pylint: disable=protected-access, too-many-locals
        """
            Show list of elements
        """
        user = request.environ['beaker.session']['current_user']
        datamgr = request.app.datamgr

        # Fetch elements per page preference for user, default is 25
        elts_per_page = datamgr.get_user_preferences(user, 'elts_per_page', 25)

        # Pagination and search
        start = int(request.query.get('start', '0'))
        count = int(request.query.get('count', elts_per_page))
        where = Helper.decode_search(request.query.get('search', ''))
        search = {
            'page': (start // count) + 1,
            'max_results': count,
            'where': where
        }

        # Get elements from the data manager
        f = getattr(datamgr, 'get_%ss' % self.backend_endpoint)
        if not f:
            self.send_user_message(_("No method to get a %s element") % self.backend_endpoint)

        elts = f(search, all_elements=False)

        # Get last total elements count
        total = datamgr.get_objects_count(
            self.backend_endpoint, search=where, refresh=True
        )

        # Get elements from the data manager
        f_get_overall_state = getattr(self, 'get_overall_state', None)

        # Get element state configuration
        items_states = ElementState()

        tree_items = []
        for item in elts:
            overall_status = 'unknown'
            if f_get_overall_state:
                (dummy, overall_status) = f_get_overall_state(element=item)

            cfg_state = items_states.get_icon_state(self.backend_endpoint, overall_status)
            logger.debug("Item state: %s", cfg_state)
            if not cfg_state:
                cfg_state = {'icon': 'life-ring', 'class': 'unknown'}
            # icon = cfg_state['icon']

            parent = '#'
            if item._parent and not isinstance(item._parent, basestring):
                parent = item['_parent'].id
            # logger.debug("Item parent: %s", parent)

            tree_item = {
                'id': item.id,
                'parent': '#' if parent == '#' else item._parent.id,
                'text': item.alias,
                'icon': 'fa fa-%s item_%s' % (cfg_state['icon'], cfg_state['class']),
                'state': {
                    "opened": True,
                    "selected": False,
                    "disabled": False
                },
                'data': {
                    'status': overall_status,
                    'name': item.name,
                    'alias': item.alias,
                    '_level': item._level,
                    'type': self.backend_endpoint,
                },
                # 'li_attr': {
                # "item_id": item.id,
                # The result with a class to color the lines is not very nice :/
                # "class" : "table-row-%s" % (overall_state)
                # },
                'a_attr': {}
            }

            if parent == '#':
                tree_item.update({'parent': parent})
                tree_item.update({'type': 'root'})
                # tree_item.update({'icon': 'fa fa-w fa-sitemap'})
            else:
                tree_item.update({'parent': item._parent.id})
                tree_item.update({'type': 'node'})
                # tree_item.update({'icon': 'fa fa-w fa-list'})

            tree_items.append(tree_item)

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
            'tree_items': tree_items,
            'elts': elts,
            'context_menu': context_menu,
            'pagination': Helper.get_pagination_control(
                '/%ss' % self.backend_endpoint, total, start, count
            ),
            'title': request.query.get('title', _('All %ss') % self.backend_endpoint)
        }

    def get_status(self, element_id=None, element=None):
        """
        Get the element overall status
        """
        datamgr = request.app.datamgr

        if not element:
            if not element_id:
                self.send_user_message(
                    _("Missing identifier for '%s'") % (self.backend_endpoint)
                )

            # Get elements from the data manager
            f = getattr(datamgr, 'get_%s' % self.backend_endpoint)
            if not f:
                self.send_user_message(_("No method to get a %s element") % self.backend_endpoint)

            logger.debug("get_status, search: %s", element_id)
            element = f(element_id)
            if not element:
                element = f(search={'max_results': 1, 'where': {'name': element_id}})
                if not element:
                    self.send_user_message(
                        _("%s '%s' not found") % (self.backend_endpoint, element_id)
                    )
            logger.debug("get_status, found: %s - %s", element, element.__dict__)

        group_state = 0
        for host in element.members:
            logger.debug("Group member: %s", host)

            # Get host services
            services = datamgr.get_services(search={'where': {'host': host.id}})

            # Get host overall state (0, 1, 2, 3)
            state = host.get_overall_state(services)
            group_state = max(state, group_state)

        logger.debug("Group state: %d", group_state)

        response.status = 200
        response.content_type = 'application/json'
        return json.dumps({'status': group_state})

    def get_form(self, element_id):
        """
            Build the form for an element.

            element_id is the _id (or name) of an object to read. If no object is found then an
            empty element is sent to the form which means a new object creation with default values.
        """
        datamgr = request.app.datamgr

        # Get element get method from the data manager
        f = getattr(datamgr, 'get_%s' % self.backend_endpoint)
        if not f:
            self.send_user_message(_("No method to get a %s element") % self.backend_endpoint)

        # Get element from the data manager
        element = f(element_id)
        if not element:
            element = f(search={
                'max_results': 1, 'where': {'name': element_id}
            })
            if not element:
                element = f(search={
                    'max_results': 1, 'where': {'_id': element_id, '_is_template': False}
                })
                if not element:
                    element = f(search={
                        'max_results': 1, 'where': {'name': element_id, '_is_template': False}
                    })
                    if not element:
                        element = f(search={
                            'max_results': 1, 'where': {'_id': element_id, '_is_template': True}
                        })
                        if not element:
                            element = f(search={
                                'max_results': 1, 'where': {
                                    'name': element_id, '_is_template': True
                                }
                            })
                            # If not found, element will remain as None to create a new element

        return {
            'plugin': self,
            'element': element
        }

    def update_form(self, element_id):
        # pylint: disable=too-many-locals, not-an-iterable, redefined-variable-type
        """
            Update an element

            If element_id is string 'None' then it is a new object creation, else element_id is the
            _id (or name) of an object to update.
        """
        datamgr = request.app.datamgr

        create = (element_id == 'None')

        # Get element get method from the data manager
        f = getattr(datamgr, 'get_%s' % self.backend_endpoint)
        if not f:
            self.send_user_message(_("No method to get a %s element") % self.backend_endpoint)

        # For an object update...
        if not create:
            # Get element from the data manager
            element = f(element_id)
            if not element:
                element = f(search={
                    'max_results': 1, 'where': {'name': element_id}
                })
                if not element:
                    element = f(search={
                        'max_results': 1, 'where': {'_id': element_id, '_is_template': True}
                    })
                    if not element:
                        element = f(search={
                            'max_results': 1, 'where': {'name': element_id, '_is_template': True}
                        })
                        if not element:
                            self.send_user_message(
                                _("%s '%s' not found") % (self.backend_endpoint, element_id)
                            )

        # Prepare update request ...
        data = {}
        for field in request.forms:
            update = False
            value = request.forms.get(field)
            field_type = self.table[field].get('type')
            logger.debug(
                "- posted field: %s (%s) = %s", field, field_type, request.forms.get(field)
            )

            if field_type == 'objectid':
                if not value:
                    value = None
            elif field_type == 'boolean':
                value = (request.forms.get(field) == 'true')
            elif field_type == 'integer':
                value = int(request.forms.get(field))
            elif field_type == 'float':
                value = float(request.forms.get(field))
            elif field_type == 'point':
                value = request.forms.getall(field)
                dict_values = {}
                for item in value:
                    splitted = item.split('|')
                    dict_values.update({splitted[0].decode('utf8'): splitted[1].decode('utf8')})
                value = {
                    u'type': u'Point',
                    u'coordinates': [
                        float(dict_values['latitude']),
                        float(dict_values['longitude'])
                    ]
                }
            elif field_type == 'dict':
                value = request.forms.getall(field)
                dict_values = {}
                for item in value:
                    splitted = item.split('|')
                    dict_values.update({splitted[0].decode('utf8'): splitted[1].decode('utf8')})
                value = dict_values
            elif field_type == 'list':
                value = request.forms.getall(field)
                if self.table[field].get('content_type') == 'dict':
                    dict_values = {}
                    for item in value:
                        splitted = item.split('|')
                        dict_values.update({splitted[0].decode('utf8'): splitted[1].decode('utf8')})
                    value = [dict_values]

            if not create and element[field] != value:
                update = True
                if isinstance(element[field], list) and element[field]:
                    if isinstance(element[field][0], BackendElement):
                        id_values = []
                        for item in element[field]:
                            id_values.append(item.id)
                        if id_values == value:
                            update = False
                if isinstance(element[field], BackendElement):
                    if element[field].id == value:
                        update = False
            if update:
                logger.warning(
                    "- updated field: %s = %s, whereas: %s", field, value, element[field]
                )
                data.update({field: value})
            if create:
                logger.warning("- field: %s = %s", field, value)
                data.update({field: value})

        # For an object update...
        if not create:
            if data:
                logger.warning("Updated element with: %s", data)
                result = datamgr.update_object(element=element, data=data)
                if result is True:
                    data.update(
                        {'_message': _("%s '%s' updated") % (self.backend_endpoint, element.name)}
                    )
                else:
                    data.update(
                        {
                            '_message': _("%s '%s' update failed!") % (
                                self.backend_endpoint, element.name
                            )
                        }
                    )
                    data.update(
                        {'_errors': result}
                    )
            else:
                data.update(
                    {'_message': _('No fields modified')}
                )
        else:
            # Create a new object
            if data:
                if '_realm' in self.table and '_realm' not in data:
                    data.update(
                        {'_realm': datamgr.my_realm.id}
                    )

                result = datamgr.add_object(self.backend_endpoint, data=data)
                if isinstance(result, basestring):
                    data.update(
                        {'_message': _("New %s created") % (self.backend_endpoint)}
                    )
                    data.update(
                        {'_id': result}
                    )
                else:
                    data.update(
                        {
                            '_message': _("%s creation failed!") % (self.backend_endpoint)
                        }
                    )
                    data.update(
                        {'_errors': result}
                    )
            else:
                self.send_user_message(
                    _("No data to create a new %s element") % self.backend_endpoint
                )

        return self.webui.response_data(data)

    def get_table(self, embedded=False, identifier=None, credentials=None):
        """
        Build the object_type table and get data to populate the table
        """
        # Table filtering: default is to restore the table saved filters
        where = {'saved_filters': True}
        if request.query.get('search') is not None:
            where = Helper.decode_search(request.query.get('search', ''))

        # Build table structure
        dt = Datatable(self.backend_endpoint, request.app.datamgr, self.table)

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
        dt = Datatable(self.backend_endpoint, request.app.datamgr, self.table)

        response.status = 200
        response.content_type = 'application/json'
        return dt.table_data()

    def get_templates(self, embedded=False):
        """
        Get the elements templates list

        Returns a JSON list containing, for each template, its id, name and alias
        """
        return self.get_list(templates=True, embedded=embedded)

    def get_list(self, templates=None, embedded=False):
        # pylint: disable=unused-argument
        """
        Get the elements list

        If the templates parameter is not None, the search is performed with this parameter (True or
        False). If a templates URL parameter (GET or POST) exists, the elements list is
        completed with the templates list to get all the elements and templates.

        Returns a JSON list containing, for each item, its id, name and alias
        """
        datamgr = request.app.datamgr

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

        items = []
        if templates is not None:
            search['where'] = {'_is_template': templates}
        else:
            templates = request.query.get('templates', '')
            if templates:
                search['where'] = {'_is_template': True}
                elts = f(search, all_elements=True)
                for elt in elts:
                    items.append({'id': elt.id, 'name': elt.name, 'alias': elt.alias})
                search = {
                    'projection': json.dumps({"_id": 1, "name": 1, "alias": 1}),
                    'where': {'_is_template': False}
                }

        elts = f(search, all_elements=True)
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
        - get_method is the datamanager method to call to get elements
        - object_type is the elements type

        - widget_id: widget identifier

        - start and count for pagination
        - search for specific elements search

        """
        user = request.environ['beaker.session']['current_user']
        datamgr = request.app.datamgr

        # Get element get method from the data manager
        if not get_method:
            # Get elements get method from the data manager
            get_method = getattr(datamgr, 'get_%ss' % self.backend_endpoint)
            if not get_method:
                self.send_user_message(_("No method to get a %s element") % self.backend_endpoint)

        if not callable(get_method):
            self.send_user_message(_("Configured method is not callable."))

        # Fetch elements per page preference for user, default is 25
        elts_per_page = datamgr.get_user_preferences(user, 'elts_per_page', 25)

        # Pagination and search
        start = int(request.params.get('start', '0'))
        count = int(request.params.get('count', elts_per_page))
        if count < 1:
            count = elts_per_page
        where = self.webui.helper.decode_search(request.params.get('search', ''))
        search = {
            'page': (start // count) + 1,
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
        elements = get_method(search)
        # Get last total elements count
        total = datamgr.get_objects_count(object_type, search=where, refresh=True)
        count = min(count, total)

        # Widget options
        widget_id = request.params.get('widget_id', '')
        if widget_id == '':
            return self.webui.response_invalid_parameters(_('Missing widget identifier'))

        widget_place = request.params.get('widget_place', 'dashboard')
        widget_template = request.params.get('widget_template', 'elements_table_widget')
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

        # Search in the saved dashboard widgets
        saved_widget = None
        saved_widgets = datamgr.get_user_preferences(user, 'dashboard_widgets', [])
        for widget in saved_widgets:
            if widget_id == widget['id']:
                saved_widget = widget
                logger.info("Saved widget found: %s", saved_widget)
                break
        # else:
            # logger.warning("Widget not found in the saved widgets: %s", widget_id)
            # return self.webui.response_invalid_parameters(_('Unknown widget'))

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
            logger.info("Saved widget option: %s", option)
            if len(option) > 1:
                if request.params.get(option[0]) != option[1]:
                    tmp_options.append("%s=%s" % (option[0], request.params.get(option[0])))
                    options[option[0]]['value'] = request.params.get(option[0])
                else:
                    tmp_options.append("%s=%s" % (option[0], option[1]))
                    options[option[0]]['value'] = option[1]

        new_options = '|'.join(tmp_options)
        logger.info("Widget new options: %s", new_options)

        if saved_options != new_options:
            logger.info("Widget new options: %s", new_options)

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
