#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2017:
#   Frederic Mohier, frederic.mohier@alignak.net
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

import collections
from logging import getLogger

from bottle import request

from alignak_webui import _
from alignak_webui.utils.plugin import Plugin

# pylint: disable=invalid-name
logger = getLogger(__name__)


class PluginMinemap(Plugin):
    """ Minemap plugin """

    def __init__(self, app, cfg_filenames=None):
        """
        Minemap plugin
        """
        self.name = 'Minemap'
        self.backend_endpoint = None

        self.pages = {
            'show_minemap': {
                'name': 'Minemap',
                'route': '/minemap',
                'view': 'minemap'
            }
        }

        super(PluginMinemap, self).__init__(app, cfg_filenames)

    def show_minemap(self):
        """
        Get the hosts / services list to build a minemap
        """
        # Yes, but that's how it is made, and it suits ;)
        # pylint: disable=too-many-locals
        user = request.environ['beaker.session']['current_user']
        datamgr = request.app.datamgr

        # Fetch elements per page preference for user, default is 25
        elts_per_page = datamgr.get_user_preferences(user, 'elts_per_page', 25)
        # elts_per_page = elts_per_page['value']

        # Pagination and search
        start = int(request.params.get('start', '0'))
        count = int(request.params.get('count', elts_per_page))
        if count < 1:
            count = elts_per_page
        where = self.webui.helper.decode_search(request.params.get('search', ''))
        search = {
            'page': (start // count) + 1,
            'max_results': count,
            'where': where,
            'embedded': {
            }
        }

        # Get elements from the data manager
        # Do not include the embedded fields to improve the loading time...
        hosts = datamgr.get_hosts(search)

        minemap = []
        columns = []
        for host in hosts:
            minemap_row = {'host_check': host}

            # Get all host services
            # Do not include the embedded fields to improve the loading time...
            services = datamgr.get_services(
                search={
                    'where': {'host': host.id}
                },
                all_elements=True
            )
            for service in services:
                columns.append(service.alias)
                minemap_row.update({service.name: service})

            minemap.append(minemap_row)

        # Sort column names by most frequent ...
        count_columns = collections.Counter(columns)
        columns = [c for c, dummy in count_columns.most_common()]

        # Get last total elements count
        total = datamgr.get_objects_count('host', search=where, refresh=True)
        # count = min(len(hosts), total)

        return {
            'params': self.plugin_parameters,
            'minemap': minemap,
            'columns': columns,
            'pagination': self.webui.helper.get_pagination_control('/minemap', total, start, count),
            'title': request.query.get('title', _('Hosts minemap'))
        }
