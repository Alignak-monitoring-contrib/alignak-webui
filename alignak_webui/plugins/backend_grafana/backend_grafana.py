#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2017:
#   Frederic Mohier, frederic.mohier@alignak.net
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

"""
    Plugin backend Grafana

    This plugin allows to display Alignak backend Grafana configuration.
"""

from logging import getLogger

from alignak_webui.utils.plugin import Plugin

# pylint: disable=invalid-name
logger = getLogger(__name__)


class PluginBackendGrafana(Plugin):
    """Backand Grafana plugin"""

    def __init__(self, webui, plugin_dir, cfg_filenames=None):
        """Alignak plugin"""
        self.name = 'BackendGrafana'
        self.backend_endpoint = 'grafana'

        self.pages = {}

        super(PluginBackendGrafana, self).__init__(webui, plugin_dir, cfg_filenames)
