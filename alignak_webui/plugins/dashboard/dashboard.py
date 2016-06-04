#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2016:
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

"""
    Plugin Dashboard
"""

import json
from logging import getLogger
from bottle import request

logger = getLogger(__name__)

# Will be valued by the plugin loader
webui = None


# Our page
def get_page():
    """
    Display dashboard page
    """
    user = request.environ['beaker.session']['current_user']
    target_user = request.environ['beaker.session']['target_user']
    datamgr = request.environ['beaker.session']['datamanager']

    username = user.get_username()
    if not target_user.is_anonymous():
        username = target_user.get_username()

    # Look for the widgets as the json entry
    saved_widgets = datamgr.get_user_preferences(username, 'widgets', {'widgets': []})
    # If void, create an empty one
    if not saved_widgets:  # pragma: no cover - widgets may exist or not ...
        datamgr.set_user_preferences(username, 'widgets', {'widgets': []})
        saved_widgets = {'widgets': []}

    widgets = []
    for w in saved_widgets['widgets']:
        if 'id' not in w or 'position' not in w:
            continue

        # by default the widget is for /dashboard
        w['for'] = w.get('for', 'dashboard')
        if not w['for'] == 'dashboard':  # pragma: no cover - not testable yet
            # Not a dashboard widget? I don't want it so
            continue

        options = w.get('options', {})
        collapsed = w.get('collapsed', '0')

        options["wid"] = w["id"]
        options["collapsed"] = collapsed
        w['options'] = options
        w['options_json'] = json.dumps(options)
        args = {'wid': w['id'], 'collapsed': collapsed}
        args.update(options)
        w['options_uri'] = '&'.join('%s=%s' % (k, v) for (k, v) in args.iteritems())
        widgets.append(w)

    return {
        'action_bar': len(widgets) != 0,
        'dashboard_widgets': widgets,
        'title': request.query.get('title', _('Dashboard'))
    }


pages = {
    get_page: {
        'name': 'Dashboard',
        'route': '/dashboard',
        'view': 'dashboard'
    }
}
