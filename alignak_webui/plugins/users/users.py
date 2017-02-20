#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (C) 2015-2016 F. Mohier

"""
    Plugin Users
"""

from logging import getLogger

from bottle import request, template

from alignak_webui.utils.plugin import Plugin

# pylint: disable=invalid-name
logger = getLogger(__name__)


class PluginUsers(Plugin):
    """ user backend elements management plugin """

    def __init__(self, app, webui, cfg_filenames=None):
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

            'show_user_preferences': {
                'name': 'User preferences',
                'route': '/preferences/user',
                'view': 'preferences'
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

            'get_user_widget': {
                'name': 'User widget',
                'route': '/user_widget/<element_id>/<widget_id>',
                'view': 'user',
                'widgets': [
                    {
                        'id': 'information',
                        'for': ['user'],
                        'name': _('Information'),
                        'template': 'user_information_widget',
                        'icon': 'info',
                        'description': _(
                            'User information: displays user general information.'
                        ),
                        'options': {}
                    },
                ]
            },
        }

        super(PluginUsers, self).__init__(app, webui, cfg_filenames)

    def show_user_add(self):  # pylint:disable=no-self-use
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

    def show_user_preferences(self):
        # pylint: disable=no-self-use
        """
            Show the user preferences view
        """
        return {}

    def get_user_widget(self, element_id, widget_id,
                        embedded=False, identifier=None, credentials=None):
        # Because there are many locals needed :)
        # pylint: disable=too-many-locals,too-many-arguments
        """
        Display a user widget
        """
        user = request.environ['beaker.session']['current_user']
        datamgr = request.app.datamgr

        logger.debug("get_user_widget: %s, %s", element_id, widget_id)

        # Get user
        user = datamgr.get_user(element_id)
        if not user:
            # Test if we got a name instead of an id
            user = datamgr.get_user(search={'max_results': 1, 'where': {'name': element_id}})
            if not user:
                return self.webui.response_invalid_parameters(_('User does not exist'))

        widget_place = request.params.get('widget_place', 'user')
        widget_template = request.params.get('widget_template', 'user_widget')
        # Search in the application widgets (all plugins widgets)
        for widget in self.webui.get_widgets_for(widget_place):
            if widget_id.startswith(widget['id']):
                widget_template = widget['template']
                logger.info("Widget found, template: %s", widget_template)
                break
        else:
            logger.info("Widget identifier not found: using default template and no options")

        title = request.params.get('title', _('User: %s') % user.name)

        # Use required template to render the widget
        return template('_widget', {
            'widget_id': widget_id,
            'widget_name': widget_template,
            'widget_place': 'user',
            'widget_template': widget_template,
            'widget_uri': request.urlparts.path,
            'options': {},

            'user': user,

            'title': title,
            'embedded': embedded,
            'identifier': identifier,
            'credentials': credentials
        })
