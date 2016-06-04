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
    Application localization
"""
import os
import traceback


# Internationalization / localization
from gettext import GNUTranslations, NullTranslations, gettext as _

# Logs
from logging import getLogger
logger = getLogger(__name__)


# --------------------------------------------------------------------------------------------------
# Localization
def init_localization(language):
    """prepare l10n"""

    try:
        # Language message file
        filename = os.path.join(
            os.path.abspath(os.path.dirname(__file__)), "../res/%s.mo" % language
        )
        logger.info("Opening message file %s for locale %s", filename, language)
        translation = GNUTranslations(open(filename, "rb"))
        translation.install()
    except IOError:
        logger.warning("Locale not found. Using default messages")
        logger.debug("Backtrace: %s", traceback.format_exc())
        default = NullTranslations()
        default.install()
    except Exception as e:
        logger.error("Locale not found. Exception: %s", str(e))
        logger.debug("Backtrace: %s", traceback.format_exc())
        default = NullTranslations()
        default.install()
    logger.info(_("Language is English (default)..."))
