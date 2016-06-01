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

'''
    Plugin Livestate
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
# Specific field to include the responsive + button used to disply hidden columns on small devices
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
schema['type'] = {
    'type': 'string',
    'ui': {
        'title': _('Type'),
        'width': '10',
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
        # 'priority': 0,
    },
    'allowed': ["host", "service"]
}
schema['host_name'] = {
    'type': 'objectid',
    'ui': {
        'title': _('Host name'),
        'width': '10',
        'visible': True,
        # 'priority': 0,
    },
    'data_relation': {
        'resource': 'host',
        'embeddable': True
    }
}
schema['display_name_host'] = {
    'type': 'string',
    'ui': {
        'title': _('Host display name'),
        'width': '10',
        'visible': True,
    },
}
schema['service_description'] = {
    'type': 'objectid',
    'ui': {
        'title': _('Service description'),
        'width': '10px',
        'visible': True,
        # 'priority': 0,
    },
    'data_relation': {
        'resource': 'service',
        'embeddable': True
    }
}
schema['display_name_service'] = {
    'type': 'string',
    'ui': {
        'title': _('Host display service'),
        'visible': True,
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
schema['business_impact'] = {
    'type': 'integer',
    'ui': {
        'title': _('Business impact'),
        'visible': True,
        # 'priority': 1,
    },
    'default': '2',
    'allowed': ["0", "1", "2", "3", "4", "5"]
}
schema['state'] = {
    'type': 'string',
    'ui': {
        'title': _('State'),
        'visible': True,
        'size': 5,
        # 'priority': 0,
    },
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
        'visible': True
    },
}
schema['downtime'] = {
    'type': 'boolean',
    'ui': {
        'title': _('In scheduled downtime'),
        'visible': True
    },
}
schema['last_check'] = {
    'type': 'integer',
    'ui': {
        'title': _('Last check'),
        'visible': True
    },
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
schema['current_attempt'] = {
    'type': 'integer',
    'ui': {
        'title': _('Current attempt'),
        'visible': True,
        'hidden': True
    },
}
schema['max_attempts'] = {
    'type': 'integer',
    'ui': {
        'title': _('Max attempts'),
        'visible': True,
        'hidden': True
    },
}
schema['next_check'] = {
    'type': 'integer',
    'ui': {
        'title': _('Next check'),
        'visible': True,
        'hidden': True
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
schema['last_state'] = {
    'type': 'string',
    'ui': {
        'title': _('State'),
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


# This to define the global information for the table
schema['ui'] = {
    'type': 'boolean',
    'default': True,

    # UI parameters for the objects
    'ui': {
        'page_title': _('Livestate table (%d items)'),
        'uid': '_id',
        'visible': True,
        'orderable': True,
        'searchable': True
    }
}


def get_livestate_table():
    '''
    Get the livestate list and transform it as a table
    '''
    datamgr = request.environ['beaker.session']['datamanager']

    # Pagination and search
    where = webui.helper.decode_search(request.query.get('search', ''))

    # Get total elements count
    total = datamgr.get_objects_count('livestate', search=where)

    # Build table structure
    dt = Datatable('livestate', datamgr.backend, schema)

    title = dt.title
    if '%d' in title:
        title = title % total

    return {
        'object_type': 'livestate',
        'dt': dt,
        'title': request.query.get('title', title)
    }


def get_livestate_table_data():
    '''
    Get the livestate list and provide table data
    '''
    datamgr = request.environ['beaker.session']['datamanager']
    dt = Datatable('livestate', datamgr.backend, schema)

    response.status = 200
    response.content_type = 'application/json'
    return dt.table_data()


pages = {
    get_livestate_table: {
        'name': 'Livestate table',
        'route': '/livestate_table',
        'view': '_table'
    },

    get_livestate_table_data: {
        'name': 'Livestate table data',
        'route': '/livestate_table_data',
        'method': 'POST'
    },
}
