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
    Plugin Timeperiods
"""

import time
import json

from collections import OrderedDict

from logging import getLogger
from bottle import request, response

from alignak_webui.objects.item import Item
from alignak_webui.objects.item import sort_items_most_recent_first

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
        'title': _('Timeperiod name'),
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
schema['alias'] = {
    'type': 'string',
    'ui': {
        'title': _('Alias'),
        'visible': True
    },
}
schema['is_active'] = {
    'type': 'boolean',
    'ui': {
        'title': _('Currently active'),
        'visible': True
    },
}
schema['dateranges'] = {
    'type': 'list',
    'ui': {
        'title': _('Date ranges'),
        'visible': True
    },
}
schema['exclude'] = {
    'type': 'list',
    'ui': {
        'title': _('Excluded'),
        'visible': True
    },
}


# This to define if the object in this model are to be used in the UI
schema['ui'] = {
    'type': 'boolean',
    'default': True,

    # UI parameters for the objects
    'ui': {
        'page_title': _('Timeperiods table (%d items)'),
        'uid': '_id',
        'visible': True,
        'orderable': True,
        'searchable': True,
        'responsive': True
    }
}


def get_timeperiods():
    """
    Get the timeperiods list
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
    timeperiods = datamgr.get_timeperiods(search)
    # Get last total elements count
    total = datamgr.get_objects_count('timeperiod', search=where, refresh=True)
    count = min(count, total)

    return {
        'timeperiods': timeperiods,
        'pagination': Helper.get_pagination_control('timeperiod', total, start, count),
        'title': request.query.get('title', _('All timeperiods')),
        'elts_per_page': elts_per_page
    }


def get_timeperiods_table():
    """
    Get the timeperiods list and transform it as a table
    """
    datamgr = request.environ['beaker.session']['datamanager']

    # Pagination and search
    where = webui.helper.decode_search(request.query.get('search', ''))

    # Get total elements count
    total = datamgr.get_objects_count('timeperiod', search=where)

    # Build table structure
    dt = Datatable('timeperiod', datamgr.backend, schema)

    title = dt.title
    if '%d' in title:
        title = title % total

    return {
        'object_type': 'timeperiod',
        'dt': dt,
        'title': request.query.get('title', title)
    }


def get_timeperiods_table_data():
    """
    Get the timeperiods list and provide table data
    """
    datamgr = request.environ['beaker.session']['datamanager']
    dt = Datatable('timeperiod', datamgr.backend, schema)

    response.status = 200
    response.content_type = 'application/json'
    return dt.table_data()


pages = {
    get_timeperiods: {
        'name': 'Timeperiods',
        'route': '/timeperiods',
        'view': 'timeperiods',
        'search_engine': False,
        'search_prefix': '',
        'search_filters': {
        }
    },
    get_timeperiods_table: {
        'name': 'Timeperiods table',
        'route': '/timeperiods_table',
        'view': '_table'
    },

    get_timeperiods_table_data: {
        'name': 'Timeperiods table data',
        'route': '/timeperiod_table_data',
        'method': 'POST'
    },
}
