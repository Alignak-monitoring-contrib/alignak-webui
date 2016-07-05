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

import os
import json
import time
import shlex
import unittest2
import subprocess
from calendar import timegm
from datetime import datetime, timedelta

from nose import with_setup
from nose.tools import *

# Test environment variables
os.environ['TEST_WEBUI'] = '1'
os.environ['WEBUI_DEBUG'] = '1'
os.environ['TEST_WEBUI_CFG'] = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'settings.cfg')
print "Configuration file", os.environ['TEST_WEBUI_CFG']

import alignak_webui.app
from alignak_webui import webapp
from alignak_webui.objects.datamanager import DataManager
import alignak_webui.utils.datatable

# from logging import getLogger, DEBUG, INFO
# loggerDm = getLogger('alignak_webui.objects.datamanager')
# loggerDm.setLevel(DEBUG)

import bottle
from bottle import BaseTemplate, TEMPLATE_PATH

from webtest import TestApp

pid = None
backend_address = "http://127.0.0.1:5000/"

def setup_module(module):
    print ("")
    print ("start alignak backend")

    global pid
    global backend_address

    if backend_address == "http://127.0.0.1:5000/":
        # Set test mode for applications backend
        os.environ['TEST_ALIGNAK_BACKEND'] = '1'
        os.environ['TEST_ALIGNAK_BACKEND_DB'] = 'alignak-backend'

        # Delete used mongo DBs
        exit_code = subprocess.call(
            shlex.split('mongo %s --eval "db.dropDatabase()"' % os.environ['TEST_ALIGNAK_BACKEND_DB'])
        )
        assert exit_code == 0
        time.sleep(1)

        # No console output for the applications backend ...
        pid = subprocess.Popen(
            shlex.split('alignak_backend')
        )
        print ("PID: %s" % pid)
        time.sleep(1)

        print ("")
        print ("populate backend content")
        exit_code = subprocess.call(
            shlex.split('alignak_backend_import --delete cfg/default/_main.cfg')
        )
        assert exit_code == 0


def teardown_module(module):
    print ("")
    print ("stop applications backend")

    if backend_address == "http://127.0.0.1:5000/":
        global pid
        pid.kill()


class tests_0_external(unittest2.TestCase):

    def setUp(self):
        print ""
        print "setting up ..."

        # Test application
        self.app = TestApp(
            webapp
        )

    def tearDown(self):
        print ""
        print "tearing down ..."

    def test_1_1_refused(self):
        print ''
        print 'refused external access'

        # Refused - no credentials
        response = self.app.get(
            '/external/widget/hosts_table?widget_id=test',
            status=401
        )
        print response
        response.mustcontain('<div><h1>External access denied.</h1><p>To embed an Alignak WebUI widget or table, you must provide credentials.<br>Log into the Alignak WebUI with your credentials, or make a request with a Basic-Authentication allowing access to Alignak backend.</p></div>')

        # Refused - bad credentials
        self.app.authorization = ('Basic', ('admin', 'fake'))
        response = self.app.get(
            '/external/widget/hosts_table?widget_id=test',
            status=401
        )
        response.mustcontain('<div><h1>External access denied.</h1><p>The provided credentials do not grant you access to Alignak WebUI.<br>Please provide proper credentials.</p></div>')

        # Refused - bad type
        self.app.authorization = ('Basic', ('admin', 'admin'))
        response = self.app.get(
            '/external/unknown/hosts_table?widget_id=test',
            status=409
        )
        response.mustcontain('<div><h1>Unknown required type: unknown.</h1><p>The required type is unknwown</p></div>')

        # Refused - unknown widget
        self.app.authorization = ('Basic', ('admin', 'admin'))
        response = self.app.get(
            '/external/widget/unknown?widget_id=test',
            status=409
        )
        response.mustcontain('<div><h1>Unknown required widget: unknown.</h1><p>The required widget is not available.</p></div>')

    def test_1_2_allowed_widgets(self):
        print ''
        print 'allowed widgets external access'

        # Allowed - default widgets parameters: widget_id and widget_template
        # Add parameter page to get a whole page: js, css, ...
        self.app.authorization = ('Basic', ('admin', 'admin'))
        response = self.app.get(
            '/external/widget/hosts_table?page&widget_id=hosts_table'
        )
        response.mustcontain(
            '<!DOCTYPE html>',
            '<html lang="en">',
            '<body>',
            '<section>',
            '<div id="wd_panel_hosts_table" class="panel panel-default alignak_webui_widget embedded">',
            '</section>',
            '</body>'
        )

        # Allowed - default widgets parameters: widget_id
        # No parameter page: only the widget
        self.app.authorization = ('Basic', ('admin', 'admin'))
        response = self.app.get(
            '/external/widget/hosts_table?widget_id=hosts_table'
        )
        response.mustcontain(
            '<div id="wd_panel_hosts_table" class="panel panel-default alignak_webui_widget embedded">',
            '<small>Graphite on VM</small>',
            '<small>check_host_alive</small>'
        )

        # Allowed - default widgets parameters: widget_id
        # No parameter page: only the widget
        # With links, but empty, so no links!
        self.app.authorization = ('Basic', ('admin', 'admin'))
        response = self.app.get(
            '/external/widget/hosts_table?links&widget_id=hosts_table'
        )
        response.mustcontain(
            '<div id="wd_panel_hosts_table" class="panel panel-default alignak_webui_widget embedded">',
            'Graphite on VM</small>',
            'check_host_alive</small>'
        )

        # Allowed - default widgets parameters: widget_id
        # No parameter page: only the widget
        # With links, not empty so URL are prefixed ...
        self.app.authorization = ('Basic', ('admin', 'admin'))
        response = self.app.get(
            '/external/widget/hosts_table?links=http://test&widget_id=hosts_table'
        )
        response.mustcontain(
            '<div id="wd_panel_hosts_table" class="panel panel-default alignak_webui_widget embedded">',
            '<a href="http://test/host/',
            'Graphite on VM</a></small>',
            'check_host_alive</a></small>'
        )

        # Allowed - default widgets parameters: widget_id
        # No parameter page: only the widget
        # With links
        self.app.authorization = ('Basic', ('admin', 'admin'))
        response = self.app.get(
            '/external/widget/hosts_graph?links&widget_id=hosts_graph'
        )
        response.mustcontain(
            '<div id="wd_panel_hosts_graph" class="panel panel-default alignak_webui_widget embedded">',
            '<div id="pc_hosts_hosts_graph">'
        )

    def test_1_3_allowed_tables(self):
        print ''
        print 'allowed tables external access'

        # Allowed - default table parameters: none
        # Add parameter page to get a whole page: js, css, ...
        print "Whole page..."
        self.app.authorization = ('Basic', ('admin', 'admin'))
        response = self.app.get(
            '/external/table/hosts_table?page'
        )
        response.mustcontain(
            '<!DOCTYPE html>',
            '<html lang="en">',
            '<body>',
            '<section>',
            '<div id="host_table" class="alignak_webui_table embedded">',
            '</section>',
            '</body>'
        )

        # Allowed - default table parameters: none
        # No parameter page: only the widget
        print "Only div..."
        self.app.authorization = ('Basic', ('admin', 'admin'))
        response = self.app.get(
            '/external/table/hosts_table'
        )
        response.mustcontain(
            '<div id="host_table" class="alignak_webui_table embedded">',
            '<th data-name="#" data-type="string"></th>',
            '<th data-name="name" data-type="string">Host name</th>',
            '<th data-name="definition_order" data-type="integer">Definition order</th>',
            '<th data-name="alias" data-type="string">Host alias</th>'
        )

        # Allowed - default table parameters: none
        # No parameter page: only the widget
        # With links, but empty
        print "Only div with links..."
        self.app.authorization = ('Basic', ('admin', 'admin'))
        response = self.app.get(
            '/external/table/hosts_table?links'
        )
        response.mustcontain(
            '<div id="host_table" class="alignak_webui_table embedded">',
            '<th data-name="#" data-type="string"></th>',
            '<th data-name="name" data-type="string">Host name</th>',
            '<th data-name="definition_order" data-type="integer">Definition order</th>',
            '<th data-name="alias" data-type="string">Host alias</th>'
        )

        # Allowed - default table parameters: none
        # No parameter page: only the widget
        # With links, not empty so URL are prefixed ...
        print "Only div with links..."
        self.app.authorization = ('Basic', ('admin', 'admin'))
        response = self.app.get(
            '/external/table/hosts_table?links=http://test'
        )
        response.mustcontain(
            '<div id="host_table" class="alignak_webui_table embedded">',
            '<th data-name="#" data-type="string"></th>',
            '<th data-name="name" data-type="string">Host name</th>',
            '<th data-name="definition_order" data-type="integer">Definition order</th>',
            '<th data-name="alias" data-type="string">Host alias</th>',
            '"url": "http://localhost:80/external/table/hosts_table/host_table_data",'
        )

    def test_0_1_4_host_widgets(self):
        print ''
        print 'allowed host widgets external access'

        # Log in to get Data manager in the session
        response = self.app.get('/login')
        response.mustcontain('<form role="form" method="post" action="/login">')

        print 'login accepted - go to home page'
        response = self.app.post('/login', {'username': 'admin', 'password': 'admin'})
        # Redirected twice: /login -> / -> /dashboard !
        redirected_response = response.follow()
        redirected_response = redirected_response.follow()
        redirected_response.mustcontain('<div id="dashboard">')

        session = redirected_response.request.environ['beaker.session']
        assert 'current_user' in session and session['current_user']
        assert session['current_user'].get_username() == 'admin'
        datamgr = session['datamanager']

        # Get host, user and realm in the backend
        host = datamgr.get_host({'where': {'name': 'webui'}})

        # Get external host widget - no widget identifier
        self.app.authorization = ('Basic', ('admin', 'admin'))
        response = self.app.get(
            '/external/host/%s' % host.id,
            status=409
        )
        response.mustcontain('<div><h1>Missing host widget name.</h1><p>You must provide a widget name</p></div>')

        # Get external host widget - unknown widget
        self.app.authorization = ('Basic', ('admin', 'admin'))
        response = self.app.get(
            '/external/host/%s/unknown' % host.id,
            status=409
        )
        response.mustcontain('<div><h1>Unknown required widget: unknown.</h1><p>The required widget is not available.</p></div>')

        ## Host information
        # Get external host widget
        self.app.authorization = ('Basic', ('admin', 'admin'))
        response = self.app.get(
            '/external/host/%s/information?page' % host.id
        )
        response.mustcontain(
            '<!DOCTYPE html>',
            '<html lang="en">',
            '<body>',
            '<section>',
            '<div id="wd_panel_information" class="panel panel-default alignak_webui_widget embedded">',
            '<!-- Hosts information widget -->',
            '</section>',
            '</body>'
        )

        # Get external host widget, no page parameter
        self.app.authorization = ('Basic', ('admin', 'admin'))
        response = self.app.get(
            '/external/host/%s/information' % host.id
        )
        response.mustcontain(
            '<div id="wd_panel_information" class="panel panel-default alignak_webui_widget embedded">',
            '<!-- Hosts information widget -->',
        )

        ## Host configuration
        # Get external host widget
        self.app.authorization = ('Basic', ('admin', 'admin'))
        response = self.app.get(
            '/external/host/%s/configuration?page' % host.id
        )
        response.mustcontain(
            '<!DOCTYPE html>',
            '<html lang="en">',
            '<body>',
            '<section>',
            '<div id="wd_panel_configuration" class="panel panel-default alignak_webui_widget embedded">',
            '<!-- Hosts configuration widget -->',
            '</section>',
            '</body>'
        )

        # Get external host widget, no page parameter
        self.app.authorization = ('Basic', ('admin', 'admin'))
        response = self.app.get(
            '/external/host/%s/configuration' % host.id
        )
        response.mustcontain(
            '<div id="wd_panel_configuration" class="panel panel-default alignak_webui_widget embedded">',
            '<!-- Hosts configuration widget -->',
        )

        ## Host metrics
        # Get external host widget
        self.app.authorization = ('Basic', ('admin', 'admin'))
        response = self.app.get(
            '/external/host/%s/metrics?page' % host.id
        )
        response.mustcontain(
            '<!DOCTYPE html>',
            '<html lang="en">',
            '<body>',
            '<section>',
            '<div id="wd_panel_metrics" class="panel panel-default alignak_webui_widget embedded">',
            '<!-- Hosts metrics widget -->',
            '</section>',
            '</body>'
        )

        # Get external host widget, no page parameter
        self.app.authorization = ('Basic', ('admin', 'admin'))
        response = self.app.get(
            '/external/host/%s/metrics' % host.id
        )
        response.mustcontain(
            '<div id="wd_panel_metrics" class="panel panel-default alignak_webui_widget embedded">',
            '<!-- Hosts metrics widget -->',
        )

        ## Host timeline
        # Get external host widget
        self.app.authorization = ('Basic', ('admin', 'admin'))
        response = self.app.get(
            '/external/host/%s/timeline?page' % host.id
        )
        response.mustcontain(
            '<!DOCTYPE html>',
            '<html lang="en">',
            '<body>',
            '<section>',
            '<div id="wd_panel_timeline" class="panel panel-default alignak_webui_widget embedded">',
            '<!-- Hosts timeline widget -->',
            '</section>',
            '</body>'
        )

        # Get external host widget, no page parameter
        self.app.authorization = ('Basic', ('admin', 'admin'))
        response = self.app.get(
            '/external/host/%s/timeline' % host.id
        )
        response.mustcontain(
            '<div id="wd_panel_timeline" class="panel panel-default alignak_webui_widget embedded">',
            '<!-- Hosts timeline widget -->',
        )

        ## Host services
        # Get external host widget
        self.app.authorization = ('Basic', ('admin', 'admin'))
        response = self.app.get(
            '/external/host/%s/services?page' % host.id
        )
        response.mustcontain(
            '<!DOCTYPE html>',
            '<html lang="en">',
            '<body>',
            '<section>',
            '<div id="wd_panel_services" class="panel panel-default alignak_webui_widget embedded">',
            '<!-- Hosts services widget -->',
            '</section>',
            '</body>'
        )

        # Get external host widget, no page parameter
        self.app.authorization = ('Basic', ('admin', 'admin'))
        response = self.app.get(
            '/external/host/%s/services' % host.id
        )
        response.mustcontain(
            '<div id="wd_panel_services" class="panel panel-default alignak_webui_widget embedded">',
            '<!-- Hosts services widget -->',
        )

        ## Host history
        # Get external host widget
        self.app.authorization = ('Basic', ('admin', 'admin'))
        response = self.app.get(
            '/external/host/%s/history?page' % host.id
        )
        response.mustcontain(
            '<!DOCTYPE html>',
            '<html lang="en">',
            '<body>',
            '<section>',
            '<div id="wd_panel_history" class="panel panel-default alignak_webui_widget embedded">',
            '<!-- Hosts history widget -->',
            '</section>',
            '</body>'
        )

        # Get external host widget, no page parameter
        self.app.authorization = ('Basic', ('admin', 'admin'))
        response = self.app.get(
            '/external/host/%s/history' % host.id
        )
        response.mustcontain(
            '<div id="wd_panel_history" class="panel panel-default alignak_webui_widget embedded">',
            '<!-- Hosts history widget -->',
        )

    def test_2_widgets(self):
        print ''
        print 'allowed widgets'

        # Hosts table
        self.app.authorization = ('Basic', ('admin', 'admin'))
        response = self.app.get(
            '/external/widget/hosts_table?widget_id=hosts_table'
        )
        response.mustcontain(
            '<div id="wd_panel_hosts_table" class="panel panel-default alignak_webui_widget embedded">',
            '<small>Graphite on VM</small>',
            '<small>check_host_alive</small>'
        )

        # Hosts graph
        self.app.authorization = ('Basic', ('admin', 'admin'))
        response = self.app.get(
            '/external/widget/hosts_graph?widget_id=hosts_graph'
        )
        response.mustcontain(
            '<div id="wd_panel_hosts_graph" class="panel panel-default alignak_webui_widget embedded">',
            '<div id="pc_hosts_hosts_graph">'
        )


if __name__ == '__main__':
    unittest.main()
