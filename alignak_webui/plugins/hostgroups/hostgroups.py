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

    def get_one(self, element_id):
        """
            Show one element
        """
        datamgr = request.app.datamgr

        # Get elements from the data manager
        f = getattr(datamgr, 'get_%s' % self.backend_endpoint)
        if not f:
            self.send_user_message(_("No method to get a %s element") % self.backend_endpoint)

        logger.debug("get_one, search: %s", element_id)
        element = f(element_id)
        if not element:
            element = f(search={'max_results': 1, 'where': {'name': element_id}})
            if not element:
                self.send_user_message(_("%s '%s' not found") % (self.backend_endpoint, element_id))
        logger.debug("get_one, found: %s - %s", element, element.__dict__)

        group_members = element.hostgroups
        if element.level == 0:
            group_members = datamgr.get_hostgroups(search={'where': {'_level': 1}})

        return {
            'object_type': self.backend_endpoint,
            'element': element,
            'groups': group_members
        }

    def get_hostgroup_status(self, hostgroup_id, hostgroup=None, no_json=False):
        """
        Get the hostgroup overall status
        """
        datamgr = request.app.datamgr

        if not hostgroup:
            hostgroup = datamgr.get_hostgroup(hostgroup_id)
            if not hostgroup:
                hostgroup = datamgr.get_hostgroup(
                    search={'max_results': 1, 'where': {'name': hostgroup_id}}
                )
                if not hostgroup:
                    return self.webui.response_invalid_parameters(_('Element does not exist: %s')
                                                                  % hostgroup_id)

        logger.debug("get_hostgroup_status: %s", hostgroup.name)
        # Hosts group real state from hosts
        hostgroup.real_state = 0
        hostgroup._status = 'unknown'
        for host in hostgroup.members:
            if isinstance(host, basestring):
                continue

            host_state = datamgr.get_host_real_state(host.id)
            logger.debug(" - host: %s, state: %d", host.name, host_state)
            hostgroup.real_state = max(hostgroup.real_state, host_state)

        logger.debug(" - state from hosts: %d -> %s", hostgroup.real_state, hostgroup.real_status)

        group_members = hostgroup.hostgroups
        if hostgroup.level == 0:
            group_members = datamgr.get_hostgroups(search={'where': {'_level': 1}})

        # Hosts group real state from group members
        for group in group_members:
            if isinstance(group, basestring):
                continue

            logger.debug(" - group: %s, state: %d", group.name, group.real_state)
            hostgroup.real_state = max(hostgroup.real_state, group.real_state)

        logger.debug(" - state from groups: %d -> %s", hostgroup.real_state, hostgroup.real_status)

        if no_json:
            return hostgroup.status

        response.status = 200
        response.content_type = 'application/json'
        return json.dumps({'status': hostgroup.real_state, 'status': hostgroup.status})

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
