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
    Application logs
"""
from __future__ import print_function

import os

# Logs
from logging import DEBUG
from logging import Formatter, StreamHandler
from logging.handlers import TimedRotatingFileHandler

# Color logs when in console mode ...
from sys import stdout
from alignak_webui.utils.termcolor import cprint


# Declare a coloured stream handler for console mode ...
class ColorStreamHandler(StreamHandler):  # pragma: no cover
    """
    Color logs ...
    """
    def emit(self, record):
        # noinspection PyBroadException
        try:
            msg = self.format(record)
            colors = {
                'DEBUG': 'cyan', 'INFO': 'green', 'WARNING': 'yellow',
                'CRITICAL': 'magenta', 'ERROR': 'red'
            }
            cprint(msg, colors[record.levelname])
        except UnicodeEncodeError:
            print(msg.encode('ascii', 'ignore'))
        except TypeError:
            self.handleError(record)


def set_console_logger(logger):
    """
    Set a console logger only if application output is sent to a terminal
    """
    if stdout.isatty():  # pragma: no cover - not testable
        # logger = getLogger(__pkg_name__)

        ch = ColorStreamHandler(stdout)
        ch.setFormatter(Formatter('%(asctime)s - %(name)-12s - %(levelname)s - %(message)s'))
        ch.setLevel(DEBUG)
        logger.addHandler(ch)


# Yes, but we need it
# pylint: disable=too-many-arguments
def set_file_logger(logger, path='/var/log', filename='application.log',
                    when="midnight", interval=1, backup_count=6):
    """
    Configure handler for file logging ...
    """
    # Log file directory exists
    if not os.path.isdir(path):
        # noinspection PyBroadException
        try:  # pragma: no cover - not testable
            os.makedirs(path)
        except Exception:
            path = '.'

    # and log file directory is writeable
    if not os.access(path, os.W_OK):
        path = '.'

    # Store logs in a daily file, keeping 6 days along ...
    fh = TimedRotatingFileHandler(
        filename=os.path.join(path, filename),
        when=when, interval=interval,
        backupCount=backup_count
    )

    # create formatter and add it to the handler
    fh.setFormatter(Formatter('[%(asctime)s] - %(name)-12s - %(levelname)s - %(message)s'))
    fh.setLevel(DEBUG)
    logger.addHandler(fh)
