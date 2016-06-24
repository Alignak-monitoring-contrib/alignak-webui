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
    Plugin Worldmap
"""

import time
import re
import random
import json

from logging import getLogger
from bottle import request

from alignak_webui.utils.helper import Helper

logger = getLogger(__name__)

# Will be populated by the UI with it's own value
webui = None

# Plugin's parameters
plugin_parameters = {
    'default_zoom': 16,
    'default_lng': 5.080625,
    'default_lat': 45.054148,
    'hosts_level': [1, 2, 3, 4, 5],
    'services_level': [1, 2, 3, 4, 5],
    'layer': ''
}


def show_worldmap():
    """
    Get the hosts list to build a worldmap
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
    where = Helper.decode_search(request.query.get('search', ''))
    search = {
        'page': start // count + 1,
        'max_results': count,
        'sort': '-_id',
        'where': where,
        'embedded': {
            'check_command': 1, 'event_handler': 1,
            'check_period': 1, 'notification_period': 1,
            # 'parents': 1, 'hostgroups': 1, 'contacts': 1, 'contact_groups': 1
        }
    }

    # Get elements from the data manager
    hosts = datamgr.get_hosts(search)

    valid_hosts = []
    for host in hosts:
        logger.debug("worldmap, found host '%s'", host.name)

        if host.business_impact not in plugin_parameters['hosts_level']:
            continue

        try:
            _lat = float(host.customs.get('_LOC_LAT', None))
            _lng = float(host.customs.get('_LOC_LNG', None))
            # lat/long must be between -180/180
            if not (-180 <= _lat <= 180 and -180 <= _lng <= 180):
                raise Exception()
        except Exception:
            logger.debug("worldmap, host '%s' has invalid GPS coordinates", host.name)
            continue

        logger.debug("worldmap, host '%s' located on worldmap: %f - %f", host.name, _lat, _lng)
        valid_hosts.append(host)

    # Get last total elements count
    total = datamgr.get_objects_count('host', search=where, refresh=True)
    count = min(len(valid_hosts), total)

    return {
        'mapId': 'hostsMap',
        'params': plugin_parameters,
        'hosts': valid_hosts,
        'pagination': Helper.get_pagination_control('/worldmap', total, start, count),
        'title': request.query.get('title', _('Hosts worldmap'))
    }


# We export our properties to the webui
pages = {
    show_worldmap: {
        'name': 'Worldmap',
        'route': '/worldmap',
        'view': 'worldmap'
    }
}
