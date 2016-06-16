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
    Plugin Log
"""

import time
import json

from collections import OrderedDict

from logging import getLogger
from bottle import request, response, redirect

from alignak_webui.objects.item import Item

from alignak_webui.utils.datatable import Datatable

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
# schema['type'] = {
    # 'type': 'string',
    # 'ui': {
        # 'title': _('Type'),
        # 'width': '10px',
        # 'visible': True,
        # 'hidden': False,
        # 'searchable': True,
        # 'regex': True,
        # 'orderable': True,
    # },
    # 'allowed': ["host", "service"]
# }
schema['host'] = {
    'type': 'objectid',
    'ui': {
        'title': _('Host'),
        'width': '10',
        'visible': True,
        'hidden': True,
    },
    'data_relation': {
        'resource': 'host',
        'embeddable': True
    }
}
schema['state'] = {
    'type': 'string',
    'ui': {
        'title': _('State'),
        'visible': True,
        'size': 5,
        # 'priority': 0,
    },
    'allowed': ["OK", "WARNING", "CRITICAL", "UNKNOWN", "UP", "DOWN", "UNREACHABLE"]
}
schema['state_type'] = {
    'type': 'string',
    'ui': {
        'title': _('State type'),
        'visible': True,
        # 'priority': 0,
    },
    'allowed': ["HARD", "SOFT"]
}
schema['state_id'] = {
    'type': 'integer',
    'ui': {
        'title': _('State identifier'),
        'visible': True,
        'hidden': True
    },
    'allowed': ['0', '1', '2', '3', '4']
}
schema['acknowledged'] = {
    'type': 'boolean',
    'ui': {
        'title': _('Acknowledged'),
        'visible': True,
        'size': 2,
    },
}
schema['last_check'] = {
    'type': 'integer',
    'ui': {
        'title': _('Last check'),
        'visible': True
    },
}
schema['last_state'] = {
    'type': 'string',
    'ui': {
        'title': _('Last state'),
        'visible': True,
        'hidden': True
    },
    'allowed': ["OK", "WARNING", "CRITICAL", "UNKNOWN", "UP", "DOWN", "UNREACHABLE"]
}
schema['output'] = {
    'type': 'string',
    'ui': {
        'title': _('Check output'),
        'visible': True
    },
}
schema['long_output'] = {
    'type': 'string',
    'ui': {
        'title': _('Check long output'),
        'visible': True
    },
}
schema['perf_data'] = {
    'type': 'string',
    'ui': {
        'title': _('Performance data'),
        'visible': True
    },
}
schema['last_state_changed'] = {
    'type': 'integer',
    'ui': {
        'title': _('Last check'),
        'visible': True,
        'hidden': True
    },
}
schema['last_state_type'] = {
    'type': 'string',
    'ui': {
        'title': _('Last state type'),
        'visible': True,
        'hidden': True
    },
    'allowed': ["HARD", "SOFT"]
}
schema['latency'] = {
    'type': 'float',
    'ui': {
        'title': _('Latency'),
        'visible': True,
        'hidden': True
    },
}
schema['execution_time'] = {
    'type': 'float',
    'ui': {
        'title': _('Execution time'),
        'visible': True,
        'hidden': True
    },
}


# This to define the global information for the table
schema['ui'] = {
    'type': 'boolean',
    'default': True,

    # UI parameters for the objects
    'ui': {
        'page_title': _('Log table (%d items)'),
        'uid': '_id',
        'visible': True,
        'orderable': True,
        'searchable': True,
        'responsive': False
    }
}


def get_log_table():
    """
    Get the log list and transform it as a table
    """
    datamgr = request.environ['beaker.session']['datamanager']

    # Pagination and search
    where = webui.helper.decode_search(request.query.get('search', ''))

    # Get total elements count
    total = datamgr.get_objects_count('log', search=where)

    # Build table structure
    dt = Datatable('log', datamgr.backend, schema)

    title = dt.title
    if '%d' in title:
        title = title % total

    return {
        'object_type': 'log',
        'dt': dt,
        'title': request.query.get('title', title)
    }


def get_log_table_data():
    """
    Get the log list and provide table data
    """
    datamgr = request.environ['beaker.session']['datamanager']
    dt = Datatable('log', datamgr.backend, schema)

    response.status = 200
    response.content_type = 'application/json'
    return dt.table_data()


def get_log(element_id):
    """
    Display the element linked to a log item
    """
    datamgr = request.environ['beaker.session']['datamanager']

    element = datamgr.get_log({'where': {'_id': element_id}})
    if not element:  # pragma: no cover, should not happen
        return webui.response_invalid_parameters(_('Log element does not exist'))

    element = element[0]
    if element['type'] == 'host':
        logger.debug("Log: %s %s %s", element, element.host_name.id, element.__dict__)
        redirect('/host/' + element.host_name.id)
    else:
        logger.debug("Log: %s %s %s", element, element.host_name.id, element.__dict__)
        redirect('/host/' + element.host_name.id + '#services')


pages = {
    get_log: {
        'name': 'Log',
        'route': '/log/<element_id>'
    },
    get_log_table: {
        'name': 'Log table',
        'route': '/log_table',
        'view': '_table'
    },

    get_log_table_data: {
        'name': 'Log table data',
        'route': '/log_table_data',
        'method': 'POST'
    },
}
