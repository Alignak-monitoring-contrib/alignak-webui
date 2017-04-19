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
    Plugin hosts groups
"""

import json
from logging import getLogger

from bottle import request, response

from alignak_webui.objects.element_state import ElementState
from alignak_webui.utils.plugin import Plugin
from alignak_webui.utils.helper import Helper

# pylint: disable=invalid-name
logger = getLogger(__name__)


class PluginHostsGroups(Plugin):
    """ Hosts groups plugin """

    def __init__(self, webui, plugin_dir, cfg_filenames=None):
        """Hosts groups plugin

        Overload the default get route to declare filters.
        """
        self.name = 'Hosts groups'
        self.backend_endpoint = 'hostgroup'

        self.pages = {
            'get_group_members': {
                'name': 'Host group members',
                'route': '/hostgroup/members/<element_id>'
            },
            'get_overall_state': {
                'name': 'Host group status',
                'route': '/hostgroup/status/<element_id>'
            },
        }

        super(PluginHostsGroups, self).__init__(webui, plugin_dir, cfg_filenames)

    def get_one(self, element_id):
        """Show one element"""
        datamgr = request.app.datamgr

        # Get elements from the data manager
        f = getattr(datamgr, 'get_%s' % self.backend_endpoint)
        if not f:  # pragma: no cover - should not happen!
            self.send_user_message(_("No method to get a %s element") % self.backend_endpoint)

        logger.debug("get_one, search: %s", element_id)
        element = f(element_id)
        if not element:
            element = f(search={'max_results': 1, 'where': {'name': element_id}})
            if not element:
                self.send_user_message(_("%s '%s' not found") % (self.backend_endpoint, element_id))
        logger.debug("get_one, found: %s - %s", element, element.__dict__)

        groups = element.hostgroups
        if element.level == 0:
            groups = datamgr.get_hostgroups(search={'where': {'_level': 1}})

        return {
            'object_type': self.backend_endpoint,
            'element': element,
            'groups': groups
        }

    def get_overall_state(self, element):  # pylint:disable=no-self-use
        """Get the hostgroup overall state:

        Args:
            element:

        Returns:
            state (int) or -1 if any problem
        """
        datamgr = request.app.datamgr

        (overall_state, overall_status) = datamgr.get_hostgroup_overall_state(element)
        logger.debug(
            " - hostgroup overall state: %d -> %s", overall_state, overall_status
        )

        return (overall_state, overall_status)

    def get_group_members(self, element_id):
        """Get the hostgroup hosts list"""
        datamgr = request.app.datamgr

        hostgroup = datamgr.get_hostgroup(element_id)
        if not hostgroup:
            hostgroup = datamgr.get_hostgroup(
                search={'max_results': 1, 'where': {'name': element_id}}
            )
            if not hostgroup:
                return self.webui.response_invalid_parameters(_('Element does not exist: %s')
                                                              % element_id)

        if not isinstance(hostgroup.members, basestring):
            # Get element state configuration
            items_states = ElementState()

            items = []
            items.append({
                'id': -1,
                'type': 'host',
                'tr': """
                    <table class="table table-invisible table-condensed">
                      <thead><tr>
                        <th></th>
                        <th>%s</th>
                        <th>%s</th>
                        <th>%s</th>
                        <th>%s</th>
                        <th>%s</th>
                      </tr></thead>

                      <tbody>
                      </tbody>
                    </table>
                """ % (
                    _("BI"), _("Element"),
                    _("Since"), _("Last check"), _("Output")
                )
            })

            for member in hostgroup.members:
                logger.debug("Group member: %s", member)
                cfg_state = items_states.get_icon_state('host', member.status)

                tr = """<tr>
                    <td>%s</td>
                    <td>%s</td>
                    <td>%s</td>
                    <td class="hidden-xs">%s</td>
                    <td class="hidden-xs">%s</td>
                    <td class="hidden-sm hidden-xs">%s: %s</td>
                </tr>""" % (
                    member.get_html_state(text=None, title=member.alias),
                    Helper.get_html_business_impact(member.business_impact, icon=True, text=False),
                    member.get_html_link(),
                    Helper.print_duration(member.last_state_changed, duration_only=True, x_elts=2),
                    Helper.print_duration(member.last_check, duration_only=True, x_elts=2),
                    Helper.print_date(member.last_check),
                    member.output
                )
                items.append({
                    'id': member.id,
                    'type': 'host',
                    'name': member.name,
                    'alias': member.alias,
                    'status': member.status,
                    'icon': 'fa fa-%s item_%s' % (cfg_state['icon'], cfg_state['class']),
                    'state': member.get_html_state(text=None, title=member.alias),
                    'tr': tr
                })

        response.status = 200
        response.content_type = 'application/json'
        return json.dumps(items)
