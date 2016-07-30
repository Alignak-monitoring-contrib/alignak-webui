#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (C) 2015-2016 F. Mohier

"""
    Plugin User roles restriction
"""

import json

from collections import OrderedDict

from logging import getLogger
from bottle import request, response

from alignak_webui import _
from alignak_webui.plugins.common.common import get_table, get_table_data

logger = getLogger(__name__)

# Will be valued by the plugin loader
webui = None

# Declare backend element endpoint
backend_endpoint = 'userrestrictrole'

# Get the same schema as the applications backend and append information for the datatable view
# Use an OrderedDict to create an ordered list of fields
schema = OrderedDict()
schema['user'] = {
    'type': 'objectid',
    'ui': {
        'title': _('Realm'),
        'visible': True,
        'searchable': True
    },
    'data_relation': {
        'resource': 'user',
        'embeddable': True
    }
}
schema['realm'] = {
    'type': 'objectid',
    'ui': {
        'title': _('Realm'),
        'visible': True,
        'searchable': True
    },
    'data_relation': {
        'resource': 'realm',
        'embeddable': True
    }
}
schema['sub_realm'] = {
    'type': 'boolean',
    'ui': {
        'title': _('Sub realm'),
        'visible': True,
        'hidden': True
    },
}
schema['resource'] = {
    'type': 'string',
    'default': 'All',
    'allowed': ['All', 'host', 'hostgroup', 'service', 'servicegroup'],
    'ui': {
        'title': _('Resource type'),
        'visible': True
    },
}
schema['crud'] = {
    'type': 'list',
    'default': ['read'],
    'allowed': ['delete', 'create', 'update', 'read'],
    'ui': {
        'title': _('CRUD'),
        'visible': True
    },
}

# This to define if the object in this model are to be used in the UI
schema['ui'] = {
    'type': 'boolean',
    'default': True,

    # UI parameters for the objects
    'ui': {
        'page_title': _('Users roles table (%d items)'),
        'id_property': '_id',
        'visible': True,
        'orderable': True,
        'editable': False,
        'selectable': True,
        'searchable': True,
        'responsive': False
    }
}


def get_userrestrictroles():
    """
        Show list of users
    """
    user = request.environ['beaker.session']['current_user']
    target_user = request.environ['beaker.session']['target_user']
    datamgr = request.environ['beaker.session']['datamanager']

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
        'where': where
    }

    # Get userrestrictroles
    userrestrictroles = datamgr.get_userrestrictroles(search)
    # Get last total elements count
    total = datamgr.get_objects_count('userrestrictrole', search=where, refresh=True, log=True)
    count = min(count, total)

    return {
        'userrestrictroles': userrestrictroles,
        'pagination': webui.helper.get_pagination_control('/userrestrictroles', total, start, count),
        'title': request.query.get('title', _('All users roles'))
    }


def get_userrestrictroles_list(embedded=False):
    """
    Get the users list
    """
    datamgr = request.environ['beaker.session']['datamanager']

    # Get elements from the data manager
    search = {'projection': json.dumps({"_id": 1, "name": 1, "alias": 1})}
    users = datamgr.get_userrestrictroles(search, all_elements=True)

    items = []
    for userrestrictrole in userrestrictroles:
        items.append({'id': userrestrictrole.id, 'name': userrestrictrole.name, 'alias': userrestrictrole.alias})

    response.status = 200
    response.content_type = 'application/json'
    return json.dumps(items)


def get_userrestrictroles_table(embedded=False, identifier=None, credentials=None):
    """
    Get the elements to build a table
    """
    return get_table('userrestrictrole', schema, embedded, identifier, credentials)


def get_userrestrictroles_table_data():
    """
    Get the elements required by the table
    """
    return get_table_data('userrestrictrole', schema)


pages = {
    get_userrestrictroles: {
        'name': 'Users roles',
        'route': '/userrestrictroles',
        'view': 'userrestrictroles',
        'search_engine': True,
        'search_prefix': '',
        'search_filters': {
            _('Administrator'): 'role:administrator',
            _('Power'): 'role:power',
            _('User'): 'role:userrestrictrole',
            _('Guest'): 'name:anonymous'
        }
    },

    get_userrestrictroles_list: {
        'routes': [
            ('/userrestrictroles_list', 'Users roles list'),
        ]
    },

    get_userrestrictroles_table: {
        'name': 'Users roles table',
        'route': '/userrestrictroles_table',
        'view': '_table',
        'tables': [
            {
                'id': 'userrestrictroles_table',
                'for': ['external'],
                'name': _('Users roles table'),
                'template': '_table',
                'icon': 'table',
                'description': _(
                    '<h4>Users roles table</h4>Displays a datatable for the users roles.<br>'
                ),
                'actions': {
                    'userrestrictroles_table_data': get_userrestrictroles_table_data
                }
            }
        ]
    },
    get_userrestrictroles_table_data: {
        'name': 'Users roles table data',
        'route': '/userrestrictroles_table_data',
        'method': 'POST'
    }
}
