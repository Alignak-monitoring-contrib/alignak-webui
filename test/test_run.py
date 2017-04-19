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
import shlex
import subprocess
import time

import unittest2

# Set test mode ...
os.environ['ALIGNAK_WEBUI_TEST'] = '1'
os.environ['ALIGNAK_WEBUI_DEBUG'] = '1'
os.environ['ALIGNAK_WEBUI_CONFIGURATION_FILE'] = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'settings.cfg')
print("Configuration file", os.environ['ALIGNAK_WEBUI_CONFIGURATION_FILE'])


class TestStart(unittest2.TestCase):
    def test_start_application_uwsgi(self):
        """ Start application with uwsgi"""
        print('test application start error')

        os.getcwd()
        print ("Launching application with UWSGI ...")

        test_dir = os.path.dirname(os.path.realpath(__file__))
        print("Dir: %s" % test_dir)

        print("Starting Alignak WebUI...")
        fnull = open(os.devnull, 'w')
        pid = subprocess.Popen(
            shlex.split('uwsgi --plugin python -w test.alignakwebui:app --socket 0.0.0.0:5001 '
                        '--protocol=http --enable-threads --pidfile /tmp/uwsgi.pid'), stdout=fnull
        )
        time.sleep(5)

        subprocess.call(['uwsgi', '--stop', '/tmp/uwsgi.pid'])
        time.sleep(1)

    def test_start_application_error(self):
        """ Start application with command line parameters error"""
        print('test application start error')

        print("Launching application ...")
        dir_path = os.path.dirname(os.path.realpath(__file__))
        os.chdir(os.path.join(dir_path, "../alignak_webui"))
        fnull = open(os.devnull, 'w')
        exit_code = subprocess.call(
            shlex.split('python ../alignak_webui/app.py -X'), stdout=fnull, stderr=fnull
        )
        assert exit_code == 64

    def test_start_application_version(self):
        """ Start application to get version"""
        print('test application version start')

        fnull = open(os.devnull, 'w')

        dir_path = os.path.dirname(os.path.realpath(__file__))
        os.chdir(os.path.join(dir_path, "../alignak_webui"))
        print("Launching application with version number...")
        exit_code = subprocess.call(
            shlex.split('python ../alignak_webui/app.py -v'), stdout=fnull, stderr=fnull
        )
        assert exit_code == 0

    def test_start_application_bad_configuration(self):
        """ Start application with bad configuration file"""

        print("Launching application with bad configuration file...")
        os.environ['ALIGNAK_WEBUI_CONFIGURATION_FILE'] = \
            os.path.join(os.path.abspath(os.path.dirname(__file__)), 'settings.bad')
        print("Configuration file", os.environ['ALIGNAK_WEBUI_CONFIGURATION_FILE'])
        exit_code = subprocess.call(
            shlex.split('python ../alignak_webui/app.py settings.bad')
        )
        assert exit_code == 1
        os.environ['ALIGNAK_WEBUI_CONFIGURATION_FILE'] = \
            os.path.join(os.path.abspath(os.path.dirname(__file__)), 'settings.cfg')
        print("Configuration file", os.environ['ALIGNAK_WEBUI_CONFIGURATION_FILE'])

    def test_start_application_help(self):
        """ Start application with help parameter"""

        print("Launching application with CLI help...")
        exit_code = subprocess.call(
            shlex.split('python ../alignak_webui/app.py -h')
        )
        assert exit_code == 0

    def test_start_application(self):
        """ Start application stand alone"""
        print('test application default start')

        fnull = open(os.devnull, 'w')

        dir_path = os.path.dirname(os.path.realpath(__file__))
        os.chdir(os.path.join(dir_path, "../alignak_webui"))
        print("Launching application default...")
        process = subprocess.Popen(
            shlex.split('python ../alignak_webui/app.py'), stdout=fnull, stderr=fnull
        )
        print('PID = ', process.pid)
        time.sleep(2.0)
        print("Killing application ...")
        process.terminate()

    def test_start_application_debug(self):
        """ Start application stand alone - debug mode"""

        print("Launching application debug mode...")
        process = subprocess.Popen(
            shlex.split('python ../alignak_webui/app.py -d')
        )
        print('PID = ', process.pid)
        time.sleep(2.0)
        print("Killing application ...")
        process.terminate()

    def test_start_application_configuration(self):
        """ Start application with configuration parameters"""
        print('test application configuration start')

        fnull = open(os.devnull, 'w')

        dir_path = os.path.dirname(os.path.realpath(__file__))
        os.chdir(os.path.join(dir_path, "../alignak_webui"))
        print("Launching application with configuration parameters...")
        process = subprocess.Popen(
            shlex.split('python ../alignak_webui/app.py -b http://127.0.0.1:8888 -n 127.0.0.1 -p 9999 --ws http://127.0.0.1:8888'),
            stdout = fnull, stderr = fnull
        )
        print('PID = ', process.pid)
        time.sleep(2.0)
        print("Killing application ...")
        process.terminate()

    def test_start_application_configuration_file(self):
        """ Start application with configuration"""

        print("Launching application with configuration file...")
        process = subprocess.Popen(
            shlex.split('python ../alignak_webui/app.py ../etc/settings.cfg')
        )
        print('PID = ', process.pid)
        time.sleep(2.0)
        print("Killing application ...")
        process.terminate()

        print("Launching application with configuration file...")
        process = subprocess.Popen(
            shlex.split('python ../alignak_webui/app.py ../test/settings.fr')
        )
        print('PID = ', process.pid)
        time.sleep(2.0)
        print("Killing application ...")
        process.terminate()

    def test_start_application_environment(self):
        """ Start application with environment variables"""

        print("Launching application with WS configuration in environment...")
        os.environ['ALIGNAK_WEBUI_WS'] = 'http://127.0.0.1:8888'
        os.environ['ALIGNAK_WEBUI_LOG'] = '/tmp'
        process = subprocess.Popen(
            shlex.split('python ../alignak_webui/app.py')
        )
        print('PID = ', process.pid)
        time.sleep(2.0)
        print("Killing application ...")
        process.terminate()

        print("Launching application with configuration file...")
        process = subprocess.Popen(
            shlex.split('python ../alignak_webui/app.py ../test/settings.fr')
        )
        print('PID = ', process.pid)
        time.sleep(2.0)
        print("Killing application ...")
        process.terminate()
