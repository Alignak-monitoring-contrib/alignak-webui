#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=global-statement, global-variable-not-assigned

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
    Alignak-WebUI application
"""
from __future__ import print_function
import os

# Logs
import logging

# Localization
import gettext
from gettext import GNUTranslations, NullTranslations

# Bottle import
from bottle import BaseTemplate
import bottle

# Session management
from beaker.middleware import SessionMiddleware

# Specific application
from alignak_webui.version import __manifest__
from alignak_webui.utils.logs import logger, setup_logger


# --------------------------------------------------------------------------------------------------
# Application logger
# pylint: disable=invalid-name
# logger = logging.getLogger(__name__)

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
    global bottle_app, app_config, _, logger

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

    # Set application log level (default is INFO (20))
    print("Configured log level: %d" % int(app_config.get('logs.level', '20')))
    log_level = int(app_config.get('logs.level', '20'))
    if app_config.get('debug', '0') == '1':  # pragma: no cover - not testable easily...
        print("-> Activated DEBUG log")
        log_level = logging.DEBUG

    # Define log file name
    log_file = os.path.join(app_config.get('logs.dir', '/usr/local/var/log/alignak-webui'),
                            app_config.get('logs.filename', '%s.log'
                                           % __manifest__['name'].lower()))
    print("Configured log file: %s" % log_file)
    logger = None
    try:
        logger = setup_logger(logger, log_level, log_file, True,
                              when=app_config.get('logs.when', 'D'),
                              interval=int(app_config.get('logs.interval', '1')),
                              backup_count=int(app_config.get('logs.backupCount', '6')))
    except IOError:
        print("Configured log file is not available")
        log_file = os.path.join('/tmp/',
                                app_config.get('logs.filename', '%s.log'
                                               % __manifest__['name'].lower()))
        logger = setup_logger(logger, log_level, log_file, True,
                              when=app_config.get('logs.when', 'D'),
                              interval=int(app_config.get('logs.interval', '1')),
                              backup_count=int(app_config.get('logs.backupCount', '6')))
    except Exception as e:  # pragma: no cover - should not happen
        print("Log file creation error. Exception: %s" % str(e))
    print("Logging to file: %s" % log_file)

    logger.info(
        "--------------------------------------------------------------------------------"
    )
    logger.info("%s, version %s", __manifest__['name'], __manifest__['version'])
    logger.info("Copyright %s", __manifest__['copyright'])
    logger.info("License: %s", __manifest__['license'])
    logger.info(
        "--------------------------------------------------------------------------------"
    )
    logger.debug("Doc: %s", __manifest__['doc'])
    logger.debug("Release notes: %s", __manifest__['release'])
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
    'session.data_dir': os.path.join('/tmp', __manifest__['name'], 'sessions'),
    'session.auto': True,
    'session.cookie_expires': 21600,    # 6 hours
    'session.key': __manifest__['name'],
    'sesssion.webtest_varname': __manifest__['name'],    # For unit tests ...
    'session.data_serializer': 'json'   # Default is pickle ... not appropriate for our data!
}
webapp = SessionMiddleware(bottle_app, session_opts)
