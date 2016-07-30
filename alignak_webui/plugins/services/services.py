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

import json
from collections import OrderedDict
from logging import getLogger

from bottle import request, template, response

from alignak_webui import _
from alignak_webui.plugins.common.common import get_table, get_table_data

logger = getLogger(__name__)

# Will be populated by the UI with it's own value
webui = None

# Declare backend element endpoint
backend_endpoint = 'service'

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
schema['_realm'] = {
    'type': 'objectid',
    'ui': {
        'title': _('Realm'),
        'visible': True,
        'hidden': True,
        'searchable': True
    },
    'data_relation': {
        'resource': 'realm',
        'embeddable': True
    }
}
schema['_is_template'] = {
    'type': 'boolean',
    'ui': {
        'title': _('Template'),
        'visible': True,
        'hidden': True
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
schema['tags'] = {
    'type': 'list',
    'default': [],
    'ui': {
        'title': _('Tags'),
        'visible': True,
    }
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
schema['notes'] = {
    'type': 'string',
    'ui': {
        'title': _('Notes')
    }
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
schema['customs'] = {
    'type': 'list',
    'default': [],
    'ui': {
        'title': _('Customs'),
        'visible': True,
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
    'default': ['w', 'u', 'c', 'r', 'f', 's'],
    'allowed': ['w', 'u', 'c', 'r', 'f', 's', 'n'],
    'ui': {
        'title': _('Flapping detection options'),
        'visible': True,
        'format': {
            'list_type': "multichoices",
            'list_allowed': {
                u"w": u"Send notifications on Warning state",
                u"c": u"Send notifications on Critical state",
                u"u": u"Send notifications on Unknown state",
                u"r": u"Send notifications on recovery",
                u"f": u"Send notifications on flapping start/stop",
                u"s": u"Send notifications on scheduled downtime start/stop",
                u"n": u"Do not send notifications"
            }
        }
    },
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
        'id_property': '_id',
        'visible': True,
        'orderable': True,
        'editable': False,
        'selectable': True,
        'searchable': True,
        'responsive': False
    }
}


def get_services(templates=False):
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
        'page': start // (count + 1),
        'max_results': count,
        'where': where
    }

    # Get elements from the data manager
    services = datamgr.get_services(search, template=templates)
    # Get last total elements count
    total = datamgr.get_objects_count('service', search=where, refresh=True)
    count = min(count, total)

    if request.params.get('list', None):
        return get_services_list()

    return {
        'services': services,
        'pagination': webui.helper.get_pagination_control('/services', total, start, count),
        'title': request.query.get('title', _('All services'))
    }


def get_services_list(embedded=False):
    # pylint: disable=unused-argument
    """
    Get the services list
    """
    datamgr = request.environ['beaker.session']['datamanager']

    # Get elements from the data manager
    search = {'projection': json.dumps({"_id": 1, "name": 1, "alias": 1})}
    services = datamgr.get_services(search, all_elements=True)

    items = []
    for service in services:
        items.append({'id': service.id, 'name': service.name, 'alias': service.alias})

    response.status = 200
    response.content_type = 'application/json'
    return json.dumps(items)


def get_services_table(embedded=False, identifier=None, credentials=None):
    """
    Get the elements to build a table
    """
    return get_table('service', schema, embedded, identifier, credentials)


def get_services_table_data():
    """
    Get the elements required by the table
    """
    return get_table_data('service', schema)


def get_services_templates():
    """
    Get the services templates list
    """
    return get_services(templates=True)


def get_services_widget(embedded=False, identifier=None, credentials=None):
    # Because there are many locals needed :)
    # pylint: disable=too-many-locals
    """
    Get the services list as a widget
    - widget_id: widget identifier

    - start and count for pagination
    - search for specific elements search

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
    start = int(request.params.get('start', '0'))
    count = int(request.params.get('count', elts_per_page))
    where = webui.helper.decode_search(request.params.get('search', ''))
    search = {
        'page': start // (count + 1),
        'max_results': count,
        'where': where
    }
    name_filter = request.params.get('filter', '')
    if name_filter:
        search['where'].update({
            '$or': [
                {'name': {'$regex': ".*%s.*" % name_filter}},
                {'alias': {'$regex': ".*%s.*" % name_filter}}
            ]
        })
    logger.info("Search parameters: %s", search)

    # Get elements from the data manager
    services = datamgr.get_services(search)
    # Get last total elements count
    total = datamgr.get_objects_count('service', search=where, refresh=True)
    count = min(count, total)

    # Widget options
    widget_id = request.params.get('widget_id', '')
    if widget_id == '':
        return webui.response_invalid_parameters(_('Missing widget identifier'))

    widget_place = request.params.get('widget_place', 'dashboard')
    widget_template = request.params.get('widget_template', 'services_table_widget')
    widget_icon = request.params.get('widget_icon', 'plug')
    # Search in the application widgets (all plugins widgets)
    options = {}
    for widget in webui.widgets[widget_place]:
        if widget_id.startswith(widget['id']):
            options = widget['options']
            widget_template = widget['template']
            widget_icon = widget['icon']
            logger.info("Widget found, template: %s, options: %s", widget_template, options)
            break
    else:
        logger.warning("Widget identifier not found: %s", widget_id)
        return webui.response_invalid_parameters(_('Unknown widget identifier'))

    if options:
        options['search']['value'] = request.params.get('search', '')
        options['count']['value'] = count
        options['filter']['value'] = name_filter
    logger.info("Widget options: %s", options)

    title = request.params.get('title', _('Hosts'))
    if name_filter:
        title = _('%s (%s)') % (title, name_filter)

    # Use required template to render the widget
    return template('_widget', {
        'widget_id': widget_id,
        'widget_name': widget_template,
        'widget_place': widget_place,
        'widget_template': widget_template,
        'widget_icon': widget_icon,
        'widget_uri': request.urlparts.path,
        'services': services,
        'options': options,
        'title': title,
        'embedded': embedded,
        'identifier': identifier,
        'credentials': credentials
    })


pages = {
    get_services: {
        'routes': [
            ('/services', 'Services'),
        ],
        'view': 'services'
    },
    get_services_list: {
        'routes': [
            ('/services_list', 'Services list'),
        ]
    },
    get_services_templates: {
        'routes': [
            ('/services_templates', 'Services templates'),
        ]
    },
    get_services_table: {
        'routes': [
            ('/services_table', 'Services table')
        ],
        'view': '_table',
        'search_engine': True,
        'search_prefix': '',
        'search_filters': {
            '01': (_('Services'), '_is_template:false'),
            '02': ('', ''),
            '03': (_('Services templates'), '_is_template:true')
        },
        'tables': [
            {
                'id': 'services_table',
                'for': ['external'],
                'name': _('Services table'),
                'template': '_table',
                'icon': 'table',
                'description': _(
                    '<h4>Services table</h4>Displays a datatable for the system '
                    'services.<br>'
                ),
                'actions': {
                    'services_table_data': get_services_table_data
                }
            }
        ]
    },

    get_services_table_data: {
        'routes': [
            ('/services_table_data', 'Services table data')
        ],
        'method': 'POST'
    },

    get_services_widget: {
        'routes': [
            ('/services/widget', 'Services widget')
        ],
        'method': 'POST',
        'view': 'services_widget',
        'widgets': [
            {
                'id': 'services_table',
                'for': ['external', 'dashboard'],
                'name': _('Services table widget'),
                'template': 'services_table_widget',
                'icon': 'table',
                'description': _(
                    '<h4>Services table widget</h4>Displays a list of the monitored system '
                    'services.<br>The number of services in this list can be defined in the widget '
                    'options. The list of services can be filtered thanks to regex on the '
                    'service name'
                ),
                'picture': 'htdocs/img/services_table_widget.png',
                'options': {
                    'search': {
                        'value': '',
                        'type': 'text',
                        'label': _('Filter (ex. status:ok)')
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
                'id': 'services_chart',
                'for': ['external', 'dashboard'],
                'name': _('Services chart widget'),
                'template': 'services_chart_widget',
                'icon': 'pie-chart',
                'description': _(
                    '<h4>Services chart widget</h4>Displays a pie chart with the system '
                    'services states.'
                ),
                'picture': 'htdocs/img/services_chart_widget.png',
                'options': {}
            }
        ]
    },
}
