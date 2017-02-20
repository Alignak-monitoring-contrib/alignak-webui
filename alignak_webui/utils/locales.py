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
    Application localization
"""
from __future__ import print_function

import os

# Internationalization / localization
from gettext import GNUTranslations, NullTranslations

# Logs
from logging import getLogger
# pylint: disable=invalid-name
logger = getLogger(__name__)


# --------------------------------------------------------------------------------------------------
# Localization
def init_localization(app):
    """prepare l10n"""

    # -----
    # Application localization
    # -----
    try:
        # Language message file
        lang_filename = os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            "../locales/%s.mo" % app.config.get('locale', 'en_US')
        )
        print("Opening message file %s for locale %s"
              % (lang_filename, app.config.get('locale', 'en_US')))
        translation = GNUTranslations(open(lang_filename, "rb"))
        translation.install(unicode=True)
        _ = translation.gettext
    except IOError:
        print("Locale not found. Using default language messages (English)")
        null_translation = NullTranslations()
        null_translation.install()
        _ = null_translation.gettext
    except Exception as e:  # pragma: no cover - should not happen
        print("Locale not found. Exception: %s" % str(e))
        null_translation = NullTranslations()
        null_translation.install()
        _ = null_translation.gettext

    # Provide translation methods to templates
    app.config['_'] = _
    print(_("Language is English (default)..."))

    return _
