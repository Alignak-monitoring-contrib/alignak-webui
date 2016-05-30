#!/usr/bin/env bash
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

# echo 'Build Sphinx API doc'
# cd docs
# sphinx-apidoc -f -T -d 2 -M -o source/dev/ ../alignak_webui
# make html
# cd ..

echo 'pep8 ...'
pep8 --max-line-length=100 --exclude='*.pyc, *.cfg, *.log, *.log.*' --ignore='E402' alignak_webui/*
if [ $? -ne 0 ]; then
    echo "PEP8 not compliant"
    exit
fi
echo 'pylint ...'
pylint --rcfile=.pylintrc alignak_webui/
if [ $? -ne 0 ]; then
    echo "pylint not compliant"
    exit
fi
# echo 'pep257 ...'
# pep257 --select=D300 alignak_webui

echo 'tests ...'
cd test
coverage erase
nosetests -xvv --nologcapture --process-restartworker --processes=1 --process-timeout=300 --with-coverage --cover-package=alignak_webui test_helper.py test_settings.py test_run.py test_alignak_webui.py
if [ $? -ne 0 ]; then
    echo "main tests not compliant"
    exit
fi
nosetests -xvv --process-restartworker --processes=1 --process-timeout=300 --with-coverage --cover-package=alignak_webui test_items.py test_datamanager.py test_datatable.py test_backend_glpi.py
if [ $? -ne 0 ]; then
    echo "data tests not compliant"
    exit
fi
nosetests -xvv --nologcapture --process-restartworker --processes=1 --process-timeout=300 --with-coverage --cover-package=alignak_webui test_web*.py
if [ $? -ne 0 ]; then
    echo "web tests not compliant"
    exit
fi
echo 'coverage combine ...'
coverage combine
coverage report -m
# cd ..
# mv test/.coverage . && coveralls -v
