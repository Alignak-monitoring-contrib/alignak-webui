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

from alignak_webui.utils.plugin import Plugin
from alignak_webui.utils.helper import Helper

# pylint: disable=invalid-name
logger = getLogger(__name__)


class PluginMinemap(Plugin):
    """ Minemap plugin """

    def __init__(self, webui, plugin_dir, cfg_filenames=None):
        """Minemap plugin"""
        self.name = 'Minemap'
        self.backend_endpoint = None

        self.pages = {
            'show_minemap': {
                'name': 'Minemap',
                'route': '/minemap',
                'view': 'minemap'
            }
        }

        super(PluginMinemap, self).__init__(webui, plugin_dir, cfg_filenames)

        self.search_engine = True
        self.search_filters = {
            '01': (_('Ok'), 'is:ok'),
            '02': (_('Acknowledged'), 'is:acknowledged'),
            '03': (_('Downtimed'), 'is:in_downtime'),
            '04': (_('Warning'), 'is:warning'),
            '05': (_('Critical'), 'is:warning'),
            '06': ('', ''),
        }

    def show_minemap(self):
        # Yes, but that's how it is made, and it suits ;)
        # pylint: disable=too-many-locals
        """Get the hosts / services list to build a minemap"""
        user = request.environ['beaker.session']['current_user']
        datamgr = request.app.datamgr

        # Fetch elements per page preference for user, default is 25
        elts_per_page = datamgr.get_user_preferences(user, 'elts_per_page', 25)

        # Minemap search engine is based upon host table
        plugin = self.webui.find_plugin('host')

        # Pagination and search
        start = int(request.params.get('start', '0'))
        count = int(request.params.get('count', elts_per_page))
        if count < 1:
            count = elts_per_page
        search = Helper.decode_search(request.params.get('search', ''), plugin.table)
        logger.info("Decoded search pattern: %s", search)
        for key, pattern in search.iteritems():
            logger.info("global search pattern '%s' / '%s'", key, pattern)

        search = {
            'page': (start // count) + 1,
            'max_results': count,
            'where': search,
            'sort': '-_overall_state_id'
        }

        # Get elements from the data manager
        # Do not include the embedded fields to improve the loading time...
        hosts = datamgr.get_hosts(search, embedded=False)

        minemap = []
        columns = []
        for host in hosts:
            # Each item contains the total number of records matching the search filter
            total = host['_total']
            minemap_row = {'host_check': host}

            # Get all host services
            # Do not include the embedded fields to improve the loading time...
            services = datamgr.get_services(
                search={
                    'where': {'host': host.id},
                    'sort': '-_overall_state_id'
                },
                all_elements=True, embedded=False
            )
            for service in services:
                columns.append(service.name)
                minemap_row.update({service.name: service})

            minemap.append(minemap_row)

        # Sort column names by most frequent ...
        count_columns = collections.Counter(columns)
        columns = [c for c, dummy in count_columns.most_common()]

        return {
            'search_engine': self.search_engine,
            'search_filters': self.search_filters,
            'params': self.plugin_parameters,
            'minemap': minemap,
            'columns': columns,
            'pagination': self.webui.helper.get_pagination_control('/minemap', total, start, count),
            'title': request.query.get('title', _('Hosts minemap'))
        }
