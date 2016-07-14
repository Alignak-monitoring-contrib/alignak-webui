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
    Plugin Log check result
"""

from collections import OrderedDict
from logging import getLogger

from bottle import request

from alignak_webui import _
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
        # defines the priority for the responsive column hidding (0 is the most important)
        # Default is 10000
        # 'priority': 0,
    }
}
schema['_created'] = {
    'type': 'integer',
    'ui': {
        'title': _('Date'),
        'visible': True
    },
}
schema['host'] = {
    'type': 'objectid',
    'ui': {
        'title': _('Host'),
        'width': '10',
        'visible': True,
        'hidden': False,
    },
    'data_relation': {
        'resource': 'host',
        'embeddable': True
    }
}
schema['service'] = {
    'type': 'objectid',
    'ui': {
        'title': _('Service'),
        'width': '10px',
        'visible': True,
        'hidden': False,
    },
    'data_relation': {
        'resource': 'service',
        'embeddable': True
    }
}
schema['user'] = {
    'type': 'objectid',
    'ui': {
        'title': _('User'),
        'width': '10',
        'visible': True,
        'hidden': False,
    },
    'data_relation': {
        'resource': 'user',
        'embeddable': True
    }
}
schema['type'] = {
    'type': 'string',
    'ui': {
        'title': _('Type'),
        'visible': True
    },
    'allowed': {
        "webui.comment": _('User comments'),
        "check.result": _('Check results'),
        "check.request": _('Check requests'),
        "check.requested": _('Forced re-check'),
        "ack.add": _('Acknowledge requests'),
        "ack.processed": _('Acknowledge processed'),
        "ack.delete": _('Acknowledge delete'),
        "downtime.add": _('Downtime schedule requests'),
        "downtime.processed": _('Downtime processed'),
        "downtime.delete": _('Downtime delete')
    }
}
schema['message'] = {
    'type': 'string',
    'ui': {
        'title': _('Message'),
        'visible': True,
    }
}
schema['check_result'] = {
    'type': 'objectid',
    'ui': {
        'title': _('Check result'),
        'width': '10',
        'visible': True,
        'hidden': False,
    },
    'data_relation': {
        'resource': 'logcheckresult',
        'embeddable': True
    }
}


# This to define the global information for the table
schema['ui'] = {
    'type': 'boolean',
    'default': True,

    # UI parameters for the objects
    'ui': {
        'page_title': _('Log check result table (%d items)'),
        'id_property': '_id',
        'visible': True,
        'orderable': True,
        'editable': False,
        'selectable': True,
        'searchable': True,
        'responsive': False
    }
}


def get_history(host_id):
    """
    Get the timeline history for an host
    """
    user = request.environ['beaker.session']['current_user']
    datamgr = request.environ['beaker.session']['datamanager']
    target_user = request.environ['beaker.session']['target_user']

    host = datamgr.get_host(host_id)
    if not host:  # pragma: no cover, should not happen
        return webui.response_invalid_parameters(_('Host does not exist'))

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
        'sort': '-_created',
        'where': where,
        'embedded': {
        }
    }

    search['where'].update({'host': host_id})

    # Fetch timeline filters preference for user, default is []
    selected_types = datamgr.get_user_preferences(username, 'timeline_filters', [])
    selected_types = selected_types['value']
    for selected_type in schema['type']['allowed']:
        if request.query.get(selected_type) == 'true':
            if selected_type not in selected_types:
                selected_types.append(type)
            logger.critical("Filter: %s=%s", selected_type, request.query.get(selected_type))
        elif request.query.get(selected_type) == 'false':
            if selected_type in selected_types:
                selected_types.remove(selected_type)

    if selected_types:
        datamgr.set_user_preferences(username, 'timeline_filters', selected_types)
        search['where'].update({'type': {'$in': selected_types}})
    logger.debug("History selected types: %s", selected_types)

    # Get host elements from the datamanager
    history = datamgr.get_history(search)
    # Get last total elements count
    total = datamgr.get_objects_count('history', search=where, refresh=True)
    count = min(count, total)

    return {
        'object_type': 'history',
        'timeline_host': host,
        'types': schema['type']['allowed'],
        'selected_types': selected_types,
        'items': history,
        'timeline_pagination': webui.helper.get_pagination_control(
            '/history/' + host_id, total, start, count
        ),
        'title': request.query.get('title', _('History for %s') % host.alias)
    }


def get_history_table(embedded=False, identifier=None, credentials=None):
    """
    Get the elements to build a table
    """
    return get_table('history', schema, embedded, identifier, credentials)


def get_history_table_data():
    """
    Get the elements required by the table
    """
    return get_table_data('history', schema)


pages = {
    get_history: {
        'name': 'History',
        'route': '/history/<host_id>',
        'view': '_timeline',
        'search_engine': False,
        'search_prefix': '',
        'search_filters': {
        }
    },

    get_history_table: {
        'name': 'History table',
        'route': '/history_table',
        'view': '_table',
        'tables': [
            {
                'id': 'history_table',
                'for': ['external'],
                'name': _('History table'),
                'template': '_table',
                'icon': 'table',
                'description': _(
                    '<h4>History table</h4>Displays a datatable for the system history.<br>'
                ),
                'actions': {
                    'history_table_data': get_history_table_data
                }
            }
        ]
    },

    get_history_table_data: {
        'name': 'History table data',
        'route': '/history_table_data',
        'method': 'POST'
    },
}
