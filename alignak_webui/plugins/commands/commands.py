#!/usr/bin/python
# -*- coding: utf-8 -*-
# pylint: disable=too-many-locals

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
    Plugin Commands
"""

import time
import json

from collections import OrderedDict

from logging import getLogger
from bottle import request, response

from alignak_webui.objects.item import Item

from alignak_webui.plugins.common.common import get_widget, get_table, get_table_data

logger = getLogger(__name__)

# Will be populated by the UI with it's own value
webui = None

# Get the same schema as the applications backend and append information for the datatable view
# Use an OrderedDict to create an ordered list of fields
schema = OrderedDict()
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
schema['command_line'] = {
    'type': 'string',
    'ui': {
        'title': _('Command line'),
        'visible': True
    },
}
schema['module_type'] = {
    'type': 'string',
    'ui': {
        'title': _('Module type'),
        'visible': True,
        'hidden': True
    },
}
schema['enable_environment_macros'] = {
    'type': 'boolean',
    'ui': {
        'title': _('Enable environment macros'),
        'visible': True
    },
}
schema['timeout'] = {
    'type': 'integer',
    'ui': {
        'title': _('Timeout'),
        'visible': True
    },
}
schema['poller_tag'] = {
    'type': 'string',
    'ui': {
        'title': _('Poller tag'),
        'visible': True,
        'hidden': True
    },
}
schema['reactionner_tag'] = {
    'type': 'string',
    'ui': {
        'title': _('Reactionner tag'),
        'visible': True,
        'hidden': True
    },
}


# This to define if the object in this model are to be used in the UI
schema['ui'] = {
    'type': 'boolean',
    'default': True,

    # UI parameters for the objects
    'ui': {
        'page_title': _('Commands table (%d items)'),
        'id_property': '_id',
        'visible': True,
        'orderable': True,
        'editable': False,
        'selectable': True,
        'searchable': True,
        'responsive': True
    }
}


def get_commands():
    """
    Get the commands list
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
        'page': start // count + 1,
        'max_results': count,
        'where': where
    }

    # Get elements from the data manager
    commands = datamgr.get_commands(search)
    # Get last total elements count
    total = datamgr.get_objects_count('command', search=where, refresh=True)
    count = min(count, total)

    if request.params.get('list', None):
        return get_commands_list()

    return {
        'commands': commands,
        'pagination': webui.helper.get_pagination_control('/commands', total, start, count),
        'title': request.query.get('title', _('All commands'))
    }


def get_commands_list():
    """
    Get the commands list
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

    # Get elements from the data manager
    search = {'projection': json.dumps({"_id": 1, "name": 1, "alias": 1})}
    commands = datamgr.get_commands(search, all_elements=True)

    items = []
    for command in commands:
        items.append({'id': command.id, 'name': command.alias})

    response.status = 200
    response.content_type = 'application/json'
    return json.dumps(items)


def get_commands_table(embedded=False, identifier=None, credentials=None):
    """
    Get the elements to build a table
    """
    return get_table('command', schema, embedded, identifier, credentials)


def get_commands_table_data():
    """
    Get the elements required by the table
    """
    return get_table_data('command', schema)


pages = {
    get_commands: {
        'name': 'Commands',
        'route': '/commands',
        'view': 'commands',
        'search_engine': False,
        'search_prefix': '',
        'search_filters': {
        }
    },
    get_commands_list: {
        'name': 'Commands list',
        'route': '/commands_list'
    },
    get_commands_table: {
        'name': 'Commands table',
        'route': '/commands_table',
        'view': '_table',
        'tables': [
            {
                'id': 'commands_table',
                'for': ['external'],
                'name': _('Commands table'),
                'template': '_table',
                'icon': 'table',
                'description': _(
                    '<h4>Commands table</h4>Displays a datatable for the system commands.<br>'
                ),
                'actions': {
                    'command_table_data': get_commands_table_data
                }
            }
        ]
    },

    get_commands_table_data: {
        'name': 'Commands table data',
        'route': '/command_table_data',
        'method': 'POST'
    },
}
