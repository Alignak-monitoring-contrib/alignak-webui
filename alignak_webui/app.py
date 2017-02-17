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
    This module is the main application file
"""

from __future__ import print_function

import os
import time
import json
import logging
import threading

# Localization
from gettext import GNUTranslations, NullTranslations

# Session management
from beaker.middleware import SessionMiddleware

# Bottle Web framework
import bottle
from bottle import run, redirect, request, response, static_file
from bottle import template, BaseTemplate, TEMPLATE_PATH
from bottle import RouteBuildError
# only needed when you run Bottle on mod_wsgi
# from bottle import default_app

# Application import
from alignak_webui import __pkg_name__, __manifest__, set_app_config
from alignak_webui.utils.logger import setup_logging
from alignak_webui.utils.helper import Helper
from alignak_webui.backend.backend import BackendException
from alignak_webui.backend.datamanager import DataManager
from alignak_webui.webui import WebUI

app = application = bottle.Bottle()

# -----
# Test mode for the application
# -----
if os.environ.get('ALIGNAK_WEBUI_TEST'):
    print("Application is in test mode")
else:
    print("Application is in production mode")

# -----
# Application configuration file
# -----
app_name = __manifest__['name'].lower()
# Search for configuration files in several locations
cfg_filenames = [
    '/usr/local/etc/%s/settings.cfg' % app_name,
    '/etc/%s/settings.cfg' % app_name,
    '~/%s/settings.cfg' % app_name,
    os.path.abspath('../etc/settings.cfg'),
    os.path.abspath('./etc/settings.cfg'),
    os.path.abspath('./settings.cfg'),
]
if os.environ.get('ALIGNAK_WEBUI_CONFIGURATION_FILE'):
    cfg_filenames = [os.environ.get('ALIGNAK_WEBUI_CONFIGURATION_FILE')]
    print("Application configuration file name from environment: %s"
          % os.environ.get('ALIGNAK_WEBUI_CONFIGURATION_FILE'))

app_configuration_file = None
for cfg_filename in cfg_filenames:
    if os.path.isfile(cfg_filename):
        app.config.load_config(cfg_filename)
        print("Configuration read from: %s" % cfg_filename)
        app_configuration_file = cfg_filename
        break
else:
    print("***** Application configuration file not found.")
    print("***** Searched in: %s" % cfg_filenames)
    exit(1)

# -----
# Check application configuration file change
# -----
if os.environ.get('ALIGNAK_WEBUI_CONFIGURATION_THREAD'):
    def check_config(app, filename, interval=5):
        print("Thread for checking configuration file change, file: %s" % filename)
        modification_time = os.path.getmtime(filename)
        while True:
            time.sleep(interval)
            print("Checking configuration file change...")
            if modification_time < os.path.getmtime(filename):
                print("Application configuration file changed, reloading configuration...")
                modification_time = os.path.getmtime(filename)
                app.config.load_config(filename)
    cfg_check_thread = threading.Thread(target=check_config,
                                        name='application_configuration_check',
                                        args=(app, app_configuration_file, 10))
    cfg_check_thread.daemon = True
    cfg_check_thread.start()

# -----
# Debug and test mode
# -----
if os.environ.get('BOTTLE_DEBUG'):
    app.config['bottle.debug'] = True
    print("Bottle is in debug mode from environment")

if os.environ.get('ALIGNAK_WEBUI_DEBUG'):
    app.config['%s.debug' % app_name] = True
    print("Application is in debug mode from environment")

# -----
# Application backend
# -----
if os.environ.get('ALIGNAK_WEBUI_BACKEND'):
    app.config['%s.alignak_backend' % app_name] = os.environ.get('ALIGNAK_WEBUI_BACKEND')
    print("Application backend from environment")
print("Application backend: %s" % app.config.get('%s.alignak_backend' % app_name,
                                                 'http://127.0.0.1:5000'))

# -----
# Application log
# -----
# Set application log level (default is INFO
log_level = 'INFO'
if app.config.get('%s.debug' % app_name, False):  # pragma: no cover - not testable easily...
    print("-> Activated DEBUG log")
    log_level = 'DEBUG'

log_filenames = [
    '/usr/local/etc/%s/logging.json' % app_name,
    '/etc/%s/logging.json' % app_name,
    '~/%s/logging.json' % app_name,
    os.path.abspath('../etc/logging.json'),
    os.path.abspath('./etc/logging.json'),
    os.path.abspath('./logging.json'),
]
if os.environ.get('ALIGNAK_WEBUI_LOGGER_FILE'):
    log_filenames = [os.environ.get('ALIGNAK_WEBUI_LOGGER_FILE')]
    print("Application logger configuration file from environment: %s"
          % os.environ.get('ALIGNAK_WEBUI_LOGGER_FILE'))

app_logger_file = None
logger = None
for log_filename in log_filenames:
    if setup_logging(log_filename):
        logger = logging.getLogger(app_name)
        logger.setLevel(log_level)
        print("Application logger configured from: %s" % log_filename)
        break
else:
    print("***** Application logger configuration file not found.")
    print("***** Searched in: %s" % log_filenames)
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
            app.config.get('debug', False))
logger.info("using Alignak Backend on %s",
            app.config.get('%s.alignak_backend' % app_name, 'http://127.0.0.1:5000'))
logger.info("--------------------------------------------------------------------------------")

logger.debug("Application settings: ")
# Make the 'application.key' also available as 'key'
add_to_config = {}
for key, value in sorted(app.config.items()):
    if key.startswith(app_name):
        add_to_config[key.replace(app_name+'.', '')] = value
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
try:
    # Language message file
    lang_filename = os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        "locales/%s.mo" % app.config.get('%s.locale' % app_name, 'en_US')
    )
    print("Opening message file %s for locale %s"
          % (lang_filename, app.config.get('%s.locale' % app_name, 'en_US')))
    translation = GNUTranslations(open(lang_filename, "rb"))
    translation.install()
    _ = translation.gettext
except IOError:
    print("Locale not found. Using default language messages (English)")
    null_translation = NullTranslations()
    null_translation.install()
    _ = null_translation.gettext
except Exception as e:  # pragma: no cover - should not happen
    print("Locale not found. Exception: %s" % str(e))
    null_translation = NullTranslations()
    null_translation.install()
    _ = null_translation.gettext

# Provide translation methods to templates
app.config['_'] = _
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
    """
    Main application static files
    Plugins declare their own static routes under /plugins
    """
    if not filename.startswith('plugins'):
        return static_file(
            filename, root=os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static')
        )
    else:
        return static_file(
            filename, root=os.path.abspath(os.path.dirname(__file__))
        )


# -----
# Application modal windows
# -----
@app.route('/modal/<modal_name>')
def give_modal(modal_name):
    """
    Return template for a modal window
    """
    logger.debug("get modal window named: %s", modal_name)
    return template('modal_' + modal_name)


# --------------------------------------------------------------------------------------------------
# WebUI hooks
# --------------------------------------------------------------------------------------------------
@app.hook('config')
def on_config_change(key, value):
    logger.warning("application configuration changed, key: %s = %s", key, value)
    if key.startswith(app_name):
        app.config[key.replace(app_name+'.', '')] = value
        logger.warning("application configuration changed, *** key: %s = %s", key.replace(app_name+'.', ''), value)


@app.hook('before_request')
def before_request():
    # pylint: disable=unsupported-membership-test, unsubscriptable-object
    """
    Function called since an HTTP request is received, and before any other function.

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

    # Session authentication ...
    if 'current_user' not in session:
        # Redirect to application login page
        logger.warning(
            "The session expired or there is no user in the session."
            " Redirecting to the login page..."
        )

        # Stop Alignak backend thread
        # *****

        redirect('/login')

    # Get the WebUI instance
    webui = request.app.config['webui']

    current_user = session['current_user']
    if not webui.user_authentication(current_user.token, None):
        # Redirect to application login page
        logger.warning(
            "user in the session is not authenticated."
            " Redirecting to the login page..."
        )
        redirect('/login')

    # Make session current user available in the templates
    BaseTemplate.defaults['current_user'] = session['current_user']
    # Make session edition mode available in the templates
    BaseTemplate.defaults['edition_mode'] = session['edition_mode']
    # Initialize data manager and make it available in the request and in the templates
    if webui.datamgr is None:
        webui.datamgr = DataManager(
            backend_endpoint=request.app.config.get('%s.alignak_backend' % webui.name,
                                                    'http://127.0.0.1:5000'),
            session=request.environ['beaker.session']
        )
    request.app.datamgr = webui.datamgr
    # # Load initial objects from the DM
    # request.app.datamgr.load()
    BaseTemplate.defaults['datamgr'] = request.app.datamgr

    # logger.debug("before_request, call function for route: %s", request.urlparts.path)


# --------------------------------------------------------------------------------------------------
# Home page and login
# --------------------------------------------------------------------------------------------------
@app.route('/', 'GET')
def home_page():
    """
    Display home page -> redirect to /Dashboard
    """
    try:
        redirect(request.app.get_url('Livestate'))
    except RouteBuildError:
        return "No home page available in the application routes!"


@app.route('/login', 'GET')
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
            'app_logo': request.app.config.get(
                'app_logo', '/static/images/alignak_white_logo.png'
            ),
            'message': message
        }
    )


@app.route('/logout', 'GET')
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


def check_backend_connection(app, token=None, interval=10):
    print("Thread for checking backend connection is alive with %s" % app.config['alignak_backend'])

    backend = app.datamgr.backend
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


@app.route('/ping')
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
            # # Get the WebUI instance
            # webui = request.app.config['webui']
            # # Initialize data manager and make it available in the request and in the templates
            # if webui.datamgr is None:
            #     webui.datamgr = DataManager(
            #         backend_endpoint=request.app.config.get('%s.alignak_backend' % webui.name,
            #                                                 'http://127.0.0.1:5000'),
            #         session=request.environ['beaker.session']
            #     )
            # request.app.datamgr = webui.datamgr
            # BaseTemplate.defaults['datamgr'] = request.app.datamgr

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


@app.route('/bi-livestate')
def livestate():
    """
    Request on /ping is a simple check alive that returns an information if UI refresh is needed

    If no session exists, it will always return 'pong' to inform that server is alive.

    Else:
        - if UI refresh is needed, requires the UI client to refresh
        - if action parameter is 'refresh', returns the required template view
        - if action parameter is 'done', the UI client did refresh the interface.

    Used by the header refresh to update the hosts/services states.
    """
    user = request.environ['beaker.session']['current_user']
    webui = request.app.config['webui']
    datamgr = webui.datamgr

    panels = datamgr.get_user_preferences(user, 'livestate', {})

    ls = Helper.get_html_livestate(datamgr, panels,
                                   int(request.query.get('bi', -1)),
                                   request.query.get('search', {}),
                                   actions=user.is_power())

    response.status = 200
    response.content_type = 'application/json'
    return json.dumps({'livestate': ls})


# --------------------------------------------------------------------------------------------------
# WebUI user's preferences
# --------------------------------------------------------------------------------------------------
# @app.route('/preferences/user')
# # User preferences page ...
# def show_user_preferences():
#     """
#         Show the user preferences view
#     """
#     return template('_preferences')


@app.route('/preference/user', 'GET')
def get_user_preference():
    """
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
        default = json.loads(default)

    response.status = 200
    response.content_type = 'application/json'
    return json.dumps(datamgr.get_user_preferences(user, _key, default))


@app.route('/preference/user/delete', 'GET')
def delete_user_preference():
    """
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
    """
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

    if datamgr.set_user_preferences(user, _key, json.loads(_value)):
        return WebUI.response_ok(message=_('User preferences saved'))
    else:
        return WebUI.response_ko(
            message=_('Problem encountered while saving common preferences')
        )


@app.error(403)
def mistake403(code):  # pylint: disable=unused-argument
    """HTTP error code 403"""
    return 'There is a mistake in your url!'


@app.error(404)
def mistake404(code):  # pylint: disable=unused-argument
    """HTTP error code 404"""
    return 'Sorry, this page does not exist!'


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
    'session.type': 'file',
    'session.data_dir': os.path.join('/tmp', __manifest__['name'], 'sessions'),
    'session.auto': True,
    'session.cookie_expires': 21600,    # 6 hours
    'session.key': __manifest__['name'],
    'sesssion.webtest_varname': __manifest__['name'],    # For unit tests ...
    'session.data_serializer': 'json'   # Default is pickle ... not appropriate for our data!
}
session_app = SessionMiddleware(app, session_opts)

if __name__ == '__main__':
    run(
        app=session_app,
        host=app.config.get('host', '127.0.0.1'),
        port=int(app.config.get('port', 5001)),
        debug=app.config.get('debug', False),
        reloader=app.config.get('debug', False)
    )
    # remember to remove reloader=True and debug(True) when you move your application
    # from development to a productive environment
