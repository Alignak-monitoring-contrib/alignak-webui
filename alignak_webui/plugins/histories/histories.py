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

import time
import json

from collections import OrderedDict

from logging import getLogger
from bottle import request, response, redirect

from alignak_webui.objects.item import Item

from alignak_webui.utils.datatable import Datatable
from alignak_webui.utils.helper import Helper

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
    'allowed': ["check.result", "ack.add", "ack.delete", "downtime.add", "downtime.delete"]
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
        'uid': '_id',
        'visible': True,
        'orderable': True,
        'editable': False,
        'selectable': True,
        'searchable': True,
        'responsive': False
    }
}


def get_history_table():
    """
    Get the history list and transform it as a table
    """
    datamgr = request.environ['beaker.session']['datamanager']

    # Pagination and search
    where = Helper.decode_search(request.query.get('search', ''))

    # Get total elements count
    total = datamgr.get_objects_count('history', search=where)

    # Build table structure
    dt = Datatable('history', datamgr.backend, schema)

    title = dt.title
    if '%d' in title:
        title = title % total

    return {
        'object_type': 'history',
        'dt': dt,
        'where': where,
        'title': request.query.get('title', title)
    }


def get_history_table_data():
    """
    Get the history list and provide table data
    """
    datamgr = request.environ['beaker.session']['datamanager']
    dt = Datatable('history', datamgr.backend, schema)

    response.status = 200
    response.content_type = 'application/json'
    return dt.table_data()


pages = {
    get_history_table: {
        'name': 'History table',
        'route': '/history_table',
        'view': '_table'
    },

    get_history_table_data: {
        'name': 'History table data',
        'route': '/history_table_data',
        'method': 'POST'
    },
}
