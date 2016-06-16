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
    Plugin Realm
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
schema['name'] = {
    'type': 'string',
    'ui': {
        'title': _('Realm name'),
        'width': '10px',
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
    }
}
schema['realm_members'] = {
    'type': 'list',
    'ui': {
        'title': _('Realm members'),
        'visible': True
    },
    'data_relation': {
        'resource': 'realm',
        'embeddable': True
    }
}
schema['default'] = {
    'type': 'boolean',
    'default': False,
    'ui': {
        'title': _('Deafult realm'),
        'visible': True,
        'hidden': True
    },
}
schema['hosts_critical_threshold'] = {
    'type': 'integer',
    'min': 0,
    'max': 100,
    'default': 5,
    'ui': {
        'title': _('Hosts critical threshold'),
        'visible': True,
        'hidden': False
    },
}
schema['hosts_warning_threshold'] = {
    'type': 'integer',
    'min': 0,
    'max': 100,
    'default': 5,
    'ui': {
        'title': _('Hosts warning threshold'),
        'visible': True,
        'hidden': False
    },
}
schema['services_critical_threshold'] = {
    'type': 'integer',
    'min': 0,
    'max': 100,
    'default': 5,
    'ui': {
        'title': _('Services critical threshold'),
        'visible': True,
        'hidden': False
    },
}
schema['services_warning_threshold'] = {
    'type': 'integer',
    'min': 0,
    'max': 100,
    'default': 5,
    'ui': {
        'title': _('Services warning threshold'),
        'visible': True,
        'hidden': False
    },
}
schema['globals_critical_threshold'] = {
    'type': 'integer',
    'min': 0,
    'max': 100,
    'default': 5,
    'ui': {
        'title': _('Global critical threshold'),
        'visible': True,
        'hidden': False
    },
}
schema['globals_warning_threshold'] = {
    'type': 'integer',
    'min': 0,
    'max': 100,
    'default': 5,
    'ui': {
        'title': _('Global warning threshold'),
        'visible': True,
        'hidden': False
    },
}


# This to define the global information for the table
schema['ui'] = {
    'type': 'boolean',
    'default': True,

    # UI parameters for the objects
    'ui': {
        'page_title': _('Realm table (%d items)'),
        'uid': '_id',
        'visible': True,
        'orderable': True,
        'searchable': True,
        'responsive': False
    }
}


def get_realm_table():
    """
    Get the realm list and transform it as a table
    """
    datamgr = request.environ['beaker.session']['datamanager']

    # Pagination and search
    where = webui.helper.decode_search(request.query.get('search', ''))

    # Get total elements count
    total = datamgr.get_objects_count('realm', search=where)

    # Build table structure
    dt = Datatable('realm', datamgr.backend, schema)

    title = dt.title
    if '%d' in title:
        title = title % total

    return {
        'object_type': 'realm',
        'dt': dt,
        'title': request.query.get('title', title)
    }


def get_realm_table_data():
    """
    Get the realm list and provide table data
    """
    datamgr = request.environ['beaker.session']['datamanager']
    dt = Datatable('realm', datamgr.backend, schema)

    response.status = 200
    response.content_type = 'application/json'
    return dt.table_data()


def get_realm(realm_id):
    """
    Display the element linked to a realm item
    """
    datamgr = request.environ['beaker.session']['datamanager']

    realm = datamgr.get_realm({'where': {'_id': realm_id}})
    if not realm:  # pragma: no cover, should not happen
        return webui.response_invalid_parameters(_('Realm element does not exist'))

    return {
        'realm_id': realm_id,
        'realm': realm,
        'title': request.query.get('title', _('Realm view'))
    }


pages = {
    get_realm: {
        'name': 'Realm',
        'route': '/realm/<realm_id>',
        'view': 'realm'
    },
    get_realm_table: {
        'name': 'Realm table',
        'route': '/realm_table',
        'view': '_table'
    },

    get_realm_table_data: {
        'name': 'Realm table data',
        'route': '/realm_table_data',
        'method': 'POST'
    },
}
