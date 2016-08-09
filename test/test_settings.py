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

from alignak_webui.utils.settings import Settings


class TestSettings(unittest2.TestCase):
    def test_1_found_not_found(self):
        print('test configuration file')

        # Default configuration - not found because of test directory location !
        print('Search default configuration file ...')
        found_cfg_files = Settings().read(None)
        print('Found:', found_cfg_files)
        assert found_cfg_files is None
        # Normal use case ... default files and application name ...
        # But ! do not get config object ...
        found_cfg_files = Settings().read('Alignak-WebUI')
        print('Found:', found_cfg_files)
        assert found_cfg_files

        # Relative file path
        cfg_file = "settings.cfg"
        print('Required configuration file:', cfg_file)
        found_cfg_files = Settings(cfg_file).read(None)
        print('Found:', found_cfg_files)
        assert found_cfg_files is None
        found_cfg_files = Settings(cfg_file).read('Alignak-WebUI')
        print('Found:', found_cfg_files)
        assert found_cfg_files

        # Absolute file path
        cfg_file = os.path.dirname(os.path.abspath(__file__)) + "/settings.cfg"
        print('Required configuration file:', cfg_file)
        found_cfg_files = Settings(cfg_file).read(None)
        print('Found:', found_cfg_files)
        assert found_cfg_files is None
        found_cfg_files = Settings(cfg_file).read('Alignak-WebUI')
        print('Found:', found_cfg_files)
        assert found_cfg_files

        # Absolute file path - bad formed file
        cfg_file = os.path.dirname(os.path.abspath(__file__)) + "/test_bad_settings.txt"
        print('Required configuration file:', cfg_file)
        found_cfg_files = Settings(cfg_file).read(None)
        print('Found:', found_cfg_files)
        assert found_cfg_files is None
        found_cfg_files = Settings(cfg_file).read('Alignak-WebUI')
        print('Found:', found_cfg_files)
        assert found_cfg_files is None

    def test_2_found(self):
        # Relative file path
        cfg_file = "settings.cfg"
        print('Required configuration file:', cfg_file)
        # Normal use case ... default files and application name ...
        # And get config object ...
        app_config = Settings(cfg_file)
        found_cfg_files = app_config.read('Alignak-WebUI')
        print('Found:', found_cfg_files)
        assert found_cfg_files

        print(app_config)
        self.assert_('about_name' in app_config)
        self.assertEqual(app_config['about_name'], 'Alignak-WebUI')

        # Variable 1 is String 1
        self.assert_('test_mode' in app_config)
        self.assertEqual(app_config['test_mode'], '1')
        self.assertIsInstance(app_config['test_mode'], basestring)

        # Variable True/true/False/false is boolean
        self.assertTrue(app_config['test_boolean1'])
        self.assertTrue(app_config['test_boolean2'])
        self.assertFalse(app_config['test_boolean3'])
        self.assertFalse(app_config['test_boolean4'])
