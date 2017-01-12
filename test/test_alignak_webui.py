#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015:
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
import alignak_webui.app
from alignak_webui import _
from alignak_webui import get_app_webui
from alignak_webui.utils.settings import Settings


# Do not set test mode ... application is tested in production mode!
os.environ['TEST_ALIGNAK_WEBUI'] = '1'
os.environ['TEST_ALIGNAK_WEBUI_CFG'] = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                                    'settings.cfg')
print("Configuration file", os.environ['TEST_ALIGNAK_WEBUI_CFG'])

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
        assert self.config.get('host', 'default_value') == 'default_value'
        assert self.config.get('locale', 'en_US') == 'en_US'
        # Variable defined in the settings.cfg test file ...
        assert self.config.get('test_mode') == '1'

        # Alignak-WebUI object is initialized
        self.alignak_webui = get_app_webui()
        print(self.alignak_webui.__dict__)
        assert self.alignak_webui
        assert self.alignak_webui.widgets is not None

    def test_1(self):
        """ Define settings """
        print('Settings fixed')

        # Get configuration from only one file ...
        print("read configuration")
        cfg = Settings(
            os.path.join(os.path.abspath(os.path.dirname(__file__)), 'settings.cfg')
        )
        found_cfg_files = cfg.read('Alignak-WebUI')
        assert found_cfg_files
        print("Found files:", found_cfg_files)
        alignak_webui.set_app_config(cfg)

        # Application configuration is loaded
        self.config = alignak_webui.get_app_config()
        assert self.config
        assert self.config.get('host', 'default_value') == 'default_value'
        assert self.config.get('locale', 'en_US') == 'en_US'
        # Variable defined in the settings.cfg test file ...
        assert self.config.get('test_mode') == '1'

        # Alignak-WebUI object is initialized
        self.alignak_webui = get_app_webui()
        assert self.alignak_webui

    def test_2(self):
        """ Defined settings (fr """
        print('Settings fixed (2)')

        # Get configuration from only one file ...
        print("read configuration")
        cfg = Settings(
            os.path.join(os.path.abspath(os.path.dirname(__file__)), 'settings.fr')
        )
        found_cfg_files = cfg.read('Alignak-WebUI')
        assert found_cfg_files
        alignak_webui.set_app_config(cfg)

        # Application configuration is loaded
        self.config = alignak_webui.get_app_config()
        assert self.config
        # Not defined in settings.fr
        assert self.config.get('alignak_backend', 'default_value') == 'default_value'
        # Defined in settings.fr
        assert self.config.get('locale', 'en_US') == 'fr_FR'
        # Variable defined in the settings.cfg test file ...
        assert self.config.get('test_mode') == '1'

        # Alignak-WebUI object is initialized
        self.alignak_webui = get_app_webui()
        assert self.alignak_webui


class TestMethods(unittest2.TestCase):
    def setUp(self):
        print("setting up ...")

        # Application configuration is loaded
        self.config = alignak_webui.get_app_config()
        print(self.config)
        assert self.config

        # Alignak-WebUI object is initialized
        self.alignak_webui = alignak_webui.get_app_webui()
        print(self.alignak_webui)
        assert self.alignak_webui

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
        assert alignak_webui.app_config

        print('alignak_webui:', self.alignak_webui)
        # assert False

    def test_1_2_plugins(self):
        """ Application plugins """
        print('test plugins')

        print('plugins count:', self.alignak_webui.plugins_count)
        for plugin in self.alignak_webui.plugins:
            print("Plugin:", plugin)

        print('get plugins routes - route name is present')
        for s_route in [r for r in bottle.app().routes if r.name]:
            print("Plugin route:", s_route.name, s_route.rule, s_route.callback)

        print('get plugins static files routes - rule starts with /plugins')
        for s_route in [r for r in bottle.app().routes if r.rule.startswith('/plugins')]:
            print("Plugin static files route:", s_route.rule)


if __name__ == '__main__':
    unittest2.main()
