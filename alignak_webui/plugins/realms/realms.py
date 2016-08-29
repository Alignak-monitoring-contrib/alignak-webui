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
    Plugin Realm
"""

import json
from logging import getLogger

from bottle import request, template, response

from alignak_webui import _
from alignak_webui.utils.helper import Helper
from alignak_webui.utils.plugin import Plugin

logger = getLogger(__name__)


class PluginRealms(Plugin):
    """ Services groups plugin """

    def __init__(self, app, cfg_filenames=None):
        """
        Services groups plugin

        Overload the default get route to declare filters.
        """
        self.name = 'Realms'
        self.backend_endpoint = 'realm'

        self.pages = {
            'get_realm_members': {
                'name': 'Realm members',
                'route': '/realm/members/<realm_id>'
            },
        }

        super(PluginRealms, self).__init__(app, cfg_filenames)

    def get_realm_members(self, realm_id):
        """
        Get the realm hosts list
        """
        datamgr = request.app.datamgr

        realm = datamgr.get_realm(realm_id)
        if not realm:
            realm = datamgr.get_realm(
                search={'max_results': 1, 'where': {'name': realm_id}}
            )
            if not realm:
                return self.webui.response_invalid_parameters(_('Element does not exist: %s')
                                                              % realm_id)

        # Get elements from the data manager
        search = {
            'where': {'_realm': realm.id}
        }
        hosts = datamgr.get_hosts(search)

        items = []
        for host in hosts:
            lv_host = datamgr.get_livestates({'where': {'type': 'host', 'host': host.id}})
            lv_host = lv_host[0]
            title = "%s - %s (%s)" % (
                lv_host.status,
                Helper.print_duration(lv_host.last_check, duration_only=True, x_elts=0),
                lv_host.output
            )

            items.append({
                'id': host.id,
                'name': host.name,
                'alias': host.alias,
                'icon': lv_host.get_html_state(text=None, title=title),
                'url': lv_host.get_html_link()
            })

        response.status = 200
        response.content_type = 'application/json'
        return json.dumps(items)
