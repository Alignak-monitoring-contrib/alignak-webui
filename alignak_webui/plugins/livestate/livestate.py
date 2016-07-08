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
    Plugin Livestate
"""

import time
import json

from collections import OrderedDict

from logging import getLogger
from bottle import request, response, redirect, template

from alignak_webui.objects.item import Item
from alignak_webui.plugins.common.common import get_widget

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
# Specific field to include the commands button
# schema['$'] = {
# 'type': 'string',
# 'ui': {
# 'title': '<i class="fa fa-bolt"></i>',
# 'visible': True,
# 'hidden': False,
# 'searchable': False,
# 'selectable': True,
# 'orderable': False,
# 'regex': False,
# }
# }
schema['type'] = {
    'type': 'string',
    'ui': {
        'title': _('Type'),
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
    },
    'allowed': ["host", "service"]
}
schema['name'] = {
    'type': 'string',
    'ui': {
        'title': _('Element name'),
        'width': '50px',
        'visible': True,
        # 'priority': 0,
    }
}
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
schema['display_name_host'] = {
    'type': 'string',
    'ui': {
        'title': _('Host display name'),
        'width': '10',
        'visible': True,
        'hidden': True,
    },
}
schema['service'] = {
    'type': 'objectid',
    'ui': {
        'title': _('Service'),
        'width': '10px',
        'visible': True,
        'hidden': True,
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
        'hidden': True,
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
schema['last_check'] = {
    'type': 'integer',
    'ui': {
        'title': _('Last check'),
        'format': 'date',
        'visible': True
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
schema['downtime'] = {
    'type': 'boolean',
    'ui': {
        'title': _('In scheduled downtime'),
        'visible': True,
        'width': '20px',
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
        'title': _('Last state changed'),
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
        'page_title': _('Livestate table (%d items)'),
        'uid': '_id',
        'visible': True,
        'orderable': True,
        'editable': False,
        'selectable': True,
        'searchable': True,
        'responsive': True,

        # Sort by descending business impact
        'initial_sort': [[9, "desc"]]
    }
}


def get_livestate_table(embedded=False, identifier=None, credentials=None):
    """
    Get the livestate list and transform it as a table
    """
    datamgr = request.environ['beaker.session']['datamanager']

    # Pagination and search
    where = Helper.decode_search(request.query.get('search', ''))

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
        'where': where,
        'title': request.query.get('title', title),
        'embedded': embedded,
        'identifier': identifier,
        'credentials': credentials
    }


def get_livestate_table_data():
    """
    Get the livestate list and provide table data
    """
    datamgr = request.environ['beaker.session']['datamanager']
    dt = Datatable('livestate', datamgr.backend, schema)

    response.status = 200
    response.content_type = 'application/json'
    return dt.table_data()


def get_livestate(livestate_id):
    """
    Display the element linked to a livestate item
    """
    datamgr = request.environ['beaker.session']['datamanager']

    livestate = datamgr.get_livestate({'where': {'_id': livestate_id}})
    if not livestate:
        return webui.response_invalid_parameters(_('Livestate element does not exist'))

    livestate = livestate[0]
    if livestate.type == 'host':
        logger.debug("Livestate: %s %s %s", livestate, livestate.host.id, livestate.__dict__)
        redirect('/host/' + livestate.host.id)
    else:
        logger.debug("Livestate: %s %s %s", livestate, livestate.host.id, livestate.__dict__)
        redirect('/host/' + livestate.host.id + '#services')


def get_livestate_widget(embedded=False, identifier=None, credentials=None):
    # Because there are many locals needed :)
    # pylint: disable=too-many-locals
    """
    Get the livestate as a widget
    - widget_id: widget identifier

    - start and count for pagination
    - search for specific elements search

    """
    datamgr = request.environ['beaker.session']['datamanager']
    return get_widget(datamgr.get_livestate, 'livestate', embedded, identifier, credentials)


pages = {
    get_livestate: {
        'name': 'Livestate',
        'route': '/livestate/<livestate_id>'
    },
    get_livestate_table: {
        'name': 'Livestate table',
        'route': '/livestate_table',
        'view': '_table',
        'tables': [
            {
                'id': 'livestate_table',
                'for': ['external'],
                'name': _('Livestate table'),
                'template': '_table',
                'icon': 'table',
                'description': _(
                    '<h4>Livestate table</h4>Displays a datatable for the monitored '
                    'system livestate.<br>'
                ),
                'actions': {
                    'livestate_table_data': get_livestate_table_data
                }
            }
        ]
    },

    get_livestate_table_data: {
        'name': 'Livestate table data',
        'route': '/livestate_table_data',
        'method': 'POST'
    },

    get_livestate_widget: {
        'name': 'Livestate widget',
        'route': '/livestate/widget',
        'method': 'POST',
        'view': 'livestate_widget',
        'widgets': [
            {
                'id': 'livestate_table',
                'for': ['external', 'dashboard'],
                'name': _('Livestate table'),
                'template': 'livestate_table_widget',
                'icon': 'table',
                'description': _(
                    '<h4>Livestate table widget</h4>Displays a list of the live state of the'
                    'monitored system hosts and services.<br>'
                    'The number of hosts/services in this list can be defined in the widget '
                    'options. The list of hosts/services can be filtered thanks to regex on the '
                    'host/service name.'
                ),
                'picture': 'htdocs/img/livestate_table_widget.png',
                'options': {
                    'search': {
                        'value': '',
                        'type': 'text',
                        'label': _('Filter (ex. status:up)')
                    },
                    'count': {
                        'value': -1,
                        'type': 'int',
                        'label': _('Number of elements')
                    },
                    'filter': {
                        'value': '',
                        'type': 'hst_srv',
                        'label': _('Host/service name search')
                    }
                }
            },
            {
                'id': 'livestate_hosts_chart',
                'for': ['external', 'dashboard'],
                'name': _('Livestate hosts chart'),
                'template': 'livestate_hosts_chart_widget',
                'icon': 'pie-chart',
                'description': _(
                    '<h4>Hosts livestate chart widget</h4>Displays a pie chart with the monitored'
                    'system hosts states.'
                ),
                'picture': 'htdocs/img/livestate_hosts_chart_widget.png',
                'options': {}
            },
            {
                'id': 'livestate_services_chart',
                'for': ['external', 'dashboard'],
                'name': _('Livestate services chart'),
                'template': 'livestate_services_chart_widget',
                'icon': 'pie-chart',
                'description': _(
                    '<h4>Services livestate chart widget</h4>Displays a pie chart with the '
                    'monitored system services states.'
                ),
                'picture': 'htdocs/img/livestate_services_chart_widget.png',
                'options': {}
            },
            {
                'id': 'livestate_hosts_history_chart',
                'for': ['external', 'dashboard'],
                'name': _('Livestate hosts history chart'),
                'template': 'livestate_hosts_history_chart_widget',
                'icon': 'pie-chart',
                'description': _(
                    '<h4>Hosts livestate history chart widget</h4>Displays a line chart with '
                    'the monitored system hosts states on a recent period of time.'
                ),
                'picture': 'htdocs/img/livestate_hosts_history_chart_widget.png',
                'options': {}
            },
            {
                'id': 'livestate_services_history_chart',
                'for': ['external', 'dashboard'],
                'name': _('Livestate services history chart'),
                'template': 'livestate_services_history_chart_widget',
                'icon': 'pie-chart',
                'description': _(
                    '<h4>Services livestate history chart widget</h4>Displays a line chart with '
                    'the monitored system sevices states on a recent period of time.'
                ),
                'picture': 'htdocs/img/livestate_services_history_chart_widget.png',
                'options': {}
            },
            {
                'id': 'livestate_hosts_counters',
                'for': ['external', 'dashboard'],
                'name': _('Livestate hosts counters'),
                'template': 'livestate_hosts_counters_widget',
                'icon': 'plus-square',
                'description': _(
                    '<h4>Hosts livestate counters widget</h4>Displays counters about the '
                    'monitored system hosts states.'
                ),
                'picture': 'htdocs/img/livestate_hosts_counters_widget.png',
                'options': {}
            },
            {
                'id': 'livestate_services_counters',
                'for': ['external', 'dashboard'],
                'name': _('Livestate services counters'),
                'template': 'livestate_services_counters_widget',
                'icon': 'plus-square',
                'description': _(
                    '<h4>Services livestate counters widget</h4>Displays counters about the '
                    'monitored system services states.'
                ),
                'picture': 'htdocs/img/livestate_services_counters_widget.png',
                'options': {}
            },
            {
                'id': 'livestate_hosts_sla',
                'for': ['external', 'dashboard'],
                'name': _('Livestate hosts SLA'),
                'template': 'livestate_hosts_sla_widget',
                'icon': 'life-saver',
                'description': _(
                    '<h4>Hosts livestate SLA widget</h4>Displays counters and SLA level about the '
                    'monitored system hosts states.'
                ),
                'picture': 'htdocs/img/livestate_hosts_sla_widget.png',
                'options': {}
            },
            {
                'id': 'livestate_services_sla',
                'for': ['external', 'dashboard'],
                'name': _('Livestate services SLA'),
                'template': 'livestate_services_sla_widget',
                'icon': 'life-saver',
                'description': _(
                    '<h4>Hosts livestate SLA widget</h4>Displays counters and SLA level about the '
                    'monitored system services states.'
                ),
                'picture': 'htdocs/img/livestate_services_sla_widget.png',
                'options': {}
            },
        ]
    },
}
