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
import time
import shlex
import unittest2
import subprocess

from nose.tools import *

# Test environment variables
os.environ['ALIGNAK_WEBUI_TEST'] = '1'
os.environ['ALIGNAK_WEBUI_DEBUG'] = '1'
os.environ['ALIGNAK_WEBUI_CONFIGURATION_FILE'] = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'settings.cfg')
print("Configuration file", os.environ['ALIGNAK_WEBUI_CONFIGURATION_FILE'])

import alignak_webui.app
# from alignak_webui import webapp
from alignak_webui.backend.datamanager import DataManager
import alignak_webui.utils.datatable

# from logging import getLogger, DEBUG, INFO
# loggerDm = getLogger('alignak_webui.objects.datamanager')
# loggerDm.setLevel(DEBUG)

from webtest import TestApp

backend_process = None
backend_address = "http://127.0.0.1:5000/"


def setup_module(module):
    # Set test mode for applications backend
    os.environ['TEST_ALIGNAK_BACKEND'] = '1'
    os.environ['ALIGNAK_BACKEND_MONGO_DBNAME'] = 'alignak-webui-tests'

    # Delete used mongo DBs
    exit_code = subprocess.call(
        shlex.split('mongo %s --eval "db.dropDatabase()"'
                    % os.environ['ALIGNAK_BACKEND_MONGO_DBNAME'])
    )
    assert exit_code == 0
    time.sleep(1)

    test_dir = os.path.dirname(os.path.realpath(__file__))
    print("Current test directory: %s" % test_dir)

    print("Starting Alignak backend...")
    global backend_process
    fnull = open(os.devnull, 'w')
    backend_process = subprocess.Popen(['uwsgi', '--plugin', 'python',
                                        '-w', 'alignak_backend.app:app',
                                        '--socket', '0.0.0.0:5000',
                                        '--protocol=http', '--enable-threads', '--pidfile',
                                        '/tmp/uwsgi.pid'],
                                       stdout=fnull)
    print("Started")

    print("Feeding Alignak backend... %s" % test_dir)
    exit_code = subprocess.call(
        shlex.split('alignak-backend-import --delete %s/cfg/default/_main.cfg' % test_dir),
        stdout=fnull
    )
    assert exit_code == 0
    print("Fed")


def teardown_module(module):
    print("Stopping Alignak backend...")
    global backend_process
    backend_process.kill()
    # subprocess.call(['pkill', 'alignak-backend'])
    print("Stopped")
    time.sleep(2)


class TestsExternal(unittest2.TestCase):

    def setUp(self):
        print("setting up ...")

        # Test application
        self.app = TestApp(alignak_webui.app.session_app)

    def test_refused(self):
        """ External - refused"""
        print('refused external access')

        # Refused - no credentials
        response = self.app.get(
            '/external/widget/hosts_table?widget_id=test',
            status=401
        )
        print(response)
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

        # Refused - unknown table
        self.app.authorization = ('Basic', ('admin', 'admin'))
        response = self.app.get(
            '/external/table/unknown?widget_id=test',
            status=409
        )
        response.mustcontain('<div><h1>Unknown required table: unknown.</h1><p>The required table is not available.</p></div>')

        # Refused - unknown list
        self.app.authorization = ('Basic', ('admin', 'admin'))
        response = self.app.get(
            '/external/list/unknown?widget_id=test',
            status=409
        )
        response.mustcontain('<div><h1>Unknown required list: unknown.</h1><p>The required list is not available.</p></div>')

        # Refused - unknown host widget
        self.app.authorization = ('Basic', ('admin', 'admin'))
        response = self.app.get(
            '/external/host/unknown?widget_id=test',
            status=409
        )
        response.mustcontain('<div><h1>Missing host widget name.</h1><p>You must provide a widget name</p></div>')
        self.app.authorization = ('Basic', ('admin', 'admin'))
        response = self.app.get(
            '/external/host/unknown/unknown?widget_id=test',
            status=409
        )
        response.mustcontain('<div><h1>Unknown required widget: unknown.</h1><p>The required widget is not available.</p></div>')

    def test_allowed_widgets(self):
        """External - allowed widgets"""
        print('allowed widgets external access')

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
            '/external/widget/hosts_chart?links&widget_id=hosts_chart'
        )
        response.mustcontain(
            '<div id="wd_panel_hosts_chart" class="panel panel-default alignak_webui_widget embedded">',
            '<div id="pc_hosts_hosts_chart">'
        )

    def test_allowed_tables(self):
        """External - allowed tables"""
        print('allowed tables external access')

        # Allowed - default table parameters: none
        # Add parameter page to get a whole page: js, css, ...
        print("Whole page...")
        self.app.authorization = ('Basic', ('admin', 'admin'))
        response = self.app.get(
            '/external/table/hosts_table?page'
        )
        response.mustcontain(
            '<!DOCTYPE html>',
            '<html lang="en">',
            '<body>',
            '<section>',
            '<div id="hosts_table" class="alignak_webui_table embedded">',
            '</section>',
            '</body>'
        )

        # Allowed - default table parameters: none
        # No parameter page: only the widget
        print("Only div...")
        self.app.authorization = ('Basic', ('admin', 'admin'))
        response = self.app.get(
            '/external/table/hosts_table'
        )
        response.mustcontain(
            '<div id="hosts_table" class="alignak_webui_table embedded">',
            '<th data-name="name" data-type="string"',
            '<th data-name="ls_state" data-type="string"',
            '<th data-name="overall_status" data-type="string"',
            '<th data-name="tags" data-type="list"',
            '<th data-name="address" data-type="string"',
            '<th data-name="business_impact" data-type="integer"'
        )

        # Allowed - default table parameters: none
        # No parameter page: only the widget
        # With links, but empty
        print("Only div with links...")
        self.app.authorization = ('Basic', ('admin', 'admin'))
        response = self.app.get(
            '/external/table/hosts_table?links'
        )
        response.mustcontain(
            '<div id="hosts_table" class="alignak_webui_table embedded">',
            '<th data-name="name" data-type="string"',
            '<th data-name="ls_state" data-type="string"',
            '<th data-name="overall_status" data-type="string"',
            '<th data-name="tags" data-type="list"',
            '<th data-name="address" data-type="string"',
            '<th data-name="business_impact" data-type="integer"'
        )

        # Allowed - default table parameters: none
        # No parameter page: only the widget
        # With links, not empty so URL are prefixed ...
        print("Only div with links...")
        self.app.authorization = ('Basic', ('admin', 'admin'))
        response = self.app.get(
            '/external/table/hosts_table?links=http://test'
        )
        response.mustcontain(
            '<div id="hosts_table" class="alignak_webui_table embedded">',
            '<th data-name="name" data-type="string"',
            '<th data-name="ls_state" data-type="string"',
            '<th data-name="overall_status" data-type="string"',
            '<th data-name="tags" data-type="list"',
            '<th data-name="address" data-type="string"',
            '<th data-name="business_impact" data-type="integer"',
            '"url": "http://localhost:80/external/table/hosts_table/hosts/table_data",'
        )

    def test_host_widgets(self):
        """External - host widgets"""
        print('allowed host widgets external access')

        # Log in to get Data manager in the session
        response = self.app.get('/login')
        response.mustcontain('<form role="form" method="post" action="/login">')

        print('login accepted - go to home page')
        response = self.app.post('/login', {'username': 'admin', 'password': 'admin'})
        # Redirected twice: /login -> / -> /dashboard !
        redirected_response = response.follow()
        redirected_response = redirected_response.follow()
        redirected_response.mustcontain('<div id="livestate">')

        session = redirected_response.request.environ['beaker.session']
        assert 'current_user' in session and session['current_user']
        assert session['current_user'].get_username() == 'admin'

        datamgr = DataManager(alignak_webui.app.app, session=session)

        # Get host in the backend
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

        # Host view
        # ---
        # Get external host widget
        self.app.authorization = ('Basic', ('admin', 'admin'))
        response = self.app.get(
            '/external/host/%s/view?page' % host.id
        )
        response.mustcontain(
            '<!DOCTYPE html>',
            '<html lang="en">',
            '<body>',
            '<section>',
            '<div id="wd_panel_view" class="panel panel-default alignak_webui_widget embedded">',
            '<!-- Hosts view widget -->',
            '</section>',
            '</body>'
        )

        # Get external host widget, no page parameter
        self.app.authorization = ('Basic', ('admin', 'admin'))
        response = self.app.get(
            '/external/host/%s/view' % host.id
        )
        response.mustcontain(
            '<div id="wd_panel_view" class="panel panel-default alignak_webui_widget embedded">',
            '<!-- Hosts view widget -->',
        )

        # Host information
        # ---
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

        # Host configuration
        # ---
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

        # Host metrics
        # ---
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

        # Host timeline
        # ---
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
            '<!-- Host timeline widget -->',
            '</section>',
            '</body>',
            '<div class="alert alert-info">',
            '<p class="font-blue">No available history events.</p>',
            '</div>'
        )

        # Get external host widget, no page parameter
        self.app.authorization = ('Basic', ('admin', 'admin'))
        response = self.app.get(
            '/external/host/%s/timeline' % host.id
        )
        response.mustcontain(
            '<div id="wd_panel_timeline" class="panel panel-default alignak_webui_widget embedded">',
            '<!-- Host timeline widget -->',
        )

        # Host services
        # ---
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

        # Temporarily disabled
        # # Host history
        # # Get external host widget
        # self.app.authorization = ('Basic', ('admin', 'admin'))
        # response = self.app.get(
        #     '/external/host/%s/history?page' % host.id
        # )
        # response.mustcontain(
        #     '<!DOCTYPE html>',
        #     '<html lang="en">',
        #     '<body>',
        #     '<section>',
        #     '<div id="wd_panel_history" class="panel panel-default alignak_webui_widget embedded">',
        #     '<!-- Hosts history widget -->',
        #     '</section>',
        #     '</body>'
        # )
        #
        # # Get external host widget, no page parameter
        # self.app.authorization = ('Basic', ('admin', 'admin'))
        # response = self.app.get(
        #     '/external/host/%s/history' % host.id
        # )
        # response.mustcontain(
        #     '<div id="wd_panel_history" class="panel panel-default alignak_webui_widget embedded">',
        #     '<!-- Hosts history widget -->',
        # )

    def test_service_widgets(self):
        """External - service widgets"""
        print('allowed service widgets external access')

        # Log in to get Data manager in the session
        response = self.app.get('/login')
        response.mustcontain('<form role="form" method="post" action="/login">')

        print('login accepted - go to home page')
        response = self.app.post('/login', {'username': 'admin', 'password': 'admin'})
        # Redirected twice: /login -> / -> /dashboard !
        redirected_response = response.follow()
        redirected_response = redirected_response.follow()
        redirected_response.mustcontain('<div id="livestate">')

        session = redirected_response.request.environ['beaker.session']
        assert 'current_user' in session and session['current_user']
        assert session['current_user'].get_username() == 'admin'

        datamgr = DataManager(alignak_webui.app.app, session=session)

        # Get host and service in the backend
        host = datamgr.get_host({'where': {'name': 'KNM-Shinken'}})
        print("Host: %s" % host)
        services = datamgr.get_host_services(host)
        print("Services: %s" % services)
        # service = datamgr.get_service({'where': {'name': 'http', 'host': host.id}})
        service = services[0]
        print("Service: %s" % service)
        # assert False

        # Get external service widget - no widget identifier
        self.app.authorization = ('Basic', ('admin', 'admin'))
        response = self.app.get(
            '/external/service/%s' % service.id,
            status=409
        )
        response.mustcontain('<div><h1>Missing service widget name.</h1><p>You must provide a widget name</p></div>')

        # Get external service widget - unknown widget
        self.app.authorization = ('Basic', ('admin', 'admin'))
        response = self.app.get(
            '/external/service/%s/unknown' % service.id,
            status=409
        )
        response.mustcontain('<div><h1>Unknown required widget: unknown.</h1><p>The required widget is not available.</p></div>')

        # Service information
        # Get external service widget
        self.app.authorization = ('Basic', ('admin', 'admin'))
        response = self.app.get(
            '/external/service/%s/information?page' % service.id
        )
        response.mustcontain(
            '<!DOCTYPE html>',
            '<html lang="en">',
            '<body>',
            '<section>',
            '<div id="wd_panel_information" class="panel panel-default alignak_webui_widget embedded">',
            '<!-- Service information widget -->',
            '</section>',
            '</body>'
        )

        # Get external service widget, no page parameter
        self.app.authorization = ('Basic', ('admin', 'admin'))
        response = self.app.get(
            '/external/service/%s/information' % service.id
        )
        response.mustcontain(
            '<div id="wd_panel_information" class="panel panel-default alignak_webui_widget embedded">',
            '<!-- Service information widget -->',
        )

        # service configuration
        # Get external service widget
        self.app.authorization = ('Basic', ('admin', 'admin'))
        response = self.app.get(
            '/external/service/%s/configuration?page' % service.id
        )
        response.mustcontain(
            '<!DOCTYPE html>',
            '<html lang="en">',
            '<body>',
            '<section>',
            '<div id="wd_panel_configuration" class="panel panel-default alignak_webui_widget embedded">',
            '<!-- Service configuration widget -->',
            '</section>',
            '</body>'
        )

        # Get external service widget, no page parameter
        self.app.authorization = ('Basic', ('admin', 'admin'))
        response = self.app.get(
            '/external/service/%s/configuration' % service.id
        )
        response.mustcontain(
            '<div id="wd_panel_configuration" class="panel panel-default alignak_webui_widget embedded">',
            '<!-- Service configuration widget -->',
        )

        # Service timeline
        # Get external service widget
        self.app.authorization = ('Basic', ('admin', 'admin'))
        response = self.app.get(
            '/external/service/%s/timeline?page' % service.id
        )
        response.mustcontain(
            '<!DOCTYPE html>',
            '<html lang="en">',
            '<body>',
            '<section>',
            '<div id="wd_panel_timeline" class="panel panel-default alignak_webui_widget embedded">',
            '<!-- Service timeline widget -->',
            '</section>',
            '</body>',
            '<div class="alert alert-info">',
            '<p class="font-blue">No available history events.</p>',
            '</div>'
        )

        # Get external service widget, no page parameter
        self.app.authorization = ('Basic', ('admin', 'admin'))
        response = self.app.get(
            '/external/service/%s/timeline' % service.id
        )
        response.mustcontain(
            '<div id="wd_panel_timeline" class="panel panel-default alignak_webui_widget embedded">',
            '<!-- Service timeline widget -->',
        )

        # service metrics
        # Get external service widget
        self.app.authorization = ('Basic', ('admin', 'admin'))
        response = self.app.get(
            '/external/service/%s/metrics?page' % service.id
        )
        response.mustcontain(
            '<!DOCTYPE html>',
            '<html lang="en">',
            '<body>',
            '<section>',
            '<div id="wd_panel_metrics" class="panel panel-default alignak_webui_widget embedded">',
            '<!-- Service metrics widget -->',
            '</section>',
            '</body>'
        )

        # Get external service widget, no page parameter
        self.app.authorization = ('Basic', ('admin', 'admin'))
        response = self.app.get(
            '/external/service/%s/metrics' % service.id
        )
        response.mustcontain(
            '<div id="wd_panel_metrics" class="panel panel-default alignak_webui_widget embedded">',
            '<!-- Service metrics widget -->',
        )

    def test_user_widgets(self):
        """External - user widgets"""
        print('allowed user widgets external access')

        # Log in to get Data manager in the session
        response = self.app.get('/login')
        response.mustcontain('<form role="form" method="post" action="/login">')

        print('login accepted - go to home page')
        response = self.app.post('/login', {'username': 'admin', 'password': 'admin'})
        # Redirected twice: /login -> / -> /dashboard !
        redirected_response = response.follow()
        redirected_response = redirected_response.follow()
        redirected_response.mustcontain('<div id="livestate">')

        session = redirected_response.request.environ['beaker.session']
        assert 'current_user' in session and session['current_user']
        assert session['current_user'].get_username() == 'admin'

        datamgr = DataManager(alignak_webui.app.app, session=session)

        # Get user in the backend
        user = datamgr.get_user({'where': {'name': 'imported_admin'}})

        # Get external user widget - no widget identifier
        self.app.authorization = ('Basic', ('admin', 'admin'))
        response = self.app.get(
            '/external/user/%s' % user.id,
            status=409
        )
        response.mustcontain(
            '<div><h1>Missing user widget name.</h1><p>You must provide a widget name</p></div>')

        # Get external user widget - unknown widget
        self.app.authorization = ('Basic', ('admin', 'admin'))
        response = self.app.get(
            '/external/user/%s/unknown' % user.id,
            status=409
        )
        response.mustcontain(
            '<div><h1>Unknown required widget: unknown.</h1><p>The required widget is not available.</p></div>')

        # Service information
        # Get external user widget
        self.app.authorization = ('Basic', ('admin', 'admin'))
        response = self.app.get(
            '/external/user/%s/information?page' % user.id
        )
        print(response)
        response.mustcontain(
            '<!DOCTYPE html>',
            '<html lang="en">',
            '<body>',
            '<section>',
            '<div id="wd_panel_information" class="panel panel-default alignak_webui_widget embedded">',
            '<!-- User information widget -->',
            '</section>',
            '</body>'
        )

        # Get external user widget, no page parameter
        self.app.authorization = ('Basic', ('admin', 'admin'))
        response = self.app.get(
            '/external/user/%s/information' % user.id
        )
        response.mustcontain(
            '<div id="wd_panel_information" class="panel panel-default alignak_webui_widget embedded">',
            '<!-- User information widget -->',
        )


class TestAllWidgets(unittest2.TestCase):

    def setUp(self):
        print("setting up ...")

        # Test application
        self.app = TestApp(alignak_webui.app.session_app)

    def test_widgets(self):
        """External - get all allowed widgets"""
        print('allowed widgets')

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
            '/external/widget/hosts_chart?widget_id=hosts_chart'
        )
        response.mustcontain(
            '<div id="wd_panel_hosts_chart" class="panel panel-default alignak_webui_widget embedded">',
            '<div id="pc_hosts_hosts_chart">'
        )

        # Services table
        self.app.authorization = ('Basic', ('admin', 'admin'))
        response = self.app.get(
            '/external/widget/services_table?widget_id=services_table'
        )
        response.mustcontain(
            '<div id="wd_panel_services_table" class="panel panel-default alignak_webui_widget embedded">',
            '<small>BigProcesses</small>'
        )

        # Services graph
        self.app.authorization = ('Basic', ('admin', 'admin'))
        response = self.app.get(
            '/external/widget/services_chart?widget_id=services_chart'
        )
        response.mustcontain(
            '<div id="wd_panel_services_chart" class="panel panel-default alignak_webui_widget embedded">',
            '<div id="pc_services_services_chart">'
        )

        # Livestate table
        self.app.authorization = ('Basic', ('admin', 'admin'))
        response = self.app.get(
            '/external/widget/livestate?widget_id=livestate'
        )
        response.mustcontain(
            '<div id="wd_panel_livestate" class="panel panel-default alignak_webui_widget embedded">',
            '<div id="livestate-bi--1">'
        )


class TestExternalFiles(unittest2.TestCase):

    def setUp(self):
        print("setting up ...")

        # Test application
        self.app = TestApp(alignak_webui.app.session_app)

    def test_request_unknown_files(self):
        """External - request list of js files - unknown files"""
        print('Request list of js files')

        # Allowed - default widgets parameters: widget_id and widget_template
        # Add parameter page to get a whole page: js, css, ...
        self.app.authorization = ('Basic', ('admin', 'admin'))
        response = self.app.get(
            '/external/files/unknown', status=409
        )
        print(response)
        assert "status" in response.json
        assert response.json['status'] == "ko"
        assert "message" in response.json
        assert response.json['message']

    def test_request_js_files(self):
        """External - request list of js files"""
        print('Request list of js files')

        # Allowed - default widgets parameters: widget_id and widget_template
        # Add parameter page to get a whole page: js, css, ...
        self.app.authorization = ('Basic', ('admin', 'admin'))
        response = self.app.get(
            '/external/files/js_list'
        )
        print(response)
        assert response.json['status'] == "ok"
        assert "files" in response.json
        assert response.json['files']

        reference =  [
            "/static/js/jquery-1.12.0.min.js",
            "/static/js/jquery-ui-1.11.4.min.js",
            "/static/js/bootstrap.min.js",
            "/static/js/moment-with-langs.min.js",
            "/static/js/daterangepicker.js",
            "/static/js/jquery.jclock.js",
            "/static/js/jquery.jTruncate.js",
            "/static/js/typeahead.bundle.min.js",
            "/static/js/screenfull.js",
            "/static/js/alertify.min.js",
            "/static/js/BootSideMenu.js",
            "/static/js/selectize.min.js",
            "/static/js/Chart.min.js",
            "/static/js/jstree.min.js",
            "/static/js/datatables.min.js",
            "/static/js/material/arrive.min.js",
            "/static/js/material/material.min.js",
            "/static/js/material/ripples.min.js"
        ]
        assert reference == response.json['files']

    def test_request_css_files(self):
        """External - request list of js files - CSS files"""
        print('Request list of css files')

        # Allowed - default widgets parameters: widget_id and widget_template
        # Add parameter page to get a whole page: js, css, ...
        self.app.authorization = ('Basic', ('admin', 'admin'))
        response = self.app.get('/external/files/css_list')
        print(response)
        assert response.json['status'] == "ok"
        assert "files" in response.json
        assert response.json['files']

        reference = [
            "/static/css/bootstrap.min.css",
            "/static/css/font-awesome.min.css",
            "/static/css/typeahead.css",
            "/static/css/daterangepicker.css",
            "/static/css/alertify/alertify.min.css",
            "/static/css/alertify/bootstrap.min.css",
            "/static/css/BootSideMenu.css",
            "/static/css/timeline.css",
            "/static/css/selectize.bootstrap3.css",
            "/static/css/font-roboto.css",
            "/static/css/material-icons.css",
            "/static/css/material/bootstrap-material-design.min.css",
            "/static/css/material/ripples.min.css",
            "/static/css/jstree/style.min.css",
            "/static/css/datatables.min.css",
            "/static/css/alignak_webui.css",
            "/static/css/alignak_webui-items.css"
        ]
        assert reference == response.json['files']


if __name__ == '__main__':
    unittest.main()
