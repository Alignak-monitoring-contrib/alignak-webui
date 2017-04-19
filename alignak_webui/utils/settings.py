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
    Application configuration and settings module
"""
from __future__ import print_function

import os
import traceback
from collections import OrderedDict
from configparser import RawConfigParser

# Do not use logger in this module ... or it may fail!


class Settings(OrderedDict):
    """
    Class used to manage configuration file and application configuration
    """

    def __init__(self, filenames=None):
        """
        Initialize configuration

        If a filename is provided it will be used instead of the default list.
        `filename` may be a list of files to use.

        :param filename: file to use for loading configuration
        """
        super(Settings, self).__init__()

        self.filenames = filenames

    def read(self, app_name='Alignak-WebUI'):
        # pylint: disable=too-many-nested-blocks
        """ Read configuration file

        Tries to load a configuration from the following files:

        - /usr/local/etc/alignak_webui/settings.cfg (FreeBSD)
        - /etc/alignak_webui/settings.cfg (Debian)
        - ~/alignak_webui/settings.cfg (Current user home directory)
        - ./etc/settings.cfg (Current working directory etc sub directory)
        - ./settings.cfg (Current working directory)
        - cfg_file parameter

        This list of file is used by the Python ConfigParser to build the application configuration.

        The parameters found in the sections of the configuration are stored in the global
        ``settings`` dictionary. A variable named *var* in the section *section* is stored with the
        key *section.var* of the ``settings`` dictionary. As of it, parameters of the *ui* section
        are all prefixed with *ui.* ...

        Returns None if no configuration file could be found, else returns ConfigParser object

        :param app_name: application name (to build configuration file name)

        """
        app_name = app_name.lower()

        settings_filenames = self.filenames
        if not isinstance(self.filenames, list):
            settings_filenames = [os.path.abspath(self.filenames)]

        try:
            config = RawConfigParser()
            found_cfg_file = config.read(settings_filenames)
            if found_cfg_file:
                # Build settings dictionnary for application parameters
                for section in config.sections():
                    for option in config.options(section):
                        if app_name == section.lower():
                            self[option] = config.get(section, option)
                            if self[option] in ['True', 'true']:
                                self[option] = True
                            if self[option] in ['False', 'false']:
                                self[option] = False
                        else:
                            self[section + '.' + option] = config.get(section, option)
                            if self[section + '.' + option] in ['True', 'true']:
                                self[section + '.' + option] = True
                            if self[section + '.' + option] in ['False', 'false']:
                                self[section + '.' + option] = False

            return found_cfg_file
        except Exception as exp:  # pragma: no cover - bad formated file
            print("Bad formed configuration file.")
            print("Exception: %s" % str(exp))
            print("Traceback: %s" % traceback.format_exc())
            return None
