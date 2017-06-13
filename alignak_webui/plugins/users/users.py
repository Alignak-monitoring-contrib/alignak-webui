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

    def __init__(self, webui, plugin_dir, cfg_filenames=None):
        """User plugin

        Declare routes for adding, deleting a user

        Overload the default get route to declare filters.
        """
        self.name = 'Users'
        self.backend_endpoint = 'user'

        self.pages = {
            'show_password_change': {
                'name': 'Password change form',
                'route': '/password_change_request',
                'view': 'change_password'
            },

            'change_password': {
                'name': 'Change password',
                'route': '/change_password',
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

            'get_user_widget': {
                'name': 'User widget',
                'route': '/user_widget/<element_id>/<widget_id>',
                'view': 'user',
                'widgets': [
                    {
                        'id': 'information',
                        'for': ['user'],
                        'order': 2,
                        'name': _('Information'),
                        'level': 0,
                        'template': 'user_information_widget',
                        'icon': 'info',
                        'description': _(
                            'User information: displays user general information.'
                        ),
                        'options': {}
                    },
                    {
                        'id': 'preferences',
                        'for': ['user'],
                        'name': _('Preferences'),
                        'level': 2,
                        'template': 'user_preferences_widget',
                        'icon': 'heart',
                        'description': _(
                            'User preferences: displays user Web UI preferences.'
                        ),
                        'options': {}
                    },
                ]
            },
        }

        super(PluginUsers, self).__init__(webui, plugin_dir, cfg_filenames)

    def show_password_change(self):  # pylint: disable=no-self-use
        """Show form to change a password"""
        return {
            'title': request.query.get('title', _('Request to change a user password')),
            'action': request.query.get('action', 'password'),
            'elements_type': request.query.get('elements_type'),
            'element_id': request.query.getall('element_id'),
            'element_name': request.query.getall('element_name'),
            'read_only': request.query.get('read_only', '0') == '1',
            'auto_post': request.query.get('auto_post', '0') == '1'
        }

    def change_password(self):
        """Change a password

        Parameters:
        - element_id[]: all the users identifiers to be updated (usual way is to have only one!)

        - password1 and password2
        """
        datamgr = request.app.datamgr

        element_ids = request.forms.getall('element_id')
        if not element_ids:
            logger.error("request to change a password: missing element_id parameter!")
            return self.webui.response_invalid_parameters(
                _('Missing user identifier: element_id')
            )

        if not request.forms.get('password1'):
            logger.error("request to change a password: missing password1 parameter!")
            return self.webui.response_invalid_parameters(
                _('The first password field must not be empty')
            )

        if not request.forms.get('password2'):
            logger.error("request to change a password: missing password2 parameter!")
            return self.webui.response_invalid_parameters(
                _('The second password field must not be empty')
            )

        # Is the form considered as valid by the client
        if request.forms.get('valid_form', 'false') != 'true':
            logger.error("request to change a password: invalid form content!")
            return self.webui.response_invalid_parameters(
                _('The form is not validated because of its content.')
            )

        problem = False
        status = ""

        # Method to get elements from the data manager
        elements_type = request.forms.get('elements_type', 'user')
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
                    'password': request.forms.get('password1')
                }

                logger.info("Changing a user password...")
                if not datamgr.update_object(element, data=data):
                    status += _("Failed updating data for the user '%s'. ") % element.name
                    problem = True
                else:
                    status += _('User %s updated.') % element.name

        logger.info("Change a password, result: %s", status)

        if not problem:
            return self.webui.response_ok(message=status)
        return self.webui.response_ko(message=status)

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
