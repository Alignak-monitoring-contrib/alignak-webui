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

import time

import unittest2

import alignak_webui.app

# from alignak_webui import set_app_config
from alignak_webui.objects.item_timeperiod import TimePeriod
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
    @unittest2.skip("Temporarily disabled ...")
    def test_search(self):
        """ Helper - decode search """

        s = helper.decode_search("")
        print("Result:", s)
        assert s == {}

        s = helper.decode_search("status:active")
        print("Result:", s)
        assert s == {'status': 'active'}

        s = helper.decode_search("status:active name:name")
        print("Result:", s)
        assert s == {'status': 'active', 'name': 'name'}

        s = helper.decode_search("status:!active")
        print("Result:", s)
        assert s == {'$ne': {'status': 'active'}}

        s = helper.decode_search("state_id:1|2|3")
        print("Result:", s)
        assert s == {'$in': {'state_id': ['1', '2', '3']}}


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
