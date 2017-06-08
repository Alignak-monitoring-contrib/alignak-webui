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
from bottle import request, response, TEMPLATE_PATH

# Application import
from alignak_webui.backend.datamanager import DataManager
from alignak_webui.utils.helper import Helper
from alignak_webui.utils.plugin import Plugin

# pylint: disable=invalid-name
logger = getLogger(__name__)


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
        self.plugins_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'plugins')
        self.plugins_count = self.load_plugins(plugins_dir=self.plugins_dir)
        logger.info("loaded %d plugins from: %s", self.plugins_count, self.plugins_dir)

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
        except OSError as exp:  # pragma: no cover - simple security ...
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
                        os.path.join(os.path.join(plugins_dir, plugin_name), 'settings.cfg'),
                        '~/%s/plugin_%s.cfg' % (self.name, plugin_name),
                        '/etc/%s/plugin_%s.cfg' % (self.name, plugin_name),
                        '/usr/local/etc/%s/plugin_%s.cfg' % (self.name, plugin_name),
                    ]

                    for p_class in p_classes:
                        # Create a plugin instance
                        plugin_instance = p_class(self, plugin_name, cfg_files)

                        if not plugin_instance.is_enabled():
                            logger.warning("Plugin '%s' is disabled!", plugin_name)
                            continue

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
            "/static/js/BootSideMenu.js",
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
            "/static/css/alertify/alertify.min.css",
            "/static/css/alertify/bootstrap.min.css",
            "/static/css/BootSideMenu.css",
            "/static/css/timeline.css",
            "/static/css/selectize.bootstrap3.css",
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

    # ---------------------------------------------------------------------------------------------
    # User authentication
    # ---------------------------------------------------------------------------------------------
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
            self.datamgr = DataManager(self.app)

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
        """Find a plugin with its name or its backend endpoint"""
        for plugin in self.plugins:
            if plugin.name == name:
                return plugin
        for plugin in self.plugins:
            if plugin.backend_endpoint == name:
                return plugin
        return None

    def get_widgets_for(self, place):
        """For a specific place like 'dashboard' or 'external', returns the widgets list
        sorted by the defined widget order property"""
        widgets_list = []
        for plugin in self.plugins:
            logger.debug("WebUI plugin %s", plugin)
            for widget in plugin.widgets.get(place, []):
                logger.debug(" - widget %s, order: %d, %s", widget['name'], widget['order'], widget)
                # Check if the widget requires a specific plugin to be present and enabled
                if widget.get('plugin', None):
                    needed_plugin = self.find_plugin(widget.get('plugin', None))
                    if not needed_plugin or not needed_plugin.is_enabled():
                        logger.debug("Widget '%s' ignored because of missing "
                                     "or disabled plugin: %s", widget['name'], plugin)
                        continue

                widgets_list.append(widget)

        sorted_widgets = sorted(widgets_list, key=lambda x: x['order'], reverse=False)
        return sorted_widgets

    def get_tables_for(self, place):
        """For a specific place like 'external', return the application tables list"""
        tables = []
        for plugin in self.plugins:
            if place in plugin.tables:
                tables = tables + plugin.tables[place]
        return tables

    ##
    # Make responses for browser client requests
    # ------------------------------------------------------------------------------------------
    @staticmethod
    def response_ok(message="Ok"):
        """Request is ok"""
        response.status = 200
        response.content_type = 'application/json'
        return json.dumps(
            {'status': 'ok', 'message': message}
        )

    @staticmethod
    def response_data(data):
        """Request is ok and contains data"""
        response.status = 200
        response.content_type = 'application/json'
        return json.dumps(data)

    @staticmethod
    def response_invalid_parameters(message="Missing parameter"):
        """Request parameters are invalid"""
        response.status = 400
        response.content_type = 'application/json'
        return json.dumps(
            {'status': 'ko', 'message': message}
        )

    @staticmethod
    def response_missing_file(message="No file selected for upload"):
        """File to upload missing parameter"""
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
