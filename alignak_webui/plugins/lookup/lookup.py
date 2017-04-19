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
    Plugin Lookup
"""

import json
from logging import getLogger

from bottle import request
from alignak_webui.utils.plugin import Plugin

# pylint: disable=invalid-name
logger = getLogger(__name__)


class PluginLookup(Plugin):
    """ Dashboard plugin """

    def __init__(self, webui, plugin_dir, cfg_filenames=None):
        """
        Dashboard plugin
        """
        self.name = 'Dashboard'
        self.backend_endpoint = None

        self.pages = {
            'lookup': {
                'name': 'Get Lookup',
                'route': '/lookup',
                'method': 'GET'
            }
        }

        super(PluginLookup, self).__init__(webui, plugin_dir, cfg_filenames)

    def lookup(self):  # pylint:disable=no-self-use
        """
        Search in the livestate for an element name
        """
        datamgr = request.app.datamgr

        query = request.query.get('query', '')

        logger.debug("lookup query: %s", query)

        elements = datamgr.get_hosts(
            search={'where': {'name': {"$regex": ".*" + query + ".*"}}}
        )
        names = [e.name for e in elements]
        logger.info("lookup found: %s", names)

        return json.dumps(names)
