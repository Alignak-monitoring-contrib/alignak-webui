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
import collections

from logging import getLogger
from bottle import request

from alignak_webui.utils.helper import Helper

logger = getLogger(__name__)

# Will be populated by the UI with it's own value
webui = None

# Plugin's parameters
plugin_parameters = {
}


def show_minemap():
    """
    Get the hosts list to build a minemap
    """
    # Yes, but that's how it is made, and it suits ;)
    # pylint: disable=too-many-locals
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
        'where': where,
        'embedded': {}
    }

    # Get elements from the data manager
    # hosts = datamgr.get_hosts(search)
    hosts = datamgr.get_livestate_hosts(search)

    minemap = []
    columns = []
    for host in hosts:
        minemap_row = {'host_check': host}

        # services = datamgr.get_services(search={'where': {'host': host.id}})
        services = datamgr.get_livestate_services(
            search={'where': {'host': host.host.id}}
        )
        if services:
            for service_check in services:
                if isinstance(service_check.service, basestring):
                    logger.critical(service_check.__dict__)
                else:
                    columns.append(service_check.service.name)
                    minemap_row.update({service_check.service.name: service_check})

        minemap.append(minemap_row)

    # Sort column names by most frequent ...
    count_columns = collections.Counter(columns)
    columns = [c for c, dummy in count_columns.most_common()]

    # Get last total elements count
    total = datamgr.get_objects_count('host', search=where, refresh=True)
    count = min(len(hosts), total)

    return {
        'params': plugin_parameters,
        'minemap': minemap,
        'columns': columns,
        'pagination': webui.helper.get_pagination_control('/minemap', total, start, count),
        'title': request.query.get('title', _('Hosts minemap'))
    }


# We export our properties to the webui
pages = {
    show_minemap: {
        'name': 'Minemap',
        'route': '/minemap',
        'view': 'minemap'
    }
}
