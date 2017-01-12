#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2017:
#   Frederic Mohier, frederic.mohier@alignak.net
#

"""
    Alignak - Web User Interface
"""
# Package name
__pkg_name__ = u"alignak_webui"

# Checks types for PyPI keywords
# Used for:
# - PyPI keywords
# - directory where to store files in the Alignak configuration (eg. arbiter/packs/checks_type)
__checks_type__ = u"demo"

# Application manifest
__application__ = u"Alignak-WebUI"

__version__ = u"0.6.6"
__short_version__ = u"0.6"
__author__ = u"Frédéric Mohier"
__author_email__ = u"frederic.mohier@alignak.net"
__copyright__ = u"(c) 2015-2017 - %s" % __author__
__license__ = u"GNU Affero General Public License, version 3"
__git_url__ = "https://github.com/Alignak-monitoring-contrib/alignak-webui"
__doc_url__ = "http://alignak-web-ui.readthedocs.io/?badge=latest"
__description__ = u"Alignak - Web User Interface"
__releasenotes__ = u"""Alignak monitoring framework Web User Interface"""

__classifiers__ = [
    'Development Status :: 5 - Production/Stable',
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

# Application manifest
manifest = {
    'name': __application__,
    'version': __version__,
    'author': __author__,
    'description': __description__,
    'copyright': __copyright__,
    'license': __license__,
    'release': __releasenotes__,
    'url': __git_url__,
    'doc': __doc_url__
}
