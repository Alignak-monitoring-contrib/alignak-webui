#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=global-statement, global-variable-not-assigned

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
    Alignak-WebUI application
"""
from __future__ import print_function
import os

# Logs
from logging import DEBUG
from logging import getLogger

# Localization
import gettext
from gettext import GNUTranslations, NullTranslations

# Bottle import
from bottle import BaseTemplate
import bottle

# Session management
from beaker.middleware import SessionMiddleware

# Specific application
from alignak_webui.version import manifest
from alignak_webui.utils.logs import set_console_logger, set_file_logger


# Application logger
logger = getLogger(__name__)

# Localization
_ = gettext.gettext

# Application configuration object
# Global variable to be used with accessor functions ...
# ... to make it package/module global!
app_config = None


def get_app_config():
    """
    Return global application configuration
    """
    global app_config
    return app_config


def set_app_config(config):
    """
    Update global application configuration
    """
    global bottle_app, app_config, _

    # Localization
    try:
        # Language message file
        filename = os.path.join(
            os.path.abspath(os.path.dirname(__file__)), "res/%s.mo" % config.get('locale', 'en_US')
        )
        print("Opening message file %s for locale %s" % (filename, config.get('locale', 'en_US')))
        translation = GNUTranslations(open(filename, "rb"))
        translation.install()
        _ = translation.gettext
    except IOError:
        print("Locale not found. Using default language messages (English)")
        default = NullTranslations()
        default.install()
        _ = default.gettext
    except Exception as e:  # pragma: no cover - should not happen
        print("Locale not found. Exception: %s" % str(e))
        default = NullTranslations()
        default.install()
        _ = default.gettext
    print(_("Language is English (default)..."))

    app_config = config
    bottle_app.config.update(config)

    # Set logging options for the application
    set_console_logger(logger)

    # Store logs in a daily file, keeping 6 days along ... as default!
    set_file_logger(
        logger,
        path=app_config.get('logs.dir', '/var/log/'),
        filename=app_config.get('logs.filename', manifest['name'].lower() + '.log'),
        when=app_config.get('logs.when', 'D'),
        interval=int(app_config.get('logs.interval', '1')),
        backup_count=int(app_config.get('logs.backupCount', '6'))
    )

    # Set application log level (default is INFO (20))
    print("Activate logs level: %d" % int(app_config.get('logs.level', '20')))
    logger.setLevel(int(app_config.get('logs.level', '20')))
    if app_config.get('debug', '0') == '1':  # pragma: no cover - not testable easily...
        print("Activate DEBUG logs")
        logger.setLevel(DEBUG)

    logger.info(
        "--------------------------------------------------------------------------------"
    )
    logger.info("%s, version %s", manifest['name'], manifest['version'])
    logger.info("Copyright %s", manifest['copyright'])
    logger.info("License: %s", manifest['license'])
    logger.info(
        "--------------------------------------------------------------------------------"
    )
    logger.debug("Doc: %s", manifest['doc'])
    logger.debug("Release notes: %s", manifest['release'])
    logger.debug(
        "--------------------------------------------------------------------------------"
    )

    logger.info(
        "--------------------------------------------------------------------------------"
    )
    logger.info(
        "%s, listening on %s:%d (debug mode: %s)",
        app_config.get('name', 'Test'),
        app_config.get('host', '127.0.0.1'), int(app_config.get('port', '5001')),
        app_config.get('debug', '0') == '1'
    )
    logger.info(
        "%s, using Alignak Backend on %s",
        app_config.get('name', 'Test'),
        app_config.get('alignak_backend', 'http://127.0.0.1:5000')
    )
    logger.info(
        "%s, using Alignak Web Services on %s",
        app_config.get('name', 'Test'),
        app_config.get('alignak_arbiter', 'http://127.0.0.1:7770')
    )
    logger.info(
        "--------------------------------------------------------------------------------"
    )

    logger.debug("Application settings: ")
    for key, value in sorted(app_config.items()):
        logger.debug(" %s = %s", key, value)
    logger.debug(
        "--------------------------------------------------------------------------------"
    )

# WebUI application object
# Global variable to be used with accessor functions ...
app_webui = None


def set_app_webui(webui):
    """
    Store global application object
    """
    global app_webui

    # Make main application object available in all Bottle templates
    app_webui = webui
    bottle_app.webui = webui
    BaseTemplate.defaults['webui'] = webui
    return app_webui


def get_app_webui():
    """
    Return global application object
    """
    global app_webui
    return app_webui

# --------------------------------------------------------------------------------------------------
# WebUI application is default bottle app
bottle_app = bottle.app()

# In test mode, let Bottle report errors to the WSGI environment (it helps debugging...)
if os.environ.get('TEST_WEBUI'):
    bottle.app().catchall = False

# Bottle templates path
bottle.TEMPLATE_PATH.append(
    os.path.join(
        os.path.abspath(os.path.dirname(__file__)), 'views'
    )
)

# Extend default WSGI application with a session middleware
session_opts = {
    # Important: somedata stored in the session cannot be pickled. Using file is not allowed!
    'session.type': 'file',
    'session.data_dir': os.path.join('/tmp', __name__, 'sessions'),
    'session.auto': True,
    'session.cookie_expires': 21600,    # 6 hours
    'session.key': manifest['name'],
    'sesssion.webtest_varname': manifest['name'],    # For unit tests ...
    'session.data_serializer': 'json'   # Default is pickle ... not appropriate for our data!
}
webapp = SessionMiddleware(bottle_app, session_opts)
