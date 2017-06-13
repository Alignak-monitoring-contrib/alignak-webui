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

# Set test mode ...
os.environ['ALIGNAK_WEBUI_TEST'] = '1'
# os.environ['ALIGNAK_WEBUI_DEBUG'] = '1'
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

# _dummy, created by the alignak backend
# 6 templates for BI level
# 2 hosts templates
hosts_templates_count = 9

# 6 templates for freshness
# 1 generic service template
# 5 for nsca_*
services_templates_count = 12

# 1 generic user template
users_templates_count = 1

def setup_module(module):
    """
    Start Alignak backend
    Add elements to the backend with the alignak-backend-cli script
    :param module:
    :return:
    """
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

    print("Feeding Alignak backend...")

    work_dir = os.path.abspath(os.path.dirname(__file__))
    work_dir = os.path.join(work_dir, 'json')

    print("Creating backend elements...")
    # Create commands
    exit_code = subprocess.call(shlex.split(
        'alignak-backend-cli -f "%s" -t command -d checks-pack-commands.json add' % work_dir
    ))
    assert exit_code == 0

    # Create groups
    exit_code = subprocess.call(shlex.split(
        'alignak-backend-cli -f "%s" -t hostgroup -d checks-pack-hostgroups.json add' % work_dir
    ))
    assert exit_code == 0
    exit_code = subprocess.call(shlex.split(
        'alignak-backend-cli -f "%s" -t servicegroup -d checks-pack-servicegroups.json add' % work_dir
    ))
    assert exit_code == 0

    # Create templates
    exit_code = subprocess.call(shlex.split(
        'alignak-backend-cli  -f "%s" -t user -d checks-pack-users-templates.json add' % work_dir
    ))
    assert exit_code == 0
    exit_code = subprocess.call(shlex.split(
        'alignak-backend-cli  -f "%s" -t host -d checks-pack-hosts-templates.json add' % work_dir
    ))
    assert exit_code == 0
    exit_code = subprocess.call(shlex.split(
        'alignak-backend-cli  -f "%s" -t service -d checks-pack-services-templates.json add' % work_dir
    ))
    assert exit_code == 0

    print("Fed")


def teardown_module(module):
    print("Stopping Alignak backend...")
    global backend_process
    backend_process.kill()
    # subprocess.call(['pkill', 'alignak-backend'])
    print("Stopped")
    time.sleep(2)


class TestCreation(unittest2.TestCase):
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

        print('Enable edition mode')
        response = self.app.post('/edition_mode', params={'state': 'on'})
        assert response.json == {'edition_mode': True, 'message': 'Edition mode enabled'}
        self.session = response.request.environ['beaker.session']
        # edition_mode is defined and activated in the session...
        assert 'edition_mode' in self.session
        assert True == self.session['edition_mode']

        self.datamgr = DataManager(alignak_webui.app.app, session=self.session)

        # Get realm in the backend
        self.realm = self.datamgr.get_realm({'where': {'name': 'All'}})
        print("Realm: %s" % self.realm)
        assert self.realm.name == 'All'

        # Count hosts templates
        self.hosts_templates_count = self.datamgr.count_objects('host', search={'where': {'_is_template': True}})
        print("Hosts templates count: %s" % self.hosts_templates_count)
        assert self.hosts_templates_count == hosts_templates_count

        # Count services templates
        self.services_templates_count = self.datamgr.count_objects('service', search={'where': {'_is_template': True}})
        print("Services templates count: %s" % self.services_templates_count)
        assert self.services_templates_count == services_templates_count

        # Count users templates
        self.users_templates_count = self.datamgr.count_objects('user', search={'where': {'_is_template': True}})
        print("Users templates count: %s" % self.users_templates_count)
        assert self.users_templates_count == users_templates_count

        # Count hosts
        self.hosts_count = self.datamgr.count_objects('host', search={'where': {'_is_template': False}})
        print("Hosts count: %s" % self.hosts_count)

        # Count services
        self.services_count = self.datamgr.count_objects('service', search={'where': {'_is_template': False}})
        print("Services count: %s" % self.services_count)

        # Count users
        self.users_count = self.datamgr.count_objects('user', search={'where': {'_is_template': False}})
        print("users count: %s" % self.users_count)

    def tearDown(self):
        self.app.get('/logout')

class TestHostCreation(TestCreation):

    def test_create_host_from_templates_table(self):
        """Host creation from the hosts templates table"""

        # Get host template in the backend
        template = self.datamgr.get_host({'where': {'name': 'windows-passive-host',
                                                    '_is_template': True}})
        print("Host template: %s" % template)
        assert template.name == 'windows-passive-host'

        print('get page /hosts/templates/table (edition mode)')
        response = self.app.get('/hosts/templates/table')
        response.mustcontain(
            '<div id="hosts_templates_table" class="alignak_webui_table ">',
            "$('#tbl_hosts_templates_table').DataTable( {",
            # Because of a templates table
            'titleAttr: "Navigate to the hosts table"',
            # Because of edition mode...
            '''titleAttr: "Create a new item"''',
            '''var url = "/host/None/form";''',
        )

        # Get templates in the table
        response = self.app.post('/hosts/templates_table_data')
        print("Response: %s" % response.json)
        assert response.json['recordsTotal'] == hosts_templates_count
        assert response.json['data']

        # Host creation form
        print('get page /host/form (edition mode) - create a new host')
        response = self.app.get('/host/None/form')
        response.mustcontain(
            '''<div id="form_host">''',
            '''<form role="form" data-element="None" class="element_form " method="post" action="/host/None/form">''',
            '''<h4>You are creating a new host.</h4>''',
            '''$('form[data-element="None"]').on("submit", function (evt) {'''
        )

        print('Host creation with a template')
        data = {
            "_is_template": False,
            "_templates": [template.id],
            'name': "New host",
            'alias': "Friendly name"
        }
        response = self.app.post('/host/None/form', params=data)
        # Returns the new item _id
        new_host_id = response.json['_id']
        resp = response.json
        resp.pop('_id')
        assert resp == {
            "_message": "New host created",
            "_realm": self.realm.id,

            "_is_template": False,
            "_templates": [template.id],
            "name": "New host",
            'alias': "Friendly name"
        }

        # Count hosts templates
        count = self.datamgr.count_objects('host', search={'where': {'_is_template': True}})
        print("Hosts templates count: %s" % count)
        assert count == hosts_templates_count

        # Count services templates
        count = self.datamgr.count_objects('service', search={'where': {'_is_template': True}})
        print("Services templates count: %s" % count)
        assert count == services_templates_count

        # Count hosts - 1 more host
        new_count = self.datamgr.count_objects('host', search={'where': {'_is_template': False}})
        print("Hosts count: %s" % new_count)
        assert new_count == self.hosts_count + 1

        # Count services - 6 more services
        new_count = self.datamgr.count_objects('service', search={'where': {'_is_template': False}})
        print("Services count: %s" % new_count)
        assert new_count == self.services_count + 6

    def test_create_host_from_templates_page(self):
        """Host creation from the hosts templates page"""

        # Get host template in the backend
        template = self.datamgr.get_host({'where': {'name': 'windows-passive-host',
                                                    '_is_template': True}})
        assert template.name == 'windows-passive-host'
        template2 = self.datamgr.get_host({'where': {'name': 'bi-business-critical',
                                                     '_is_template': True}})
        assert template2.name == 'bi-business-critical'

        print('get page /hosts/templates (edition mode)')
        response = self.app.get('/hosts/templates')
        response.mustcontain(
            '<div id="hosts-templates">',
            '<form role="form" data-element="None" class="element_form" method="post" action="/host/None/form">',
            '<legend>Creating a new host:</legend>',
            '<input class="form-control" type="text" id="name" name="name" placeholder="Host name"  value="">',
            '<input class="form-control" type="text" id="alias" alias="alias" placeholder="Host alias"  value="">',
            '<input class="form-control" type="text" id="address" name="address" placeholder="0.0.0.0"  value="">',
            '<input class="form-control" type="text" id="realm" realm="realm" placeholder="Host realm"  value="">',
            '<input type="checkbox" id="_is_template" name="_is_template">',
            '<input id="_dummy" name="_dummy" type="checkbox" data-linked=""',
            '<input id="generic-passive-host" name="generic-passive-host" type="checkbox" data-linked=""',
            '<input id="windows-passive-host" name="windows-passive-host" type="checkbox" data-linked="generic-passive-host"',
            '<input id="bi-none" name="bi-none" type="checkbox" data-linked="" ',
            '<input id="bi-low" name="bi-low" type="checkbox" data-linked="" ',
            '<input id="bi-normal" name="bi-normal" type="checkbox" data-linked="" ',
            '<input id="bi-important" name="bi-important" type="checkbox" data-linked="" ',
            '<input id="bi-very-important" name="bi-very-important" type="checkbox" data-linked="" ',
            '<input id="bi-business-critical" name="bi-business-critical" type="checkbox" data-linked="" ',
        )

        print('Host creation with templates')
        data = {
            "realm": self.realm["_id"],
            "name": "New host bis",
            "alias": "Friendly name",
            "address": "127.0.0.1",
            "_is_template": False,
            "_templates": [template.id, template2.id],
        }
        response = self.app.post('/host/None/form', params=data)
        # Returns the new item _id
        new_host_id = response.json['_id']
        resp = response.json
        resp.pop('_id')
        assert resp == {
            "_message": "New host created",
            "_realm": self.realm.id,

            "_is_template": False,
            "_templates": [template.id, template2.id],
            "name": "New host bis",
            "alias": "Friendly name",
            "address": "127.0.0.1"
        }

        # Count hosts templates
        count = self.datamgr.count_objects('host', search={'where': {'_is_template': True}})
        print("Hosts templates count: %s" % count)
        assert count == hosts_templates_count

        # Count services templates
        count = self.datamgr.count_objects('service', search={'where': {'_is_template': True}})
        print("Services templates count: %s" % count)
        assert count == services_templates_count

        # Count hosts - 1 more host
        new_count = self.datamgr.count_objects('host', search={'where': {'_is_template': False}})
        print("Hosts count: %s" % new_count)
        assert new_count == self.hosts_count + 1

        # Count services - 6 more services
        new_count = self.datamgr.count_objects('service', search={'where': {'_is_template': False}})
        print("Services count: %s" % new_count)
        assert new_count == self.services_count + 6

class TestServiceCreation(TestCreation):

    def test_create_service_from_templates_table(self):
        """Service creation from the services templates table"""

        # Count hosts
        new_count = self.datamgr.count_objects('host', search={'where': {'_is_template': False}})
        print("Hosts count: %s" % new_count)

        # Count services
        new_count = self.datamgr.count_objects('service', search={'where': {'_is_template': False}})
        print("Services count: %s" % new_count)

        # Get host template in the backend
        template = self.datamgr.get_host({'where': {'name': '_dummy', '_is_template': True}})
        assert template.name == '_dummy'

        print('Create a new host')
        data = {
            "_realm": self.realm.id,
            "name": "New host ter",
            "_is_template": False,
            "_templates": [template.id],
            # Without templating services, else we will inherit from all the services templates ;)
            '_templates_with_services': False
        }
        response = self.app.post('/host/None/form', params=data)
        # Returns the new item _id
        new_host_id = response.json['_id']
        resp = response.json
        resp.pop('_id')
        assert resp == {
            "_message": "New host created",
            "_realm": self.realm.id,

            "_is_template": False,
            "_templates": [template.id],
            '_templates_with_services': False,
            "name": "New host ter",
        }

        # Get new host services
        services = self.datamgr.get_services({'where': {'host': new_host_id}})
        for service in services:
            print("- new service: %s" % service)

        # Count hosts - 1 more host
        new_count = self.datamgr.count_objects('host', search={'where': {'_is_template': False}})
        print("Hosts count: %s" % new_count)
        assert new_count == self.hosts_count + 1

        # Count services - not any service more
        new_count = self.datamgr.count_objects('service', search={'where': {'_is_template': False}})
        print("Services count: %s" % new_count)
        assert new_count == self.services_count


        # Get service template in the backend
        template = self.datamgr.get_service({'where': {'name': 'windows-passive-service',
                                                       '_is_template': True}})
        print("Service template: %s" % template)
        assert template.name == 'windows-passive-service'

        print('get page /services/templates/table (edition mode)')
        response = self.app.get('/services/templates/table')
        response.mustcontain(
            '<div id="services_templates_table" class="alignak_webui_table ">',
            "$('#tbl_services_templates_table').DataTable( {",
            # Because of a templates table
            'titleAttr: "Navigate to the services table"',
            # Because of edition mode...
            '''titleAttr: "Create a new item"''',
            '''var url = "/service/None/form";''',
        )

        # Get templates in the table
        response = self.app.post('/services/templates_table_data')
        print("Response: %s" % response.json)
        assert response.json['recordsTotal'] == services_templates_count
        assert response.json['data']

        # service creation form
        print('get page /service/form (edition mode) - create a new service')
        response = self.app.get('/service/None/form')
        response.mustcontain(
            '''<div id="form_service">''',
            '''<form role="form" data-element="None" class="element_form " method="post" action="/service/None/form">''',
            '''<h4>You are creating a new service.</h4>''',
            '''$('form[data-element="None"]').on("submit", function (evt) {'''
        )

        print('service creation with a template')
        data = {
            "_realm": self.realm.id,
            "_is_template": False,
            "_templates": [template.id],
            "host": new_host_id,
            'name': "New service",
            'alias': "Friendly name"
        }
        response = self.app.post('/service/None/form', params=data)
        print(response.json)
        # Returns the new item _id
        new_service_id = response.json['_id']
        resp = response.json
        resp.pop('_id')
        assert resp == {
            "_message": "New service created",
            "_realm": self.realm.id,

            "_is_template": False,
            "_templates": [template.id],
            "host": new_host_id,
            "name": "New service",
            'alias': "Friendly name"
        }

        # Count hosts templates
        count = self.datamgr.count_objects('host', search={'where': {'_is_template': True}})
        print("Hosts templates count: %s" % count)
        assert count == hosts_templates_count

        # Count services templates
        count = self.datamgr.count_objects('service', search={'where': {'_is_template': True}})
        print("Services templates count: %s" % count)
        assert count == services_templates_count

        # Count hosts - 1 more host
        new_count = self.datamgr.count_objects('host', search={'where': {'_is_template': False}})
        print("Hosts count: %s" % new_count)
        assert new_count == self.hosts_count + 1

        # Count services - 1 more service
        new_count = self.datamgr.count_objects('service', search={'where': {'_is_template': False}})
        print("Services count: %s" % new_count)
        assert new_count == self.services_count + 1

class TestUserCreation(TestCreation):

    def test_create_user(self):
        """User creation from the users templates table"""

        # Get user template in the backend
        template = self.datamgr.get_user({'where': {'name': 'user', '_is_template': True}})
        print("user template: %s" % template)
        assert template.name == 'user'

        print('get page /users/templates/table (edition mode)')
        response = self.app.get('/users/templates/table')
        response.mustcontain(
            '<div id="users_templates_table" class="alignak_webui_table ">',
            "$('#tbl_users_templates_table').DataTable( {",
            # Because of a templates table
            'titleAttr: "Navigate to the users table"',
            # Because of edition mode...
            '''titleAttr: "Create a new item"''',
            '''var url = "/user/None/form";''',
        )

        # Get templates in the table
        response = self.app.post('/users/templates_table_data')
        print("Response: %s" % response.json)
        assert response.json['recordsTotal'] == users_templates_count
        assert response.json['data']

        # user creation form
        print('get page /user/form (edition mode) - create a new user')
        response = self.app.get('/user/None/form')
        response.mustcontain(
            '''<div id="form_user">''',
            '''<form role="form" data-element="None" class="element_form " method="post" action="/user/None/form">''',
            '''<h4>You are creating a new user.</h4>''',
            '''$('form[data-element="None"]').on("submit", function (evt) {'''
        )

        print('user creation with a template')
        data = {
            "_is_template": False,
            "_templates": [template.id],
            'name': "New user",
            'alias': "Friendly name"
        }
        response = self.app.post('/user/None/form', params=data)
        # Returns the new item _id
        new_user_id = response.json['_id']
        resp = response.json
        resp.pop('_id')
        assert resp == {
            "_message": "New user created",
            "_realm": self.realm.id,

            "_is_template": False,
            "_templates": [template.id],
            "name": "New user",
            'alias': "Friendly name"
        }

        # Count users templates
        count = self.datamgr.count_objects('user', search={'where': {'_is_template': True}})
        print("users templates count: %s" % count)
        assert count == users_templates_count

        # Count users - 1 more user
        new_count = self.datamgr.count_objects('user', search={'where': {'_is_template': False}})
        print("users count: %s" % new_count)
        assert new_count == self.users_count + 1


if __name__ == '__main__':
    unittest2.main()
