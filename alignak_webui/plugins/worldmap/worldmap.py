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

from logging import getLogger

from bottle import request

from alignak_webui.utils.plugin import Plugin
from alignak_webui.utils.helper import Helper

# pylint: disable=invalid-name
logger = getLogger(__name__)


class PluginWorldmap(Plugin):
    """ Worldmap plugin """

    def __init__(self, webui, plugin_dir, cfg_filenames=None):
        """Worldmap plugin"""
        self.name = 'Worldmap'
        self.backend_endpoint = None

        self.pages = {
            'show_worldmap': {
                'name': 'Worldmap',
                'route': '/worldmap',
                'view': 'worldmap'
            },
            # todo: remove temporarily, to reactivate (#212)
            # 'get_worldmap_widget': {
            #     'name': 'Worlmap widget',
            #     'route': '/worldmap/widget',
            #     'method': 'POST',
            #     'view': 'worldmap_widget',
            #     'widgets': [
            #         {
            #             'id': 'worldmap',
            #             'for': ['external', 'dashboard'],
            #             'name': _('Worldmap widget'),
            #             'template': 'worldmap_widget',
            #             'icon': 'globe',
            #             'description': _(
            #                 '<h4>Worldmap widget</h4>Displays a world map of the monitored '
            #                 'system hosts.<br>The number of hosts on the map can be defined in '
            #                 'the widget options. The list of hosts can be filtered thanks to '
            #                 'regex on the host name.'
            #             ),
            #             'picture': 'static/img/worldmap_widget.png',
            #             'options': {
            #                 'search': {
            #                     'value': '',
            #                     'type': 'text',
            #                     'label': _('Filter (ex. status:ok)')
            #                 },
            #                 'count': {
            #                     'value': -1,
            #                     'type': 'int',
            #                     'label': _('Number of elements')
            #                 },
            #                 'filter': {
            #                     'value': '',
            #                     'type': 'hst_srv',
            #                     'label': _('Host/service name search')
            #                 }
            #             }
            #         }
            #     ]
            # }
        }

        super(PluginWorldmap, self).__init__(webui, plugin_dir, cfg_filenames)

        self.search_engine = True
        self.search_filters = {
            '01': (_('Ok'), 'is:ok'),
            '02': (_('Acknowledged'), 'is:acknowledged'),
            '03': (_('Downtimed'), 'is:in_downtime'),
            '04': (_('Warning'), 'is:warning'),
            '05': (_('Critical'), 'is:warning'),
            '06': ('', ''),
        }

        bis = self.plugin_parameters.get('hosts_business_impacts',
                                         '0,1,2,3,4,5').replace(' ', '').split(',')
        if not bis:
            bis = [0, 1, 2, 3, 4, 5]
        else:
            bis = [int(num) for num in bis]
        self.plugin_parameters['hosts_business_impacts'] = bis

        bis = self.plugin_parameters.get('services_business_impacts',
                                         '0,1,2,3,4,5').replace(' ', '').split(',')
        if not bis:
            bis = [0, 1, 2, 3, 4, 5, 6]
        else:
            bis = [int(num) for num in bis]
        self.plugin_parameters['services_business_impacts'] = bis
        logger.debug("Plugin parameters: %s", self.plugin_parameters)

    def show_worldmap(self, for_my_widget=False):
        """Get the hosts list to build a worldmap

        Get the list of the valid hosts t display onthe map

         If `for_my_widget` is True this function returns the list of the concerned hosts
         else it returns the worldmap view.

        :param for_my_widget: defaults to False
        :return:
        """
        user = request.environ['beaker.session']['current_user']
        datamgr = request.app.datamgr

        # Fetch elements per page preference for user, default is 25
        elts_per_page = datamgr.get_user_preferences(user, 'elts_per_page', 25)

        # Pagination and search
        start = int(request.query.get('start', '0'))
        count = int(request.query.get('count', elts_per_page))
        where = Helper.decode_search(request.query.get('search', ''), self.table)
        search = {
            'page': (start // count) + 1,
            'max_results': count,
            'sort': '-_id',
            'where': where
        }
        if self.plugin_parameters.get('hosts_business_impacts'):
            # Only get hosts which business impact is configured...
            logger.debug("worldmap, only hosts with BI in: %s",
                         self.plugin_parameters['hosts_business_impacts'])
            search['where'].update(
                {'business_impact': {'$in': self.plugin_parameters['hosts_business_impacts']}})
        if self.plugin_parameters.get('hosts_included'):
            # Include some hosts...
            logger.debug("worldmap, included hosts: %s", self.plugin_parameters['hosts_included'])
            search['where'].update({'name': {
                "$regex": self.plugin_parameters['hosts_included']}})
        if self.plugin_parameters.get('hosts_excluded'):
            # Exclude some hosts...
            logger.debug("worldmap, excluded hosts: %s", self.plugin_parameters['hosts_excluded'])
            search['where'].update({'name': {
                "$regex": "^((?!%s).)*$" % self.plugin_parameters['hosts_excluded']}})

        # Do not include the embedded fields to improve the loading time...
        hosts = datamgr.get_hosts(search, embedded=False)

        # Get positionned and not-positionned hosts
        (positionned_hosts, dummy) = self.get_map_elements(hosts)

        # Get last total elements count
        total = len(positionned_hosts)
        logger.info("worldmap, found %d positionned hosts", total)
        if hosts:
            total = hosts[0]['_total']
            logger.info("worldmap, total %d hosts", total)

        if for_my_widget:
            return positionned_hosts

        map_style = "width: %s; height: %s;" % (self.plugin_parameters.get('map_width', "100%"),
                                                self.plugin_parameters.get('map_height', "100%"))

        return {
            'search_engine': self.search_engine,
            'search_filters': self.search_filters,
            'options_panel': False,
            'mapId': 'hostsMap',
            'mapStyle': map_style,
            'params': self.plugin_parameters,
            'hosts': positionned_hosts,
            'pagination': self.webui.helper.get_pagination_control(
                '/worldmap', total, start, count),
            'title': request.query.get('title', _('Hosts worldmap'))
        }

    def get_map_elements(self, hosts):
        # pylint:disable=no-self-use, too-many-locals
        """Get hosts valid for a map:

        :param hosts: list of hosts to search in
        :return: tuple with a list of positionned hosts and a list of not yet positionned hosts
        """
        user = request.environ['beaker.session']['current_user']
        datamgr = request.app.datamgr

        # Get elements from the data manager
        logger.info("worldmap, searching valid hosts...")

        positionned_hosts = []
        not_positionned_hosts = []
        for host in hosts:
            map_host = {}
            logger.debug("worldmap, found host '%s'", host.name)

            positionned = True
            if 'type' not in host.position or host.position['type'] != 'Point':
                # logger.warning("worldmap, host '%s', invalid position: %s",
                #                host.name, host.position)
                # continue
                logger.warning("worldmap, host '%s' is not yet positionned", host.name)
                positionned = False
                map_host['lat'] = self.plugin_parameters['default_latitude']
                map_host['lng'] = self.plugin_parameters['default_longitude']
            else:
                logger.debug("worldmap, host '%s' located: %s", host.name, host.position)

                map_host['lat'] = host['position']['coordinates'][0]
                map_host['lng'] = host['position']['coordinates'][1]

            for attr in ['id', 'name', 'alias', 'business_impact', 'tags',
                         'position', 'tags', 'notes', 'notes_url', 'action_url',
                         'overall_state', 'overall_status', 'state_id', 'state_type',
                         'acknowledged', 'downtimed',
                         'last_check', 'output', 'long_output']:
                map_host[attr] = host[attr]

            host_iw = self.plugin_parameters['host_info_content']
            host_iw = host_iw.replace("\n", '')
            host_iw = host_iw.replace("\r", '')
            host_iw = host_iw.replace("##id##", map_host['id'])
            host_iw = host_iw.replace("##name##", map_host['name'])
            host_iw = host_iw.replace("##state##", map_host['overall_status'])
            host_iw = host_iw.replace("##bi##", str(map_host['business_impact']))
            host_iw = host_iw.replace("##url##", host.get_html_link())
            host_iw = host_iw.replace("##html_bi##",
                                      Helper.get_html_business_impact(host.business_impact,
                                                                      icon=True, text=False))
            host_iw = host_iw.replace("##html_state##",
                                      host.get_html_state(text=None,
                                                          use_status=host.overall_status))
            if user.is_power():
                host_iw = host_iw.replace("##html_actions##", Helper.get_html_commands_buttons(
                    host, _('<span class="fa fa-bolt"></span>')
                ))
            else:
                host_iw = host_iw.replace("##html_actions##", "")

            # Get host services
            # todo: using a projection with selected fields may help to improve more?
            search = {
                'sort': '-_overall_state_id,name',
                'where': {}
            }
            if self.plugin_parameters.get('services_excluded'):
                search['where'].update({'name': {
                    "$regex": "^((?!%s).)*$" % self.plugin_parameters['services_excluded']}})
            if self.plugin_parameters.get('services_included'):
                search['where'].update({'name': {
                    "$regex": self.plugin_parameters['services_included']}})

            services = datamgr.get_host_services(host, search=search, embedded=False)
            services_iw = ""
            for service in services:
                svc_iw = self.plugin_parameters['service_info_content']
                svc_iw = svc_iw.replace("\n", '')
                svc_iw = svc_iw.replace("\r", '')
                svc_iw = svc_iw.replace("##id##", service['id'])
                svc_iw = svc_iw.replace("##name##", service['name'])
                svc_iw = svc_iw.replace("##state##", service['overall_status'])
                svc_iw = svc_iw.replace("##bi##", str(service['business_impact']))
                svc_iw = svc_iw.replace("##url##", service.get_html_link())
                svc_iw = svc_iw.replace("##html_bi##",
                                        Helper.get_html_business_impact(service.business_impact,
                                                                        icon=True, text=False))
                svc_iw = svc_iw.replace("##html_state##",
                                        service.get_html_state(text=None,
                                                               use_status=service.overall_status))
                if user.is_power():
                    svc_iw = svc_iw.replace("##html_actions##", Helper.get_html_commands_buttons(
                        service, _('<span class="fa fa-bolt"></span>')
                    ))
                else:
                    svc_iw = svc_iw.replace("##html_actions##", "")

                services_iw += svc_iw

            logger.debug("worldmap, host '%s' services: %s", host.name, services)
            map_host.update({'services': services})

            host_iw = host_iw.replace("##services##", services_iw)
            map_host.update({'content': host_iw})

            if positionned:
                positionned_hosts.append(map_host)
            else:
                not_positionned_hosts.append(map_host)

        logger.info("worldmap, found %d positionned hosts and %d not yet positionned",
                    len(positionned_hosts), len(not_positionned_hosts))

        return (positionned_hosts, not_positionned_hosts)

    def get_widget_hosts(self, search):  # pylint: disable=unused-argument
        """Get the hosts list for the widget"""
        return self.show_worldmap(for_my_widget=True)

    def get_worldmap_widget(self, embedded=False, identifier=None, credentials=None):
        """Get the worldmap widget"""
        return self.get_widget(self.get_widget_hosts, 'host', embedded, identifier, credentials)
