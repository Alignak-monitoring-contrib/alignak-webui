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
from collections import OrderedDict

import time

import unittest2

import alignak_webui.app

# from alignak_webui import set_app_config
from alignak_webui.objects.item_timeperiod import TimePeriod
from alignak_webui.objects.item_host import Host
from alignak_webui.utils.helper import Helper
from alignak_webui.utils.settings import Settings

helper = Helper()


class TestDate(unittest2.TestCase):
    def test_print_date(self):
        """ Helper - date """

        now = time.time()

        # Timestamp errors
        s = helper.print_date(None)
        print("Result:", s)
        assert s == 'n/a'

        s = helper.print_date(0)
        print("Result:", s)
        assert s == 'n/a'

        # Now, default format
        s = helper.print_date(now)
        print("Result:", s)

        # Now, specified format
        s = helper.print_date(now, fmt='%Y-%m-%d')
        print("Result:", s)

        s = helper.print_date(now, fmt='%H:%M:%S')
        print("Result:", s)

        # Now, force local specified format
        s = helper.print_date(now, fmt=None)
        print("Result:", s)


class TestDuration(unittest2.TestCase):
    def test_print_duration(self):
        """ Helper - duration """
        now = int(time.time())

        # Timestamp errors
        s = helper.print_duration(None)
        print("Result:", s)
        assert s == 'n/a'
        s = helper.print_duration(0)
        print("Result:", s)
        assert s == 'n/a'

        # Now, default format
        s = helper.print_duration(now)
        print("Result:", s)
        assert s == 'Just now'
        # 2s ago
        s = helper.print_duration(now - 2)
        print("Result:", s)
        assert s == 'Just now'

        # In the past ...
        # 4s ago
        s = helper.print_duration(now - 4)
        print("Result:", s)
        assert s == ' 4s ago'

        # Only the duration string
        s = helper.print_duration(now - 4, duration_only=True)
        print("Result:", s)
        assert s == '4s'

        # Got 2minutes
        s = helper.print_duration(now - 120)
        print("Result:", s)
        assert s == ' 2m ago'

        # Go 2hours ago
        s = helper.print_duration(now - 3600 * 2)
        print("Result:", s)
        assert s == ' 2h ago'

        # Go 2 days ago
        s = helper.print_duration(now - 3600 * 24 * 2)
        print("Result:", s)
        assert s == ' 2d ago'

        # Go 2 weeks ago
        s = helper.print_duration(now - 86400 * 14)
        print("Result:", s)
        assert s == ' 2w ago'

        # Go 2 months ago
        s = helper.print_duration(now - 86400 * 56)
        print("Result:", s)
        assert s == ' 2M ago'

        # Go 1 year ago
        s = helper.print_duration(now - 86400 * 365 * 2)
        print("Result:", s)
        assert s == ' 2y ago'

        # Now a mix of all of this :)
        s = helper.print_duration(
            now - 2 - 120 - 3600 * 2 - 3600 * 24 * 2 - 86400 * 14 - 86400 * 56)
        print("Result:", s)
        assert s == ' 2M 2w 2d 2h 2m 2s ago'

        # Now with a limit, because here it's just a nightmare to read
        s = helper.print_duration(
            now - 2 - 120 - 3600 * 2 - 3600 * 24 * 2 - 86400 * 14 - 86400 * 56, x_elts=2)
        print("Result:", s)
        assert s == ' 2M 2w ago'

        # Now with another limit
        s = helper.print_duration(
            now - 2 - 120 - 3600 * 2 - 3600 * 24 * 2 - 86400 * 14 - 86400 * 56, x_elts=3)
        print("Result:", s)
        assert s == ' 2M 2w 2d ago'

        # Now with another limit
        s = helper.print_duration(
            now - 2 - 120 - 3600 * 2 - 3600 * 24 * 2 - 86400 * 14 - 86400 * 56, x_elts=4)
        print("Result:", s)
        assert s == ' 2M 2w 2d 2h ago'

        # Now with another limit
        s = helper.print_duration(
            now - 2 - 120 - 3600 * 2 - 3600 * 24 * 2 - 86400 * 14 - 86400 * 56, x_elts=5)
        print("Result:", s)
        assert s == ' 2M 2w 2d 2h 2m ago'

        # Not a timestamp but a duration !
        s = helper.print_duration(2 + 120 + 3600 * 2 + 3600 * 24 * 2 + 86400 * 14 + 86400 * 56,
                                  x_elts=2, duration_only=True, ts_is_duration=True)
        print("Result:", s)
        assert s == '2M 2w'
        s = helper.print_duration(2 + 120 + 3600 * 2 + 3600 * 24 * 2 + 86400 * 14 + 86400 * 56,
                                  x_elts=6, duration_only=True, ts_is_duration=True)
        print("Result:", s)
        assert s == '2M 2w 2d 2h 2m 2s'

        # Return to the future
        # Get the 2s ago
        s = helper.print_duration(now + 2)
        print("Result:", s)
        assert s == 'Very soon'

        s = helper.print_duration(now + 4)
        print("Result:", s)
        assert s == 'in 4s'

        # Go 2 minutes
        s = helper.print_duration(now + 120)
        print("Result:", s)
        assert s == 'in 2m'

        # Go 2 hours ago
        s = helper.print_duration(now + 3600 * 2)
        print("Result:", s)
        assert s == 'in 2h'

        # Go 2 days ago
        s = helper.print_duration(now + 3600 * 24 * 2)
        print("Result:", s)
        assert s == 'in 2d'

        # Go 2 weeks ago
        s = helper.print_duration(now + 86400 * 14)
        print("Result:", s)
        assert s == 'in 2w'

        # Go 2 months ago
        s = helper.print_duration(now + 86400 * 56)
        print("Result:", s)
        assert s == 'in 2M'

        # Go 1 year ago
        s = helper.print_duration(now + 86400 * 365 * 2)
        print("Result:", s)
        assert s == 'in 2y'

        # Now a mix of all of this :)
        s = helper.print_duration(
            now + 2 + 120 + 3600 * 2 + 3600 * 24 * 2 + 86400 * 14 + 86400 * 56)
        print("Result:", s)
        assert s == 'in 2M 2w 2d 2h 2m 2s'

        # Now with a limit, because here it's just a nightmare to read
        s = helper.print_duration(
            now + 2 - 120 + 3600 * 2 + 3600 * 24 * 2 + 86400 * 14 + 86400 * 56, x_elts=2)
        print("Result:", s)
        assert s == 'in 2M 2w'


class TestOnOff(unittest2.TestCase):
    def test_print_on_off(self):
        """ Helper - on/off """

        # Call errors
        s = helper.get_on_off()
        print("Result:", s)
        assert s == '<span title="Disabled" class="fa fa-fw fa-close text-danger"></span>'

        # Status only
        s = helper.get_on_off(False)
        print("Result:", s)
        assert s == '<span title="Disabled" class="fa fa-fw fa-close text-danger"></span>'

        s = helper.get_on_off(True)
        print("Result:", s)
        assert s == '<span title="Enabled" class="fa fa-fw fa-check text-success"></span>'

        # Title
        s = helper.get_on_off(False, 'Title')
        print("Result:", s)
        assert s == '<span title="Title" class="fa fa-fw fa-close text-danger"></span>'

        s = helper.get_on_off(True, 'Title')
        print("Result:", s)
        assert s == '<span title="Title" class="fa fa-fw fa-check text-success"></span>'

        # Message
        s = helper.get_on_off(False, message='Message')
        print("Result:", s)
        assert s == '<span title="Disabled" class="fa fa-fw fa-close text-danger">Message</span>'

        s = helper.get_on_off(True, message='Message')
        print("Result:", s)
        assert s == '<span title="Enabled" class="fa fa-fw fa-check text-success">Message</span>'

        # Title and message
        s = helper.get_on_off(True, title='Title', message='Message')
        print("Result:", s)
        assert s == '<span title="Title" class="fa fa-fw fa-check text-success">Message</span>'

        # Title as array
        s = helper.get_on_off(True, title=['on', 'off'], message='Message')
        print("Result:", s)
        assert s == '<span title="on" class="fa fa-fw fa-check text-success">Message</span>'

        s = helper.get_on_off(False, title=['on', 'off'], message='Message')
        print("Result:", s)
        assert s == '<span title="off" class="fa fa-fw fa-close text-danger">Message</span>'


class TestNavigation(unittest2.TestCase):
    def test_navigation_control(self):
        """ Helper - navigation """

        # Parameters: page, total, start, count, nb_max_items
        s = helper.get_pagination_control('test', 0, 0, 0, 0)
        assert s == [('test', 0, 0, 0, False)]
        s = helper.get_pagination_control('test', 0, 0)
        # Default is 25 elements per page
        assert s == [('test', 0, 25, 0, False)]

        # first page, default pagination: 25 elements/page, 5 pages/sequence
        s = helper.get_pagination_control('test', 1, 0)
        print("Result:", s)
        # At least a global element and a local element ...
        assert len(s) == 2
        # Still the same page
        s = helper.get_pagination_control('test', 25, 0)
        print("Result:", s)
        assert len(s) == 2
        s = helper.get_pagination_control('test', 26, 0)
        print("Result:", s)
        assert len(s) == 3
        s = helper.get_pagination_control('test', 51, 0)
        print("Result:", s)
        assert len(s) == 4
        s = helper.get_pagination_control('test', 76, 0)
        print("Result:", s)
        assert len(s) == 5
        s = helper.get_pagination_control('test', 101, 0)
        print("Result:", s)
        # More than 5 pages ... must have forward controls (2 more elements than expected).
        assert len(s) == 8

        # first page, default pagination: 5 elements/page, 5 pages/sequence
        s = helper.get_pagination_control('test', 1, 0, 5)
        print("Result:", s)
        assert len(s) == 2
        s = helper.get_pagination_control('test', 11, 0, 5)
        print("Result:", s)
        assert len(s) == 4
        # More than 5 pages ... must have forward controls.
        s = helper.get_pagination_control('test', 26, 0, 5)
        print("Result:", s)
        assert len(s) == 8

        # List pages, default pagination: 5 elements/page, 5 pages/sequence
        # More than 5 pages ... must have forward controls.
        s = helper.get_pagination_control('test', 40, 0, 5)
        print("Result:", s)
        assert len(s) == 8
        s = helper.get_pagination_control('test', 40, 5, 5)
        print("Result:", s)
        assert len(s) == 8
        s = helper.get_pagination_control('test', 40, 10, 5)
        print("Result:", s)
        assert len(s) == 8
        # Current page no more in the page sequence ... must have also backward controls.
        s = helper.get_pagination_control('test', 40, 15, 5)
        print("Result:", s)
        assert len(s) == 10
        s = helper.get_pagination_control('test', 40, 20, 5)
        print("Result:", s)
        assert len(s) == 10
        # Last page is now in the page sequence ... no more forward controls.
        s = helper.get_pagination_control('test', 40, 25, 5)
        print("Result:", s)
        assert len(s) == 8
        s = helper.get_pagination_control('test', 40, 30, 5)
        print("Result:", s)
        assert len(s) == 8
        s = helper.get_pagination_control('test', 40, 35, 5)
        print("Result:", s)
        assert len(s) == 8
        s = helper.get_pagination_control('test', 40, 40, 5)
        print("Result:", s)
        assert len(s) == 8


class TestSearch(unittest2.TestCase):
    def setUp(self):
        # data_model
        self.data_model = OrderedDict([
            # Global table field
            ('_table',
             {u'page_title': u'Hosts table (%d items)', u'searchable': True, u'paginable': True,
              u'editable': True, u'visible': True, u'responsive': False, u'orderable': True,
              u'selectable': True, u'template_page_title': u'Hosts templates table (%d items)',
              u'css': u'display nowrap'}),
            # name field
            (u'name', {u'regex': True, u'required': True, u'searchable': True,
                       u'hint': u'This field is the host name', u'title': u'Host name',
                       u'editable': True, u'orderable': True, u'unique': True, u'type': u'string',
                       u'empty': False, u'templates_table': True}),
            # ...
            (u'ls_state',
             {u'hint': u'This field is the host status', u'required': True, u'editable': False,
              u'allowed': u'UP,DOWN,UNREACHABLE', u'title': u'Status', u'unique': True,
              u'type': u'string', u'empty': False}),
            (u'overall_status', {u'regex': False,
                                 u'hint': u'This field is the real host status, aggregating services status',
                                 u'title': u'Overall status', u'editable': False, u'visible': True,
                                 u'allowed': u'ok,acknowledged,in_downtime,warning,critical',
                                 u'type': u'string'}),

            (u'fake', {u'default': u'Default value', u'searchable': False, u'type': u'string',
                       u'title': u'Fake'}),

            (u'_realm',
             {u'regex': False, u'resource': u'realm', u'searchable': True, u'title': u'Realm',
              u'visible': True, u'allowed': u'inner://realms/list', u'hidden': True,
              u'type': u'objectid', u'templates_table': True}),
            (u'_is_template',
             {u'title': u'Template', u'default': False, u'visible': False, u'hidden': True,
              u'type': u'boolean', u'templates_table': True}),
            (u'_templates',
             {u'regex': False, u'resource': u'host', u'format': u'multiple', u'default': u'[]',
              u'title': u'Templates', u'visible': False, u'content_type': u'objectid',
              u'allowed': u'inner://hosts/templates/list', u'hidden': True, u'type': u'list',
              u'templates_table': True}),

            (u'_template_fields',
             {u'format': u'multiple', u'default': u'[]', u'title': u'Template fields',
              u'visible': False, u'content_type': u'string', u'hidden': True, u'type': u'list'}),
            (u'definition_order',
             {u'title': u'Definition order', u'default': u'100', u'editable': True,
              u'visible': False, u'orderable': True, u'hidden': True, u'type': u'integer',
              u'templates_table': True}),
            (u'tags',
             {u'regex': False, u'format': u'multiple', u'default': u'[]', u'title': u'Tags',
              u'content_type': u'string', u'allowed': u'inner://hosts/templates/list',
              u'type': u'list'}),
            (u'alias', {u'hidden': True, u'type': u'string', u'title': u'Host alias'}),
            (u'business_impact', {u'hint': u'Host business impact level', u'default': u'2',
                                  u'title': u'Business impact', u'allowed_4': u'Very important',
                                  u'allowed_5': u'Business critical', u'allowed_0': u'None',
                                  u'allowed_1': u'Low', u'allowed_2': u'Normal',
                                  u'allowed': u'0,1,2,3,4,5', u'type': u'integer',
                                  u'allowed_3': u'Important'}),

            # Some more ... removed for test purpose.

            (u'ls_last_check', {u'editable': False, u'type': u'datetime', u'title': u'Last check'}),
            (u'ls_state_type', {u'editable': False, u'allowed': u'HARD,SOFT', u'type': u'string',
                                u'title': u'State type'}),
            (u'ls_state_id',
             {u'title': u'State', u'default': u'0', u'hint': u'Choose the host state',
              u'allowed_3': u'Unreachable', u'editable': False, u'allowed_0': u'Up',
              u'allowed_1': u'Down (1)', u'allowed_2': u'Down (2)', u'allowed': u'0,1,2,3',
              u'type': u'integer'}),
            (u'ls_acknowledged',
             {u'editable': False, u'type': u'boolean', u'title': u'Acknowledged'}),
            (u'ls_downtimed',
             {u'editable': False, u'type': u'boolean', u'title': u'In scheduled downtime'}),
            (u'ls_output', {u'default': u'Output from WebUI', u'editable': False,
                            u'hint': u'enter the desired check output', u'type': u'string',
                            u'title': u'Output'}),
            (u'ls_long_output', {u'editable': False, u'type': u'string', u'title': u'Long output'}),
            (u'ls_perf_data',
             {u'editable': False, u'type': u'string', u'title': u'Performance data'}),
            (u'ls_current_attempt',
             {u'editable': False, u'type': u'integer', u'title': u'Current attempt'}),
            (u'ls_max_attempts',
             {u'editable': False, u'type': u'integer', u'title': u'Max attempts'}),
            (u'ls_next_check', {u'editable': False, u'type': u'integer', u'title': u'Next check'}),
            (u'ls_last_state_changed',
             {u'editable': False, u'type': u'datetime', u'title': u'Last state changed'}),
            (u'ls_last_state',
             {u'editable': False, u'allowed': u'OK,WARNING,CRITICAL,UNKNOWN,UP,DOWN,UNREACHABLE',
              u'type': u'string', u'title': u'Last state'}),
            (u'ls_last_state_type',
             {u'editable': False, u'allowed': u'HARD,SOFT', u'type': u'string',
              u'title': u'Last state type'}),
            (u'ls_latency', {u'editable': False, u'type': u'float', u'title': u'Latency'}),
            (u'ls_execution_time',
             {u'editable': False, u'type': u'float', u'title': u'Execution time'})
        ])

    def test_decode_search_simple(self):
        """Helper - decode_search, simple search"""

        # Empty search
        s = helper.decode_search("", self.data_model)
        print("Result:", s)
        assert s == {}

        # Unknown column search
        s = helper.decode_search("status:search", self.data_model)
        print("Result:", s)
        # A warning log is emitted and result is empty
        assert s == {}

        # Non searchable column search
        s = helper.decode_search("fake:search", self.data_model)
        print("Result:", s)
        # A warning log is emitted and result is empty
        assert s == {}

        # Search a default field (eg. name)
        s = helper.decode_search("test", self.data_model)
        print("Result:", s)
        # Search name with a regex pattern
        assert s == {'name': {'$regex': '.*test.*'}}

        # Search and specify field (yet another name) with regex
        s = helper.decode_search("name:test", self.data_model)
        print("Result:", s)
        # Search name with a regex pattern
        assert s == {'name': {'$regex': '.*test.*'}}

        # Search and specify field (yet another name) without regex
        s = helper.decode_search("overall_status:test", self.data_model)
        print("Result:", s)
        # Search name with no regex pattern
        assert s == {'overall_status': 'test'}

    def test_decode_search_type(self):
        """Helper - decode_search, typed fields search"""

        # Search a string field
        s = helper.decode_search("name:test", self.data_model)
        # Search field with a regex pattern
        assert s == {'name': {'$regex': '.*test.*'}}

        # Search an integer field
        s = helper.decode_search("name:test", self.data_model)
        # Search field with a regex pattern
        assert s == {'name': {'$regex': '.*test.*'}}

        # Search a boolean field
        s = helper.decode_search("_is_template:true", self.data_model)
        assert s == {'_is_template': True}
        s = helper.decode_search("_is_template:1", self.data_model)
        assert s == {'_is_template': True}
        s = helper.decode_search("_is_template:yes", self.data_model)
        assert s == {'_is_template': True}

        s = helper.decode_search("_is_template:false", self.data_model)
        assert s == {'_is_template': False}
        s = helper.decode_search("_is_template:0", self.data_model)
        assert s == {'_is_template': False}
        s = helper.decode_search("_is_template:no", self.data_model)
        assert s == {'_is_template': False}

        # Search an integer field
        s = helper.decode_search("definition_order:test", self.data_model)
        # A warning log is emitted and result is empty
        assert s == {}
        s = helper.decode_search("definition_order:1524.12", self.data_model)
        # A warning log is emitted and result is empty
        assert s == {}
        s = helper.decode_search("definition_order:1", self.data_model)
        assert s == {'definition_order': 1}
        s = helper.decode_search("definition_order:1524", self.data_model)
        assert s == {'definition_order': 1524}

        # Search a float field
        s = helper.decode_search("ls_latency:test", self.data_model)
        # A warning log is emitted and result is empty
        assert s == {}
        s = helper.decode_search("ls_latency:1", self.data_model)
        assert s == {'ls_latency': 1.0}
        s = helper.decode_search("ls_latency:1524.12", self.data_model)
        assert s == {'ls_latency': 1524.12}

        # todo: Missing some tests for objectid, list, ... fields ...

    def test_decode_search_specific(self):
        """Helper - decode_search, specific (livestate, bi, ...) field search"""

        # Search a live state field (eg. ls_output) - can omit the ls_ prefix for the field
        s = helper.decode_search("ls_output:test", self.data_model)
        # Search field with a regex pattern
        assert s == {'ls_output': {'$regex': '.*test.*'}}
        s = helper.decode_search("output:test", self.data_model)
        # Search field with a regex pattern
        assert s == {'ls_output': {'$regex': '.*test.*'}}

        # Search business impact field - can use bi rather than business_impact
        s = helper.decode_search("business_impact:0", self.data_model)
        # Search field with a regex pattern
        assert s == {'business_impact': 0}
        s = helper.decode_search("bi:0", self.data_model)
        # Search field with a regex pattern
        assert s == {'business_impact': 0}

        # Search overall state field - can use is/isnot with a list of allowed values
        s = helper.decode_search("is:ok", self.data_model)
        assert s == {'_overall_state_id': 0}
        s = helper.decode_search("is:acknowledged", self.data_model)
        assert s == {'_overall_state_id': 1}
        s = helper.decode_search("is:in_downtime", self.data_model)
        assert s == {'_overall_state_id': 2}
        s = helper.decode_search("is:warning", self.data_model)
        assert s == {'_overall_state_id': 3}
        s = helper.decode_search("is:critical", self.data_model)
        assert s == {'_overall_state_id': 4}

        s = helper.decode_search("isnot:ok", self.data_model)
        assert s == {'_overall_state_id': {'$ne': 0}}
        s = helper.decode_search("isnot:acknowledged", self.data_model)
        assert s == {'_overall_state_id': {'$ne': 1}}
        s = helper.decode_search("isnot:in_downtime", self.data_model)
        assert s == {'_overall_state_id': {'$ne': 2}}
        s = helper.decode_search("isnot:warning", self.data_model)
        assert s == {'_overall_state_id': {'$ne': 3}}
        s = helper.decode_search("isnot:critical", self.data_model)
        assert s == {'_overall_state_id': {'$ne': 4}}

        s = helper.decode_search("is:unallowed", self.data_model)
        # A warning log is emitted and result is empty
        assert s == {}
        s = helper.decode_search("isnot:unallowed", self.data_model)
        # A warning log is emitted and result is empty
        assert s == {}

    def test_decode_search_not(self):
        """Helper - decode_search, not search"""

        # Search field that do not contain a value
        s = helper.decode_search("name:!test", self.data_model)
        # Search name with a regex pattern
        assert s == {'name': {'$regex': '/^((?!test).)*$/'}}

        # Search and specify field (yet another name) without regex
        s = helper.decode_search("overall_status:!test", self.data_model)
        # Search name with no regex pattern
        assert s == {'overall_status': {'$ne': 'test'}}

    def test_decode_search_complex(self):
        """Helper - decode_search, complex search"""

        # Search for several values in name
        s = helper.decode_search("test test2", self.data_model)
        # Search several values with a regex pattern
        assert s == {'$or': [{'name': {'$regex': '.*test.*'}}, {'name': {'$regex': '.*test2.*'}}]}
        # Search for several values in name
        s = helper.decode_search("name:test name:test2", self.data_model)
        # Search several values with a regex pattern
        assert s == {'$or': [{'name': {'$regex': '.*test.*'}}, {'name': {'$regex': '.*test2.*'}}]}

        # Search for several values in live state
        s = helper.decode_search("is:ok is:warning", self.data_model)
        # Search several values in a list
        assert s == {'_overall_state_id': {'$in': [0, 3]}}
        # Search for several values in name
        s = helper.decode_search("is:ok is:warning isnot:critical", self.data_model)
        # Search several values with a regex pattern
        assert s == {'_overall_state_id': {'$in': [0, 3], '$nin': [4]}}


class TestBI(unittest2.TestCase):
    def test_print_business_impact(self):
        """ Helper - business impact """

        # Invalid values
        s = helper.get_html_business_impact(-1, icon=True, text=False)
        print("Result:", s)
        assert s == 'n/a - value'
        s = helper.get_html_business_impact(6, icon=False, text=True)
        print("Result:", s)
        assert s == 'n/a - value'
        s = helper.get_html_business_impact(0, icon=False, text=False)
        print("Result:", s)
        assert s == 'n/a - parameters'

        # Default with stars
        s = helper.get_html_business_impact(0, icon=True, text=False)
        print("Result:", s)
        assert s == '<span class="text-default"></span><span>&nbsp;</span>'  # No star
        s = helper.get_html_business_impact(1, icon=True, text=False)
        print("Result:", s)
        assert s == '<span class="text-default"><span class="fa fa-star"></span></span><span>&nbsp;</span>'  # 1 star
        s = helper.get_html_business_impact(2, icon=True, text=False)
        print("Result:", s)
        assert s == '<span class="text-default"><span class="fa fa-star"></span><span class="fa fa-star"></span></span><span>&nbsp;</span>'  # 2 stars
        s = helper.get_html_business_impact(3, icon=True, text=False)
        print("Result:", s)
        assert s == '<span class="text-default"><span class="fa fa-star"></span><span class="fa fa-star"></span><span class="fa fa-star"></span></span><span>&nbsp;</span>'# 3 stars
        s = helper.get_html_business_impact(4, icon=True, text=False)
        print("Result:", s)
        assert s == '<span class="text-default"><span class="fa fa-star"></span><span class="fa fa-star"></span><span class="fa fa-star"></span><span class="fa fa-star"></span></span><span>&nbsp;</span>'# 4 stars
        s = helper.get_html_business_impact(5, icon=True, text=False)
        print("Result:", s)
        assert s == '<span class="text-default"><span class="fa fa-star"></span><span class="fa fa-star"></span><span class="fa fa-star"></span><span class="fa fa-star"></span><span class="fa fa-star"></span></span><span>&nbsp;</span>'# 5 stars

        # Default with text
        s = helper.get_html_business_impact(0, icon=False, text=True)
        print("Result:", s)
        assert s == 'None'
        s = helper.get_html_business_impact(1, icon=False, text=True)
        print("Result:", s)
        assert s == 'Low'
        s = helper.get_html_business_impact(2, icon=False, text=True)
        print("Result:", s)
        assert s == 'Normal'
        s = helper.get_html_business_impact(3, icon=False, text=True)
        print("Result:", s)
        assert s == 'Important'
        s = helper.get_html_business_impact(4, icon=False, text=True)
        print("Result:", s)
        assert s == 'Very important'
        s = helper.get_html_business_impact(5, icon=False, text=True)
        print("Result:", s)
        assert s == 'Business critical'

        # Default with icon and text
        s = helper.get_html_business_impact(0, icon=True, text=True)
        print("Result:", s)
        assert s == '<span class="text-default"></span><span>&nbsp;None</span>'
        s = helper.get_html_business_impact(1, icon=True, text=True)
        print("Result:", s)
        assert s == '<span class="text-default"><span class="fa fa-star"></span></span><span>&nbsp;Low</span>'
        s = helper.get_html_business_impact(2, icon=True, text=True)
        print("Result:", s)
        assert s == '<span class="text-default"><span class="fa fa-star"></span><span class="fa fa-star"></span></span><span>&nbsp;Normal</span>'
        s = helper.get_html_business_impact(3, icon=True, text=True)
        print("Result:", s)
        assert s == '<span class="text-default"><span class="fa fa-star"></span><span class="fa fa-star"></span><span class="fa fa-star"></span></span><span>&nbsp;Important</span>'
        s = helper.get_html_business_impact(4, icon=True, text=True)
        print("Result:", s)
        assert s == '<span class="text-default"><span class="fa fa-star"></span><span class="fa fa-star"></span><span class="fa fa-star"></span><span class="fa fa-star"></span></span><span>&nbsp;Very important</span>'
        s = helper.get_html_business_impact(5, icon=True, text=True)
        print("Result:", s)
        assert s == '<span class="text-default"><span class="fa fa-star"></span><span class="fa fa-star"></span><span class="fa fa-star"></span><span class="fa fa-star"></span><span class="fa fa-star"></span></span><span>&nbsp;Business critical</span>'


class TestTP(unittest2.TestCase):
    def test_print_timeperiod(self):
        """ Helper - timeperiod """

        # Invalid values
        s = helper.get_html_timeperiod(None)
        print("Result:", s)
        assert s == ''

        tp = TimePeriod(
            {'_updated': 1465548247, '_total': 5, '_type': 'timeperiod', 'definition_order': 100,
             '_default_date': 0, '_comment': '', 'is_active': True,
             '_name': u'All time default 24x7',
             'dateranges': [{u'monday': u'00:00-24:00'}, {u'tuesday': u'00:00-24:00'},
                            {u'wednesday': u'00:00-24:00'}, {u'thursday': u'00:00-24:00'},
                            {u'friday': u'00:00-24:00'}, {u'saturday': u'00:00-24:00'},
                            {u'sunday': u'00:00-24:00'}],
             '_alias': u'',
             '_links': {
                u'self': {u'href': u'timeperiod/575a7dd74c988c170e857988', u'title': u'Timeperiod'}
             },
             '_created': 1465548247, 'exclude': [],
             '_status': 'unknown',
             '_id': u'575a7dd74c988c170e857988',
             '_etag': u'e9f5fb031b79f9abdc42f44d413f8220c321767b', 'imported_from': u''})
        s = helper.get_html_timeperiod(tp)
        print("Result:", s)
        assert s == '<button class="btn btn-default btn-xs btn-block" type="button" data-toggle="collapse" data-target="#html_tp_575a7dd74c988c170e857988" aria-expanded="false" aria-controls="html_tp_575a7dd74c988c170e857988">All time default 24x7</button><div class="collapse" id="html_tp_575a7dd74c988c170e857988"><div class="well"><ul class="list-group"><li class="list-group-item"><span class="fa fa-hourglass">&nbsp;monday - 00:00-24:00</li><li class="list-group-item"><span class="fa fa-hourglass">&nbsp;tuesday - 00:00-24:00</li><li class="list-group-item"><span class="fa fa-hourglass">&nbsp;wednesday - 00:00-24:00</li><li class="list-group-item"><span class="fa fa-hourglass">&nbsp;thursday - 00:00-24:00</li><li class="list-group-item"><span class="fa fa-hourglass">&nbsp;friday - 00:00-24:00</li><li class="list-group-item"><span class="fa fa-hourglass">&nbsp;saturday - 00:00-24:00</li><li class="list-group-item"><span class="fa fa-hourglass">&nbsp;sunday - 00:00-24:00</li></ul></div></div>'


class TestHtmlList(unittest2.TestCase):
    def test_html_list(self):
        """ Helper - HTML list """

        self.maxDiff = None

        # Empty list
        s = helper.get_html_item_list('id', 'type', [])
        print("Result:", s)
        assert s == ''

        # Default
        s = helper.get_html_item_list('id', 'type', ['1', '2'])
        print("Result:", s)
        assert s == \
                         '<button class="btn btn-xs btn-raised" ' \
                         'data-toggle="collapse" data-target="#list_type_id" aria-expanded="false">' \
                         'type' \
                         '</button>' \
                         '<div class="collapse" id="list_type_id">' \
                         '<ul class="list-group">' \
                         '<li class="list-group-item"><span class="fa fa-check">&nbsp;1</span></li>' \
                         '<li class="list-group-item"><span class="fa fa-check">&nbsp;2</span></li>' \
                         '</ul>' \
                         '</div>'

        # Default
        s = helper.get_html_item_list('id', 'type', ['1', '2'], 'title')
        print("Result:", s)
        assert s == \
                         '<button class="btn btn-xs btn-raised" ' \
                         'data-toggle="collapse" data-target="#list_type_id" aria-expanded="false">' \
                         'title' \
                         '</button>' \
                         '<div class="collapse" id="list_type_id">' \
                         '<ul class="list-group">' \
                         '<li class="list-group-item"><span class="fa fa-check">&nbsp;1</span></li>' \
                         '<li class="list-group-item"><span class="fa fa-check">&nbsp;2</span></li>' \
                         '</ul>' \
                         '</div>'


class TestObjectUrls(unittest2.TestCase):
    def test_notes_url(self):
        """ Helper - get_element_notes_url """

        host = Host({
            '_id': u'575a7dd74c988c170e857988',
            '_status': 'OK',
            'name': 'test',
            '_created': 1470995433,
            '_updated': 1470995450,
        })
        assert host

        html_notes = Helper.get_element_notes_url(host, default_title="Note", default_icon="tag")
        # Empty list when no notes exist
        assert html_notes == []

        host = Host({
            '_id': u'575a7dd74c988c170e857988',
            '_status': 'OK',
            'name': 'test',
            '_created': 1470995433,
            '_updated': 1470995450,
            'notes': u'note simple|Libellé::note avec un libellé|KB1023,,tag::<strong>Lorem ipsum dolor sit amet</strong>, consectetur adipiscing elit. Proin et leo gravida, lobortis nunc nec, imperdiet odio. Vivamus quam velit, scelerisque nec egestas et, semper ut massa. Vestibulum id tincidunt lacus. Ut in arcu at ex egestas vestibulum eu non sapien. Nulla facilisi. Aliquam non blandit tellus, non luctus tortor. Mauris tortor libero, egestas quis rhoncus in, sollicitudin et tortor.|note simple|Tag::tagged note ...',
            'notes_url': 'http://www.my-KB.fr?host=$HOSTADDRESS$|http://www.my-KB.fr?host=$HOSTNAME$',
        })
        assert host

        html_notes = Helper.get_element_notes_url(host, default_title="Note", default_icon="tag")
        # 5 declared notes, but only 2 URLs
        # Expecting 5 links
        assert html_notes == [
            u'<a href="http://www.my-KB.fr?host=$HOSTADDRESS$" target="_blank" role="button" data-toggle="popover urls" data-container="body" data-html="true" data-content="note simple" data-trigger="hover focus" data-placement="bottom"><span class="fa fa-tag"></span>&nbsp;Note</a>',
            u'<a href="http://www.my-KB.fr?host=$HOSTNAME$" target="_blank" role="button" data-toggle="popover urls" data-container="body" data-html="true" data-content="note avec un libellé" data-trigger="hover focus" data-placement="bottom"><span class="fa fa-tag"></span>&nbsp;Libellé</a>',
            u'<a href="#" role="button" data-toggle="popover urls" data-container="body" data-html="true" data-content="<strong>Lorem ipsum dolor sit amet</strong>, consectetur adipiscing elit. Proin et leo gravida, lobortis nunc nec, imperdiet odio. Vivamus quam velit, scelerisque nec egestas et, semper ut massa. Vestibulum id tincidunt lacus. Ut in arcu at ex egestas vestibulum eu non sapien. Nulla facilisi. Aliquam non blandit tellus, non luctus tortor. Mauris tortor libero, egestas quis rhoncus in, sollicitudin et tortor." data-trigger="hover focus" data-placement="bottom"><span class="fa fa-tag"></span>&nbsp;KB1023</span></a>',
            u'<a href="#" role="button" data-toggle="popover urls" data-container="body" data-html="true" data-content="note simple" data-trigger="hover focus" data-placement="bottom"><span class="fa fa-tag"></span>&nbsp;Note</span></a>',
            u'<a href="#" role="button" data-toggle="popover urls" data-container="body" data-html="true" data-content="tagged note ..." data-trigger="hover focus" data-placement="bottom"><span class="fa fa-tag"></span>&nbsp;Tag</span></a>'
        ]

    def test_actions_url(self):
        """ Helper - get_element_notes_url """

        host = Host({
            '_id': u'575a7dd74c988c170e857988',
            '_status': 'OK',
            'name': 'test',
            '_created': 1470995433,
            '_updated': 1470995450,
        })
        assert host

        html_actions = Helper.get_element_actions_url(host, default_title="Url", default_icon="globe")
        assert html_actions == []

        host = Host({
            '_id': u'575a7dd74c988c170e857988',
            '_status': 'OK',
            'name': 'test',
            '_created': 1470995433,
            '_updated': 1470995450,
            'action_url': 'http://www.google.fr|url1::http://www.google.fr|My KB,,tag::http://www.my-KB.fr?host=$HOSTNAME$|Last URL,,tag::<strong>Lorem ipsum dolor sit amet</strong>, consectetur adipiscing elit. Proin et leo gravida, lobortis nunc nec, imperdiet odio. Vivamus quam velit, scelerisque nec egestas et, semper ut massa.,,http://www.my-KB.fr?host=$HOSTADDRESS$',
        })
        assert host

        html_actions = Helper.get_element_actions_url(host, default_title="Url", default_icon="globe")
        # 3 declared actions, with different parameters
        # Expecting 3 links
        assert html_actions == [
            '<a href="http://www.google.fr" target="_blank" role="button" data-toggle="popover urls" data-container="body" data-html="true" data-content="No description provided" data-trigger="hover focus" data-placement="bottom"><span class="fa fa-globe"></span>&nbsp;Url</a>', '<a href="http://www.google.fr" target="_blank" role="button" data-toggle="popover urls" data-container="body" data-html="true" data-content="No description provided" data-trigger="hover focus" data-placement="bottom"><span class="fa fa-globe"></span>&nbsp;url1</a>',
            '<a href="http://www.my-KB.fr?host=$HOSTNAME$" target="_blank" role="button" data-toggle="popover urls" data-container="body" data-html="true" data-content="No description provided" data-trigger="hover focus" data-placement="bottom"><span class="fa fa-tag"></span>&nbsp;My KB</a>',
            '<a href="http://www.my-KB.fr?host=$HOSTADDRESS$" target="_blank" role="button" data-toggle="popover urls" data-container="body" data-html="true" data-content="<strong>Lorem ipsum dolor sit amet</strong>, consectetur adipiscing elit. Proin et leo gravida, lobortis nunc nec, imperdiet odio. Vivamus quam velit, scelerisque nec egestas et, semper ut massa." data-trigger="hover focus" data-placement="bottom"><span class="fa fa-tag"></span>&nbsp;Last URL</a>'
        ]
