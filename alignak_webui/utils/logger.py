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
    Application logs
"""
from __future__ import print_function
import os
import json
import time

# Logs
import logging
import logging.config
from logging import StreamHandler

from termcolor import cprint

# Default values for root logger
ROOT_LOGGER_NAME = 'alignak_bottle_webui'
ROOT_LOGGER_LEVEL = logging.INFO

logger = logging.getLogger(ROOT_LOGGER_NAME)  # pylint: disable=invalid-name
logger.setLevel(ROOT_LOGGER_LEVEL)


class UTCFormatter(logging.Formatter):
    """
    This logging formatter converts the log date/time to UTC
    """
    converter = time.gmtime


class ColorStreamHandler(StreamHandler):
    """
    This log handler provides colored logs when logs are emitted to a tty.
    """
    def emit(self, record):
        try:
            msg = self.format(record)
            colors = {'DEBUG': 'cyan', 'INFO': 'blue', 'WARNING': 'magenta', 'ERROR': 'red',
                      'CRITICAL': 'red'}
            cprint(msg, colors[record.levelname])
        except UnicodeEncodeError:
            print(msg.encode('ascii', 'ignore'))
        except TypeError:
            self.handleError(record)


def setup_logging(default_path='logging.json', default_level=logging.INFO, env_key='WEBUI_LOG_CFG'):
    """Setup logging configuration

    Get the logger configuration from a file which name is specified in `default_path`.
    This file name can be overriden by the environment variable `env_key` which may
    contain an alternate file name. If the logger configurationsucceeds, this
    function returns True.

    If the logger configuration cannot be get from a file, then this function returnes False.
    Except if `default_logger`is set then the logger is configured with the basic
    configuration and its level is set to the `default_level`.
    """
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as file_handler:
            config = json.load(file_handler)
        logging.config.dictConfig(config)
        return True

    else:
        logging.basicConfig(level=default_level)

    return False
