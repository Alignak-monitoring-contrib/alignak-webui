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
    Plugin actions - actions and commands notified to Alignak from the Web UI
"""

import json
import time
from logging import getLogger
from copy import deepcopy

from bottle import request, response

from alignak_webui.utils.plugin import Plugin
from .external_commands import commands

# pylint: disable=invalid-name
logger = getLogger(__name__)


class PluginActions(Plugin):
    """Actions plugin"""

    def __init__(self, webui, plugin_dir, cfg_filenames=None):
        """Actions plugin"""
        self.name = 'Actions'
        self.backend_endpoint = None

        self.pages = {
            'show_acknowledge_add': {
                'name': 'Acknowledge add form',
                'route': '/acknowledge/form/add',
                'view': 'acknowledge_form_add'
            },
            'add_acknowledge': {
                'name': 'Acknowledge',
                'route': '/acknowledge/add',
                'method': 'POST'
            },
            'show_recheck_add': {
                'name': 'Recheck add form',
                'route': '/recheck/form/add',
                'view': 'recheck_form_add'
            },
            'show_command_add': {
                'name': 'Command add form',
                'route': '/command/form/add',
                'view': 'command_form_add'
            },
            'get_command_parameters': {
                'name': 'Command parameters',
                'route': '/command/parameters'
            },
            'add_recheck': {
                'name': 'Recheck',
                'route': '/recheck/add',
                'method': 'POST'
            },
            'show_downtime_add': {
                'name': 'Downtime add form',
                'route': '/downtime/form/add',
                'view': 'downtime_form_add'
            },
            'add_downtime': {
                'name': 'Downtime',
                'route': '/downtime/add',
                'method': 'POST'
            },
            'add_command': {
                'name': 'Command',
                'route': '/command/add',
                'method': 'POST'
            }
        }

        super(PluginActions, self).__init__(webui, plugin_dir, cfg_filenames)

    def show_acknowledge_add(self):  # pylint:disable=no-self-use
        """Show form to add an acknowledge"""
        return {
            'title': request.query.get('title', _('Request an acknowledge')),
            'action': request.query.get('action', 'add'),
            'elements_type': request.query.get('elements_type'),
            'element_id': request.query.getall('element_id'),
            'element_name': request.query.getall('element_name'),
            'sticky': request.query.get('sticky', '1') == '1',
            'notify': request.query.get('notify', '1') == '1',
            'persistent': request.query.get('persistent', '1') == '1',
            'comment': request.query.get('comment', _('Acknowledge requested from WebUI')),
            'read_only': request.query.get('read_only', '0') == '1',
            'auto_post': request.query.get('auto_post', '0') == '1'
        }

    def add_acknowledge(self):
        """Add an acknowledgement

        Parameters:
        - element_id[]: all the livestate elements identifiers to be acknowledged

        - sticky
        - notify
        - persistent
        - comment
        """
        user = request.environ['beaker.session']['current_user']
        datamgr = request.app.datamgr

        element_ids = request.forms.getall('element_id')
        if not element_ids:
            logger.error("request to send an acknowledge: missing element_id parameter!")
            return self.webui.response_invalid_parameters(
                _('Missing element identifier: element_id')
            )

        problem = False
        status = ""

        # Method to get elements from the data manager
        elements_type = request.forms.get('elements_type', 'host')
        f = getattr(datamgr, 'get_%s' % elements_type)
        if not f:
            status += (_("No method to get a %s element") % elements_type)
        else:
            for element_id in element_ids:
                element = f(element_id)
                if not element:
                    status += _('%s element %s does not exist. ') % (elements_type, element_id)
                    continue

                # Prepare post request ...
                data = {
                    'action': 'add',
                    'host': element.id,
                    'service': None,
                    'user': user.id,
                    'sticky': request.forms.get('sticky', 'false') == 'true',
                    'notify': request.forms.get('notify', 'false') == 'true',
                    'persistent': request.forms.get('persistent', 'false') == 'true',
                    'comment': request.forms.get('comment', _('No comment'))
                }
                if elements_type == 'service':
                    data.update({'host': element.host.id, 'service': element.id})

                logger.info("Request an acknowledge, data: %s", data)
                if not datamgr.add_acknowledge(data=data):
                    status += _("Failed adding an acknowledge for %s. ") % element.name
                    problem = True
                else:
                    if elements_type == 'service':
                        data.update({'host': element.host.id, 'service': element.id})
                        status += _('Acknowledge sent for %s/%s. ') % \
                            (element.host.name, element.name)
                    else:
                        status += _('Acknowledge sent for %s. ') % \
                            element.name

        logger.info("Request an acknowledge, result: %s", status)

        if not problem:
            return self.webui.response_ok(message=status)
        return self.webui.response_ko(message=status)

    def show_recheck_add(self):  # pylint:disable=no-self-use
        """Show form to request a forced check"""
        return {
            'title': request.query.get('title', _('Send a check request')),
            'elements_type': request.query.get('elements_type'),
            'element_id': request.query.getall('element_id'),
            'element_name': request.query.getall('element_name'),
            'comment': request.query.get('comment', _('Re-check requested from WebUI')),
            'read_only': request.query.get('read_only', '0') == '1',
            'auto_post': request.query.get('auto_post', '0') == '1'
        }

    def add_recheck(self):
        """Request a forced check"""
        user = request.environ['beaker.session']['current_user']
        datamgr = request.app.datamgr

        element_ids = request.forms.getall('element_id')
        if not element_ids:
            logger.error("request to send an recheck: missing element_id parameter!")
            return self.webui.response_invalid_parameters(
                _('Missing element identifier: element_id')
            )

        problem = False
        status = ""

        # Method to get elements from the data manager
        elements_type = request.forms.get('elements_type', 'host')
        f = getattr(datamgr, 'get_%s' % elements_type)
        if not f:
            status += (_("No method to get a %s element") % elements_type)
        else:
            for element_id in element_ids:
                element = f(element_id)
                if not element:
                    status += _('%s element %s does not exist. ') % (elements_type, element_id)
                    continue

                # Prepare post request ...
                data = {
                    'host': element.id,
                    'service': None,
                    'user': user.id,
                    'comment': request.forms.get('comment', _('No comment'))
                }
                if elements_type == 'service':
                    data.update({'host': element.host.id, 'service': element.id})

                logger.info("Request a recheck, data: %s", data)
                if not datamgr.add_recheck(data=data):
                    status += _("Failed adding a check request for %s. ") % element.name
                    problem = True
                else:
                    if elements_type == 'service':
                        data.update({'host': element.host.id, 'service': element.id})
                        status += _('Check request sent for %s/%s. ') % \
                            (element.host.name, element.name)
                    else:
                        status += _('Check request sent for %s. ') % element.name

        logger.info("Request a re-check, result: %s", status)

        if not problem:
            return self.webui.response_ok(message=status)
        return self.webui.response_ko(message=status)

    def show_downtime_add(self):  # pylint:disable=no-self-use
        """Show form to add a downtime"""
        return {
            'title': request.query.get('title', _('Request a downtime')),
            'action': request.query.get('action', 'add'),
            'elements_type': request.query.get('elements_type'),
            'element_id': request.query.getall('element_id'),
            'element_name': request.query.getall('element_name'),
            'start_time': request.query.get('start_time'),
            'end_time': request.query.get('end_time'),
            'fixed': request.query.get('fixed', '1') == '1',
            'duration': request.query.get('duration', 86400),
            'comment': request.query.get('comment', _('Downtime requested from WebUI')),
            'read_only': request.query.get('read_only', '0') == '1',
            'auto_post': request.query.get('auto_post', '0') == '1'
        }

    def add_downtime(self):
        """Add a downtime"""
        user = request.environ['beaker.session']['current_user']
        datamgr = request.app.datamgr

        element_ids = request.forms.getall('element_id')
        if not element_ids:
            logger.error("request to send an downtime: missing element_id parameter!")
            return self.webui.response_invalid_parameters(
                _('Missing element identifier: element_id')
            )

        problem = False
        status = ""

        # Method to get elements from the data manager
        elements_type = request.forms.get('elements_type', 'host')
        f = getattr(datamgr, 'get_%s' % elements_type)
        if not f:
            status += (_("No method to get a %s element") % elements_type)
        else:
            for element_id in element_ids:
                element = f(element_id)
                if not element:
                    status += _('%s element %s does not exist. ') % (elements_type, element_id)
                    continue

                # Prepare post request ...
                data = {
                    'action': 'add',
                    'host': element.id,
                    'service': None,
                    'user': user.id,
                    'start_time': request.forms.get('start_time'),
                    'end_time': request.forms.get('end_time'),
                    'fixed': request.forms.get('fixed', 'false') == 'true',
                    'duration': int(request.forms.get('duration', '86400')),
                    'comment': request.forms.get('comment', _('No comment'))
                }
                if elements_type == 'service':
                    data.update({'host': element.host.id, 'service': element.id})

                logger.info("Request a downtime, data: %s", data)
                if not datamgr.add_downtime(data=data):
                    status += _("Failed adding a downtime for %s. ") % element.name
                    problem = True
                else:
                    if elements_type == 'service':
                        data.update({'host': element.host.id, 'service': element.id})
                        status += _('Downtime sent for %s/%s. ') % \
                            (element.host.name, element.name)
                    else:
                        status += _('Downtime sent for %s. ') % \
                            element.name

        logger.info("Request a downtime, result: %s", status)

        if not problem:
            return self.webui.response_ok(message=status)
        return self.webui.response_ko(message=status)

    def show_command_add(self):  # pylint:disable=no-self-use
        """Show form to send a command"""
        elements_type = request.query.get('elements_type')

        commands_list = {}
        for command in commands:
            # Ignore global commands
            if commands[command].get('global', True):
                continue
            # Ignore commands that do not concern our current elements type
            if elements_type != commands[command].get('elements_type', ""):
                continue
            commands_list.update({command: commands[command]})

        return {
            'title': request.query.get('title', _('Send a command')),
            'elements_type': request.query.get('elements_type'),
            'element_id': request.query.getall('element_id'),
            'element_name': request.query.getall('element_name'),
            'comment': request.query.get('comment', _('Command requested from WebUI')),
            'read_only': request.query.get('read_only', '0') == '1',
            'auto_post': request.query.get('auto_post', '0') == '1',
            'commands_list': commands_list
        }

    def get_command_parameters(self):
        """Get a command parameters list

        Returns a JSON object containing, for the requested command, all the parameters list
        """
        elements_type = request.query.get('elements_type')
        command = request.query.get('command')

        # Get elements from the commands list
        if command not in commands:
            response.status = 409
            response.content_type = 'application/json'
            return json.dumps(
                {'error': "the command '%s' does not exist" % command}
            )

        logger.info("Element type: %s", elements_type)
        plugin = self.webui.find_plugin(elements_type)
        if not plugin:
            response.status = 409
            response.content_type = 'application/json'
            return json.dumps(
                {'error': "the plugin for '%s' is not existing or not installed" % elements_type}
            )
        logger.info("Found plugin: %s", plugin.name)

        # Provide the described parameters
        parameters = {}
        for parameter in commands[command].get('parameters', {}):
            logger.debug("Got plugin table parameter: %s / %s", parameter, plugin.table[parameter])
            parameters[parameter] = deepcopy(plugin.table[parameter])
            logger.info("Got plugin parameter: %s / %s", parameter, parameters[parameter])

            if 'allowed' in plugin.table[parameter]:
                allowed_values = {}
                allowed = plugin.table[parameter].get('allowed', '')
                if not isinstance(allowed, list):
                    allowed = allowed.split(',')
                logger.debug("Get real allowed values for %s: %s", parameter, allowed)
                if allowed[0] == '':
                    allowed = []
                for allowed_value in allowed:
                    value = plugin.table[parameter].get('allowed_%s' % allowed_value, allowed_value)
                    allowed_values.update({'%s' % allowed_value: value})

                parameters[parameter]['allowed'] = allowed_values
                logger.debug("Real allowed values for %s: %s", parameter, allowed_values)

        logger.info("Parameters: %s", parameters)
        response.status = 200
        response.content_type = 'application/json'
        return json.dumps(parameters)

    def add_command(self):
        """Send a command"""
        datamgr = request.app.datamgr

        # Get the command from the request parameters
        command = request.forms.get('command')
        if not command or command == "None":
            logger.error("request to send an unknown command: missing command parameter!")
            return self.webui.response_invalid_parameters(
                _('Missing command name: command')
            )

        # Get elements from the commands list
        if command not in commands:
            logger.error("request to send an unknown command: unknown command: %s!", command)
            return self.webui.response_invalid_parameters(
                _('Unknown command: %s' % command)
            )

        # Provide the described parameters
        parameters = []
        for parameter in commands[command].get('parameters', {}):
            parameter_value = request.forms.get(parameter, None)
            if parameter_value is None:
                logger.error("missing command parameter in the request: %s", parameter)
                return self.webui.response_invalid_parameters(
                    _('Missing parameter: %s' % parameter)
                )
            logger.debug("Command parameter: %s = %s", parameter, parameter_value)
            parameters.append(parameter_value)
        logger.info("Command parameters: %s", parameters)

        element_ids = request.forms.getall('element_id')
        if not element_ids:
            logger.error("request to send an command: missing element_id parameter!")
            return self.webui.response_invalid_parameters(
                _('Missing element identifier: element_id')
            )

        problem = False
        status = ""

        # Method to get elements from the data manager
        elements_type = request.forms.get('elements_type', 'host')
        f = getattr(datamgr, 'get_%s' % elements_type)
        if not f:
            status += (_("No method to get a %s element") % elements_type)
        else:
            for element_id in element_ids:
                element = f(element_id)
                if not element:
                    status += _('%s element %s does not exist. ') % (elements_type, element_id)
                    continue

                # Prepare post request ...
                data = {
                    'timestamp': int(time.time()),
                    'command': command,
                    'element': element.name,
                    'parameters': ';'.join(parameters)
                }
                if elements_type == 'service':
                    data.update({'element': '%s/%s' % (element.host.name, element.name)})

                logger.info("Send a command, data: %s", data)
                if not datamgr.add_command(data=data):
                    status += _("Failed sending a command for %s. ") % element.name
                    problem = True
                else:
                    if elements_type == 'service':
                        data.update({'host': element.host.id, 'service': element.id})
                        status += _('Sent a command %s for %s/%s. ') % \
                            (command, element.host.name, element.name)
                    else:
                        status += _('Sent a command %s for %s. ') % (command, element.name)

        logger.info("Sent a command, result: %s", status)

        if not problem:
            return self.webui.response_ok(message=status)
        return self.webui.response_ko(message=status)
