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

'''
    Plugin Hosts
'''

import time
import json

from collections import OrderedDict

from logging import getLogger
from bottle import request, response

from alignak_webui.objects.item import Item
from alignak_webui.objects.item import sort_items_most_recent_first

from alignak_webui.utils.datatable import Datatable

logger = getLogger(__name__)

# Will be populated by the UI with it's own value
webui = None

# Get the same schema as the applications backend and append information for the datatable view
# Use an OrderedDict to create an ordered list of fields
schema = OrderedDict()
schema['name'] = {
    'type': 'string',
    'ui': {
        'title': _('Host name'),
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
        'title': _('Host alias'),
        'visible': True
    },
}
schema['display_name'] = {
    'type': 'string',
    'ui': {
        'title': _('Host display name'),
        'visible': True
    },
}
schema['address'] = {
    'type': 'string',
    'ui': {
        'title': _('Address'),
        'visible': True
    },
}
schema['check_command'] = {
    'type': 'objectid',
    'ui': {
        'title': _('Check command'),
        'visible': True
    },
    'data_relation': {
        'resource': 'command',
        'embeddable': True,
    }
}
schema['check_command_args'] = {
    'type': 'string',
    'ui': {
        'title': _('Check command arguments'),
        'visible': True
    },
}
schema['active_checks_enabled'] = {
    'type': 'boolean',
    'ui': {
        'title': _('Active checks enabled'),
        'visible': True
    },
}
schema['passive_checks_enabled'] = {
    'type': 'boolean',
    'ui': {
        'title': _('Passive checks enabled'),
        'visible': True
    },
}
schema['parents'] = {
    'type': 'list',
    'ui': {
        'title': _('Parents'),
        'visible': True
    },
    'data_relation': {
        'resource': 'host',
        'embeddable': True,
    }
}
schema['hostgroups'] = {
    'type': 'list',
    'ui': {
        'title': _('Hosts groups'),
        'visible': True
    },
    'schema': {
        'type': 'objectid',
        'data_relation': {
            'resource': 'hostgroup',
            'embeddable': True,
        }
    },
}
schema['business_impact'] = {
    'type': 'integer',
    'ui': {
        'title': _('Business impact'),
        'visible': True
    },
}


# This to define if the object in this model are to be used in the UI
schema['ui'] = {
    'type': 'boolean',
    'default': True,

    # UI parameters for the objects
    'ui': {
        'page_title': _('Hosts table (%d items)'),
        'uid': '_id',
        'visible': True,
        'orderable': True,
        'searchable': True
    }
}


def get_hosts():
    '''
    Get the hosts list
    '''
    user = request.environ['beaker.session']['current_user']
    datamgr = request.environ['beaker.session']['datamanager']
    target_user = request.environ['beaker.session']['target_user']

    username = user.get_username()
    if not target_user.is_anonymous():
        username = target_user.get_username()

    # Fetch elements per page preference for user, default is 25
    elts_per_page = webui.prefs_module.get_ui_user_preference(username, 'elts_per_page', 25)

    # Fetch sound preference for user, default is 'no'
    sound_pref = webui.prefs_module.get_ui_user_preference(
        username, 'sound', request.app.config.get('play_sound', 'no')
    )
    sound = request.query.get('sound', '')
    if sound != sound_pref and sound in ['yes', 'no']:  # pragma: no cover - RFU sound
        webui.prefs_module.set_ui_user_preference(user.get_username(), 'sound', sound)
        sound_pref = sound

    # Pagination and search
    start = int(request.query.get('start', '0'))
    count = int(request.query.get('count', elts_per_page))
    where = webui.helper.decode_search(request.query.get('search', ''))
    search = {
        'page': start // count + 1,
        'max_results': count,
        'sort': '-opening_date',
        'where': where,
        'embedded': {
            'userservice': 1, 'userservice_session': 1,
            'user_creator': 1, 'user_participant': 1
        }
    }

    # Get elements from the data manager
    hosts = datamgr.get_hosts(search)
    # Get last total elements count
    total = datamgr.get_objects_count('host', search=where, refresh=True)
    count = min(count, total)

    return {
        'hosts': hosts,
        'start': start, 'count': count, 'total': total,
        'pagination': webui.helper.get_pagination_control(total, start, count),
        'title': request.query.get('title', _('All hosts')),
        'bookmarks': webui.prefs_module.get_user_bookmarks(user.get_username()),
        'bookmarksro': webui.prefs_module.get_common_bookmarks(),
        'sound': sound_pref,
        'elts_per_page': elts_per_page
    }


def get_hosts_table():
    '''
    Get the hosts list and transform it as a table
    '''
    user = request.environ['beaker.session']['current_user']
    datamgr = request.environ['beaker.session']['datamanager']
    target_user = request.environ['beaker.session']['target_user']

    username = user.get_username()
    if not target_user.is_anonymous():
        username = target_user.get_username()

    # Fetch elements per page preference for user, default is 25
    elts_per_page = webui.prefs_module.get_ui_user_preference(username, 'elts_per_page', 25)

    # Fetch sound preference for user, default is 'no'
    sound_pref = webui.prefs_module.get_ui_user_preference(
        username, 'sound', request.app.config.get('play_sound', 'no')
    )
    sound = request.query.get('sound', '')
    if sound != sound_pref and sound in ['yes', 'no']:  # pragma: no cover - RFU sound
        webui.prefs_module.set_ui_user_preference(username, 'sound', sound)
        sound_pref = sound

    # Pagination and search
    where = webui.helper.decode_search(request.query.get('search', ''))

    # Get total elements count
    total = datamgr.get_objects_count('host', search=where)

    # Build table structure
    dt = Datatable('host', datamgr.backend, schema)

    title = dt.title
    if '%d' in title:
        title = title % total

    return {
        'dt': dt,
        'title': request.query.get('title', title),
        'bookmarks': webui.prefs_module.get_user_bookmarks(user.get_username()),
        'bookmarksro': webui.prefs_module.get_common_bookmarks(),
        'sound': sound_pref,
        'elts_per_page': elts_per_page
    }


def get_hosts_table_data():
    '''
    Get the hosts list and provide table data
    '''
    datamgr = request.environ['beaker.session']['datamanager']
    dt = Datatable('host', datamgr.backend, schema)

    response.status = 200
    response.content_type = 'application/json'
    return dt.table_data()


pages = {
    get_hosts: {
        'name': 'Hosts',
        'route': '/hosts',
        'view': 'hosts',
        'search_engine': True,
        'search_prefix': '',
        'search_filters': {
            _('Hosts up'): 'state:up',
            _('Hosts down'): 'state:down',
            _('Hosts unreachable'): 'state:unreachable',
        }
    },
    get_hosts_table: {
        'name': 'Hosts table',
        'route': '/hosts_table',
        'view': 'hosts_table'
    },

    get_hosts_table_data: {
        'name': 'Hosts table data',
        'route': '/hosts_table_data',
        'method': 'POST'
    },
}
