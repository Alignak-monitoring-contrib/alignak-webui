#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2017:
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
# import the unit testing module

from __future__ import print_function

import os

import unittest2
import bottle

# Set test mode ...
os.environ['ALIGNAK_WEBUI_TEST'] = '1'
os.environ['ALIGNAK_WEBUI_DEBUG'] = '1'
os.environ['ALIGNAK_WEBUI_CONFIGURATION_FILE'] = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'settings.cfg')
print("Configuration file", os.environ['ALIGNAK_WEBUI_CONFIGURATION_FILE'])

import alignak_webui.app


pid = None
appli = None


class TestInitialization(unittest2.TestCase):
    def test_0(self):
        """ Default initialization - production mode, no test mode configuration """
        print('Default initialization - production mode, no test mode configuration')

        # Application configuration is already loaded
        # Default is to get all the possible files ... as of it, event the settings.cfg in the
        # current directory is active!
        self.config = alignak_webui.get_app_config()
        print(self.config)
        assert self.config
        # Bottle variables
        assert self.config.get('host', 'default_value') == '0.0.0.0'
        assert self.config.get('port', 'default_value') == '5001'
        # Application variables
        assert self.config.get('locale', 'default_value') == 'default_value'
        # Variable defined in the settings.cfg test file ...
        assert self.config.get('test_mode') == '1'

        # Alignak-WebUI object is initialized
        self.webui = self.config.get('webui', None)
        print(self.webui.__dict__)
        assert self.webui
        assert self.webui.app is not None
        assert self.webui.config is not None
        assert self.webui.plugins_count is not None

    def test_1_1(self):
        """ Application configuration (manifest) """
        print('test configuration')

        manifest = alignak_webui.__manifest__
        print('manifest:', manifest)
        assert manifest
        assert manifest['name']
        assert manifest['version']
        assert manifest['author']
        assert manifest['copyright']
        assert manifest['license']
        assert manifest['release']
        assert manifest['doc']

        print(_)
        assert _

        print(alignak_webui.app_config)
        self.config = alignak_webui.get_app_config()
        assert alignak_webui.app_config == self.config

    def test_1_2_plugins(self):
        """ Application plugins """
        print('test plugins')

        self.config = alignak_webui.get_app_config()
        self.webui = self.config.get('webui', None)

        print('plugins count:', self.webui.plugins_count)
        for plugin in self.webui.plugins:
            print("Plugin:", plugin)

        print('get plugins routes - route name is present')
        for s_route in [r for r in bottle.app().routes if r.name]:
            print("Plugin route:", s_route.name, s_route.rule, s_route.callback)

        print('get plugins static files routes - rule starts with /plugins')
        for s_route in [r for r in bottle.app().routes if r.rule.startswith('/plugins')]:
            print("Plugin static files route:", s_route.rule)


if __name__ == '__main__':
    unittest2.main()
