#!/usr/bin/python
# -*- coding: utf-8 -*-

# Else pylint alerts on declared global variables
# pylint: disable=invalid-name

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
Usage:
    {command} [-h] [-v] [-d] [-w=url] [-b=url] [-n=hostname] [-p=port] [<cfg_file>...]

Options:
    -h, --help                  Show this screen.
    -v, --version               Show application version.
    -b, --backend url           Specify backend URL
    -w, --ws url                Specify Alignak Web Services URL
    -n, --hostname host         Specify WebUI host (or ip address)
    -p, --port port             Specify WebUI port
    -d, --debug                 Run in debug mode (more info to display) [default: False]

Use cases:
    Display help message:
        {command} -h
    Display current version:
        {command} -v

    Run application in default mode:
        {command}

    Run application in default mode and specify a configuration file:
        {command} /etc/ui-settings.cfg

    Run application and specify the backend URL:
        {command} -b=backend

    Run application in debug mode and listen on all interfaces:
        {command} -d -b=backend -n=0.0.0.0 -p=5001

    Exit code:
        0 if all is ok
        1 configuration error
        2 run error
        64 if command line parameters are not used correctly
        99 application started but server not run (test application start)

"""

from __future__ import print_function

import os
import time
import json
import logging
import threading

# Bottle Web framework
import bottle
from bottle import run, redirect, request, response, static_file
from bottle import template, BaseTemplate, TEMPLATE_PATH
from bottle import RouteBuildError, parse_auth

# Session management
from beaker.middleware import SessionMiddleware

# Command line interpreter
from docopt import docopt, DocoptExit

# Application import
from alignak_webui import __manifest__, set_app_config
from alignak_webui.utils.logger import setup_logging, ROOT_LOGGER_NAME
from alignak_webui.utils.locales import init_localization
from alignak_webui.backend.backend import BackendException
from alignak_webui.backend.datamanager import DataManager
from alignak_webui.webui import WebUI

app = application = bottle.Bottle()

# -----
# Test mode for the application
# -----
if os.environ.get('ALIGNAK_WEBUI_TEST'):
    print("Application is in test mode")
else:  # pragma: no cover, because tests are run in test mode
    print("Application is in production mode")

args = {}
if __name__ == '__main__':
    try:
        print("Parsing command line arguments")
        args = docopt(__doc__, version=__manifest__['version'])
    except DocoptExit as exp:
        print("Command line parsing error: \n%s" % exp)
        exit(64)

# -----
# Application configuration file
# -----
app_name = __manifest__['name'].lower()
# Search for configuration files in several locations
cfg_filenames = [
    '/usr/local/etc/%s/settings.cfg' % app_name,
    '/etc/%s/settings.cfg' % app_name,
    '~/%s/settings.cfg' % app_name,
    os.path.abspath('./etc/%s/settings.cfg' % app_name),
    os.path.abspath('../etc/settings.cfg'),
    os.path.abspath('./etc/settings.cfg'),
    os.path.abspath('./settings.cfg'),
]
# Configuration file name in environment
if os.environ.get('ALIGNAK_WEBUI_CONFIGURATION_FILE'):
    cfg_filenames = [os.environ.get('ALIGNAK_WEBUI_CONFIGURATION_FILE')]
    print("Application configuration file name from environment: %s" % cfg_filenames)
# Configuration file name in command line parameters
if '<cfg_file>' in args and args['<cfg_file>']:  # pragma: no cover, tested but not coverable
    cfg_filenames = args['<cfg_file>']
    print("Application configuration file name from command line: %s" % cfg_filenames)


app_configuration_file = None
for cfg_filename in cfg_filenames:
    if os.path.isfile(cfg_filename):
        app.config.load_config(cfg_filename)
        print("Configuration read from: %s" % cfg_filename)
        app_configuration_file = cfg_filename
        break
else:  # pragma: no cover, tested but not coverable
    print("***** Application configuration file not found.")
    print("***** Searched in: %s" % cfg_filenames)
    exit(1)

# -----
# Check application configuration file change
# -----
# todo: not yet tested
if os.environ.get('ALIGNAK_WEBUI_CONFIGURATION_THREAD'):  # pragma: no cover, not yet tested
    def check_config(_app, filename, interval=5):
        """Thread to check if configuration file changed"""
        print("Thread for checking configuration file change, file: %s" % filename)
        modification_time = os.path.getmtime(filename)
        while True:
            time.sleep(interval)
            print("Checking configuration file change...")
            if modification_time < os.path.getmtime(filename):
                print("Application configuration file changed, reloading configuration...")
                modification_time = os.path.getmtime(filename)
                _app.config.load_config(filename)
    cfg_check_thread = threading.Thread(target=check_config,
                                        name='application_configuration_check',
                                        args=(app, app_configuration_file, 10))
    cfg_check_thread.daemon = True
    cfg_check_thread.start()

# -----
# Debug and test mode
# -----
env_debug = os.environ.get('BOTTLE_DEBUG')
if env_debug and env_debug == '1':  # pragma: no cover, tested but not coverable
    app.config['bottle.debug'] = True
    print("Bottle is in debug mode from environment")

env_debug = os.environ.get('ALIGNAK_WEBUI_DEBUG')
if env_debug and env_debug == '1':  # pragma: no cover, tested but not coverable
    app.config['%s.debug' % app_name] = True
    print("Application is in debug mode from environment")

if '--debug' in args and args['--debug']:  # pragma: no cover, tested but not coverable
    app.config['bottle.debug'] = True
    app.config['%s.debug' % app_name] = True
    print("Application is in debug mode from command line")

# -----
# Application backend
# -----
if os.environ.get('ALIGNAK_WEBUI_BACKEND'):  # pragma: no cover, tested but not coverable
    app.config['%s.alignak_backend' % app_name] = os.environ.get('ALIGNAK_WEBUI_BACKEND')
    print("Application backend from environment: %s" % os.environ.get('ALIGNAK_WEBUI_BACKEND'))
if '--backend' in args and args['--backend']:  # pragma: no cover, tested but not coverable
    app.config['%s.alignak_backend' % app_name] = args['--backend']
    print("Application backend from command line: %s" % args['--backend'])

print("Application backend: %s" % app.config.get('%s.alignak_backend' % app_name,
                                                 'http://127.0.0.1:5000'))

# -----
# Alignak web services
# -----
if os.environ.get('ALIGNAK_WEBUI_WS'):
    app.config['%s.alignak_ws' % app_name] = os.environ.get('ALIGNAK_WEBUI_WS')
    print("Alignak Web Services from environment: %s" % os.environ.get('ALIGNAK_WEBUI_WS'))
if '--ws' in args and args['--ws']:
    app.config['%s.alignak_ws' % app_name] = args['--ws']
    print("Alignak Web Services from command line: %s" % args['--ws'])

print("Alignak Web Services: %s" % app.config.get('%s.alignak_ws' % app_name,
                                                  'http://127.0.0.1:8888'))

if '--host' in args and args['--host']:  # pragma: no cover, tested but not coverable
    app.config['host'] = args['--host']
    print("Listening interface from command line: %s" % app.config.get('host', '127.0.0.1'))

if '--port' in args and args['--port']:  # pragma: no cover, tested but not coverable
    app.config['port'] = args['--port']
    print("Listening port from command line: %s" % app.config.get('port', '5001'))

# -----
# Application log
# -----
# Set application log level (default is INFO
log_level = 'INFO'
if app.config.get('%s.debug' % app_name, False):  # pragma: no cover - not testable easily...
    print("-> Activated DEBUG log")
    log_level = 'DEBUG'

# Search log file location
log_locations = [
    '/usr/local/var/log/%s' % app_name,
    '/var/log/%s' % app_name,
    '/tmp/%s' % app_name
]
if os.environ.get('ALIGNAK_WEBUI_LOG'):  # pragma: no cover, tested but not coverable
    log_locations = [os.environ.get('ALIGNAK_WEBUI_LOG')]
    print("Application log directory from environment: %s" % os.environ.get('ALIGNAK_WEBUI_LOG'))
for log_location in log_locations:
    if os.path.isdir(log_location):
        print("Log file location: %s" % log_location)
        break
else:
    print("***** Log files location not found.")
    print("***** Searched in: %s" % log_locations)
    log_location = '/tmp/%s' % app_name
    os.mkdir(log_location)

# Search logger configuration
cfg_log_filenames = [
    '/usr/local/etc/%s/logging.json' % app_name,
    '/etc/%s/logging.json' % app_name,
    '~/%s/logging.json' % app_name,
    os.path.abspath('../etc/logging.json'),
    os.path.abspath('./etc/logging.json'),
    os.path.abspath('./logging.json'),
]
if os.environ.get('ALIGNAK_WEBUI_LOGGER_FILE'):  # pragma: no cover, tested but not coverable
    cfg_log_filenames = [os.environ.get('ALIGNAK_WEBUI_LOGGER_FILE')]
    print("Application logger configuration file from environment: %s"
          % os.environ.get('ALIGNAK_WEBUI_LOGGER_FILE'))

app_logger_file = None
logger = None
for cfg_log_filename in cfg_log_filenames:
    if setup_logging(cfg_log_filename, log_location):
        logger = logging.getLogger(ROOT_LOGGER_NAME)
        logger.setLevel(log_level)
        print("Application logger configured from: %s" % cfg_log_filename)
        break
else:  # pragma: no cover, tested but not coverable
    print("***** Application logger configuration file not found.")
    print("***** Searched in: %s" % cfg_log_filenames)
    exit(2)

logger.info("--------------------------------------------------------------------------------")
logger.info("%s, version %s", __manifest__['name'], __manifest__['version'])
logger.info("Copyright %s", __manifest__['copyright'])
logger.info("License: %s", __manifest__['license'])
logger.info("--------------------------------------------------------------------------------")
logger.info("Doc: %s", __manifest__['doc'])
logger.info("Release notes: %s", __manifest__['release'])
logger.info("--------------------------------------------------------------------------------")

logger.info("--------------------------------------------------------------------------------")
logger.info("listening on %s:%d (debug mode: %s)",
            app.config.get('host', '127.0.0.1'),
            int(app.config.get('port', '5001')),
            app.config.get('%s.debug' % app_name, False))
logger.info("using Alignak Backend on %s",
            app.config.get('%s.alignak_backend' % app_name, 'http://127.0.0.1:5000'))
logger.info("--------------------------------------------------------------------------------")

logger.debug("Application settings: ")
# Make the 'application.key' also available as 'key'
add_to_config = {}
for key, value in sorted(app.config.items()):
    if key.startswith(app_name):
        add_to_config[key.replace(app_name + '.', '')] = value
    if isinstance(value, basestring):
        value = value.replace('\n', '')
    logger.debug(" %s = %s", key, value)
logger.debug("--------------------------------------------------------------------------------")
logger.debug("Webui settings: ")
for key, value in add_to_config.items():
    app.config[key] = value
    logger.debug(" %s = %s", key, value)
logger.debug("--------------------------------------------------------------------------------")

# -----
# Application localization
# -----
_ = init_localization(app)
# Update configuration with translation method to use
app.config['_'] = _
# Provide translation methods to templates
BaseTemplate.defaults['_'] = _
print(_("Language is English (default)..."))

# -----
# Application extension
# -----
webapp = WebUI(app, name=app_name, config=app.config)
BaseTemplate.defaults['webui'] = webapp
app.config['webui'] = webapp

# -----
# Gloval application configuration
# -----
set_app_config(app.config)


# -----
# Application static files
# -----
@app.route('/static/<filename:path>')
def static(filename):
    """Main application static files

    Plugins declare their own static routes under /plugins
    """
    if not filename.startswith('plugins'):
        return static_file(
            filename, root=os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static')
        )
    return static_file(
        filename, root=os.path.abspath(os.path.dirname(__file__))
    )


# -----
# Application modal windows
# -----
# todo: to be tested...
@app.route('/modal/<modal_name>')
def give_modal(modal_name):
    """Return template for a modal window"""
    logger.debug("get modal window named: %s", modal_name)
    return template('modal_' + modal_name)


# --------------------------------------------------------------------------------------------------
# WebUI hooks
# --------------------------------------------------------------------------------------------------
@app.hook('config')
def on_config_change(_key, _value):  # pragma: no cover, not yet tested
    """Hook called if configuration dictionary changed"""
    logger.warning("application configuration changed, key: %s = %s", _key, _value)
    if _key.startswith(app_name):
        app.config[_key.replace(app_name + '.', '')] = _value
        logger.warning("application configuration changed, *** key: %s = %s",
                       _key.replace(app_name + '.', ''), _value)


@app.hook('before_request')
def before_request():
    # pylint: disable=unsupported-membership-test, unsubscriptable-object
    """Function called since an HTTP request is received, and before any other function.

    Checks if a user session exists

    Some URLs do not need any authentication:
        - ping, heartbeat mechanism used for page or page elements refresh
        - login / logout
        - static files (js, css, ...)
    """
    logger.debug("before_request, url: %s", request.urlparts.path)

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
    logger.debug("before_request, edition mode: %s", session['edition_mode'])

    if 'current_user' in session:
        # Make session current user available in the templates
        BaseTemplate.defaults['current_user'] = session['current_user']

    # Public URLs routing ...
    if request.urlparts.path == '/ping' or request.urlparts.path == '/heartbeat':
        return

    # Login/logout URLs routing ...
    if request.urlparts.path == '/login' or request.urlparts.path == '/logout':
        return

    # Session authentication ...
    if 'current_user' not in session:
        # Redirect to application login page
        logger.warning("The session expired or there is no user in the session. "
                       "Redirecting to the login page...")

        # Stop Alignak backend thread
        # *****

        redirect('/login')

    # Get the WebUI instance
    webui = request.app.config['webui']

    current_user = session['current_user']
    if not webui.user_authentication(current_user.token, None):
        # Redirect to application login page
        logger.warning("user in the session is not authenticated. "
                       "Redirecting to the login page...")
        redirect('/login')

    logger.debug("before_request, user authenticated")

    # Make session current user available in the templates
    BaseTemplate.defaults['current_user'] = session['current_user']
    # Make session edition mode available in the templates
    BaseTemplate.defaults['edition_mode'] = session['edition_mode']
    # Initialize data manager and make it available in the request and in the templates
    if webui.datamgr is None:  # pragma: no cover, should never happen!
        webui.datamgr = DataManager(request.app, session=request.environ['beaker.session'])
        if not webui.datamgr.connected:
            redirect('/login')

    request.app.datamgr = webui.datamgr
    # # Load initial objects from the DM
    # request.app.datamgr.load()
    BaseTemplate.defaults['datamgr'] = request.app.datamgr

    logger.debug("before_request, call function for route: %s", request.urlparts.path)


# --------------------------------------------------------------------------------------------------
# Home page and login
# --------------------------------------------------------------------------------------------------
@app.route('/', 'GET')
def home_page():
    """Display home page -> redirect to /Dashboard"""
    try:
        redirect(request.app.get_url('Livestate'))
    except RouteBuildError:  # pragma: no cover, should never happen!
        return "No home page available in the application routes!"


@app.route('/login', 'GET')
def user_login():
    """Display user login page"""
    session = request.environ['beaker.session']
    message = None
    if 'login_message' in session and session['login_message']:
        message = session['login_message']
        session['login_message'] = None
        logger.warning("login page with error message: %s", message)

    # Send login form
    return template(
        'login', {
            'message': message
        }
    )


@app.route('/logout', 'GET')
def user_logout():
    """Log-out the current logged-in user

    Clear and delete the user session
    """
    # Store user information in the server session
    session = request.environ['beaker.session']
    session.delete()

    # Log-out from application
    logger.info("Logout for current user")

    redirect('/login')


# todo: not yet implemented... see #172
def check_backend_connection(_app, token=None, interval=10):  # pragma: no cover, not yet!
    """Thread to check if backend connection is alive"""
    print("Thread for checking backend connection is alive with %s" % app.config['alignak_backend'])

    backend = _app.datamgr.backend
    object_type = 'user'
    params = {}
    while True:
        time.sleep(interval)
        if not token:
            continue
        print("Checking backend connection...")
        try:
            result = backend.get(object_type, params=params, all_elements=False)
            logger.debug("check_backend_connection, found: %s: %s", object_type, result)
        except BackendException as exp:  # pragma: no cover, simple protection
            logger.exception("object_type, exception: %s", exp)
            raise ValueError(
                '%s, search: %s was not found in the backend' % (object_type, params)
            )


@app.route('/login', 'POST')
def user_auth():
    """Receive user login parameters (username / password) to authenticate a user

    Allowed authentication:
    - username/password from a login form
    - token and empty password
    """
    username = request.forms.get('username', None)
    password = request.forms.get('password', None)
    logger.info("login, user '%s' is signing in ...", username)

    session = request.environ['beaker.session']
    session['login_message'] = None

    # Empty password?
    if not password:  # pragma: no cover, should never happen, tested before calling this function!
        # Redirect to application login page with an error message
        session['login_message'] = _("Login is not authorized without a password")
        logger.warning("user '%s' access denied, no passowrd provided", username)
        redirect('/login')

    if not webapp.user_authentication(username, password):
        # Redirect to application login page with an error message
        if 'login_message' not in session:
            session['login_message'] = _("Invalid username or password")
        logger.warning("user '%s' access denied, message: %s", username, session['login_message'])
        redirect('/login')

    logger.info("user '%s' (%s) signed in", username, session['current_user'].name)

    # -----
    # Start Alignak backend thread
    # -----
    # pylint: disable=fixme
    # TODO: run backend connection check thread
    # cfg_backend_thread = threading.Thread(target=check_backend_connection,
    #                                       name='backend_connection_check',
    #                                       args=(app, session['current_user'].token, 10))
    # cfg_backend_thread.daemon = True
    # cfg_backend_thread.start()

    redirect('/')


# --------------------------------------------------------------------------------------------------
# Ping / heartbeat
# --------------------------------------------------------------------------------------------------
@app.route('/heartbeat')
def heartbeat():
    """Application heartbeat"""
    # Session authentication ...
    session = request.environ['beaker.session']
    if not session:
        response.status = 401
        response.content_type = 'application/json'
        return json.dumps({'status': 'ok', 'message': 'Session expired'})

    if 'current_user' not in session or not session['current_user']:
        response.status = 401
        response.content_type = 'application/json'
        return json.dumps({'status': 'ok', 'message': 'Session expired'})

    response.status = 200
    response.content_type = 'application/json'
    return json.dumps({'status': 'ok',
                       'message': "Current logged-in user: %s"
                                  % session['current_user'].get_username()})


@app.route('/ping')
def ping():
    # pylint: disable=too-many-return-statements
    """Request on /ping is a simple check alive that returns an information if UI refresh is needed

    If no session exists, it will return an HTTP 401 to inform that no session exists or the
    session has expired

    Else, the specified `action` may be:
        - done, to inform that the server required action has been performed by the client
        - refresh, to get some information from a specified `template`

    If no action is specified, the application answers with a JSON pong ;)

    Used by the header refresh to update the hosts/services live state.
    """
    session = request.environ['beaker.session']
    if not session:
        response.status = 401
        response.content_type = 'application/json'
        return json.dumps({'status': 'ok', 'message': 'Session expired'})

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
        return json.dumps({'status': 'ok',
                           'message': 'missing template name. '
                                      'Use /ping?action=refresh&template=name.'})
    elif action:
        response.status = 204
        response.content_type = 'application/json'
        return json.dumps({'status': 'ok',
                           'message': 'Unknown ping action parameter: %s' % action})

    response.status = 200
    response.content_type = 'application/json'
    return json.dumps({'status': 'ok', 'message': 'pong'})


# --------------------------------------------------------------------------------------------------
# WebUI routes
# --------------------------------------------------------------------------------------------------
# CORS decorator
def enable_cors(fn):
    """CORS decorator

    Send the CORS headers for ajax request
    """
    def _enable_cors(*_args, **_kwargs):
        # set CORS headers
        response.headers['Access-Control-Allow-Origin'] = \
            request.app.config.get('cors_acao', 'http://127.0.0.1')
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = \
            'Origin, Accept, Authorization, X-HTTP-Method-Override, If-Match, Content-Type'
        response.headers['Access-Control-Allow-Credentials'] = 'true'

        if bottle.request.method != 'OPTIONS':
            # actual request; reply with the actual response
            return fn(*_args, **_kwargs)

        # response.status = 204

    return _enable_cors


@app.route('/external/<widget_type>/<identifier>/<action:path>', method=['GET', 'POST', 'OPTIONS'])
@app.route('/external/<widget_type>/<identifier>', method=['GET', 'POST', 'OPTIONS'])
@enable_cors
def external(widget_type, identifier, action=None):
    # pylint: disable=too-many-return-statements, unsupported-membership-test
    # pylint: disable=unsubscriptable-object
    """Application external identifier

    Use internal authentication (if a user is logged-in) or external basic authentication provided
    by the requiring application.

    Search in the known 'widget_type' (widget or table) to find the element 'identifier'.

    Use the 'links' parameter to prefix the navigation URLs.
    """

    logger.info("external...")
    # Get the WebUI instance
    webui = request.app.config['webui']

    session = request.environ['beaker.session']
    if 'current_user' in session:
        current_user = session['current_user']

        if not webui.user_authentication(current_user.token, None):
            # Redirect to application login page
            logger.warning("External request. User in the session is not authenticated. "
                           "Redirecting to the login page...")
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

        if not webui.user_authentication(username, password):
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
        request.app.datamgr = DataManager(request.app, session=request.environ['beaker.session'])
        BaseTemplate.defaults['datamgr'] = request.app.datamgr

    logger.info("External request, element type: %s", widget_type)

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
            return json.dumps({'status': 'ok', 'files': webui.js_list})

        if identifier == 'css_list':
            response.status = 200
            response.content_type = 'application/json'
            return json.dumps({'status': 'ok', 'files': webui.css_list})

        logger.warning("External application requested unknown files: %s", identifier)
        response.status = 409
        response.content_type = 'application/json'
        return json.dumps({'status': 'ko', 'message': "Unknown files list: %s" % identifier})

    if widget_type == 'widget':
        found_widget = None
        for widget in webui.get_widgets_for('external'):
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
        for table in webui.get_tables_for('external'):
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
        logger.info("Found table: %s", found_table)

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
        if identifier in webui.lists:
            return webui.lists[identifier]['function'](embedded=True)

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
        for widget in webui.get_widgets_for(widget_type):
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
# WebUI user's preferences
# --------------------------------------------------------------------------------------------------
@app.route('/preference/user', 'GET')
def get_user_preference():
    """Get user's preferences for the current logged-in user

        Request parameters:

        - key, string identifying the parameter
        - default, default value if parameter does not exist
    """
    user = request.environ['beaker.session']['current_user']
    datamgr = request.app.datamgr

    _key = request.query.get('key', None)
    if not _key:
        return WebUI.response_invalid_parameters(_('Missing mandatory parameters'))

    default = request.query.get('default', None)
    if default:
        try:
            default = json.loads(default)
        except Exception:
            pass

    key_value = datamgr.get_user_preferences(user, _key, default)
    if key_value is None:
        response.status = 404
        response.content_type = 'application/json'
        return json.dumps({'status': 'ko',
                           'message': 'Unknown key: %s' % _key})

    response.status = 200
    response.content_type = 'application/json'
    return json.dumps(key_value)


@app.route('/preference/user/delete', 'GET')
def delete_user_preference():
    """Delete current logged-in user's preference

        Request parameters:

        - key, string identifying the parameter
    """
    user = request.environ['beaker.session']['current_user']
    datamgr = request.app.datamgr

    _key = request.query.get('key', None)
    if not _key:
        return WebUI.response_invalid_parameters(_('Missing mandatory parameters'))

    response.status = 200
    response.content_type = 'application/json'
    return json.dumps(datamgr.delete_user_preferences(user, _key))


@app.route('/preference/user', 'POST')
def set_user_preference():
    """Update current logged-in user's preference
        Request parameters:

        - key, string identifying the parameter
        - value, as a JSON formatted string
    """
    user = request.environ['beaker.session']['current_user']
    datamgr = request.app.datamgr

    _key = request.forms.get('key', None)
    _value = request.forms.get('value', None)
    if _key is None or _value is None:
        return WebUI.response_invalid_parameters(_('Missing mandatory parameters'))

    try:
        _value = json.loads(_value)
    except Exception:
        pass

    if datamgr.set_user_preferences(user, _key, _value):
        return WebUI.response_ok(message=_('User preferences saved'))

    return WebUI.response_ko(message=_('Problem encountered while saving user preferences'))


# --------------------------------------------------------------------------------------------------
# WebUI edition mode
# --------------------------------------------------------------------------------------------------
@app.route('/edition_mode', 'POST')
# User preferences page ...
def edition_mode():
    """Set edition mode on / off

    The `state` parameter is 'on' or 'off' to enable / disable the edition mode in the session

    If this parameter is not present, this function do not change the current edition mode that
    is simply returned in the response.

    Returns a JSON response:
        {'edition_mode': False, 'message': 'Edition mode disabled'}
    """
    # Session...
    session = request.environ['beaker.session']
    user = session['current_user']
    if not user.can_edit_configuration():
        logger.warning("Current user '%s' is not authorized to change edition_mode",
                       user.get_username())
        response.status = 401
        response.content_type = 'application/json'
        return json.dumps({'status': 'ko', 'message': 'Not authorized to change edition mode'})

    required_state = request.params.get('state', None)
    logger.debug("edition_mode, required state: %s", required_state)

    if required_state is not None:
        # Make session edition mode available in the session and in the templates
        session['edition_mode'] = (required_state == 'on')
        BaseTemplate.defaults['edition_mode'] = session['edition_mode']
    logger.debug("edition_mode, session: %s", session['edition_mode'])

    if session['edition_mode']:
        user_message = _('Edition mode enabled')
    else:
        user_message = _('Edition mode disabled')

    response.status = 200
    response.content_type = 'application/json'
    return json.dumps({'edition_mode': session['edition_mode'], 'message': user_message})


# Bottle templates path
TEMPLATE_PATH.append(
    os.path.join(
        os.path.abspath(os.path.dirname(__file__)), 'views'
    )
)

# -----
# Extend default WSGI application with a session middleware
# -----
session_opts = {
    'session.type': app.config.get('session.type', 'file'),
    'session.data_dir': app.config.get('session.data_dir',
                                       os.path.join('/tmp', __manifest__['name'], 'sessions')),
    'session.auto': app.config.get('session.auto', True),
    'session.cookie_expires': app.config.get('session.cookie_expires', 43200),
    'session.key': app.config.get('session.key', __manifest__['name']),
    'session.save_accessed_time': True,
    'session.timeout': app.config.get('session.timeout', None),
    'session.data_serializer': app.config.get('session.data_serializer', 'json'),
    # Do not remove! For unit tests only...
    'sesssion.webtest_varname': __manifest__['name'],
}
logger.debug("Session parameters: %s", session_opts)
session_app = SessionMiddleware(app, session_opts)


def main():  # pragma: no cover, because of test mode
    """Function called by the setup.py console script"""
    logger.info("Running Bottle, debug mode: %s", app.config.get('debug', False))

    run(
        app=session_app,
        host=app.config.get('host', '127.0.0.1'),
        port=int(app.config.get('port', 5001)),
        debug=app.config.get('debug', False),
        reloader=app.config.get('debug', False)
    )
    # remember to remove reloader=True and debug(True) when you move your application
    # from development to a production environment

if __name__ == '__main__':
    main()
