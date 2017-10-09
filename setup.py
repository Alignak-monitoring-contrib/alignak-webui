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

import os
import sys

try:
    from setuptools import setup, find_packages
except:
    sys.exit("Error: missing python-setuptools library")

try:
    python_version = sys.version_info
except:
    python_version = (1, 5)
if python_version < (2, 7):
    sys.exit("This application requires a minimum Python 2.7.x, sorry!")
elif python_version >= (3,):
    sys.exit("This application is not yet compatible with Python 3.x, sorry!")

try:
    import distutils.cmd
    import distutils.log
    import distutils.core
    from distutils.core import setup
    from distutils.command.install_data import install_data as _install_data
except:
    sys.exit("Error: missing python-distutils library")

# Overloading setup.py install_data
class install_data(_install_data):
    """Overload the default data installation"""
    def run(self):
        """Overload the default copy of files:"""
        self.announce("\n====================================================", distutils.log.INFO)
        self.announce("Installing data files copy...", distutils.log.INFO)
        self.announce("Installation directory: %s" % self.install_dir, distutils.log.INFO)

        self.announce("\n====================================================", distutils.log.INFO)
        self.announce("Before data files copy...", distutils.log.INFO)
        self.announce("Installation directory: %s" % self.install_dir, distutils.log.INFO)
        for (target, origin) in self.data_files:
            for file in origin:
                filename = os.path.basename(file)
                self.announce(" - file: '%s'" % (file), distutils.log.INFO)
                if os.path.isfile(os.path.join(self.install_dir, file)):
                    self.announce(" - found an existing '%s'" % (filename), distutils.log.INFO)
        self.announce("====================================================\n", distutils.log.INFO)

        # Setuptools install_data ...
        _install_data.run(self)

        # After data files installation ...
        # ... try to find if an installer file exists
        # ... and then run this installer.
        self.announce("\n====================================================", distutils.log.INFO)
        self.announce("After data files copy...", distutils.log.INFO)
        for (target, origin) in self.data_files:
            for file in origin:
                if os.path.basename(file) in ['setup.sh']:
                    filename = os.path.basename(file)
                    self.announce(" - found '%s'" % (filename), distutils.log.INFO)

                    # Run found installation script
                    self.announce("\n----------------------------------------------------",
                                  distutils.log.INFO)
                    self.announce(" - running '%s'..." % (
                        os.path.join(self.install_dir, target, filename)), distutils.log.INFO)
                    exit_code = subprocess.call(os.path.join(self.install_dir, target, filename))
                    self.announce(" - result: %s" % (exit_code), distutils.log.INFO)
                    if exit_code > 0:
                        self.announce("\n****************************************************",
                                      distutils.log.INFO)
                        self.announce("Some errors were encountered during the installation \n"
                                      "script execution! Please check out the former log to \n"
                                      "get more information about the encountered problems.",
                                      distutils.log.INFO)
                        self.announce("****************************************************\n",
                                      distutils.log.INFO)
                    self.announce("----------------------------------------------------\n",
                                  distutils.log.INFO)
        self.announce("====================================================\n", distutils.log.INFO)

# Better to use exec to load the package information from a version.py file
# so to not have to import the package. as of it, the setup.py do not need to be modified
# for each package that is built from this one...
with open(os.path.join('alignak_webui/__init__.py')) as fh:
    manifest = {}
    exec(fh.read(), manifest)
# The `manifest` dictionary now contains the package metadata

# Get the package name from the manifest
package_name = manifest["__pkg_name__"]

data_files=[('etc/alignak-webui', ['etc/settings.cfg', 'etc/uwsgi.ini', 'etc/logging.json']),
            ('bin', ['bin/alignak-webui-uwsgi']),
            ('var/log/alignak-webui', [])]

# Specific for Read the docs build process
on_rtd = os.environ.get('READTHEDOCS') == 'True'
if on_rtd:
    print "RTD build, no data_files"
    data_files = []
print("Data files: %s" % data_files)

setup(
    # Package name and version
    name=manifest["__pkg_name__"],
    version=manifest["__version__"],

    # Metadata for PyPI
    author=manifest["__author__"],
    author_email=manifest["__author_email__"],
    keywords="alignak monitoring webui",
    url=manifest["__git_url__"],
    license=manifest["__license__"],
    description=manifest["__description__"],
    long_description=open('README.rst').read(),

    classifiers = manifest["__classifiers__"],

    # Unzip Egg
    zip_safe=False,

    # Specific data files installer method
    cmdclass={
        "install_data": install_data
    },

    # Package data
    packages=find_packages(),
    include_package_data=True,
    # package_data = {'alignak_webui': ['alignak_webui/*']},
    # package_data={'': ['LICENSE', 'README.rst', 'requirements.txt', 'version.py']},

    # Where to install distributed files
    data_files=data_files,

    # Dependencies (if some) ...
    install_requires=[
        'future', 'configparser', 'docopt',
        'bottle>=0.12.0,<0.13', 'Beaker>=1.8.0', 'CherryPy<9.0.0',
        'pymongo>=3.2', 'requests>=2.9.1',
        'python-gettext', 'termcolor',
        'python-dateutil==2.4.2', 'pytz',
        'uwsgi',
        'alignak-backend-client'
    ],

    # Entry points (if some) ...
    entry_points={
        'console_scripts': [
            'alignak-webui = alignak_webui.app:main'
        ],
    }
)
