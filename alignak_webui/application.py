#!/usr/bin/python
# -*- coding: utf-8 -*-
# pylint: disable=fixme, too-many-locals, too-many-nested-blocks, too-many-public-methods

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

'''
    WebUI application
'''

import traceback
import sys
import os
import time
import datetime
import json
import threading

from importlib import import_module

from logging import getLogger

# import gettext

import setproctitle

import pytz

# Bottle import
from bottle import hook, route, request, response, redirect, static_file, view
from bottle import BaseTemplate, template, TEMPLATE_PATH
import bottle

# Local import
from alignak_webui.objects.datamanager import DataManager, User
from alignak_webui.utils.helper import Helper


logger = getLogger(__name__)


# --------------------------------------------------------------------------------------------------
# WebUI hooks
# --------------------------------------------------------------------------------------------------
@hook('before_request')
def before_request():
    '''
    Function called since an HTTP request is received, and before any other function.

    Checks if a user session exists

    Some URLs do not need any authentication:
        - ping, heartbeat mechanism used for page or page elements refresh
        - login / logout
        - static files (js, css, ...)
    '''
    # logger.debug("before_request, url: %s", request.urlparts.path)

    # Static application and plugins files
    if request.urlparts.path.startswith('/static'):
        return

    # Get the server session (if it exists ...)
    session = None
    if 'beaker.session' in request.environ:
        session = request.environ['beaker.session']

    if 'current_user' in session:
        # Make session current user available in the templates
        # BaseTemplate.defaults['user'] = session['current_user']
        BaseTemplate.defaults['current_user'] = session['current_user']

    if 'target_user' in session:
        # Make session target user available in the templates
        BaseTemplate.defaults['target_user'] = session['target_user']

    if 'datamanager' in session:
        # Make session datamanager available in the templates
        BaseTemplate.defaults['datamgr'] = session['datamanager']

    # Public URLs routing ...
    if request.urlparts.path == '/ping' or \
       request.urlparts.path == '/heartbeat':
        return

    if request.urlparts.path == '/login' or \
       request.urlparts.path == '/logout':
        return

    logger.debug("before_request, url: %s", request.urlparts.path)

    # Session authentication ...
    if 'current_user' not in session:
        # Redirect to application login page
        logger.warning(
            "before_request, no current_user in the session. Redirecting to the login page..."
        )
        redirect('/login')

    current_user = session['current_user']
    if not user_authentication(current_user.get_token(), None):
        # Redirect to application login page
        logger.warning(
            "before_request, current_user in the session is not authenticated."
            " Redirecting to the login page..."
        )
        redirect('/login')

    session['current_user'] = session['datamanager'].get_logged_user()
    logger.debug("before_request, session authenticated user: %s", session['current_user'])

    # Set/change target user in the session
    target_user_username = request.query.get('target_user', None)
    if target_user_username == "":
        if 'target_user' in session and not session['target_user'].is_anonymous():
            logger.warning("no more target user in the session")
            session['target_user'] = User()

            # Reload data ...
            session['datamanager'].load(reset=True)
    elif target_user_username is not None:
        if 'target_user' in session and \
           session['target_user'].get_username() != target_user_username:
            logger.info("new target user specified: %s", target_user_username)
            target_user = session['datamanager'].get_user({
                'where': {'name': target_user_username}
            })
            if target_user:
                logger.debug(
                    "before_request, target_user set in the session: %s", target_user_username
                )
                session['target_user'] = target_user

                # Reload data ...
                session['datamanager'].load(reset=True)
            else:
                logger.warning("before_request, no more target_user in the session")
                session['target_user'] = User()

    # Make session target user available in the templates
    BaseTemplate.defaults['target_user'] = session['target_user']

    logger.debug("before_request, Url: %s", request.urlparts.path)


# --------------------------------------------------------------------------------------------------
# WebUI routes
# --------------------------------------------------------------------------------------------------
@route('/heartbeat')
def heartbeat():
    '''
    Application heartbeat
    '''
    # Session authentication ...
    session = request.environ['beaker.session']
    if session and 'current_user' in session and session['current_user']:
        response.status = 200
        response.content_type = 'application/json'
        return json.dumps(
            {
                'status': 'ok',
                'message': "Current logged-in user: %s" % session['current_user'].get_username()
            }
        )

    response.status = 401
    response.content_type = 'application/json'
    return json.dumps(
        {'status': 'ok', 'message': 'Session expired'}
    )


@route('/ping')
def ping():
    '''
    Request on /ping is a simple check alive that returns an information if UI refresh is needed

    If no session exists, it will always return 'pong' to inform that server is alive.

    Else:
        - if UI refresh is needed, requires the UI client to refresh
        - if action parameter is 'header', returns the updated header
        - if action parameter is 'done', the UI client did refresh the interface.
    '''
    session = request.environ['beaker.session']
    if not session:  # pragma: no cover - simple security!
        response.status = 200
        response.content_type = 'application/json'
        return json.dumps({'status': 'ok', 'message': 'pong'})

    action = request.query.get('action', None)
    if action == 'done':
        # Acknowledge UI refresh
        session['refresh_required'] = False
        if 'datamanager' in session:
            session['datamanager'].new_data = []
            session['datamanager'].refresh_required = False

            response.status = 200
            response.content_type = 'application/json'
            return json.dumps(
                {
                    'status': 'ok', 'message': 'pong'
                }
            )
        logger.info("ping, refresh: %s", session['refresh_required'])
    elif action == 'header':
        # Send UI header
        return template('_header_hosts_state')
    elif action:
        response.status = 204
        response.content_type = 'application/json'
        return json.dumps(
            {
                'status': 'ok', 'message': 'Unknown ping action parameter: %s' % action
            }
        )

    # Check new data in the data manager for the page refresh
    session = request.environ['beaker.session']
    if session and 'datamanager' in session:
        # Test without cache
        if session['datamanager'].refresh_required:
            session['refresh_required'] = True
            logger.warning("Data manager says a refresh is required")
        # if session['datamanager'].refresh_required or session['datamanager'].load(refresh=True):
            # session['refresh_required'] = True
            # logger.warning("Data manager says a refresh is required")

    if 'refresh_required' in session and session['refresh_required']:
        # Require UI refresh
        response.status = 200
        response.content_type = 'application/json'
        return json.dumps(
            {
                'status': 'ok', 'message': 'refresh'
            }
        )

    response.status = 200
    response.content_type = 'application/json'
    return json.dumps({'status': 'ok', 'message': 'pong'})


def user_authentication(username, password):
    '''
    Authenticate a user thanks to his username / password

    The authentication is requested near the data manager. This functions uses the data manager
    of the current session, else it creates a new one.

    Stores the authenticated User object in the session to make it available
    '''

    logger.info("user_authentication, authenticating: %s", username)

    # Session...
    session = request.environ['beaker.session']

    # Get backend in the server session (if it exists ... else create)
    if 'datamanager' not in session:
        logger.info("user authentication, creating a new data manager in the session...")
        logger.info(
            "Backend: %s",
            request.app.config.get('alignak_backend', 'http://127.0.0.1:5002')
        )
        session['datamanager'] = DataManager(
            request.app.config.get(
                'alignak_backend',
                'http://127.0.0.1:5002'
            ),
            {
                'glpi_ws_backend': request.app.config.get(
                    'glpi_ws_backend', None
                ),
                'glpi_ws_login': request.app.config.get(
                    'glpi_ws_login', None
                ),
                'glpi_ws_password': request.app.config.get(
                    'glpi_ws_password', None
                )
            }
        )

    # Set user for the data manager and try to log-in.
    if not session['datamanager'].user_login(username, password, load=(password is not None)):
        session['message'] = session['datamanager'].connection_message
        logger.warning("user authentication refused: %s", session['message'])
        return False

    # Create a new target user in the session
    if 'target_user' not in session:
        session['target_user'] = User()

    session['message'] = session['datamanager'].connection_message
    session['current_user'] = session['datamanager'].get_logged_user()
    logger.debug("user_authentication, current user authenticated")
    return True


@route('/', 'GET')
def home_page():
    '''
    Display home page -> redirect to /sessions
    '''
    redirect(bottle.default_app().get_url('Dashboard'))


@route('/login', 'GET')
def user_login():
    '''
    Display user login page
    '''
    session = request.environ['beaker.session']
    message = None
    if 'message' in session and session['message']:
        message = session['message']
        logger.warning("login page with error message: %s", message)

    # Send login form
    return template(
        'login', {
            'login_text': request.app.config.get(
                'login_text', _('Welcome!<br> Log-in to use the application')
            ),
            'company_logo': request.app.config.get(
                'company_logo', 'default_company'
            ),
            'message': message
        }
    )


@route('/logout', 'GET')
def user_logout():
    '''
    Log-out the current logged-in user

    Clear and delete the user session
    '''
    # Store user information in the server session
    session = request.environ['beaker.session']
    session.delete()

    # Log-out from application
    logger.info("Logout for current user")

    redirect('/login')


@route('/login', 'POST')
def user_auth():
    '''
    Receive user login parameters (username / password) to authenticate a user

    Allowed authentication:
    - username/password from a login form
    - token and empty password
    '''
    username = request.forms.get('username', None)
    password = request.forms.get('password', None)
    logger.info("login, user '%s' is signing in ...", username)

    session = request.environ['beaker.session']
    session['message'] = None
    if not user_authentication(username, password):
        # Redirect to application login page with an error message
        if 'message' not in session:
            session['message'] = _("Invalid username or password")
        logger.warning("user '%s' access denied, message: %s", username, session['message'])
        redirect('/login')

    logger.warning("user '%s' (%s) signed in", username, session['current_user'].get_name())
    redirect('/')


@route('/static/photos/<name>')
def give_photo(name):
    '''
    User picture URL
    '''
    # logger.debug("Get photo for: %s", name)
    # Find WebUI root directory
    images_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'htdocs', 'images'))
    if os.path.exists(os.path.join(images_dir, name + '.png')):
        return static_file(name + '.png', root=images_dir)
    else:
        return static_file('images/default_user.png', root=images_dir)


@route('/static/logo/<name>')
def give_logo(name):
    '''
    Company logo URL
    '''
    # logger.debug("Get logo named: %s", name)
    app_dir = os.path.abspath(os.path.dirname(__file__))
    htdocs_dir = os.path.join(app_dir, 'htdocs')
    return static_file('images/%s.png' % name, root=htdocs_dir)


@route('/static/<path:path>')
def server_static(path):
    '''
    Main application static files
    Plugins declare their own static routes under /plugins
    '''
    # logger.debug("Application static file: %s", path)
    if not path.startswith('plugins'):
        return static_file(
            path, root=os.path.join(os.path.abspath(os.path.dirname(__file__)), 'htdocs')
        )
    else:
        return static_file(
            path, root=os.path.abspath(os.path.dirname(__file__))
        )


@route('/favicon.ico')
def give_favicon():
    '''
    Web site favicon
    '''
    # Find WebUI root directory
    app_dir = os.path.abspath(os.path.dirname(__file__))
    htdocs_dir = os.path.join(app_dir, 'htdocs')
    return static_file('favicon.ico', root=os.path.join(htdocs_dir, 'images'))


@route('/modal/<modal_name>')
def give_modal(modal_name):
    '''
    User picture URL
    '''
    logger.debug("get modal window named: %s", modal_name)
    return template('modal_' + modal_name)


class WebUI(object):
    '''
    WebUI application
    '''
    def __init__(self):
        '''
        Application configuration

        :param id: app_conf
        :type id: dict

        :param id: app
        :type id: Bottle instance

        :param id: logger
        :type id: Python logger instance
        '''

        logger.info("Initializing...")

        # Store all the widgets
        self.widgets = {}

        # Store all the plugins
        self.plugins = []

        # User preferences module
        self.prefs_module = None

        # Helper class
        self.helper = Helper()

        # Look at the plugins directory ...
        self.plugins_count = self.load_plugins(
            bottle.app(),
            os.path.join(os.path.abspath(os.path.dirname(__file__)), 'plugins')
        )

    def load_plugins(self, app, plugins_dir):
        '''
        Load plugins from the provided directory

        If the plugin has
        - 'pages', declare routes for the pages
        - 'widgets', declare widgets in the main widgets list

        Register the plugin 'views' directory in the Bottle views

        If the plugin has a 'load_config' function, call it

        If the plugin has a 'get_user_preferences' function, it is a user preferences module
        '''
        logger.info("load plugins from: %s", plugins_dir)

        # Get list of sub directories
        plugin_names = [
            fname for fname in os.listdir(plugins_dir)
            if os.path.isdir(os.path.join(plugins_dir, fname))
        ]

        # Try to import all found plugins
        i = 0
        for plugin_name in plugin_names:
            logger.info("trying to load plugin '%s' ...", plugin_name)
            try:
                # Import the plugin in the package namespace
                plugin = import_module(
                    '.%s.%s.%s' % (plugins_dir.rsplit('/')[-1], plugin_name, plugin_name),
                    __package__
                )

                # Plugin defined routes ...
                if hasattr(plugin, 'pages'):
                    for (f, entry) in plugin.pages.items():
                        logger.debug("page entry: %s", entry)

                        # IMPORTANT: apply the view before the route!
                        page_view = entry.get('view', None)
                        if page_view:
                            f = view(page_view)(f)

                        # Maybe there is no route to link, so pass
                        page_route = entry.get('route', None)
                        page_name = entry.get('name', None)
                        if page_route:
                            method = entry.get('method', 'GET')

                            f = app.route(
                                page_route, callback=f, method=method, name=page_name,
                                search_engine=entry.get('search_engine', False),
                                search_prefix=entry.get('search_prefix', ''),
                                search_filters=entry.get('search_filters', {})
                            )

                        # It's a valid widget entry if it got all data, and at least one route
                        # ONLY the first route will be used for Add!
                        widget_lst = entry.get('widget', [])
                        widget_id = entry.get('widget_id', None)
                        widget_desc = entry.get('widget_desc', None)
                        widget_name = entry.get('widget_name', None)
                        widget_picture = entry.get('widget_picture', None)
                        if widget_id and widget_name and widget_desc and \
                                widget_lst != [] and page_route:
                            for place in widget_lst:
                                if place not in self.widgets:
                                    self.widgets[place] = []
                                self.widgets[place].append({
                                    'widget_id': widget_id,
                                    'widget_name': widget_name,
                                    'widget_desc': widget_desc,
                                    'base_uri': page_route,
                                    'widget_picture': os.path.join(
                                        os.path.join('/static/plugins/', plugin_name),
                                        widget_picture
                                    )
                                })

                # Add the views sub-directory of the plugin in the Bottle templates path
                dir_views = os.path.join(
                    os.path.join(plugins_dir, plugin_name), 'views'
                )
                if os.path.isdir(dir_views):
                    TEMPLATE_PATH.append(os.path.join(
                        os.path.join(plugins_dir, plugin_name), 'views'
                    ))
                    logger.debug("register views directory '%s'", os.path.join(
                        os.path.join(plugins_dir, plugin_name), 'views'
                    ))

                # Self register in the plugin so the pages can get my data
                plugin.webui = self

                # Load/set plugin configuration
                config = True
                f = getattr(plugin, 'load_config', None)
                if f and callable(f):
                    config = False
                    logger.info(
                        "plugin '%s' needs to load its configuration. Configuring...", plugin_name
                    )
                    config = f(app)
                    if config:
                        logger.info("plugin '%s' configured.", plugin_name)
                    else:  # pragma: no cover - if any ...
                        logger.warning("plugin '%s' configuration failed.", plugin_name)

                # Manage plugin type
                f = getattr(plugin, 'get_user_preferences', None)
                if config and f and callable(f):
                    logger.info(
                        "plugin '%s' is a user's preferences module. Configuring...", plugin_name
                    )
                    self.prefs_module = f(app)
                    if self.prefs_module:
                        logger.info(
                            "plugin '%s' is a user's preferences plugin.", plugin_name
                        )
                    else:  # pragma: no cover - if any ...
                        logger.warning(
                            "plugin '%s' user's preferences load failed.", plugin_name
                        )

                i += 1
                self.plugins.append({
                    'name': plugin_name,
                    'module': plugin
                })
                logger.info("registered plugin '%s'", plugin_name)

            except Exception as e:  # pragma: no cover - simple security ...
                logger.error("loading plugin %s, exception: %s", plugin_name, str(e))
                logger.error("traceback: %s", traceback.format_exc())

        logger.info("loaded %d plugins from: %s", i, plugins_dir)
        # exit()
        return i

    def get_url(self, name):
        '''
        Get the URL for a named route
        '''
        return bottle.default_app().get_url(name)

    def get_widgets_for(self, place):
        '''
        For a specific place like 'dashboard', return the application widgets list
        '''
        return self.widgets.get(place, [])

    ##
    # Make responses for browser client requests
    # ------------------------------------------------------------------------------------------
    def response_ok(self, message="Ok"):
        '''
        Request is ok
        '''
        response.status = 200
        response.content_type = 'application/json'
        return json.dumps(
            {'status': 'ok', 'message': message}
        )

    def response_data(self, data):
        '''
        Request is ok and contains data
        '''
        response.status = 200
        response.content_type = 'application/json'
        return json.dumps(data)

    def response_invalid_parameters(self, message="Missing parameter"):
        '''
        Request parameters are invalid
        '''
        response.status = 204
        response.content_type = 'application/json'
        return json.dumps(
            {'status': 'ko', 'message': message}
        )

    def response_missing_file(self, message="No file selected for upload"):
        '''
        File to upload missing parameter
        '''
        return self.response_ko(message=message, code=412)

    def response_ko(self, message="Error!", code=409):
        '''
        Request failed
        '''
        response.status = code
        response.content_type = 'application/json'

        return json.dumps(
            {'status': 'ko', 'message': message}
        )
