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
schema['inherits_parent'] = {
    'type': 'boolean',
    'ui': {
        'title': _('Inherits from parents'),
        'visible': True,
        'hidden': True
    },
}
schema['dependency_period'] = {
    'type': 'objectid',
    'ui': {
        'title': _('Dependency period'),
        'visible': True,
        'format': 'select',
        'format_parameters': 'hostdependency'
    },
    'data_relation': {
        'resource': 'timeperiod',
        'embeddable': True
    }
}
schema['execution_failure_criteria'] = {
    'type': 'list',
    'default': ['n'],
    'allowed': ['o', 'd', 'u', 'p', 'n'],
    'ui': {
        'title': _('Execution failure criteria'),
        'visible': True,
        'format': {
            'list_type': "multichoices",
            'list_allowed': {
                u"o": u"Fail on Up state",
                u"d": u"Fail on Down state",
                u"u": u"Fail on Unreachable state",
                u"p": u"Fail on Pending state",
                u"n": u"Never fail and always check"
            }
        }
    },
}
schema['notification_failure_criteria'] = {
    'type': 'list',
    'default': ['n'],
    'allowed': ['o', 'd', 'u', 'p', 'n'],
    'ui': {
        'title': _('Execution failure criteria'),
        'visible': True,
        'format': {
            'list_type': "multichoices",
            'list_allowed': {
                u"o": u"Fail on Up state",
                u"d": u"Fail on Down state",
                u"u": u"Fail on Unreachable state",
                u"p": u"Fail on Pending state",
                u"n": u"Never fail and always check"
            }
        }
    },
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
        'recursive': False
    }
}


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


pages = {
    get_hostdependencys_table: {
        'name': 'Hosts dependencies table',
        'route': '/hostdependencys_table',
        'view': '_table',
        'tables': [
            {
                'id': 'hostdependencys_table',
                'for': ['external'],
                'name': _('Hosts dependencies table'),
                'template': '_table',
                'icon': 'table',
                'description': _(
                    '<h4>Hosts dependencies table</h4>Displays a datatable for the system '
                    'hosts dependencies.<br>'
                ),
                'actions': {
                    'hostdependencys_table_data': get_hostdependencys_table_data
                }
            }
        ]
    },

    get_hostdependencys_table_data: {
        'name': 'Hosts dependencies table data',
        'route': '/hostdependencys_table_data',
        'method': 'POST'
    },
}
