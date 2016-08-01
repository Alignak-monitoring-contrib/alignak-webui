from __future__ import print_function

import os
import shlex
import subprocess
import time

import unittest2

os.environ['TEST_WEBUI'] = '1'
os.environ['ALIGNAK_WEBUI_CONFIGURATION_FILE'] = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                            'settings.cfg')
print("Configuration file: %s" % os.environ['ALIGNAK_WEBUI_CONFIGURATION_FILE'])


class TestStart(unittest2.TestCase):
    def test_3_0_start_application_uwsgi(self):
        print('test application start error')

        os.getcwd()
        print ("Launching application with UWSGI ...")
        # uwsgi process is not stoppable ...
        # os.chdir("..")
        # FNULL = open(os.devnull, 'w')
        # pid = subprocess.Popen(
        # shlex.split('bash run.sh')
        # )
        # print ("PID: %s" % pid)
        # time.sleep(5)

        # pid.kill()
        # os.chdir(mydir)

    def test_3_1_start_application_error(self):
        print('test application start error')

        mydir = os.getcwd()
        print("Launching application ...")
        os.chdir("../alignak_webui")
        exit_code = subprocess.call(
            shlex.split('python app.py -X')
        )
        assert exit_code == 64
        os.chdir(mydir)

    def test_3_2_start_application_version(self):
        print('test application version start')

        mydir = os.getcwd()
        os.chdir("../alignak_webui")
        print("Launching application with version number...")
        exit_code = subprocess.call(
            shlex.split('python app.py -v')
        )
        assert exit_code == 0

        print("Launching application with bad configuration file...")
        os.environ['ALIGNAK_WEBUI_CONFIGURATION_FILE'] = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                                    'settings.bad')
        print("Configuration file", os.environ['ALIGNAK_WEBUI_CONFIGURATION_FILE'])
        exit_code = subprocess.call(
            shlex.split('python app.py settings.bad')
        )
        assert exit_code == 1
        os.environ['ALIGNAK_WEBUI_CONFIGURATION_FILE'] = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                                    'settings.cfg')
        print("Configuration file", os.environ['ALIGNAK_WEBUI_CONFIGURATION_FILE'])

        print("Launching application with CLI help...")
        exit_code = subprocess.call(
            shlex.split('python app.py -h')
        )
        assert exit_code == 0

        print("Launching application with CLI exit...")
        exit_code = subprocess.call(
            shlex.split('python app.py -x')
        )
        print("Launching application with CLI exit...", exit_code)
        assert exit_code == 99
        os.chdir(mydir)

    def test_3_3_start_application(self):
        print('test application default start')

        mydir = os.getcwd()
        os.chdir("../alignak_webui")
        print("Launching application default...")
        process = subprocess.Popen(
            shlex.split('python app.py')
        )
        print('PID = ', process.pid)
        time.sleep(2.0)
        print("Killing application ...")
        process.terminate()

        print("Launching application debug mode...")
        process = subprocess.Popen(
            shlex.split('python app.py -d')
        )
        print('PID = ', process.pid)
        time.sleep(2.0)
        print("Killing application ...")
        process.terminate()
        os.chdir(mydir)

    def test_3_4_start_application_configuration(self):
        print('test application configuration start')

        mydir = os.getcwd()
        os.chdir("../alignak_webui")
        print("Launching application with configuration parameters...")
        process = subprocess.Popen(
            shlex.split('python app.py -b http://127.0.0.1:8888 -n 127.0.0.1 -p 9999')
        )
        print('PID = ', process.pid)
        time.sleep(2.0)
        print("Killing application ...")
        process.terminate()

        print("Launching application with configuration file...")
        process = subprocess.Popen(
            shlex.split('python app.py ../test/settings.cfg')
        )
        print('PID = ', process.pid)
        time.sleep(2.0)
        print("Killing application ...")
        process.terminate()

        print("Launching application with configuration file...")
        process = subprocess.Popen(
            shlex.split('python app.py ../test/settings.fr')
        )
        print('PID = ', process.pid)
        time.sleep(2.0)
        print("Killing application ...")
        process.terminate()
        os.chdir(mydir)


if __name__ == '__main__':
    unittest2.main()
