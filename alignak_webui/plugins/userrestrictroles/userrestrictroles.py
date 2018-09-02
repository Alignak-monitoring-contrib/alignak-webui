#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (C) 2015-2016 F. Mohier

"""
    Plugin User roles restriction
"""

from logging import getLogger

from alignak_webui.utils.plugin import Plugin

# pylint: disable=invalid-name
logger = getLogger(__name__)


class PluginUserRestrictRoles(Plugin):
    """ user backend elements management plugin """

    def __init__(self, webui, plugin_dir, cfg_filenames=None):
        """
        User plugin

        Declare routes for adding, deleting a user

        Overload the default get route to declare filters.
        """
        self.name = 'User restrict roles'
        self.backend_endpoint = 'userrestrictrole'

        self.pages = {}

        super(PluginUserRestrictRoles, self).__init__(webui, plugin_dir, cfg_filenames)
