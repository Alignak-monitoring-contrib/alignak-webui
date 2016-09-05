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
import re
del os.link
from importlib import import_module

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

from alignak_webui import __application__, __version__, __copyright__
from alignak_webui import __releasenotes__, __license__, __doc_url__
from alignak_webui import __name__ as __pkg_name__

package = import_module('alignak_webui')

install_requires = [
    'future',
    'configparser',
    'docopt',
    'bottle>=0.12.9,<0.13',
    'Beaker==1.8.0',
    'CherryPy',
    'pymongo>=3.2',
    'requests>=2.9.1',
    'python-gettext',
    'termcolor',
    'python-dateutil==2.4.2',
    'pytz',
    'alignak_backend_client'
]

# Define paths
if 'linux' in sys.platform or 'sunos5' in sys.platform:
    installation_paths = {
        'bin':     "/usr/bin",
        'var':     "/var/lib/alignak-webui/",
        'etc':     "/etc/alignak-webui",
        'run':     "/var/run/alignak-webui",
        'log':     "/var/log/alignak-webui"
    }
elif 'bsd' in sys.platform or 'dragonfly' in sys.platform:
    installation_paths = {
        'bin':     "/usr/local/bin",
        'var':     "/usr/local/libexec/alignak-webui",
        'etc':     "/usr/local/etc/alignak-webui",
        'run':     "/usr/local/var/run/alignak-webui",
        'log':     "/usr/local/var/log/alignak-webui"
    }
else:
    print "Unsupported platform, sorry!"
    exit(1)

data_files = [
    (installation_paths['etc'], ['etc/settings.cfg'])
]

# Specific for Read the docs build process
on_rtd = os.environ.get('READTHEDOCS') == 'True'
if on_rtd:
    print "RTD build, no data_files"
    data_files = []

setup(
    name=__pkg_name__,
    version=__version__,

    license=__license__,

    # metadata for upload to PyPI
    author="Frédéric MOHIER",
    author_email="frederic.mohier@gmail.com",
    keywords="alignak web ui",
    url="https://github.com/Alignak-monitoring-contrib/alignak-webui",
    description=package.__doc__.strip(),
    long_description=open('README.rst').read(),

    zip_safe=False,

    packages=find_packages(),
    include_package_data=True,
    # package_data={
        # 'sample': ['package_data.dat'],
    # },
    data_files=data_files,

    install_requires=install_requires,

    entry_points={
        'console_scripts': [
            'alignak_webui = alignak_webui.app:main',
        ],
    },

    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Bottle',
        'Intended Audience :: Developers',
        'Intended Audience :: Customer Service',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Topic :: System :: Monitoring',
        'Topic :: System :: Systems Administration'
    ]
)
