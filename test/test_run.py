from __future__ import print_function

import os
import shlex
import subprocess
import time

import unittest2

os.environ['TEST_WEBUI'] = '1'
os.environ['ALIGNAK_WEBUI_CONFIGURATION_FILE'] = \
    os.path.join(os.path.abspath(os.path.dirname(__file__)), 'settings.cfg')
print("Configuration file: %s" % os.environ['ALIGNAK_WEBUI_CONFIGURATION_FILE'])


class TestStart(unittest2.TestCase):
    def test_start_application_uwsgi(self):
        """ Start application with uwsgi"""
        print('test application start error')

        os.getcwd()
        print ("Launching application with UWSGI ...")

        # No console output for the applications backend ...
        fnull = open(os.devnull, 'w')
        subprocess.Popen(
            shlex.split('uwsgi --plugin python -w alignakwebui:app --socket 0.0.0.0:5000 '
                        '--protocol=http --enable-threads --pidfile /tmp/uwsgi.pid '
                        '--logto /tmp/uwsgi.log'), stdout=fnull
        )
        time.sleep(5)

        subprocess.call(['uwsgi', '--stop', '/tmp/uwsgi.pid'])
        time.sleep(1)

    def test_start_application_error(self):
        """ Start application with errors"""
        print('test application start error')

        print("Launching application ...")
        dir_path = os.path.dirname(os.path.realpath(__file__))
        os.chdir(os.path.join(dir_path, "../alignak_webui"))
        fnull = open(os.devnull, 'w')
        exit_code = subprocess.call(
            shlex.split('python app.py -X'), stdout=fnull
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
            shlex.split('python app.py -v'), stdout=fnull
        )
        assert exit_code == 0

        print("Launching application with bad configuration file...")
        os.environ['ALIGNAK_WEBUI_CONFIGURATION_FILE'] = \
            os.path.join(os.path.abspath(os.path.dirname(__file__)), 'settings.bad')
        print("Configuration file", os.environ['ALIGNAK_WEBUI_CONFIGURATION_FILE'])
        exit_code = subprocess.call(
            shlex.split('python app.py settings.bad'), stdout=fnull
        )
        assert exit_code == 1
        os.environ['ALIGNAK_WEBUI_CONFIGURATION_FILE'] = \
            os.path.join(os.path.abspath(os.path.dirname(__file__)), 'settings.cfg')
        print("Configuration file", os.environ['ALIGNAK_WEBUI_CONFIGURATION_FILE'])

        print("Launching application with CLI help...")
        exit_code = subprocess.call(
            shlex.split('python app.py -h'), stdout=fnull
        )
        assert exit_code == 0

        print("Launching application with CLI exit...")
        exit_code = subprocess.call(
            shlex.split('python app.py -x'), stdout=fnull
        )
        print("Launching application with CLI exit...", exit_code)
        assert exit_code == 99

    def test_start_application(self):
        """ Start application stand alone"""
        print('test application default start')

        fnull = open(os.devnull, 'w')

        dir_path = os.path.dirname(os.path.realpath(__file__))
        os.chdir(os.path.join(dir_path, "../alignak_webui"))
        print("Launching application default...")
        process = subprocess.Popen(
            shlex.split('python app.py'), stdout=fnull
        )
        print('PID = ', process.pid)
        time.sleep(2.0)
        print("Killing application ...")
        process.terminate()

        print("Launching application debug mode...")
        process = subprocess.Popen(
            shlex.split('python app.py -d'), stdout=fnull
        )
        print('PID = ', process.pid)
        time.sleep(2.0)
        print("Killing application ...")
        process.terminate()

    def test_start_application_configuration(self):
        """ Start application with configuration"""
        print('test application configuration start')

        fnull = open(os.devnull, 'w')

        dir_path = os.path.dirname(os.path.realpath(__file__))
        os.chdir(os.path.join(dir_path, "../alignak_webui"))
        print("Launching application with configuration parameters...")
        process = subprocess.Popen(
            shlex.split('python app.py -b http://127.0.0.1:8888 -n 127.0.0.1 -p 9999'), stdout=fnull
        )
        print('PID = ', process.pid)
        time.sleep(2.0)
        print("Killing application ...")
        process.terminate()

        print("Launching application with configuration file...")
        process = subprocess.Popen(
            shlex.split('python app.py ../test/settings.cfg'), stdout=fnull
        )
        print('PID = ', process.pid)
        time.sleep(2.0)
        print("Killing application ...")
        process.terminate()

        print("Launching application with configuration file...")
        process = subprocess.Popen(
            shlex.split('python app.py ../test/settings.fr'), stdout=fnull
        )
        print('PID = ', process.pid)
        time.sleep(2.0)
        print("Killing application ...")
        process.terminate()
