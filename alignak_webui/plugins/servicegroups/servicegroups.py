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

    def get_servicegroup_members(servicegroup_id):
        """
        Get the servicegroup services list
        """
        datamgr = request.environ['beaker.session']['datamanager']

        servicegroup = datamgr.get_servicegroup(servicegroup_id)
        if not servicegroup:  # pragma: no cover, should not happen
            return webui.response_invalid_parameters(_('Services group element does not exist'))

        # Not JSON serializable!
        # items = servicegroup.members

        items = []
        for service in servicegroup.services:
            lv_service = datamgr.get_livestates({'where': {'type': 'service', 'service': service.id}})
            lv_service = lv_service[0]
            title = "%s - %s (%s)" % (
                lv_service.status,
                Helper.print_duration(lv_service.last_check, duration_only=True, x_elts=0),
                lv_service.output
            )

            items.append({
                'id': service.id,
                'name': service.name,
                'alias': service.alias,
                'icon': lv_service.get_html_state(text=None, title=title),
                'url': lv_service.get_html_link()
            })

        response.status = 200
        response.content_type = 'application/json'
        return json.dumps(items)
