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

# Set test mode ...
os.environ['ALIGNAK_WEBUI_TEST'] = '1'
os.environ['ALIGNAK_WEBUI_DEBUG'] = '1'
os.environ['ALIGNAK_WEBUI_CONFIGURATION_FILE'] = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'settings.cfg')
print("Configuration file", os.environ['ALIGNAK_WEBUI_CONFIGURATION_FILE'])

import alignak_webui.app

import alignak_webui.utils.datatable
from alignak_webui.backend.datamanager import DataManager

import bottle
from bottle import BaseTemplate, TEMPLATE_PATH

from webtest import TestApp

backend_process = None
backend_address = "http://127.0.0.1:5000/"


def setup_module(module):
    # Set test mode for applications backend
    os.environ['TEST_ALIGNAK_BACKEND'] = '1'
    os.environ['ALIGNAK_BACKEND_MONGO_DBNAME'] = 'alignak-backend-test'

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


class TestEditionMode(unittest2.TestCase):
    def setUp(self):
        # Test application
        self.app = TestApp(alignak_webui.app.session_app)

        print('login accepted - go to home page')
        self.login_response = self.app.post('/login', {'username': 'admin', 'password': 'admin'})

        # A session cookie exist
        assert self.app.cookies['Alignak-WebUI']
        for cookie in self.app.cookiejar:
            if cookie.name=='Alignak-WebUI':
                assert cookie.expires

        # A session exists and it contains: current user, his realm and his live synthesis
        self.session = self.login_response.request.environ['beaker.session']
        assert 'current_user' in self.session and self.session['current_user']
        assert self.session['current_user'].name == 'admin'
        assert 'current_realm' in self.session and self.session['current_realm']
        assert self.session['current_realm'].name == 'All'
        assert 'current_ls' in self.session and self.session['current_ls']

        # edition_mode is defined but not activated in the session...
        assert 'edition_mode' in self.session
        assert False == self.session['edition_mode']

    def tearDown(self):
        print('logout')
        self.app.get('/logout')

    def test_enable_disable(self):
        """Enable / disable edition mode"""

        print('Enable edition mode')
        response = self.app.post('/edition_mode', params={'state': 'on'})
        session = response.request.environ['beaker.session']
        # edition_mode is defined and activated in the session...
        assert 'edition_mode' in session
        assert True == session['edition_mode']
        assert response.json == {'edition_mode': True, 'message': 'Edition mode enabled'}

        print('Disable edition mode')
        response = self.app.post('/edition_mode', params={'state': 'off'})
        session = response.request.environ['beaker.session']
        # edition_mode is defined and activated in the session...
        assert 'edition_mode' in session
        assert False == session['edition_mode']
        assert response.json == {'edition_mode': False, 'message': 'Edition mode disabled'}

        print('Disable edition mode')
        # Any value other than 'on', edition is False
        response = self.app.post('/edition_mode', params={'state': ''})
        session = response.request.environ['beaker.session']
        # edition_mode is defined and activated in the session...
        assert 'edition_mode' in session
        assert False == session['edition_mode']
        assert response.json == {'edition_mode': False, 'message': 'Edition mode disabled'}
        # No state parameter, edition is False
        response = self.app.post('/edition_mode')
        session = response.request.environ['beaker.session']
        # edition_mode is defined and activated in the session...
        assert 'edition_mode' in session
        assert False == session['edition_mode']
        assert response.json == {'edition_mode': False, 'message': 'Edition mode disabled'}

    def test_edition_mode_menu(self):
        """In edition mode, a new menu exist in the menu bar"""
        print('test edition mode menu')

        print('get dashboard')
        response = self.app.get('/dashboard')
        response.mustcontain(
            '<div id="dashboard">',
            no=[
                '<!-- Templates actions bar -->',
                '<li class="dropdown" data-toggle="tooltip" data-placement="bottom" title="Templates menu">',
                '<ul class="dropdown-menu" role="menu" aria-labelledby="Edition mode menu">',
                '<span>Hosts templates</span>',
                '<span>Services templates</span>',
                '<span>Users templates</span>'
            ]
        )

        print('Enable edition mode')
        response = self.app.post('/edition_mode', params={'state': 'on'})
        session = response.request.environ['beaker.session']
        # edition_mode is defined and activated in the session...
        assert 'edition_mode' in session
        assert True == session['edition_mode']
        assert response.json == {'edition_mode': True, 'message': 'Edition mode enabled'}

        print('get dashboard (edition mode)')
        response = self.app.get('/dashboard')
        response.mustcontain(
            '<div id="dashboard">',
            '<!-- Templates actions bar -->',
            '<li class="dropdown" data-toggle="tooltip" data-placement="bottom" title="Templates menu">',
            '<ul class="dropdown-menu" role="menu" aria-labelledby="Edition mode menu">',
            '<span>Hosts templates</span>',
            '<span>Services templates</span>',
            '<span>Users templates</span>'
        )

        print('Disable edition mode')
        response = self.app.post('/edition_mode', params={'state': 'off'})
        session = response.request.environ['beaker.session']
        # edition_mode is defined and activated in the session...
        assert 'edition_mode' in session
        assert False == session['edition_mode']
        assert response.json == {'edition_mode': False, 'message': 'Edition mode disabled'}

        print('get dashboard')
        response = self.app.get('/dashboard')
        response.mustcontain(
            '<div id="dashboard">',
            no=[
                '<!-- Templates actions bar -->',
                '<li class="dropdown" data-toggle="tooltip" data-placement="bottom" title="Templates menu">',
                '<ul class="dropdown-menu" role="menu" aria-labelledby="Edition mode menu">',
                '<span>Hosts templates</span>',
                '<span>Services templates</span>',
                '<span>Users templates</span>'
            ]
        )


class TestHosts(unittest2.TestCase):
    def setUp(self):
        # Test application
        self.app = TestApp(alignak_webui.app.session_app)

        print('login accepted - go to home page')
        self.login_response = self.app.post('/login', {'username': 'admin', 'password': 'admin'})

        # A session cookie exist
        assert self.app.cookies['Alignak-WebUI']
        for cookie in self.app.cookiejar:
            if cookie.name=='Alignak-WebUI':
                assert cookie.expires

        # A session exists and it contains: current user, his realm and his live synthesis
        self.session = self.login_response.request.environ['beaker.session']
        assert 'current_user' in self.session and self.session['current_user']
        assert self.session['current_user'].name == 'admin'
        assert 'current_realm' in self.session and self.session['current_realm']
        assert self.session['current_realm'].name == 'All'
        assert 'current_ls' in self.session and self.session['current_ls']

        # edition_mode is defined but not activated in the session...
        assert 'edition_mode' in self.session
        assert False == self.session['edition_mode']

    def tearDown(self):
        print('logout')
        self.app.get('/logout')

    def test_hosts_table(self):
        """View hosts table in edition mode"""
        print('get page /hosts/table (normal mode)')
        response = self.app.get('/hosts/table')
        response.mustcontain(
            '<div id="hosts_table" class="alignak_webui_table ">',
            "$('#tbl_host').DataTable( {",
            '<table id="tbl_host" ',
            no = [
                '''text: "<span class='fa fa-edit'></span>"''',
                '''titleAttr: "Edit the selected item"''',
            ]
        )

        print('Enable edition mode')
        response = self.app.post('/edition_mode', params={'state': 'on'})
        session = response.request.environ['beaker.session']
        # edition_mode is defined and activated in the session...
        assert 'edition_mode' in session
        assert True == session['edition_mode']
        assert response.json == {'edition_mode': True, 'message': 'Edition mode enabled'}

        print('get page /hosts/table (edition mode)')
        response = self.app.get('/hosts/table')
        response.mustcontain(
            '<div id="hosts_table" class="alignak_webui_table ">',
            "$('#tbl_host').DataTable( {",
            '<table id="tbl_host" ',
            '''text: "<span class='fa fa-edit'></span>"''',
            '''titleAttr: "Edit the selected item"''',
        )

    def test_host_form(self):
        """View host edition form"""

        # Get host in the backend
        datamgr = DataManager(alignak_webui.app.app, session=self.session)
        host = datamgr.get_host({'where': {'name': 'KNM-Shinken'}})

        print('get page /host/form (reading mode)')
        response = self.app.get('/host/%s/form' % host.id)
        response.mustcontain(
            '''<div id="form_host">''',
            '''<form role="form" data-element="%s" class="element_form " >''' % host.id,
            no = [
                '''$('form[data-element="%s"]').on("submit", function (evt) {''' % host.id
            ]
        )

        print('Enable edition mode')
        response = self.app.post('/edition_mode', params={'state': 'on'})
        session = response.request.environ['beaker.session']
        # edition_mode is defined and activated in the session...
        assert 'edition_mode' in session
        assert True == session['edition_mode']
        assert response.json == {'edition_mode': True, 'message': 'Edition mode enabled'}

        print('get page /host/form (edition mode) - with an host id')
        response = self.app.get('/host/%s/form' % host.id)
        response.mustcontain(
            '''<div id="form_host">''',
            '''<form role="form" data-element="%s" class="element_form " method="post" action="/host/%s/form">''' % (
            host.id, host.id),
            '''$('form[data-element="%s"]').on("submit", function (evt) {''' % host.id
        )

        print('get page /host/form (edition mode) - with an host name')
        response = self.app.get('/host/%s/form' % host.name)
        response.mustcontain(
            '''<div id="form_host">''',
            '''<form role="form" data-element="%s" class="element_form " method="post" action="/host/%s/form">''' % (
            host.id, host.id),
            '''$('form[data-element="%s"]').on("submit", function (evt) {''' % host.id
        )

        print('get page /host/form (edition mode) - for a new host')
        response = self.app.get('/host/unknown_host/form')
        response.mustcontain(
            '''<div id="form_host">''',
            '''<form role="form" data-element="None" class="element_form " method="post" action="/host/None/form">''',
            '''<h4>You are creating a new host.</h4>''',
            '''$('form[data-element="None"]').on("submit", function (evt) {'''
        )

    def test_host_new_host(self):
        """Create a new host edition form"""

        datamgr = DataManager(alignak_webui.app.app, session=self.session)

        # Get realm in the backend
        realm = datamgr.get_realm({'where': {'name': 'All'}})
        # Get host template in the backend
        template = datamgr.get_host({'where': {'name': 'generic-host', '_is_template': True}})

        print('Enable edition mode')
        response = self.app.post('/edition_mode', params={'state': 'on'})
        session = response.request.environ['beaker.session']
        # edition_mode is defined and activated in the session...
        assert 'edition_mode' in session
        assert True == session['edition_mode']
        assert response.json == {'edition_mode': True, 'message': 'Edition mode enabled'}

        print('get page /host/form (edition mode) - for a new host')
        response = self.app.get('/host/unknown_host/form')
        response.mustcontain(
            '''<div id="form_host">''',
            '''<form role="form" data-element="None" class="element_form " method="post" action="/host/None/form">''',
            '''<h4>You are creating a new host.</h4>''',
            '''$('form[data-element="None"]').on("submit", function (evt) {'''
        )

        print('Host creation fails - missing template')
        data = {
            "_is_template": False,
            'name': "New host",
            'display_name': "Display name"
        }
        response = self.app.post('/host/None/form', params=data)
        assert response.json == {
            "_message": "host creation failed!",
            "_realm": realm.id,

            "_is_template": False,
            "name": "New host",
            'display_name': "Display name",

            "_errors": {
                "name": "field 'check_command' is required"
            }
        }

        print('Host creation')
        data = {
            "_is_template": False,
            "_templates": [template.id],
            'name': "New host",
            'display_name': "Display name"
        }
        response = self.app.post('/host/None/form', params=data)
        # Returns the new item _id
        new_host_id = response.json['_id']
        resp = response.json
        resp.pop('_id')
        assert resp == {
            "_message": "New host created",
            "_realm": realm.id,

            "_is_template": False,
            "_templates": [template.id],
            "name": "New host",
            'display_name': "Display name",
        }

        # Get the new host in the backend
        host = datamgr.get_host({'where': {'name': 'New host'}})
        assert host
        assert host.id == new_host_id
        assert host.name == "New host"
        assert host.display_name == "Display name"

    def test_host_submit_form(self):
        """Edit and submit host edition form"""
        datamgr = DataManager(alignak_webui.app.app, session=self.session)

        # Get host and service in the backend
        host = datamgr.get_host({'where': {'name': 'graphite'}})
        services = datamgr.get_host_services(host)
        service = services[0]

        print('Enable edition mode')
        response = self.app.post('/edition_mode', params={'state': 'on'})
        session = response.request.environ['beaker.session']
        # edition_mode is defined and activated in the session...
        assert 'edition_mode' in session
        assert True == session['edition_mode']
        assert response.json == {'edition_mode': True, 'message': 'Edition mode enabled'}

        print('get page /host/form (edition mode) - with an host id')
        response = self.app.get('/host/%s/form' % host.id)
        response.mustcontain(
            '''<div id="form_host">''',
            '''<form role="form" data-element="%s" class="element_form " method="post" action="/host/%s/form">''' % (
            host.id, host.id),
            '''$('form[data-element="%s"]').on("submit", function (evt) {''' % host.id
        )

        print('Post form updates')
        data = {
            'name': host.name,
            'display_name': "Display name edited"
        }
        response = self.app.post('/host/%s/form' % host.id, params=data)
        assert response.json == {
            "_message": "host 'graphite' updated", "display_name": "Display name edited"
        }


if __name__ == '__main__':
    unittest.main()
