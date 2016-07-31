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
    Plugin hosts dependencies
"""

import json
from collections import OrderedDict
from logging import getLogger

from bottle import request, response

from alignak_webui import _
from alignak_webui.utils.helper import Helper
from alignak_webui.plugins.common.common import get_table, get_table_data

logger = getLogger(__name__)

# Will be populated by the UI with it's own value
webui = None

# Get the same schema as the applications backend and append information for the datatable view
# Use an OrderedDict to create an ordered list of fields
schema = OrderedDict()
# Specific field to include the responsive + button used to display hidden columns on small devices
schema['#'] = {
    'type': 'string',
    'ui': {
        'title': '',
        # This field is visible (default: False)
        'visible': True,
        # This field is initially hidden (default: False)
        'hidden': False,
        # This field is searchable (default: True)
        'searchable': False,
        # This field is orderable (default: True)
        'orderable': False,
        # search as a regex (else strict value comparing when searching is performed)
        'regex': False,
    }
}
schema['name'] = {
    'type': 'string',
    'ui': {
        'title': _('Name'),
        # This field is visible (default: False)
        'visible': True,
        # This field is initially hidden (default: False)
        'hidden': False,
        # This field is searchable (default: True)
        'searchable': True,
        # search as a regex (else strict value comparing when searching is performed)
        'regex': True,
        # This field is orderable (default: True)
        'orderable': True,
    },
}
schema['definition_order'] = {
    'type': 'integer',
    'ui': {
        'title': _('Definition order'),
        'visible': True,
        'hidden': True,
        'orderable': False,
    },
}
schema['alias'] = {
    'type': 'string',
    'ui': {
        'title': _('Alias'),
        'visible': True
    },
}
schema['notes'] = {
    'type': 'string',
    'ui': {
        'title': _('Notes')
    }
}
schema['hosts'] = {
    'type': 'list',
    'ui': {
        'title': _('Hosts members'),
        'visible': True
    },
    'data_relation': {
        'resource': 'host',
        'embeddable': True
    }
}
schema['hostgroups'] = {
    'type': 'list',
    'ui': {
        'title': _('Hosts groups members'),
        'visible': True
    },
    'data_relation': {
        'resource': 'hostgroup',
        'embeddable': True
    }
}
schema['dependent_hosts'] = {
    'type': 'list',
    'ui': {
        'title': _('Dependent hosts'),
        'visible': True
    },
    'data_relation': {
        'resource': 'host',
        'embeddable': True
    }
}
schema['dependent_hostgroups'] = {
    'type': 'list',
    'ui': {
        'title': _('Dependent hosts groups'),
        'visible': True
    },
    'data_relation': {
        'resource': 'hostgroup',
        'embeddable': True
    }
}


# This to define the global information for the table
schema['ui'] = {
    'type': 'boolean',
    'default': True,

    # UI parameters for the objects
    'ui': {
        'page_title': _('Hosts dependencies table (%d items)'),
        'id_property': '_id',
        'visible': True,
        'orderable': True,
        'editable': False,
        'selectable': True,
        'searchable': True,
        'responsive': False,
        'recursive': True
    }
}


def get_hostdependencys():
    """
    Get the hostdependencys list
    """
    user = request.environ['beaker.session']['current_user']
    datamgr = request.environ['beaker.session']['datamanager']
    target_user = request.environ['beaker.session']['target_user']

    username = user.get_username()
    if not target_user.is_anonymous():
        username = target_user.get_username()

    # Fetch elements per page preference for user, default is 25
    elts_per_page = datamgr.get_user_preferences(username, 'elts_per_page', 25)
    elts_per_page = elts_per_page['value']

    # Pagination and search
    start = int(request.query.get('start', '0'))
    count = int(request.query.get('count', elts_per_page))
    where = webui.helper.decode_search(request.query.get('search', ''))
    search = {
        'page': start // (count + 1),
        'max_results': count,
        'sort': '-_id',
        'where': where
    }

    # Get elements from the data manager
    items = datamgr.get_hostdependencys(search)
    # Get last total elements count
    total = datamgr.get_objects_count('hostdependency', search=where, refresh=True)
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
        'tree_type': 'hostdependency',
        'items': items,
        'selectable': False,
        'context_menu': context_menu,
        'pagination': webui.helper.get_pagination_control('/hostdependencys', total, start, count),
        'title': request.query.get('title', _('All hostdependencys'))
    }


def get_hostdependencys_list():
    """
    Get the hostdependencys list
    """
    datamgr = request.environ['beaker.session']['datamanager']

    # Get elements from the data manager
    search = {'projection': json.dumps({"_id": 1, "name": 1, "alias": 1})}
    hostdependencys = datamgr.get_hostdependencys(search, all_elements=True)

    items = []
    for hostdependency in hostdependencys:
        items.append({'id': hostdependency.id, 'name': hostdependency.alias})

    response.status = 200
    response.content_type = 'application/json'
    return json.dumps(items)


def get_hostdependency_members(hostdependency_id):
    """
    Get the hostdependency hosts list
    """
    datamgr = request.environ['beaker.session']['datamanager']

    hostdependency = datamgr.get_hostdependency(hostdependency_id)
    if not hostdependency:  # pragma: no cover, should not happen
        return webui.response_invalid_parameters(_('Hosts group element does not exist'))

    # Not JSON serializable!
    # items = hostdependency.members

    items = []
    for host in hostdependency.members:
        lv_host = datamgr.get_livestate({'where': {'type': 'host', 'host': host.id}})
        lv_host = lv_host[0]
        title = "%s - %s (%s)" % (
            lv_host.status,
            Helper.print_duration(lv_host.last_check, duration_only=True, x_elts=0),
            lv_host.output
        )

        items.append({
            'id': host.id,
            'name': host.name,
            'alias': host.alias,
            'icon': lv_host.get_html_state(text=None, title=title),
            'url': lv_host.get_html_link()
        })

    response.status = 200
    response.content_type = 'application/json'
    return json.dumps(items)


def get_hostdependencys_table(embedded=False, identifier=None, credentials=None):
    """
    Get the elements to build a table
    """
    return get_table('hostdependency', schema, embedded, identifier, credentials)


def get_hostdependencys_table_data():
    """
    Get the elements required by the table
    """
    return get_table_data('hostdependency', schema)


def get_hostdependency(hostdependency_id):
    """
    Display the element linked to a hostdependency item
    """
    datamgr = request.environ['beaker.session']['datamanager']

    hostdependency = datamgr.get_hostdependency(hostdependency_id)
    if not hostdependency:  # pragma: no cover, should not happen
        return webui.response_invalid_parameters(_('Hosts group element does not exist'))

    return get_hostdependencys_table()


pages = {
    get_hostdependency: {
        'name': 'Host group',
        'route': '/hostdependency/<hostdependency_id>'
    },
    get_hostdependency_members: {
        'name': 'Host group members',
        'route': '/hostdependency/members/<hostdependency_id>'
    },
    get_hostdependencys: {
        'routes': [
            ('/hostdependencys', 'Hosts groups'),
            ('/hostdependencys_tree', 'Hosts groups tree')
        ],
        'view': '_tree',
        'search_engine': False,
        'search_prefix': '',
        'search_filters': {
        }
    },
    get_hostdependencys_list: {
        'routes': [
            ('/hostdependencys_list', 'Hosts groups list'),
        ]
    },

    get_hostdependencys_table: {
        'name': 'Hosts groups table',
        'route': '/hostdependencys_table',
        'view': '_table',
        'tables': [
            {
                'id': 'hostdependencys_table',
                'for': ['external'],
                'name': _('Hosts groups table'),
                'template': '_table',
                'icon': 'table',
                'description': _(
                    '<h4>Hosts groups table</h4>Displays a datatable for the system '
                    'hosts groups.<br>'
                ),
                'actions': {
                    'hostdependencys_table_data': get_hostdependencys_table_data
                }
            }
        ]
    },

    get_hostdependencys_table_data: {
        'name': 'Hosts groups table data',
        'route': '/hostdependencys_table_data',
        'method': 'POST'
    },
}
