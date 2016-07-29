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
    }
}
schema['last_check'] = {
    'type': 'integer',
    'ui': {
        'title': _('Last check'),
        'format': 'date',
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
schema['state_changed'] = {
    'type': 'boolean',
    'ui': {
        'title': _('State changed'),
        'visible': True
    },
}
schema['acknowledged'] = {
    'type': 'boolean',
    'ui': {
        'title': _('Acknowledged'),
        'visible': True,
        'hidden': True
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
schema['last_state_type'] = {
    'type': 'string',
    'ui': {
        'title': _('Last state type'),
        'visible': True,
        'hidden': True
    },
    'allowed': ["HARD", "SOFT"]
}
schema['last_state_id'] = {
    'type': 'integer',
    'ui': {
        'title': _('Last state identifier'),
        'visible': True,
        'hidden': True
    },
    'allowed': ['0', '1', '2', '3', '4']
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
        'responsive': False,

        'css': "nowrap",

        'initial_sort': [[1, 'desc']]
    }
}


def get_logcheckresults_table(embedded=False, identifier=None, credentials=None):
    """
    Get the elements to build a table
    """
    return get_table('logcheckresult', schema, embedded, identifier, credentials)


def get_logcheckresults_table_data():
    """
    Get the elements required by the table
    """
    return get_table_data('logcheckresult', schema)


pages = {
    get_logcheckresults_table: {
        'name': 'Log check result table',
        'route': '/logcheckresults_table',
        'view': '_table',
        'tables': [
            {
                'id': 'logcheckresults_table',
                'for': ['external'],
                'name': _('Checks results table'),
                'template': '_table',
                'icon': 'table',
                'description': _(
                    '<h4>Checks results table</h4>Displays a datatable for the system '
                    'logged checks results.<br>'
                ),
                'actions': {
                    'logcheckresults_table_data': get_logcheckresults_table_data
                }
            }
        ]
    },

    get_logcheckresults_table_data: {
        'name': 'Log check result table data',
        'route': '/logcheckresults_table_data',
        'method': 'POST'
    },
}
