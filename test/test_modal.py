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
os.environ['ALIGNAK_WEBUI_DEBUG'] = '1'
os.environ['ALIGNAK_WEBUI_CONFIGURATION_FILE'] = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'settings.cfg')
print("Configuration file", os.environ['ALIGNAK_WEBUI_CONFIGURATION_FILE'])

import alignak_webui.app

from webtest import TestApp

backend_process =  None

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


def teardown_module(module):
    print("Stopping Alignak backend...")
    global backend_process
    backend_process.kill()
    # subprocess.call(['pkill', 'alignak-backend'])
    print("Stopped")
    time.sleep(2)


class TestModal(unittest2.TestCase):

    def setUp(self):
        # Test application
        self.app = TestApp(alignak_webui.app.session_app)

        response = self.app.get('/login')
        response.mustcontain('<form role="form" method="post" action="/login">')
        response = self.app.post('/login', {'username': 'admin', 'password': 'admin'})

    def tearDown(self):
        self.app.get('/logout')

    def test_modal_about_box(self):
        """Modal about box"""
        print('test modal about box')

        # /modal/about
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

        response = self.app.get('/modal/about')
        print('Response: %s' % response)
        response.mustcontain(
            '<div class="modal-header">',
            '<div class="modal-body">',
            '<!-- About Form -->',
            '<input readonly="" id="app_version" type="text" class="form-control" placeholder="Not set" class="input-medium" value="%s, version: %s">' % (manifest['name'], manifest['version']),
            '<input readonly="" id="app_copyright" type="text" class="form-control" placeholder="Not set" class="input-medium" value="%s">' % manifest['copyright'],
            '<a id="alignak_url" href="http://www.alignak.net" target="_blank">http://www.alignak.net/</a>',
            '<a id="app_url" href="%s" target="_blank">%s</a>' % (manifest['url'], manifest['url']),
            '<a id="app_doc" href="%s" target="_blank">%s</a>' % (manifest['doc'], manifest['doc']),
            '<textarea id="app_release" readonly="" rows="5" class="form-control">%s</textarea>' % (manifest['release'])
        )

    def test_modal_waiting(self):
        """Modal waiting"""
        print('test modal waiting')

        # /modal/waiting
        response = self.app.get('/modal/waiting')
        print('Response: %s' % response)
        response.mustcontain(
            '<!-- A modal div that will be filled and shown to create a waiting box... -->',
            '<div id="waitingModal"',
            '<div class="modal-header text-center">',
            '<div class="modal-body">',
            '<h4 class="modal-title">Default waiting message</h4>',
        )
