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
        'title': '#',
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
        'title': _('Realm alias'),
        'visible': True
    },
}
schema['notes'] = {
    'type': 'string',
    'ui': {
        'title': _('Notes')
    }
}
schema['default'] = {
    'type': 'boolean',
    'default': False,
    'ui': {
        'title': _('Default realm'),
        'visible': True,
        'hidden': True
    },
}
schema['_level'] = {
    'type': 'integer',
    'ui': {
        'title': _('Level'),
        'visible': True,
    },
}
schema['_parent'] = {
    'type': 'objectid',
    'ui': {
        'title': _('Parent'),
        'visible': True
    },
    'data_relation': {
        'resource': 'realm',
        'embeddable': True
    }
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
        'editable': False,
        'selectable': True,
        'searchable': False,
        'responsive': True
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


def get_realms():
    """
    Get the realms list
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
        }
    }

    # Get elements from the data manager
    items = datamgr.get_realms(search)
    # Get last total elements count
    total = datamgr.get_objects_count('realm', search=where, refresh=True)
    count = min(count, total)

    # Define contextual menu
    context_menu = {
        'actions': {
            'action1': {
                "label": "Cueillir des fraises...",
                "icon": "ion-monitor",
                "separator_before": False,
                "separator_after": True,
                "action": '''function (obj) {
                   console.log('Miam!');
                }'''
            },
            'action2': {
                "label": "... et encore des fraises!",
                "icon": "ion-monitor",
                "separator_before": False,
                "separator_after": False,
                "action": '''function (obj) {
                   console.log('Et que ça saute !');
                }'''
            }
        }
    }

    return {
        'object_type': 'realm',
        'items': items,
        'selectable': False,
        'context_menu': context_menu,
        'pagination': Helper.get_pagination_control('realm', total, start, count),
        'title': request.query.get('title', _('All realms'))
    }


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
    get_realms: {
        'name': 'Realms',
        'route': '/realms',
        'view': '_tree',
        'search_engine': False,
        'search_prefix': '',
        'search_filters': {
        }
    },

    get_realm_table: {
        'name': 'Realms table',
        'route': '/realm_table',
        'view': '_table'
    },

    get_realm_table_data: {
        'name': 'Realms table data',
        'route': '/realm_table_data',
        'method': 'POST'
    },
}
