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
    Plugin hosts groups
"""

import json
from logging import getLogger

from bottle import request, response

from alignak_webui import _
from alignak_webui.utils.helper import Helper
from alignak_webui.utils.plugin import Plugin

logger = getLogger(__name__)


class PluginHostsGroups(Plugin):
    """ Hosts groups plugin """

    def __init__(self, app, cfg_filenames=None):
        """
        Hosts groups plugin

        Overload the default get route to declare filters.
        """
        self.name = 'Hosts groups'
        self.backend_endpoint = 'hostgroup'

        self.pages = {
            'get_hostgroup_members': {
                'name': 'Host group members',
                'route': '/hostgroup/members/<hostgroup_id>'
            },
            'get_hostgroup_status': {
                'name': 'Host group status',
                'route': '/hostgroup/status/<hostgroup_id>'
            },
        }

        super(PluginHostsGroups, self).__init__(app, cfg_filenames)

    def get_hostgroup_status(self, hostgroup_id):
        """
        Get the hostgroup overall status
        """
        datamgr = request.app.datamgr

        hostgroup = datamgr.get_hostgroup(hostgroup_id)
        if not hostgroup:
            hostgroup = datamgr.get_hostgroup(
                search={'max_results': 1, 'where': {'name': hostgroup_id}}
            )
            if not hostgroup:
                return self.webui.response_invalid_parameters(_('Element does not exist: %s')
                                                              % hostgroup_id)

        group_state = 0
        for host in hostgroup.members:
            logger.debug("Group member: %s", host)

            # Get host services
            services = datamgr.get_services(search={'where': {'host': host.id}})

            # Get host overall state (0, 1, 2, 3)
            state = host.get_real_state(services)
            group_state = max(state, group_state)

        logger.debug("Group state: %d", group_state)

        response.status = 200
        response.content_type = 'application/json'
        return json.dumps({'status': group_state})

    def get_hostgroup_members(self, hostgroup_id):
        """
        Get the hostgroup hosts list
        """
        datamgr = request.app.datamgr

        hostgroup = datamgr.get_hostgroup(hostgroup_id)
        if not hostgroup:
            hostgroup = datamgr.get_hostgroup(
                search={'max_results': 1, 'where': {'name': hostgroup_id}}
            )
            if not hostgroup:
                return self.webui.response_invalid_parameters(_('Element does not exist: %s')
                                                              % hostgroup_id)

        items = []
        for host in hostgroup.members:
            logger.debug("Group member: %s", host)

            items.append({
                'id': host.id,
                'name': host.name,
                'alias': host.alias,
                'icon': host.get_html_state(text=None, title=host.alias),
                'url': host.get_html_link()
            })

        response.status = 200
        response.content_type = 'application/json'
        return json.dumps(items)
