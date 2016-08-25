#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (C) 2015-2016 F. Mohier

"""
    Plugin Users
"""

import json

from collections import OrderedDict

from logging import getLogger
from bottle import request, response

from alignak_webui import _
from alignak_webui.utils.plugin import Plugin

logger = getLogger(__name__)


class PluginUsers(Plugin):
    """ user backend elements management plugin """

    def __init__(self, app, cfg_filenames=None):
        """
        User plugin

        Declare routes for adding, deleting a user

        Overload the default get route to declare filters.
        """
        self.name = 'Users'
        self.backend_endpoint = 'user'

        self.pages = {
            'show_user_add': {
                'name': 'User add form',
                'route': '/user/form/add',
                'view': 'user_form_add'
            },
            'add_user': {
                'name': 'User add',
                'route': '/user/add',
                'method': 'POST'
            },
            'show_user_delete': {
                'name': 'User delete form',
                'route': '/user/form/delete',
                'view': 'user_form_delete'
            },
            'delete_user': {
                'name': 'User delete',
                'route': '/user/delete',
                'method': 'POST'
            },

            'get_all': {
                'name': '%s' % self.name,
                'route': '/%ss' % self.backend_endpoint,
                'view': '%ss' % self.backend_endpoint,
                'search_engine': True,
                'search_prefix': '',
                'search_filters': {
                    '01': (_('Administrator'), 'role:administrator'),
                    '02': (_('Power'), 'role:power'),
                    '03': (_('User'), 'role:user'),
                    '04': (_('Guest'), 'name:anonymous'),
                }
            },
        }

        super(PluginUsers, self).__init__(app, cfg_filenames)

    def show_user_add(self):  # pragma: no cover - not yet implemented
        """
            Show form to add a user
        """
        return {
            'name': request.query.get('name', ''),
            'password': request.query.get('password', 'no_password'),
            'alias': request.query.get('alias', 'Friendly name'),
            'is_admin': request.query.get('is_admin', '0') == '1',
            'expert': request.query.get('expert', '1') == '1',
            'can_submit_commands': request.query.get('can_submit_commands', '1') == '1',
            'notes': request.query.get('notes', _('User description ...')),
            'title': request.query.get('title', _('Create a new user')),
        }

    def add_user(self):
        """
            Add a user
        """
        datamgr = request.app.datamgr

        name = request.forms.get('name', '')
        if not name:
            logger.error("request to add a user: missing name parameter!")
            return self.webui.response_invalid_parameters(_('Missing user name'))

        # Get main realm
        default_realm = datamgr.get_realm({'where': {'name': 'All'}})

        # Get main TP
        default_tp = datamgr.get_timeperiod({'where': {'name': '24x7'}})

        # Prepare post request ...
        data = {
            'imported_from': self.webui.app_config['name'],
            'definition_order': 100,

            'name': name,
            'password': request.forms.get('password', ''),
            'alias': request.forms.get('alias', ''),
            'notes': request.forms.get('notes', ''),
            'is_admin': request.forms.get('is_admin') == '1',
            'expert': request.forms.get('expert') == '1',
            'can_submit_commands': request.forms.get('can_submit_commands') == '1',

            'email': request.forms.get('email'),

            'customs': request.forms.get('customs', default={}, type=dict),

            'host_notifications_enabled':
                request.forms.get('host_notifications_enabled') == '1',
            'host_notification_period':
                request.forms.get('host_notification_period', default_tp),
            'host_notification_commands':
                request.forms.get('host_notification_commands', default=[], type=list),
            'host_notification_options':
                request.forms.get('host_notification_options', default=[], type=list),

            'service_notifications_enabled':
                request.forms.get('service_notifications_enabled') == '1',
            'service_notification_period':
                request.forms.get('service_notification_period', default_tp),
            'service_notification_commands':
                request.forms.get('service_notification_commands', default=[], type=list),
            'service_notification_options':
                request.forms.get('service_notification_options', default=[], type=list),

            'min_business_impact': request.forms.get('min_business_impact', 0),

            '_realm': request.forms.get('_realm', default_realm)
        }
        user_id = datamgr.add_user(data=data)
        if not user_id:
            return self.webui.response_ko(_('User creation failed'))

        # Refresh data ...
        # datamgr.require_refresh()

        return self.webui.response_ok(message=_('User created'))

    def show_user_delete(self):  # pragma: no cover - not yet implemented
        """
        User deletion form
        """
        datamgr = request.app.datamgr

        user_id = request.query.get('user_id', -1)
        if user_id == -1:
            logger.error("request to show a user deletion form: missing user_id parameter!")
            return self.webui.response_invalid_parameters(_('Missing user identifier'))

        user = datamgr.get_user(user_id)
        if not user:  # pragma: no cover - should never happen
            return self.webui.response_invalid_parameters(_('User does not exist'))

        return {
            'user_id': user_id,
            'name': user.get_username(),
            'notes': request.query.get('notes', _('Optional notes ...')),
            'title': request.query.get('title', _('Delete a user')),
        }

    def delete_user(self):  # pragma: no cover - not yet implemented
        """
            Delete a user
        """
        datamgr = request.app.datamgr

        user_id = request.forms.get('user_id', -1)
        if user_id == -1:  # pragma: no cover - should never happen
            logger.error("request to close a user: missing user_id parameter!")
            return self.webui.response_invalid_parameters(_('Missing user identifier'))

        # User deletion request ...
        if not datamgr.delete_user(user_id):  # pragma: no cover - should never happen
            return self.webui.response_ko(_('User deletion failed'))

        # Refresh data ...
        # datamgr.require_refresh()

        return self.webui.response_ok(message=_('User deleted'))
