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
import time
import shlex
import unittest2
import subprocess
from calendar import timegm
from datetime import datetime, timedelta

from nose.tools import *

# Test environment variables
os.environ['TEST_WEBUI'] = '1'
os.environ['WEBUI_DEBUG'] = '1'
os.environ['ALIGNAK_WEBUI_CONFIGURATION_FILE'] = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'settings.cfg')
print("Configuration file", os.environ['ALIGNAK_WEBUI_CONFIGURATION_FILE'])

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
    print ("start alignak backend")

    global pid
    global backend_address

    if backend_address == "http://127.0.0.1:5000/":
        # Set test mode for applications backend
        os.environ['TEST_ALIGNAK_BACKEND'] = '1'
        os.environ['ALIGNAK_BACKEND_MONGO_DBNAME'] = 'alignak-backend-test'

        # Delete used mongo DBs
        exit_code = subprocess.call(
            shlex.split('mongo %s --eval "db.dropDatabase()"' % os.environ['ALIGNAK_BACKEND_MONGO_DBNAME'])
        )
        assert exit_code == 0
        time.sleep(1)

        print("Starting Alignak backend...")
        # No console output for the applications backend ...
        fnull = open(os.devnull, 'w')
        pid = subprocess.Popen(
            shlex.split('uwsgi --plugin python -w alignakbackend:app --socket 0.0.0.0:5000 '
                        '--protocol=http --enable-threads --pidfile /tmp/uwsgi.pid '
                        '--logto /tmp/uwsgi.log'), stdout=fnull
        )
        time.sleep(1)

        print("Feeding backend...")
        q = subprocess.Popen(
            shlex.split('alignak-backend-import --delete cfg/default/_main.cfg'), stdout=fnull
        )
        (stdoutdata, stderrdata) = q.communicate()  # now wait
        assert exit_code == 0


def teardown_module(module):
    print("Stopping Alignak backend...")
    subprocess.call(['uwsgi', '--stop', '/tmp/uwsgi.pid'])
    time.sleep(2)


class tests_actions(unittest2.TestCase):

    def setUp(self):
        # Test application
        self.app = TestApp(
            webapp
        )

        response = self.app.get('/login')
        response.mustcontain('<form role="form" method="post" action="/login">')

        response = self.app.post('/login', {'username': 'admin', 'password': 'admin'})
        # Redirected twice: /login -> / -> /dashboard !
        redirected_response = response.follow()
        redirected_response = redirected_response.follow()
        redirected_response.mustcontain('<div id="dashboard">')
        self.stored_response = redirected_response
        # A host cookie now exists
        assert self.app.cookies['Alignak-WebUI']

    def tearDown(self):
        response = self.app.get('/logout')
        redirected_response = response.follow()
        redirected_response.mustcontain('<form role="form" method="post" action="/login">')

    def test_acknowledge(self):
        """ Actions - acknowledge"""
        print('test actions')

        print('get page /acknowledge/form/add')
        response = self.app.get('/acknowledge/form/add')
        response.mustcontain(
            '<form data-item="acknowledge" data-action="add"'
        )

        # Get Data manager in the session
        session = response.request.environ['beaker.session']
        assert 'current_user' in session and session['current_user']
        assert session['current_user'].get_username() == 'admin'

        datamgr = DataManager(
            user=session['current_user'],
            backend_endpoint='http://127.0.0.1:5000'
        )

        # Get host and user in the backend
        host = datamgr.get_host({'where': {'name': 'webui'}})
        user = datamgr.get_user({'where': {'name': 'admin'}})

        # -------------------------------------------
        # Add an acknowledge
        # Missing element_id!
        data = {
            "action": "add",
            "host": host.id,
            "service": None,
            "sticky": True,
            "persistent": True,
            "notify": True,
            "comment": "User comment",
        }
        self.app.post('/acknowledge/add', data, status=204)

        # Acknowledge an host
        data = {
            "action": "add",
            "elements_type": 'host',    # Default value, can be omitted ...
            "element_id": host.id,
            "sticky": True,
            "persistent": True,
            "notify": True,
            "comment": "User comment",
        }
        response = self.app.post('/acknowledge/add', data)
        assert response.json['status'] == "ok"
        assert response.json['message'] == \
                         "Acknowledge sent for webui. Check request sent for webui. "

        # Acknowledge a service
        service = datamgr.get_service({'where': {'host': host.id, 'name': 'Shinken2-arbiter'}})
        data = {
            "action": "add",
            "elements_type": 'service',
            "element_id": service.id,
            "sticky": True,
            "persistent": True,
            "notify": True,
            "comment": "User comment",
        }
        response = self.app.post('/acknowledge/add', data)
        assert response.json['status'] == "ok"
        assert response.json['message'] == \
                         "Acknowledge sent for webui/Shinken2-arbiter. " \
                         "Check request sent for webui/Shinken2-arbiter. "

        # Acknowledge several services
        service1 = datamgr.get_service({'where': {'host': host.id, 'name': 'Shinken2-arbiter'}})
        service2 = datamgr.get_service({'where': {'host': host.id, 'name': 'Shinken2-reactionner'}})
        data = {
            "action": "add",
            "elements_type": 'service',
            "element_id": [service1.id, service2.id],
            "sticky": True,
            "persistent": True,
            "notify": True,
            "comment": "User comment",
        }
        response = self.app.post('/acknowledge/add', data)
        assert response.json['status'] == "ok"
        assert response.json['message'] == \
                         "Acknowledge sent for webui/Shinken2-arbiter. " \
                         "Check request sent for webui/Shinken2-arbiter. " \
                         "Acknowledge sent for webui/Shinken2-reactionner. " \
                         "Check request sent for webui/Shinken2-reactionner. "

        # Acknowledge several services
        service1 = datamgr.get_service({'where': {'host': host.id, 'name': 'Shinken2-arbiter'}})
        service2 = datamgr.get_service({'where': {'host': host.id, 'name': 'Shinken2-reactionner'}})
        data = {
            "action": "add",
            "elements_type": 'service',
            "element_id": [service1.id, service2.id, 'test'],
            "sticky": True,
            "persistent": True,
            "notify": True,
            "comment": "User comment",
        }
        response = self.app.post('/acknowledge/add', data)
        assert response.json['status'] == "ok"
        assert response.json['message'] == \
                         "Acknowledge sent for webui/Shinken2-arbiter. " \
                         "Check request sent for webui/Shinken2-arbiter. " \
                         "Acknowledge sent for webui/Shinken2-reactionner. " \
                         "Check request sent for webui/Shinken2-reactionner. " \
                         "service element test does not exist. "

    def test_downtime(self):
        """ Actions - downtime"""
        print('test actions')

        print('get page /downtime/form/add')
        response = self.app.get('/downtime/form/add')
        response.mustcontain(
            '<form data-item="downtime" data-action="add"'
        )

        # Current user is admin
        session = response.request.environ['beaker.session']
        assert 'current_user' in session and session['current_user']
        assert session['current_user'].get_username() == 'admin'

        # Data manager
        datamgr = DataManager(
            user=session['current_user'],
            backend_endpoint='http://127.0.0.1:5000'
        )

        # Get host, user and realm in the backend
        host = datamgr.get_host({'where': {'name': 'webui'}})
        user = datamgr.get_user({'where': {'name': 'admin'}})

        now = datetime.utcnow()
        later = now + timedelta(days=2, hours=4, minutes=3, seconds=12)
        now = timegm(now.timetuple())
        later = timegm(later.timetuple())

        # -------------------------------------------
        # Add an downtime
        # Missing livestate_id!
        data = {
            "action": "add",
            "host": host.id,
            "service": None,
            "start_time": now,
            "end_time": later,
            "fixed": False,
            'duration': 86400,
            "comment": "User comment",
        }
        self.app.post('/downtime/add', data, status=204)

        # downtime an host
        data = {
            "action": "add",
            "element_id": host.id,
            "start_time": now,
            "end_time": later,
            "fixed": False,
            'duration': 86400,
            "comment": "User comment",
        }
        response = self.app.post('/downtime/add', data)
        assert response.json['status'] == "ok"
        assert response.json['message'] == \
                         "Downtime sent for webui. Check request sent for webui. "

        # downtime a service
        service = datamgr.get_service({'where': {'host': host.id, 'name': 'Shinken2-arbiter'}})
        data = {
            "action": "add",
            "elements_type": 'service',
            "element_id": service.id,
            "start_time": now,
            "end_time": later,
            "fixed": False,
            'duration': 86400,
            "comment": "User comment",
        }
        response = self.app.post('/downtime/add', data)
        assert response.json['status'] == "ok"
        assert response.json['message'] == \
                         "Downtime sent for webui/Shinken2-arbiter. " \
                         "Check request sent for webui/Shinken2-arbiter. "

        # downtime several services
        service1 = datamgr.get_service({'where': {'host': host.id, 'name': 'Shinken2-arbiter'}})
        service2 = datamgr.get_service({'where': {'host': host.id, 'name': 'Shinken2-reactionner'}})
        data = {
            "action": "add",
            "elements_type": 'service',
            "element_id": [service1.id, service2.id, 'test'],
            "start_time": now,
            "end_time": later,
            "fixed": False,
            'duration': 86400,
            "comment": "User comment",
        }
        response = self.app.post('/downtime/add', data)
        assert response.json['status'] == "ok"
        assert response.json['message'] == \
                         "Downtime sent for webui/Shinken2-arbiter. " \
                         "Check request sent for webui/Shinken2-arbiter. " \
                         "Downtime sent for webui/Shinken2-reactionner. " \
                         "Check request sent for webui/Shinken2-reactionner. " \
                         "service element test does not exist. "

    def test_recheck(self):
        """ Actions - recheck"""
        print('test recheck')

        print('get page /recheck/form/add')
        response = self.app.get('/recheck/form/add')
        response.mustcontain(
            '<form data-item="recheck" data-action="recheck" '
        )

        # Current user is admin
        session = response.request.environ['beaker.session']
        assert 'current_user' in session and session['current_user']
        assert session['current_user'].get_username() == 'admin'

        # Data manager
        datamgr = DataManager(
            user=session['current_user'],
            backend_endpoint='http://127.0.0.1:5000'
        )

        # Get host, user and realm in the backend
        host = datamgr.get_host({'where': {'name': 'webui'}})
        user = datamgr.get_user({'where': {'name': 'admin'}})

        # -------------------------------------------
        # Add a recheck
        # Missing livestate_id!
        data = {
            "host": host.id,
            "service": None,
            "sticky": True,
            "persistent": True,
            "notify": True,
            "comment": "User comment",
        }
        response = self.app.post('/recheck/add', data, status=204)

        # Recheck an host
        data = {
            "elements_type": 'host',
            "element_id": host.id,
            "comment": "User comment",
        }
        response = self.app.post('/recheck/add', data)
        assert response.json['status'] == "ok"
        assert response.json['message'] == "Check request sent for webui. "

        # Recheck a service
        service = datamgr.get_service({'where': {'host': host.id, 'name': 'Shinken2-arbiter'}})
        data = {
            "elements_type": 'service',
            "element_id": service.id,
            "comment": "User comment",
        }
        response = self.app.post('/recheck/add', data)
        assert response.json['status'] == "ok"
        assert response.json['message'] == "Check request sent for webui/Shinken2-arbiter. "

        # Recheck several services
        service1 = datamgr.get_service({'where': {'host': host.id, 'name': 'Shinken2-arbiter'}})
        service2 = datamgr.get_service({'where': {'host': host.id, 'name': 'Shinken2-reactionner'}})
        data = {
            "action": "add",
            "elements_type": 'service',
            "element_id": [service1.id, service2.id, 'test'],
            "comment": "User comment",
        }
        response = self.app.post('/recheck/add', data)
        assert response.json['status'] == "ok"
        assert response.json['message'] == "Check request sent for webui/Shinken2-arbiter. Check request sent for webui/Shinken2-reactionner. service element test does not exist. "


if __name__ == '__main__':
    unittest.main()
