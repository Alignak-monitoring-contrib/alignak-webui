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
    WebUI application
"""

from __future__ import print_function

import json
import os
from importlib import import_module
import inspect
from logging import getLogger

# Bottle import
from bottle import hook, route, request, response, redirect, static_file, parse_auth
from bottle import BaseTemplate, template, TEMPLATE_PATH
import bottle

# Application import
from alignak_webui.backend.datamanager import DataManager
from alignak_webui.utils.helper import Helper
from alignak_webui.utils.plugin import Plugin

# pylint: disable=invalid-name
logger = getLogger(__name__)

# --------------------------------------------------------------------------------------------------
# WebUI routes
# --------------------------------------------------------------------------------------------------
# CORS decorator
def enable_cors(fn):
    """
    CORS decorator

    Send the CORS headers for ajax request
    """
    def _enable_cors(*args, **kwargs):
        # set CORS headers
        response.headers['Access-Control-Allow-Origin'] = \
            request.app.config.get('cors_acao', 'http://127.0.0.1')
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = \
            'Origin, Accept, Authorization, X-HTTP-Method-Override, If-Match, Content-Type'
        response.headers['Access-Control-Allow-Credentials'] = 'true'

        if bottle.request.method != 'OPTIONS':
            # actual request; reply with the actual response
            return fn(*args, **kwargs)

        # response.status = 204

    return _enable_cors


@route('/external/<widget_type>/<identifier>/<action:path>', method=['GET', 'POST', 'OPTIONS'])
@route('/external/<widget_type>/<identifier>', method=['GET', 'POST', 'OPTIONS'])
@enable_cors
def external(widget_type, identifier, action=None):
    # pylint: disable=too-many-return-statements, unsupported-membership-test
    # pylint: disable=unsubscriptable-object
    """
    Application external identifier

    Use internal authentication (if a user is logged-in) or external basic authentication provided
    by the requiring application.

    Search in the known 'widget_type' (widget or table) to find the element 'identifier'.

    Use the 'links' parameter to prefix the navigation URLs.
    """

    session = request.environ['beaker.session']
    if 'current_user' in session:
        current_user = session['current_user']
        if not user_authentication(current_user.token, None):
            # Redirect to application login page
            logger.warning(
                "user in the session is not authenticated."
                " Redirecting to the login page..."
            )
            redirect('/login')
        credentials = current_user.token + ':'

    else:
        # Authenticate external access...
        if 'Authorization' not in request.headers or not request.headers['Authorization']:
            logger.warning("external application access denied")
            response.status = 401
            response.content_type = 'text/html'
            return _(
                '<div>'
                '<h1>External access denied.</h1>'
                '<p>To embed an Alignak WebUI widget or table, you must provide credentials.<br>'
                'Log into the Alignak WebUI with your credentials, or make a request '
                'with a Basic-Authentication allowing access to Alignak backend.</p>'
                '</div>'
            )

        # Get HTTP authentication
        authentication = request.headers.get('Authorization')
        username, password = parse_auth(authentication)

        if not user_authentication(username, password):
            logger.warning("external application access denied for %s", username)
            response.status = 401
            response.content_type = 'text/html'
            return _(
                '<div>'
                '<h1>External access denied.</h1>'
                '<p>The provided credentials do not grant you access to Alignak WebUI.<br>'
                'Please provide proper credentials.</p>'
                '</div>'
            )

        current_user = session['current_user']
        credentials = current_user.token + ':'

        # Make session data available in the templates
        BaseTemplate.defaults['current_user'] = session['current_user']

        # Make data manager available in the request and in the templates
        request.app.datamgr = DataManager(
            backend_endpoint=request.app.config.get(
                'alignak_backend',
                'http://127.0.0.1:5000'
            ),
            alignak_endpoint=request.app.config.get(
                'alignak_arbiter',
                'http://127.0.0.1:7070'
            ),
            session=request.environ['beaker.session']
        )
        BaseTemplate.defaults['datamgr'] = request.app.datamgr

    logger.debug(
        "External request, element type: %s", widget_type
    )

    if widget_type not in ['files', 'widget', 'table', 'list', 'host', 'service', 'user']:
        logger.warning("External application requested unknown type: %s", widget_type)
        response.status = 409
        response.content_type = 'text/html'
        return _(
            '<div><h1>Unknown required type: %s.</h1>'
            '<p>The required type is unknwown</p></div>' % widget_type
        )

    if widget_type == 'files':
        if identifier == 'js_list':
            response.status = 200
            response.content_type = 'application/json'
            return json.dumps(
                {'status': 'ok', 'files': get_app_webui().js_list}
            )
        elif identifier == 'css_list':
            response.status = 200
            response.content_type = 'application/json'
            return json.dumps(
                {'status': 'ok', 'files': get_app_webui().css_list}
            )
        else:
            logger.warning("External application requested unknown files: %s", identifier)
            response.status = 409
            response.content_type = 'application/json'
            return json.dumps(
                {'status': 'ko', 'message': "Unknown files list: %s" % identifier}
            )

    if widget_type == 'widget':
        found_widget = None
        for widget in get_app_webui().get_widgets_for('external'):
            if identifier == widget['id']:
                found_widget = widget
                break
        else:
            logger.warning("External application requested unknown widget: %s", identifier)
            response.status = 409
            response.content_type = 'text/html'
            return _(
                '<div><h1>Unknown required widget: %s.</h1>'
                '<p>The required widget is not available.</p></div>' % identifier
            )
        logger.debug("Found widget: %s", found_widget)

        embedded_element = found_widget['function'](
            embedded=True,
            identifier=identifier, credentials=credentials
        )

        if request.params.get('page', 'no') == 'no':
            return embedded_element

        return template('external_widget', {
            'embedded_element': embedded_element
        })

    if widget_type == 'table':
        found_table = None
        for table in get_app_webui().get_tables_for('external'):
            if identifier == table['id']:
                found_table = table
                break
        else:
            logger.warning("External application requested unknown table: %s", identifier)
            response.status = 409
            response.content_type = 'text/html'
            return _(
                '<div><h1>Unknown required table: %s.</h1>'
                '<p>The required table is not available.</p></div>' % identifier
            )
        logger.debug("Found table: %s", found_table)

        if action and action in found_table['actions']:
            logger.info("Required action: %s = %s", action, found_table['actions'][action])
            return found_table['actions'][action]()

        if request.params.get('page', 'no') == 'no':
            return found_table['function'](
                embedded=True, identifier=identifier, credentials=credentials
            )

        return template('external_table', {
            'embedded_element': found_table['function'](
                embedded=True, identifier=identifier, credentials=credentials
            )
        })

    if widget_type == 'list':
        if identifier in get_app_webui().lists:
            return get_app_webui().lists[identifier]['function'](embedded=True)
        else:
            logger.warning("External application requested unknown list: %s", identifier)
            response.status = 409
            response.content_type = 'text/html'
            return _(
                '<div><h1>Unknown required list: %s.</h1>'
                '<p>The required list is not available.</p></div>' % identifier
            )

    if widget_type in ['host', 'service', 'user']:
        if not action:
            logger.warning(
                "External application requested %s widget without widget name", widget_type
            )
            response.status = 409
            response.content_type = 'text/html'
            return _(
                '<div><h1>Missing %s widget name.</h1>'
                '<p>You must provide a widget name</p></div>' % widget_type
            )

        # Identifier is the element identifier, not the widget one !
        found_widget = None
        for widget in get_app_webui().get_widgets_for(widget_type):
            if action == widget['id']:
                found_widget = widget
                break
        else:
            logger.warning("External application requested unknown widget: %s", action)
            response.status = 409
            response.content_type = 'text/html'
            return _(
                '<div><h1>Unknown required widget: %s.</h1>'
                '<p>The required widget is not available.</p></div>' % action
            )
        logger.debug("Found %s widget: %s", widget_type, found_widget)

        if request.params.get('page', 'no') == 'no':
            return found_widget['function'](
                element_id=identifier, widget_id=found_widget['id'],
                embedded=True, identifier=identifier, credentials=credentials
            )

        return template('external_widget', {
            'embedded_element': found_widget['function'](
                element_id=identifier, widget_id=found_widget['id'],
                embedded=True, identifier=identifier, credentials=credentials
            )
        })


# --------------------------------------------------------------------------------------------------
# WebUI edition mode
# --------------------------------------------------------------------------------------------------
@route('/edition_mode', 'POST')
# User preferences page ...
def edition_mode():
    """
        Set edition mode on / off
    """
    # Session...
    session = request.environ['beaker.session']
    logger.debug("edition_mode, session: %s", session)

    current_state = request.params.get('state', 'on')
    logger.debug("edition_mode, current state: %s", current_state)

    session['edition_mode'] = (current_state == 'off')

    # Make session edition mode available in the templates
    BaseTemplate.defaults['edition_mode'] = session['edition_mode']
    logger.debug("edition_mode, session: %s", session)

    if session['edition_mode']:
        return _('Edition mode enabled')
    else:
        return _('Edition mode disabled')


class WebUI(object):
    """
    WebUI application
    """
    def __init__(self, app, name='alignak_webui', config=None):
        """
        Application initialization

        :param: config
        :type: dict
        """

        logger.info("Initializing application...")

        try:
            # Store all the plugins
            self.plugins = []

            # Store all the widgets
            self.widgets = {}

            # Store all the tables
            self.tables = {}

            # Store all the lists
            self.lists = {}

            # Helper class
            self.helper = Helper()

            # Application configuration
            self.app = app
            self.name = name
            self.config = config

            # Application data manager and connection
            self.datamgr = None
            self.current_user = None

            # Load plugins in the plugins directory ...
            plugins_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'plugins')
            self.plugins_count = self.load_plugins(plugins_dir=plugins_dir)
            logger.info("loaded %d plugins from: %s", self.plugins_count, plugins_dir)
        except Exception as exp:
            logger.exception("Application initialization exception: %s", exp)

    def load_plugins(self, plugins_dir):
        # pylint: disable=too-many-locals, too-many-nested-blocks, undefined-loop-variable
        """
        Load plugins from the provided directory

        If the plugin has
        - 'pages', declare routes for the pages
        - 'widgets', declare widgets in the main widgets list

        Register the plugin 'views' directory in the Bottle views

        If the plugin has a 'load_config' function, call it
        """
        logger.info("load plugins from: %s", plugins_dir)

        # Get list of sub directories
        try:
            plugin_names = [
                fname for fname in os.listdir(plugins_dir)
                if os.path.isdir(os.path.join(plugins_dir, fname))
            ]
        except OSError as exp:
            logger.error("plugins directory '%s' does not exist!", plugins_dir)
            return 0

        # Try to import all found supposed modules
        i = 0
        for plugin_name in plugin_names:
            logger.info("trying to load plugin '%s' ...", plugin_name)
            try:
                # Import the module in the package namespace
                plugin = import_module(
                    '.%s.%s.%s' % (plugins_dir.rsplit('/')[-1], plugin_name, plugin_name),
                    __package__
                )

                # Plugin declared classes ...
                classes = inspect.getmembers(plugin, inspect.isclass)

                # Find "Plugin" sub classes in imported module ...
                p_classes = [co for dummy, co in classes if issubclass(co, Plugin) and co != Plugin]
                if p_classes:
                    logger.debug("Found plugins classes: %s", p_classes)
                    cfg_files = [
                        '/usr/local/etc/%s/plugin_%s.cfg' % (self.name, plugin_name),
                        '/etc/%s/plugin_%s.cfg' % (self.name, plugin_name),
                        '~/%s/plugin_%s.cfg' % (self.name, plugin_name),
                        os.path.join(os.path.join(plugins_dir, plugin_name), 'settings.cfg')
                    ]

                    for p_class in p_classes:
                        # Create a plugin instance
                        plugin_instance = p_class(self.app, self, cfg_files)

                        i += 1
                        self.plugins.append(plugin_instance)

                # Add the views sub-directory of the plugin in the Bottle templates path
                dir_views = os.path.join(
                    os.path.join(plugins_dir, plugin_name), 'views'
                )
                if os.path.isdir(dir_views):
                    TEMPLATE_PATH.append(os.path.join(
                        os.path.join(plugins_dir, plugin_name), 'views'
                    ))
                    logger.debug("registered views directory '%s'", os.path.join(
                        os.path.join(plugins_dir, plugin_name), 'views'
                    ))

                logger.info("registered plugin '%s'", plugin_name)

            except Exception as exp:  # pragma: no cover - simple security ...
                logger.exception("loading plugin %s, exception: %s", plugin_name, exp)

        return i

    def get_url(self, name):  # pylint:disable=no-self-use
        """
        Get the URL for a named route
        :param name:
        :return:
        """
        return self.app.get_url(name)

    @property
    def js_list(self):
        """
        Get the list of Javascript files
        :return:
        """
        js_list = [
            "/static/js/jquery-1.12.0.min.js",
            "/static/js/jquery-ui-1.11.4.min.js"
        ]

        if self.config.get('bootstrap4', '0') == '1':
            js_list += [
                "/static/js/bootstrap4.min.js"
            ]
        else:
            js_list += [
                "/static/js/bootstrap.min.js"
            ]

        js_list += [
            "/static/js/moment-with-langs.min.js",
            "/static/js/daterangepicker.js",
            "/static/js/jquery.jclock.js",
            "/static/js/jquery.jTruncate.js",
            "/static/js/typeahead.bundle.min.js",
            "/static/js/screenfull.js",
            "/static/js/alertify.min.js",
            "/static/js/selectize.min.js",
            "/static/js/Chart.min.js",
            "/static/js/jstree.min.js",
        ]

        if self.config.get('bootstrap4', '0') == '1':
            js_list += [
                "/static/js/datatables.bootstrap4.min.js"
            ]
        else:
            js_list += [
                "/static/js/datatables.min.js"
                # "/static/js/datatables.js"
            ]

        js_list += [
            "/static/js/material/arrive.min.js",
            "/static/js/material/material.min.js",
            "/static/js/material/ripples.min.js"
        ]

        return js_list

    @property
    def css_list(self):
        """
        Get the list of Javascript files
        :return:
        """
        if self.config.get('bootstrap4', '0') == '1':
            css_list = [
                "/static/css/bootstrap4.min.css"
            ]
        else:
            css_list = [
                "/static/css/bootstrap.min.css"
            ]

        css_list += [
            "/static/css/font-awesome.min.css",
            "/static/css/typeahead.css",
            "/static/css/daterangepicker.css",
            "/static/css/alertify.min.css",
            "/static/css/alertify.bootstrap.min.css",
            "/static/css/timeline.css"
        ]

        css_list += [
            "/static/css/font-roboto.css",
            "/static/css/material-icons.css",
            "/static/css/material/bootstrap-material-design.min.css",
            "/static/css/material/ripples.min.css"
        ]

        css_list += [
            "/static/css/jstree/style.min.css",
        ]
        if self.config.get('bootstrap4', '0') == '1':
            css_list += [
                "/static/css/datatables.bootstrap4.min.css",
            ]
        else:
            css_list += [
                "/static/css/datatables.min.css",
            ]

        css_list += [
            "/static/css/alignak_webui.css",
            "/static/css/alignak_webui-items.css"
        ]

        return css_list

    # --------------------------------------------------------------------------------------------------
    # User authentication
    # --------------------------------------------------------------------------------------------------
    def user_authentication(self, username, password):
        """
        Authenticate a user thanks to his username / password

        The authentication is requested near the data manager. This functions uses the data manager
        of the current session, else it creates a new one.

        Stores the authenticated User object in the session to make it available
        """

        logger.debug("user_authentication, authenticating: %s", username)

        # Session...
        session = request.environ['beaker.session']

        session['login_message'] = None
        if 'current_user' not in session or not session['current_user']:
            # Build DM without any session or user parameter
            self.datamgr = DataManager(
                backend_endpoint=self.app.config.get('%s.alignak_backend' % self.name,
                                                     'http://127.0.0.1:5000'))

            # Set user for the data manager and try to log-in.
            if not self.datamgr.user_login(username, password, load=(password is not None)):
                session['login_message'] = self.datamgr.connection_message

                logger.warning("user authentication refused: %s", session['login_message'])
                return False

            # Update application variables
            self.current_user = self.datamgr.logged_in_user

            # Update session variables
            session['current_user'] = self.current_user
            session['current_realm'] = self.datamgr.my_realm
            session['current_ls'] = self.datamgr.my_ls

        logger.debug("user_authentication, current user authenticated")
        return True

    def find_plugin(self, name):
        """
        Find a plugin with its name
        """
        for plugin in self.plugins:
            if plugin.name == name:
                return plugin
        return None

    def get_widgets_for(self, place):
        """
        For a specific place like 'dashboard' or 'external', returns the application widgets list
        """
        widgets_list = self.widgets.get(place, [])
        for plugin in self.plugins:
            widgets_list += plugin.widgets.get(place, [])
        return widgets_list

    def get_tables_for(self, place):
        """
        For a specific place like 'external', return the application tables list
        """
        tables = self.tables.get(place, [])
        for plugin in self.plugins:
            if place in plugin.tables:
                tables = tables + plugin.tables[place]
        return tables

    ##
    # Make responses for browser client requests
    # ------------------------------------------------------------------------------------------
    @staticmethod
    def response_ok(message="Ok"):
        """
        Request is ok
        """
        response.status = 200
        response.content_type = 'application/json'
        return json.dumps(
            {'status': 'ok', 'message': message}
        )

    @staticmethod
    def response_data(data):
        """
        Request is ok and contains data
        """
        response.status = 200
        response.content_type = 'application/json'
        return json.dumps(data)

    @staticmethod
    def response_invalid_parameters(message="Missing parameter"):
        """
        Request parameters are invalid
        """
        response.status = 204
        response.content_type = 'application/json'
        return json.dumps(
            {'status': 'ko', 'message': message}
        )

    @staticmethod
    def response_missing_file(message="No file selected for upload"):
        """
        File to upload missing parameter
        """
        return WebUI.response_ko(message=message, code=412)

    @staticmethod
    def response_ko(message="Error!", code=409):
        """
        Request failed
        """
        response.status = code
        response.content_type = 'application/json'

        return json.dumps(
            {'status': 'ko', 'message': message}
        )
