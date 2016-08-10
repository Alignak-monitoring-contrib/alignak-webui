#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (C) 2015-2016 F. Mohier

"""
    Plugin User roles restriction
"""

import json

from collections import OrderedDict

from logging import getLogger
from bottle import request, response

from alignak_webui import _
from alignak_webui.utils.plugin import Plugin

logger = getLogger(__name__)


class PluginUserRestrictRoles(Plugin):
    """ user backend elements management plugin """

    def __init__(self, app, cfg_filenames=None):
        """
        User plugin

        Declare routes for adding, deleting a user

        Overload the default get route to declare filters.
        """
        self.name = 'User restrict roles'
        self.backend_endpoint = 'userrestrictrole'

        self.pages = {}

        super(PluginUserRestrictRoles, self).__init__(app, cfg_filenames)
