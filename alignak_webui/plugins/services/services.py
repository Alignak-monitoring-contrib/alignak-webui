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
    Plugin Services
"""

import time
import json

from collections import OrderedDict

from logging import getLogger
from bottle import request, response

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
schema['name'] = {
    'type': 'string',
    'ui': {
        'title': _('Service name'),
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
        'title': _('Service alias'),
        'visible': True
    },
}
schema['display_name'] = {
    'type': 'string',
    'ui': {
        'title': _('Service display name'),
        'visible': True
    },
}
schema['host'] = {
    'type': 'objectid',
    'ui': {
        'title': _('Host'),
        'visible': True
    },
    'data_relation': {
        'resource': 'host',
        'embeddable': True
    }
}
schema['hostgroup_name'] = {
    'type': 'string',
    'ui': {
        'title': _('Hosts group name'),
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
        'embeddable': True
    }
}
schema['check_command_args'] = {
    'type': 'string',
    'ui': {
        'title': _('Check command arguments'),
        'visible': True
    },
}
schema['check_period'] = {
    'type': 'objectid',
    'ui': {
        'title': _('Check period'),
        'visible': True
    },
    'data_relation': {
        'resource': 'timeperiod',
        'embeddable': True
    }
}
schema['check_interval'] = {
    'type': 'integer',
    'ui': {
        'title': _('Check interval'),
        'visible': True
    },
}
schema['retry_interval'] = {
    'type': 'integer',
    'ui': {
        'title': _('Retry interval'),
        'visible': True
    },
}
schema['max_check_attempts'] = {
    'type': 'integer',
    'ui': {
        'title': _('Maximum check attempts'),
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
schema['servicegroups'] = {
    'type': 'list',
    'ui': {
        'title': _('Services groups'),
        'visible': True
    },
    'schema': {
        'type': 'objectid',
        'data_relation': {
            'resource': 'servicegroup',
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
schema['business_impact'] = {
    'type': 'integer',
    'ui': {
        'title': _('Business impact'),
        'visible': True
    },
}
schema['contacts'] = {
    'type': 'list',
    'ui': {
        'title': _('Users'),
        'visible': True
    },
    'data_relation': {
        'resource': 'contact',
        'embeddable': True
    }
}
schema['contact_groups'] = {
    'type': 'list',
    'ui': {
        'title': _('Users groups'),
        'visible': True
    },
    'data_relation': {
        'resource': 'contactgroup',
        'embeddable': True
    }
}
schema['notifications_enabled'] = {
    'type': 'boolean',
    'ui': {
        'title': _('Notifications enabled'),
        'visible': True
    },
}
schema['notification_period'] = {
    'type': 'objectid',
    'ui': {
        'title': _('Notification period'),
        'visible': True
    },
    'data_relation': {
        'resource': 'timeperiod',
        'embeddable': True
    }
}
schema['notification_interval'] = {
    'type': 'integer',
    'ui': {
        'title': _('Notification interval'),
        'visible': True
    },
}
schema['first_notification_delay'] = {
    'type': 'integer',
    'ui': {
        'title': _('First notification delay'),
        'visible': True
    },
}
schema['notification_options'] = {
    'type': 'list',
    'default': ['o', 'd', 'u'],
    'allowed': ['o', 'd', 'u'],
    'ui': {
        'title': _('Flapping detection options'),
        'visible': True,
        'format': {
            'list_type': "multichoices",
            'list_allowed': {
                u"d": u"Send notifications on Down state",
                u"r": u"Send notifications on recoveries",
                u"u": u"Send notifications on Unreachable state",
                u"f": u"Send notifications on flapping start/stop",
                u"s": u"Send notifications on scheduled downtime start/stop",
                u"n": u"Do not send notifications"
            }
        }
    },
}
schema['notes'] = {
    'type': 'string',
    'ui': {
        'title': _('Notes')
    }
}
schema['notes_url'] = {
    'type': 'string',
    'ui': {
        'title': _('Notes URL')
    }
}
schema['action_url'] = {
    'type': 'string',
    'ui': {
        'title': _('Action URL')
    }
}
schema['stalking_options'] = {
    'type': 'list',
    'default': [],
    'allowed': ['o', 'd', 'u'],
    'ui': {
        'title': _('Flapping detection options'),
        'visible': True,
        'format': {
            'list_type': "multichoices",
            'list_allowed': {
                u"d": u"Down",
                u"o": u"Up",
                u"u": u"Unreachable"
            }
        }
    },
}
schema['check_freshness'] = {
    'type': 'boolean',
    'ui': {
        'title': _('Freshness check enabled'),
        'visible': True
    },
}
schema['freshness_threshold'] = {
    'type': 'integer',
    'ui': {
        'title': _('Freshness threshold'),
        'visible': True
    },
}
schema['flap_detection_enabled'] = {
    'type': 'boolean',
    'ui': {
        'title': _('Flapping detection enabled'),
        'visible': True
    },
}
schema['flap_detection_options'] = {
    'type': 'list',
    'default': ['o', 'd', 'u'],
    'allowed': ['o', 'd', 'u'],
    'ui': {
        'title': _('Flapping detection options'),
        'visible': True
    },
}
schema['low_flap_threshold'] = {
    'type': 'integer',
    'ui': {
        'title': _('Low flapping threshold'),
        'visible': True,
        'hidden': True,
    },
}
schema['high_flap_threshold'] = {
    'type': 'integer',
    'ui': {
        'title': _('High flapping threshold'),
        'visible': True,
        'hidden': True,
    },
}
schema['event_handler_enabled'] = {
    'type': 'boolean',
    'ui': {
        'title': _('Event handler enabled'),
        'visible': True
    },
}
schema['event_handler'] = {
    'type': 'objectid',
    'ui': {
        'title': _('Event handler command'),
        'visible': True
    },
    'data_relation': {
        'resource': 'command',
        'embeddable': True
    }
}
schema['process_perf_data'] = {
    'type': 'boolean',
    'ui': {
        'title': _('Process performance data'),
        'visible': True
    },
}

# This to define the global information for the table
schema['ui'] = {
    'type': 'boolean',
    'default': True,

    # UI parameters for the objects
    'ui': {
        'page_title': _('Services table (%d items)'),
        'uid': '_id',
        'visible': True,
        'orderable': True,
        'editable': False,
        'selectable': True,
        'searchable': True,
        'responsive': True
    }
}


def get_services():
    """
    Get the services list
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
            'host': 1,
            'check_command': 1, 'event_handler': 1,
            'check_period': 1, 'notification_period': 1,
            'servicegroups': 1, 'contacts': 1, 'contact_groups': 1
        }
    }

    # Get elements from the data manager
    services = datamgr.get_services(search)
    # Get last total elements count
    total = datamgr.get_objects_count('service', search=where, refresh=True)
    count = min(count, total)

    return {
        'services': services,
        'pagination': Helper.get_pagination_control('/services', total, start, count),
        'title': request.query.get('title', _('All services'))
    }


def get_services_table():
    """
    Get the services list and transform it as a table
    """
    datamgr = request.environ['beaker.session']['datamanager']

    # Pagination and search
    where = Helper.decode_search(request.query.get('search', ''))

    # Get total elements count
    total = datamgr.get_objects_count('service', search=where)

    # Build table structure
    dt = Datatable('service', datamgr.backend, schema)

    title = dt.title
    if '%d' in title:
        title = title % total

    return {
        'object_type': 'service',
        'dt': dt,
        'where': where,
        'title': request.query.get('title', title)
    }


def get_services_table_data():
    """
    Get the services list and provide table data
    """
    datamgr = request.environ['beaker.session']['datamanager']
    dt = Datatable('service', datamgr.backend, schema)

    response.status = 200
    response.content_type = 'application/json'
    return dt.table_data()


pages = {
    get_services: {
        'name': 'Services',
        'route': '/services',
        'view': 'services',
        'search_engine': True,
        'search_prefix': '',
        'search_filters': {
            _('Services ok'): 'state:ok',
            _('Services warning'): 'state:warning',
            _('Services critical'): 'state:critical',
        }
    },
    get_services_table: {
        'name': 'Services table',
        'route': '/services_table',
        'view': '_table'
    },

    get_services_table_data: {
        'name': 'Services table data',
        'route': '/service_table_data',
        'method': 'POST'
    },
}
