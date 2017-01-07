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

# Better to use exec to load the package information from a version.py file
# so to not have to import the package. as of it, the setup.py do not need to be modified
# for each package that is built from this one...
with open(os.path.join('alignak_webui/version.py')) as fh:
    manifest = {}
    exec(fh.read(), manifest)
# The `manifest` dictionary now contains the package metadata

# Get the package name from the manifest
package_name = manifest["__pkg_name__"]

# Build list of all installable data files
# This will get:
# - all the files from the package `etc` subdir
# - all the files from the package `libexec` subdir
# and will define the appropriate target installation directory
print("\n====================================================")
print("Searching for data files...")
data_files = [
    # ('.', ['LICENSE', 'README.rst', 'requirements.txt', 'version.py'])
]
for subdir, dirs, files in os.walk(package_name):
    target = None
    # Plugins directory
    if subdir and 'libexec' in subdir:
        target = os.path.join('var/libexec/alignak',
                              re.sub(r"^(%s\/|%s$)" % (
                                  os.path.join(package_name, 'libexec'),
                                  os.path.join(package_name, 'libexec')),
                                     "", subdir))
    # Configuration directory
    elif subdir and 'etc' in subdir:
        target = os.path.join('etc/alignak',
                              re.sub(r"^(%s\/|%s$)" % (
                                  os.path.join(package_name, 'etc'),
                                  os.path.join(package_name, 'etc')),
                                     "", subdir))

    if target is None:
        print("Ignoring directory: %s" % (subdir))
        continue

    package_files = []
    for file in files:
        # Ignore files which name starts with __
        if file.startswith('__'):
            continue

        package_files.append(os.path.join(subdir, file))

    if package_files:
        data_files.append((target, package_files))

for (target, origin) in data_files:
    print("Target directory: %s:" % (target))
    for file in origin:
        print(" - %s" % (file))
print("====================================================\n")

# Specific for Read the docs build process
on_rtd = os.environ.get('READTHEDOCS') == 'True'
if on_rtd:
    print "RTD build, no data_files"
    data_files = []

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

    # Package data
    packages=find_packages(),
    # package_data={'': ['LICENSE', 'README.rst', 'requirements.txt', 'version.py']},

    # Where to install distributed files
    data_files = data_files,

    # Dependencies (if some) ...
    install_requires=install_requires,

    # Entry points (if some) ...
    entry_points={
        'console_scripts': [
            'alignak-webui = alignak_webui.app:main',
            'alignak_webui = alignak_webui.app:main_old'
        ],
    }
)
