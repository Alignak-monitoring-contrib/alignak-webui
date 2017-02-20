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
    Plugin services groups
"""

import json
from logging import getLogger

from bottle import request, response

from alignak_webui.objects.element_state import ElementState
from alignak_webui.utils.plugin import Plugin

# pylint: disable=invalid-name
logger = getLogger(__name__)


class PluginServicesGroups(Plugin):
    """ Services groups plugin """

    def __init__(self, app, webui, cfg_filenames=None):
        """
        Services groups plugin

        Overload the default get route to declare filters.
        """
        self.name = 'Services groups'
        self.backend_endpoint = 'servicegroup'
        _ = app.config['_']

        self.pages = {
            'get_servicegroup_members': {
                'name': 'Services group members',
                'route': '/servicegroup/members/<group_id>'
            },
        }

        super(PluginServicesGroups, self).__init__(app, webui, cfg_filenames)

    def get_servicegroup_members(self, group_id):
        """
        Get the servicegroup services list
        """
        datamgr = request.app.datamgr

        servicegroup = datamgr.get_servicegroup(group_id)
        if not servicegroup:
            servicegroup = datamgr.get_servicegroup(
                search={'max_results': 1, 'where': {'name': group_id}}
            )
            if not servicegroup:
                return self.webui.response_invalid_parameters(_('Element does not exist: %s')
                                                              % group_id)

        items = []
        if not isinstance(servicegroup.members, basestring):
            # Get element state configuration
            items_states = ElementState()

            for member in servicegroup.members:
                logger.debug("Group member: %s", member)
                cfg_state = items_states.get_icon_state('service', member.status)

                items.append({
                    'id': member.id,
                    'type': 'service',
                    'name': "%s/%s" % (member.host.name, member.name),
                    'alias': "%s/%s" % (member.host.alias, member.alias),
                    'status': member.status,
                    'icon': 'fa fa-%s item_%s' % (cfg_state['icon'], cfg_state['class']),
                    'state': member.get_html_state(text=None, title=member.alias),
                    'url': member.get_html_link()
                })

        response.status = 200
        response.content_type = 'application/json'
        return json.dumps(items)
