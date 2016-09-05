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
    Plugin users groups
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
        self.name = 'Users groups'
        self.backend_endpoint = 'usergroup'

        self.pages = {
            'get_usergroup_members': {
                'name': 'Users group members',
                'route': '/usergroup/members/<usergroup_id>'
            },
        }

        super(PluginServicesGroups, self).__init__(app, cfg_filenames)

    def get_usergroup_members(self, usergroup_id):
        """
        Get the usergroup users list
        """
        datamgr = request.app.datamgr

        usergroup = datamgr.get_usergroup(usergroup_id)
        if not usergroup:
            usergroup = datamgr.get_usergroup(
                search={'max_results': 1, 'where': {'name': usergroup_id}}
            )
            if not usergroup:
                return self.webui.response_invalid_parameters(_('Element does not exist: %s')
                                                              % usergroup_id)

        items = []
        for user in usergroup.users:
            items.append({
                'id': user.id,
                'name': user.name,
                'alias': user.alias,
                'icon': user.get_html_state(text=None, title=user.alias),
                'url': user.get_html_link()
            })

        response.status = 200
        response.content_type = 'application/json'
        return json.dumps(items)
