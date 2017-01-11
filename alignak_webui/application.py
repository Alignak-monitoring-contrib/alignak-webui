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
    WebUI application
"""

import json
import os
import traceback
from importlib import import_module
import inspect
from logging import getLogger

# Bottle import
from bottle import hook, route, request, response, redirect, static_file, view, parse_auth
from bottle import BaseTemplate, template, TEMPLATE_PATH
import bottle

# Application import
from alignak_webui import _
from alignak_webui import get_app_webui
from alignak_webui.objects.item_user import User
from alignak_webui.objects.datamanager import DataManager
from alignak_webui.utils.helper import Helper
from alignak_webui.utils.plugin import Plugin


logger = getLogger(__name__)


# --------------------------------------------------------------------------------------------------
# WebUI hooks
# --------------------------------------------------------------------------------------------------
@hook('before_request')
def before_request():
    """
    Function called since an HTTP request is received, and before any other function.

    Checks if a user session exists

    Some URLs do not need any authentication:
        - ping, heartbeat mechanism used for page or page elements refresh
        - login / logout
        - static files (js, css, ...)
    """
    # logger.debug("before_request, url: %s", request.urlparts.path)

    # Static application and plugins files
    if request.urlparts.path.startswith('/static'):
        return

    # External URLs routing ...
    if request.urlparts.path.startswith('/external'):
        return

    # Get the server session (if it exists ...)
    session = request.environ['beaker.session']

    if 'edition_mode' in session:
        # Make session edition mode available in the templates
        BaseTemplate.defaults['edition_mode'] = session['edition_mode']
    else:
        session['edition_mode'] = False

    if 'current_user' in session:
        # Make session current user available in the templates
        BaseTemplate.defaults['current_user'] = session['current_user']

    # Public URLs routing ...
    if request.urlparts.path == '/ping' or \
       request.urlparts.path == '/heartbeat':
        return

    # Login/logout URLs routing ...
    if request.urlparts.path == '/login' or \
       request.urlparts.path == '/logout':
        return

    logger.debug("before_request, url: %s", request.urlparts.path)

    # Session authentication ...
    if 'current_user' not in session:
        # Redirect to application login page
        logger.warning(
            "The session expired or there is no user in the session."
            " Redirecting to the login page..."
        )
        redirect('/login')

    current_user = session['current_user']
    if not user_authentication(current_user.token, None):  # pragma: no cover - simple security!
        # Redirect to application login page
        logger.warning(
            "user in the session is not authenticated."
            " Redirecting to the login page..."
        )
        redirect('/login')

    logger.debug("before_request, session authenticated user: %s", session['current_user'])

    # Make session current user available in the templates
    BaseTemplate.defaults['current_user'] = session['current_user']
    # Make session edition mode available in the templates
    BaseTemplate.defaults['edition_mode'] = session['edition_mode']
    # Initialize data manager and make it available in the request and in the templates
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
    # # Load initial objects from the DM
    # request.app.datamgr.load()
    BaseTemplate.defaults['datamgr'] = request.app.datamgr

    # logger.debug("before_request, call function for route: %s", request.urlparts.path)


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


@route('/heartbeat')
def heartbeat():
    """
    Application heartbeat
    """
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
    # pylint: disable=too-many-return-statements
    """
    Request on /ping is a simple check alive that returns an information if UI refresh is needed

    If no session exists, it will always return 'pong' to inform that server is alive.

    Else:
        - if UI refresh is needed, requires the UI client to refresh
        - if action parameter is 'refresh', returns the required template view
        - if action parameter is 'done', the UI client did refresh the interface.

    Used by the header refresh to update the hosts/services states.
    """
    session = request.environ['beaker.session']
    if not session:
        response.status = 401
        response.content_type = 'application/json'
        return json.dumps(
            {'status': 'ok', 'message': 'Session expired'}
        )

    action = request.query.get('action', None)
    if action == 'done':
        # Acknowledge UI refresh
        session['refresh_required'] = False
        logger.debug("ping, refresh: %s", session['refresh_required'])
    elif action == 'refresh':
        page_template = request.query.get('template', None)
        if page_template:
            # Send rendered template
            return template(page_template)

        # pragma: no cover - should not happen
        response.status = 200
        response.content_type = 'application/json'
        return json.dumps(
            {
                'status': 'ok',
                'message': 'missing template name. Use /ping?action=refresh&template=name.'
            }
        )
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


@route('/', 'GET')
def home_page():
    """
    Display home page -> redirect to /sessions
    """
    redirect(bottle.default_app().get_url('Dashboard'))


@route('/login', 'GET')
def user_login():
    """
    Display user login page
    """
    session = request.environ['beaker.session']
    message = None
    if 'login_message' in session and session['login_message']:
        message = session['login_message']
        session['login_message'] = None
        logger.warning("login page with error message: %s", message)

    # Send login form
    return template(
        'login', {
            'login_text': request.app.config.get(
                'login_text', _('Welcome!<br> Log-in to use the application')
            ),
            'company_logo': request.app.config.get(
                'company_logo', '/static/images/default_company.png'
            ),
            'message': message
        }
    )


@route('/logout', 'GET')
def user_logout():
    """
    Log-out the current logged-in user

    Clear and delete the user session
    """
    # Store user information in the server session
    session = request.environ['beaker.session']
    session.delete()

    # Log-out from application
    logger.info("Logout for current user")

    redirect('/login')


@route('/login', 'POST')
def user_auth():
    """
    Receive user login parameters (username / password) to authenticate a user

    Allowed authentication:
    - username/password from a login form
    - token and empty password
    """
    username = request.forms.get('username', None)
    password = request.forms.get('password', None)
    logger.info("login, user '%s' is signing in ...", username)

    session = request.environ['beaker.session']
    session['login_message'] = None
    if not user_authentication(username, password):
        # Redirect to application login page with an error message
        if 'login_message' not in session:
            session['login_message'] = _("Invalid username or password")
        logger.warning("user '%s' access denied, message: %s", username, session['login_message'])
        redirect('/login')

    logger.info("user '%s' (%s) signed in", username, session['current_user'].name)
    redirect('/')


@route('/static/<path:path>')
def server_static(path):
    """
    Main application static files
    Plugins declare their own static routes under /plugins
    """
    if not path.startswith('plugins'):
        return static_file(
            path, root=os.path.join(os.path.abspath(os.path.dirname(__file__)), 'htdocs')
        )
    else:
        return static_file(
            path, root=os.path.abspath(os.path.dirname(__file__))
        )


@route('/modal/<modal_name>')
def give_modal(modal_name):
    """
    User picture URL
    """
    logger.debug("get modal window named: %s", modal_name)
    return template('modal_' + modal_name)


# --------------------------------------------------------------------------------------------------
# User authentication
# --------------------------------------------------------------------------------------------------
def user_authentication(username, password):
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
        datamgr = DataManager(
            backend_endpoint=request.app.config.get('alignak_backend', 'http://127.0.0.1:5000'),
            alignak_endpoint=request.app.config.get('alignak_arbiter', 'http://127.0.0.1:7070')
        )

        # Set user for the data manager and try to log-in.
        if not datamgr.user_login(username, password, load=(password is not None)):
            session['login_message'] = datamgr.connection_message

            logger.warning("user authentication refused: %s", session['login_message'])
            return False

        # Update session variables
        session['current_user'] = datamgr.logged_in_user
        session['current_realm'] = datamgr.my_realm
        session['current_ls'] = datamgr.my_ls

    logger.debug("user_authentication, current user authenticated")
    return True


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


# --------------------------------------------------------------------------------------------------
# WebUI user's preferences
# --------------------------------------------------------------------------------------------------
@route('/preferences/user')
# User preferences page ...
def show_user_preferences():
    """
        Show the user preferences view
    """
    return template('_preferences')


@route('/preference/user', 'GET')
def get_user_preference():
    """
        Request parameters:

        - key, string identifying the parameter
        - default, default value if parameter does not exist
    """
    user = request.environ['beaker.session']['current_user']
    datamgr = DataManager(
        backend_endpoint=request.app.config.get(
            'alignak_backend', 'http://127.0.0.1:5000'
        ),
        alignak_endpoint=request.app.config.get(
            'alignak_arbiter',
            'http://127.0.0.1:7070'
        ),
        session=request.environ['beaker.session']
    )

    key = request.query.get('key', None)
    if not key:
        return WebUI.response_invalid_parameters(_('Missing mandatory parameters'))

    default = request.query.get('default', None)
    if default:
        default = json.loads(default)

    response.status = 200
    response.content_type = 'application/json'
    return json.dumps(datamgr.get_user_preferences(user, key, default))


@route('/preference/user/delete', 'GET')
def delete_user_preference():
    """
        Request parameters:

        - key, string identifying the parameter
    """
    user = request.environ['beaker.session']['current_user']
    datamgr = DataManager(
        backend_endpoint=request.app.config.get(
            'alignak_backend', 'http://127.0.0.1:5000'
        ),
        alignak_endpoint=request.app.config.get(
            'alignak_arbiter',
            'http://127.0.0.1:7070'
        ),
        session=request.environ['beaker.session']
    )

    key = request.query.get('key', None)
    if not key:
        return WebUI.response_invalid_parameters(_('Missing mandatory parameters'))

    response.status = 200
    response.content_type = 'application/json'
    return json.dumps(datamgr.delete_user_preferences(user, key))


@route('/preference/user', 'POST')
def set_user_preference():
    """
        Request parameters:

        - key, string identifying the parameter
        - value, as a JSON formatted string
    """
    user = request.environ['beaker.session']['current_user']
    datamgr = DataManager(
        backend_endpoint=request.app.config.get(
            'alignak_backend', 'http://127.0.0.1:5000'
        ),
        alignak_endpoint=request.app.config.get(
            'alignak_arbiter',
            'http://127.0.0.1:7070'
        ),
        session=request.environ['beaker.session']
    )

    key = request.forms.get('key', None)
    value = request.forms.get('value', None)
    if key is None or value is None:
        return WebUI.response_invalid_parameters(_('Missing mandatory parameters'))

    if datamgr.set_user_preferences(user, key, json.loads(value)):
        return WebUI.response_ok(message=_('User preferences saved'))
    else:
        return WebUI.response_ko(
            message=_('Problem encountered while saving common preferences')
        )


class WebUI(object):
    """
    WebUI application
    """
    def __init__(self, config=None):
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
        self.app_config = config

        # Application data manager
        self.datamgr = None

        # Load plugins in the plugins directory ...
        self.plugins_count = self.load_plugins(
            os.path.join(os.path.abspath(os.path.dirname(__file__)), 'plugins')
        )

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
        plugin_names = [
            fname for fname in os.listdir(plugins_dir)
            if os.path.isdir(os.path.join(plugins_dir, fname))
        ]

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
                    logger.info("Found plugins classes: %s", p_classes)
                    cfg_files = [
                        '/usr/local/etc/%s/plugin_%s.cfg' % (
                            self.app_config['name'].lower(), plugin_name
                        ),
                        '/etc/%s/plugin_%s.cfg' % (
                            self.app_config['name'].lower(), plugin_name
                        ),
                        '~/%s/plugin_%s.cfg' % (
                            self.app_config['name'].lower(), plugin_name
                        ),
                        os.path.join(os.path.join(plugins_dir, plugin_name), 'settings.cfg')
                    ]

                    for p_class in p_classes:
                        # Create a plugin instance
                        p = p_class(self, cfg_files)

                        i += 1
                        self.plugins.append(p)

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

                logger.info("registered plugin '%s'", plugin_name)

            except Exception as e:  # pragma: no cover - simple security ...
                logger.error("loading plugin %s, exception: %s", plugin_name, str(e))
                logger.error("traceback: %s", traceback.format_exc())

        logger.info("loaded %d plugins from: %s", i, plugins_dir)
        return i

    def get_url(self, name):
        """
        Get the URL for a named route
        :param name:
        :return:
        """
        return bottle.default_app().get_url(name)

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

        if self.app_config.get('bootstrap4', '0') == '1':
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

        if self.app_config.get('bootstrap4', '0') == '1':
            js_list += [
                "/static/js/datatables.bootstrap4.min.js"
            ]
        else:
            js_list += [
                "/static/js/datatables.min.js"
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
        if self.app_config.get('bootstrap4', '0') == '1':
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
        if self.app_config.get('bootstrap4', '0') == '1':
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
