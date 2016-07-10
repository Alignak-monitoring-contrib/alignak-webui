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
    Plugin Hosts
"""

import time
import json

from collections import OrderedDict

from logging import getLogger
from bottle import request, template, response

from alignak_webui.objects.item import Item

from alignak_webui.plugins.histories.histories import schema as history_schema

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
        'title': _('Host name'),
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
schema['_is_template'] = {
    'type': 'boolean',
    'ui': {
        'title': _('Is an host template'),
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
schema['alias'] = {
    'type': 'string',
    'ui': {
        'title': _('Host alias'),
        'visible': True
    },
}
schema['display_name'] = {
    'type': 'string',
    'ui': {
        'title': _('Host display name'),
        'visible': True
    },
}
schema['address'] = {
    'type': 'string',
    'ui': {
        'title': _('Address'),
        'visible': True
    },
}
schema['check_command'] = {
    'type': 'objectid',
    'ui': {
        'title': _('Check command'),
        'visible': True,
        'searchable': False
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
        'visible': True,
        'searchable': False
    },
}
schema['check_period'] = {
    'type': 'objectid',
    'ui': {
        'title': _('Check period'),
        'visible': True,
        # 'searchable': False
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
schema['parents'] = {
    'type': 'list',
    'ui': {
        'title': _('Parents'),
        'visible': True,
        'searchable': False
    },
    'data_relation': {
        'resource': 'host',
        'embeddable': True
    }
}
schema['hostgroups'] = {
    'type': 'list',
    'ui': {
        'title': _('Hosts groups'),
        'visible': True,
        'searchable': False
    },
    'data_relation': {
        'resource': 'hostgroup',
        'embeddable': True
    }
}
schema['business_impact'] = {
    'type': 'integer',
    'ui': {
        'title': _('Business impact'),
        'visible': True
    },
}
schema['users'] = {
    'type': 'list',
    'ui': {
        'title': _('Users'),
        'visible': True,
        'searchable': False
    },
    'data_relation': {
        'resource': 'user',
        'embeddable': True
    }
}
schema['usergroups'] = {
    'type': 'list',
    'ui': {
        'title': _('Users groups'),
        'visible': True,
        'searchable': False
    },
    'data_relation': {
        'resource': 'usergroup',
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
schema['maintenance_period'] = {
    'type': 'objectid',
    'ui': {
        'title': _('Maintenance period'),
        'visible': True,
        'hidden': True
    },
    'data_relation': {
        'resource': 'timeperiod',
        'embeddable': True
    }
}
schema['snapshot_period'] = {
    'type': 'objectid',
    'ui': {
        'title': _('Snapshot period'),
        'visible': True,
        'hidden': True
    },
    'data_relation': {
        'resource': 'timeperiod',
        'embeddable': True
    }
}
schema['location'] = {
    'type': 'point',
    'ui': {
        'title': _('Location')
    }
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
        'visible': True,
        'searchable': False
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
        'page_title': _('Hosts table (%d items)'),
        'uid': '_id',
        'visible': True,
        'orderable': True,
        'editable': False,
        'selectable': True,
        'searchable': True,
        'responsive': True
    }
}


def get_hosts(templates=False):
    """
    Get the hosts list
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
        'page': start // count + 1,
        'max_results': count,
        'where': where,
    }

    # Get elements from the data manager
    hosts = datamgr.get_hosts(search, template=templates)
    # Get last total elements count
    total = datamgr.get_objects_count('host', search=where, refresh=True)
    count = min(count, total)

    return {
        'hosts': hosts,
        'pagination': Helper.get_pagination_control(
            '/hosts_templates' if templates else '/hosts', total, start, count
        ),
        'title': request.params.get('title', _('All hosts'))
    }


def get_hosts_templates():
    """
    Get the hosts templates list
    """
    return get_hosts(templates=True)


def get_hosts_widget(embedded=False, identifier=None, credentials=None):
    # Because there are many locals needed :)
    # pylint: disable=too-many-locals
    """
    Get the hosts list as a widget
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
        'page': start // count + 1,
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
    hosts = datamgr.get_hosts(search)
    # Get last total elements count
    total = datamgr.get_objects_count('host', search=where, refresh=True)
    count = min(count, total)

    # Widget options
    widget_id = request.params.get('widget_id', '')
    if widget_id == '':
        return webui.response_invalid_parameters(_('Missing widget identifier'))

    widget_place = request.params.get('widget_place', 'dashboard')
    widget_template = request.params.get('widget_template', 'hosts_table_widget')
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
        'hosts': hosts,
        'options': options,
        'title': title,
        'embedded': embedded,
        'identifier': identifier,
        'credentials': credentials
    })


def get_hosts_table(embedded=False, identifier=None, credentials=None):
    """
    Get the hosts list and transform it as a table
    """
    datamgr = request.environ['beaker.session']['datamanager']

    # Pagination and search
    where = Helper.decode_search(request.params.get('search', ''))

    # Get total elements count
    total = datamgr.get_objects_count('host', search=where)

    # Build table structure
    dt = Datatable('host', datamgr.backend, schema)

    title = dt.title
    if '%d' in title:
        title = title % total

    return {
        'object_type': 'host',
        'dt': dt,
        'where': where,
        'title': request.params.get('title', title),
        'embedded': embedded,
        'identifier': identifier,
        'credentials': credentials
    }


def get_hosts_table_data():
    """
    Get the hosts list and provide table data
    """
    datamgr = request.environ['beaker.session']['datamanager']
    dt = Datatable('host', datamgr.backend, schema)

    response.status = 200
    response.content_type = 'application/json'
    return dt.table_data()


def get_host(host_id):
    # Because there are many locals needed :)
    # pylint: disable=too-many-locals
    """
    Display an host
    """
    user = request.environ['beaker.session']['current_user']
    datamgr = request.environ['beaker.session']['datamanager']
    target_user = request.environ['beaker.session']['target_user']

    username = user.get_username()
    if not target_user.is_anonymous():
        username = target_user.get_username()

    # Get host
    host = datamgr.get_host(host_id)
    if not host:  # pragma: no cover, should not happen
        return webui.response_invalid_parameters(_('Host does not exist'))

    # Get host services
    services = datamgr.get_services(search={'where': {'host': host_id}})

    # Get host livestate
    livestate = datamgr.get_livestate(
        search={'where': {'type': 'host', 'name': '%s' % host.name}}
    )
    if livestate:
        livestate = livestate[0]

    # Get host services livestate
    livestate_services = datamgr.get_livestate(
        search={'where': {'type': 'service', 'host': host.id}}
    )

    # Fetch elements per page preference for user, default is 25
    elts_per_page = datamgr.get_user_preferences(username, 'elts_per_page', 25)
    elts_per_page = elts_per_page['value']

    # Host history pagination and search parameters
    start = int(request.params.get('start', '0'))
    count = int(request.params.get('count', elts_per_page))
    where = webui.helper.decode_search(request.params.get('search', ''))
    search = {
        'page': start // count + 1,
        'max_results': count,
        'where': {'host': host_id}
    }

    # Fetch timeline filters preference for user, default is []
    selected_types = datamgr.get_user_preferences(username, 'timeline_filters', [])
    selected_types = selected_types['value']
    for selected_type in history_schema['type']['allowed']:
        if request.params.get(selected_type) == 'true':
            if selected_type not in selected_types:
                selected_types.append(selected_type)
        elif request.params.get(selected_type) == 'false':
            if selected_type in selected_types:
                selected_types.remove(selected_type)

    datamgr.set_user_preferences(username, 'timeline_filters', selected_types)
    if selected_types:
        search['where'].update({'type': {'$in': selected_types}})
    logger.warning("History selected types: %s", selected_types)

    history = datamgr.get_history(search=search)
    if history is None:
        history = []

    # Get last total elements count
    total = datamgr.get_objects_count('history', search=where, refresh=True)

    return {
        'host': host,
        'services': services,
        'livestate': livestate,
        'livestate_services': livestate_services,
        'history': history,
        'timeline_pagination': Helper.get_pagination_control('/host/' + host_id,
                                                             total, start, count),
        'types': history_schema['type']['allowed'],
        'selected_types': selected_types,
        'title': request.params.get('title', _('Host view'))
    }


def get_host_widget(host_id, widget_id, embedded=False, identifier=None, credentials=None):
    # Because there are many locals needed :)
    # pylint: disable=too-many-locals
    """
    Display an host
    """
    user = request.environ['beaker.session']['current_user']
    datamgr = request.environ['beaker.session']['datamanager']
    target_user = request.environ['beaker.session']['target_user']

    username = user.get_username()
    if not target_user.is_anonymous():
        username = target_user.get_username()

    # Get host
    host = datamgr.get_host(host_id)
    if not host:  # pragma: no cover, should not happen
        return webui.response_invalid_parameters(_('Host does not exist'))

    # Get host services
    services = datamgr.get_services(search={'where': {'host': host_id}})

    # Get host livestate
    livestate = datamgr.get_livestate(
        search={'where': {'type': 'host', 'name': '%s' % host.name}}
    )
    if livestate:
        livestate = livestate[0]

    # Get host services livestate
    livestate_services = datamgr.get_livestate(
        search={'where': {'type': 'service', 'host': host.id}}
    )

    # Fetch elements per page preference for user, default is 25
    elts_per_page = datamgr.get_user_preferences(username, 'elts_per_page', 25)
    elts_per_page = elts_per_page['value']

    # Host history pagination and search parameters
    start = int(request.params.get('start', '0'))
    count = int(request.params.get('count', elts_per_page))
    where = webui.helper.decode_search(request.params.get('search', ''))
    search = {
        'where': {'host': host_id}
    }

    # Fetch timeline filters preference for user, default is []
    selected_types = datamgr.get_user_preferences(username, 'timeline_filters', [])
    selected_types = selected_types['value']
    for selected_type in history_schema['type']['allowed']:
        if request.params.get(selected_type) == 'true':
            if selected_type not in selected_types:
                selected_types.append(selected_type)
        elif request.params.get(selected_type) == 'false':
            if selected_type in selected_types:
                selected_types.remove(selected_type)

    if selected_types:
        datamgr.set_user_preferences(username, 'timeline_filters', selected_types)
        search['where'].update({'type': {'$in': selected_types}})
    logger.warning("History selected types: %s", selected_types)

    history = datamgr.get_history(search=search)
    if history is None:
        history = []

    # Get last total elements count
    total = datamgr.get_objects_count('history', search=where, refresh=True)

    widget_place = request.params.get('widget_place', 'host')
    widget_template = request.params.get('widget_template', 'host_widget')
    # Search in the application widgets (all plugins widgets)
    for widget in webui.widgets[widget_place]:
        if widget_id.startswith(widget['id']):
            widget_template = widget['template']
            logger.info("Widget found, template: %s", widget_template)
            break
    else:
        logger.info("Widget identifier not found: using default template and no options")

    title = request.params.get('title', _('Host: %s') % host.name)

    # Use required template to render the widget
    return template('_widget', {
        'widget_id': widget_id,
        'widget_name': widget_template,
        'widget_place': 'host',
        'widget_template': widget_template,
        'widget_uri': request.urlparts.path,
        'options': {},

        'host': host,
        'services': services,
        'livestate': livestate,
        'livestate_services': livestate_services,
        'history': history,
        'timeline_pagination': Helper.get_pagination_control('/host/' + host_id,
                                                             total, start, count),
        'types': history_schema['type']['allowed'],
        'selected_types': selected_types,

        'title': title,
        'embedded': embedded,
        'identifier': identifier,
        'credentials': credentials
    })


pages = {
    get_host_widget: {
        'name': 'Host widget',
        'route': '/host_widget/<host_id>/<widget_id>',
        'view': 'host',
        'widgets': [
            {
                'id': 'information',
                'for': ['host'],
                'name': _('Information'),
                'template': 'host_information_widget',
                'icon': 'info',
                'description': _(
                    'Host information: displays host general information.'
                ),
                'options': {}
            },
            {
                'id': 'configuration',
                'for': ['host'],
                'name': _('Configuration'),
                'template': 'host_configuration_widget',
                'icon': 'gear',
                'read_only': True,
                'description': _(
                    'Host configuration: displays host customs configuration variables.'
                ),
                'options': {}
            },
            {
                'id': 'services',
                'for': ['host'],
                'name': _('Services'),
                'template': 'host_services_widget',
                'icon': 'cubes',
                'description': _(
                    '<h4>Host service widget</h4>Displays host services.'
                ),
                'options': {}
            },
            {
                'id': 'timeline',
                'for': ['host'],
                'name': _('Timeline'),
                'template': 'host_timeline_widget',
                'icon': 'clock-o',
                'description': _(
                    '<h4>Host timeline widget</h4>Displays host timeline.'
                ),
                'picture': 'htdocs/img/host_timeline_widget.png',
                'options': {}
            },
            {
                'id': 'metrics',
                'for': ['host'],
                'name': _('Metrics'),
                'template': 'host_metrics_widget',
                'icon': 'line-chart',
                'description': _(
                    '<h4>Host metrics widget</h4>Displays host (and its services) last '
                    'received metrics.'
                ),
                'picture': 'htdocs/img/host_metrics_widget.png',
                'options': {}
            },
            {
                'id': 'history',
                'for': ['host'],
                'name': _('History'),
                'template': 'host_history_widget',
                'icon': 'history',
                'description': _(
                    '<h4>Host history widget</h4>Displays host history.'
                ),
                'options': {}
            },
            {
                'id': 'grafana',
                'for': ['host'],
                'name': _('Grafana'),
                'template': 'host_grafana_widget',
                'icon': 'area-chart',
                'description': _(
                    '<h4>Host grafana widget</h4>Displays host Grafana panel.'
                ),
                'options': {}
            }
        ]
    },
    get_host: {
        'name': 'Host',
        'route': '/host/<host_id>',
        'view': 'host'
    },
    get_hosts: {
        'name': 'Hosts',
        'route': '/hosts',
        'view': 'hosts',
        'search_engine': True,
        'search_prefix': '',
        'search_filters': {
            _('Hosts up'): 'state:up',
            _('Hosts down'): 'state:down',
            _('Hosts unreachable'): 'state:unreachable',
        }
    },
    get_hosts_templates: {
        'name': 'Hosts templates',
        'route': '/hosts_templates'
    },

    get_hosts_table: {
        'name': 'Hosts table',
        'route': '/hosts_table',
        'view': '_table',
        'tables': [
            {
                'id': 'hosts_table',
                'for': ['external'],
                'name': _('Hosts table'),
                'template': '_table',
                'icon': 'table',
                'description': _(
                    '<h4>Hosts table</h4>Displays a datatable for the monitored system hosts.<br>'
                ),
                'actions': {
                    'host_table_data': get_hosts_table_data
                }
            }
        ]
    },

    get_hosts_table_data: {
        'name': 'Hosts table data',
        'route': '/host_table_data',
        'method': 'POST'
    },

    get_hosts_widget: {
        'name': 'Hosts widget',
        'route': '/hosts/widget',
        'method': 'POST',
        'view': 'hosts_widget',
        'widgets': [
            {
                'id': 'hosts_table',
                'for': ['external', 'dashboard'],
                'name': _('Hosts table widget'),
                'template': 'hosts_table_widget',
                'icon': 'table',
                'description': _(
                    '<h4>Hosts table widget</h4>Displays a list of the monitored system hosts.<br>'
                    'The number of hosts in this list can be defined in the widget options.'
                    'The list of hosts can be filtered thanks to regex on the host name'
                ),
                'picture': 'htdocs/img/hosts_table_widget.png',
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
                        'label': _('Host name search')
                    }
                }
            },
            {
                'id': 'hosts_chart',
                'for': ['external', 'dashboard'],
                'name': _('Hosts chart widget'),
                'template': 'hosts_chart_widget',
                'icon': 'pie-chart',
                'description': _(
                    '<h4>Hosts chart widget</h4>Displays a pie chart with the system hosts states.'
                ),
                'picture': 'htdocs/img/hosts_chart_widget.png',
                'options': {}
            }
        ]
    },
}
