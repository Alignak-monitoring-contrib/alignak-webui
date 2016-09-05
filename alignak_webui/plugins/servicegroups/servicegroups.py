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
    Plugin services groups
"""

import json
from logging import getLogger

from bottle import request, response

from alignak_webui import _
from alignak_webui.utils.helper import Helper
from alignak_webui.utils.plugin import Plugin

logger = getLogger(__name__)


class PluginServicesGroups(Plugin):
    """ Services groups plugin """

    def __init__(self, app, cfg_filenames=None):
        """
        Services groups plugin

        Overload the default get route to declare filters.
        """
        self.name = 'Services groups'
        self.backend_endpoint = 'servicegroup'

        self.pages = {
            'get_servicegroup_members': {
                'name': 'Services group members',
                'route': '/servicegroup/members/<servicegroup_id>'
            },
        }

        super(PluginServicesGroups, self).__init__(app, cfg_filenames)

    def get_servicegroup_members(self, servicegroup_id):
        """
        Get the servicegroup services list
        """
        datamgr = request.app.datamgr

        servicegroup = datamgr.get_servicegroup(servicegroup_id)
        if not servicegroup:
            servicegroup = datamgr.get_servicegroup(
                search={'max_results': 1, 'where': {'name': servicegroup_id}}
            )
            if not servicegroup:
                return self.webui.response_invalid_parameters(_('Element does not exist: %s')
                                                              % servicegroup_id)

        items = []
        for service in servicegroup.services:

            items.append({
                'id': service.id,
                'name': service.name,
                'alias': service.alias,
                'icon': service.get_html_state(text=None, title=service.alias),
                'url': service.get_html_link()
            })

        response.status = 200
        response.content_type = 'application/json'
        return json.dumps(items)
