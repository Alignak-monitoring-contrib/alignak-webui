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

from alignak_webui.utils.datatable import Datatable
from alignak_webui.utils.helper import Helper

logger = getLogger(__name__)

# Will be populated by the UI with it's own value
webui = None

# Get the same schema as the applications backend and append information for the datatable view
# Use an OrderedDict to create an ordered list of fields
schema = OrderedDict()
schema['name'] = {
    'type': 'string',
    'ui': {
        'title': _('Command name'),
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
        'orderable': True,
    },
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
        'visible': True
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
        'visible': True
    },
}
schema['reactionner_tag'] = {
    'type': 'string',
    'ui': {
        'title': _('Reactionner tag'),
        'visible': True
    },
}


# This to define if the object in this model are to be used in the UI
schema['ui'] = {
    'type': 'boolean',
    'default': True,

    # UI parameters for the objects
    'ui': {
        'page_title': _('Commands table (%d items)'),
        'uid': '_id',
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
        'sort': '-_id',
        'where': where,
        'embedded': {
            'userservice': 1, 'userservice_session': 1,
            'user_creator': 1, 'user_participant': 1
        }
    }

    # Get elements from the data manager
    commands = datamgr.get_commands(search)
    # Get last total elements count
    total = datamgr.get_objects_count('command', search=where, refresh=True)
    count = min(count, total)

    return {
        'commands': commands,
        'pagination': Helper.get_pagination_control('/commands', total, start, count),
        'title': request.query.get('title', _('All commands'))
    }


def get_commands_table():
    """
    Get the commands list and transform it as a table
    """
    datamgr = request.environ['beaker.session']['datamanager']

    # Pagination and search
    where = Helper.decode_search(request.query.get('search', ''))

    # Get total elements count
    total = datamgr.get_objects_count('command', search=where)

    # Build table structure
    dt = Datatable('command', datamgr.backend, schema)

    title = dt.title
    if '%d' in title:
        title = title % total

    return {
        'object_type': 'command',
        'dt': dt,
        'where': where,
        'title': request.query.get('title', title)
    }


def get_commands_table_data():
    """
    Get the commands list and provide table data
    """
    datamgr = request.environ['beaker.session']['datamanager']
    dt = Datatable('command', datamgr.backend, schema)

    response.status = 200
    response.content_type = 'application/json'
    return dt.table_data()


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
    get_commands_table: {
        'name': 'Commands table',
        'route': '/commands_table',
        'view': '_table'
    },

    get_commands_table_data: {
        'name': 'Commands table data',
        'route': '/command_table_data',
        'method': 'POST'
    },
}
