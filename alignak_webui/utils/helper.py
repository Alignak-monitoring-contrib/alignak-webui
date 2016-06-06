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
    This module contains helper functions used in HTML application templates.

    An ``helper`` object linked to the application is created by this module to be used in all
    the application.
"""
import re
import time
import math

from logging import getLogger
logger = getLogger(__name__)


class Helper(object):
    """
    Helper functions
    """
    def __init__(self):
        """ Empty ... """
        pass

    @staticmethod
    def print_date(timestamp, fmt='%Y-%m-%d %H:%M:%S'):
        """
        For a unix timestamp return something like
        2015-09-18 00:00:00

        Returns n/a if provided timestamp is not valid

        :param timestamp: unix timestamp
        :type timestamp: long int
        :param fmt: python date/time format string
        :type fmt: sting
        :return: formatted date
        :rtype: string
        """
        if not timestamp:
            return 'n/a'

        if fmt:
            return time.strftime(fmt, time.localtime(timestamp))
        else:
            return time.asctime(time.localtime(timestamp))

    @staticmethod
    def print_duration(timestamp, duration_only=False, x_elts=0, ts_is_duration=False):
        """
        For a unix timestamp return something like
        1h 15m 12s

        Returns n/a if provided timestamp is not valid

        Returns:
        in 1h 15m 12s
        Now
        1h 15m 12s ago

        Returns 1h 15m 12s if only_duration is True

        :param timestamp: unix timestamp
        :type timestamp: long int
        :param fmt: python date/time format string
        :type fmt: sting
        :return: formatted date
        :rtype: string
        """
        if not timestamp:
            return 'n/a'

        # Get the seconds elapsed since the timestamp
        seconds = timestamp
        if not ts_is_duration:
            seconds = int(time.time()) - int(timestamp)

        # If it's now, say it :)
        if seconds == 0:
            return _('Now')

        in_future = False

        # Remember if it's in the future or not
        if seconds < 0:
            in_future = True

        # Now manage all case like in the past
        seconds = abs(seconds)

        seconds = long(round(seconds))
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)
        weeks, days = divmod(days, 7)
        months, weeks = divmod(weeks, 4)
        years, months = divmod(months, 12)

        minutes = long(minutes)
        hours = long(hours)
        days = long(days)
        weeks = long(weeks)
        months = long(months)
        years = long(years)

        duration = []
        if years > 0:
            duration.append(_('%dy') % years)
        else:
            if months > 0:
                duration.append(_('%dM') % months)
            if weeks > 0:
                duration.append(_('%dw') % weeks)
            if days > 0:
                duration.append(_('%dd') % days)
            if hours > 0:
                duration.append(_('%dh') % hours)
            if minutes > 0:
                duration.append(_('%dm') % minutes)
            if seconds > 0:
                duration.append(_('%ds') % seconds)

        # Now filter the number of printed elements if ask
        if x_elts >= 1:
            duration = duration[:x_elts]

        # Maybe the user just want the duration
        if duration_only:
            return ' '.join(duration)

        # Now manage the future or not print
        if in_future:
            return _('in ') + ' '.join(duration)
        else:
            return _('') + ' '.join(duration) + _(' ago')

    @staticmethod
    def get_on_off(status=False, title=None, message=''):
        """
        Give an enabled/disabled state based on glyphicons with optional title and message
        """
        if not title:
            title = _('Enabled') if status else _('Disabled')

        if isinstance(title, list):
            if status:
                title = title[0]
            else:
                title = title[1]

        if status:
            return '''<i title="%s" class="fa fa-fw fa-check text-success">%s</i>''' % (
                title, message
            )
        else:
            return '''<i title="%s" class="fa fa-fw fa-close text-danger">%s</i>''' % (
                title, message
            )

    @staticmethod
    def get_html_business_impact(business_impact, icon=True, text=False):
        """
            Give a business impact as text and stars if needed.
            If text=True, returns text+stars, else returns stars only ...
        """
        if not 0 <= business_impact <= 5:
            return 'n/a - value'

        if not icon and not text:
            return 'n/a - parameters'

        bi_texts = {
            0: _('None'),
            1: _('Low'),
            2: _('Normal'),
            3: _('Important'),
            4: _('Very important'),
            5: _('Business critical')
        }

        nb_stars = max(0, business_impact - 2)
        stars = '<i class="fa fa-star text-primary"></i>' * nb_stars

        if not text:
            return stars

        if not icon:
            return bi_texts.get(business_impact, _('Unknown'))

        text = "%s %s" % (bi_texts.get(business_impact, _('Unknown')), stars)
        return text.strip()

    @staticmethod
    def get_urls(obj, url, default_title="Url", default_icon="globe", popover=False):
        """
        Returns formatted HTML for an element URL

        url string may contain a list of urls separated by | (pipe symbol)

        Each url may be formatted as:
            - url,,description
            - title::description,,url
            - title,,icon::description,,url

        description is optional

        If title is not specified, default_title is used as title
        If icon is not specified, default_icon is used as icon

        If popover is true, a bootstrap popover is built, else a standard link ...
        """
        logger.debug(
            "get_urls: %s / %s / %s / %d", url, default_title, default_icon, popover
        )

        result = []
        for item in url.split('|'):
            try:
                (title, url) = item.split('::')
            except Exception:
                title = "%s,,%s" % (default_title, default_icon)
                url = item

            try:
                (title, icon) = title.split(',,')
            except Exception:
                icon = default_icon

            try:
                (description, real_url) = url.split(',,')
            except Exception:
                description = 'No description provided'
                real_url = url

            # Replace MACROS in url and description
            if hasattr(obj, 'get_data_for_checks'):
                # url = MacroResolver().resolve_simple_macros_in_string(
                # real_url, obj.get_data_for_checks()
                # )
                url = real_url
                # description = MacroResolver().resolve_simple_macros_in_string(
                # description, obj.get_data_for_checks()
                # )

            logger.debug("get_urls, found: %s / %s / %s / %s", title, icon, url, description)

            if popover:
                if url != '':
                    result.append(
                        '<a href="%s" target="_blank" role="button" data-toggle="popover medium" '
                        'data-html="true" data-content="%s" data-trigger="hover focus" '
                        'data-placement="bottom"><i class="fa fa-%s"></i>&nbsp;%s</a>' % (
                            url, description, icon, title
                        )
                    )
                else:
                    result.append(
                        '<span data-toggle="popover medium" data-html="true" data-content="%s" '
                        'data-trigger="hover focus" data-placement="bottom">'
                        '<i class="fa fa-%s"></i>&nbsp;%s</span>''' % (
                            description, icon, title
                        )
                    )
            else:
                if url != '':
                    result.append(
                        '<a href="%s" target="_blank" title="%s">'
                        '<i class="fa fa-%s"></i>&nbsp;%s</a>' % (
                            url, description, icon, title
                        )
                    )
                else:
                    result.append(
                        '<span title="%s"><i class="fa fa-%s"></i>&nbsp;%s</span>' % (
                            description, icon, title
                        )
                    )

        return result

    @staticmethod
    def get_element_actions_url(obj, default_title="Url", default_icon="globe", popover=False):
        """
        Return list of element action urls
        """

        if obj is not None:
            return Helper.get_urls(
                obj, obj.action_url,
                default_title=default_title, default_icon=default_icon, popover=popover
            )

        return None

    @staticmethod
    def get_element_notes_url(obj, default_title="Url", default_icon="globe", popover=False):
        """
        Return list of element notes urls
        """

        if obj is not None and obj.notes:
            notes = []
            i = 0
            for item in obj.notes.split('|'):
                if not obj.notes_url:
                    notes.append("%s,," % (item))
                else:
                    notes_url = obj.notes_url.split('|')
                    if len(notes_url) > i:
                        notes.append("%s,,%s" % (item, notes_url[i]))
                    else:
                        notes.append("%s,," % (item))
                i += 1
                logger.debug("get_element_notes_url, note: %s", notes)

            return Helper.get_urls(
                obj, '|'.join(notes),
                default_title=default_title, default_icon=default_icon, popover=popover
            )

        return []

    @staticmethod
    def decode_search(search):
        """
            Convert string from:
                isnot:0 isnot:ack isnot:"downtime fred" name "vm fred"
            to:
                {
                    'isnot': 0,
                    'isnot':'ack',
                    'name': name,
                    'name': 'vm fred'
                }

            :search: Search string
            :returns: list of matching items
        """
        logger.debug("decode_search, search string:%s", search)

        # Search patterns like: isnot:0 isnot:ack isnot:"downtime test" name "vm test"
        regex = re.compile(
            r"""
                                    # 1/ Search a key:value pattern.
                (?P<key>\w+):       # Key consists of only a word followed by a colon
                (?P<quote2>["']?)   # Optional quote character.
                (?P<value>.*?)      # Value is a non greedy match
                (?P=quote2)         # Closing quote equals the first.
                ($|\s)              # Entry ends with whitespace or end of string
                |                   # OR
                                    # 2/ Search a single string quoted or not
                (?P<quote>["']?)    # Optional quote character.
                (?P<name>.*?)       # Name is a non greedy match
                (?P=quote)          # Closing quote equals the opening one.
                ($|\s)              # Entry ends with whitespace or end of string
            """,
            re.VERBOSE
        )

        patterns = []
        for match in regex.finditer(search):
            if match.group('name'):
                patterns.append(('name', match.group('name')))
            elif match.group('key'):
                patterns.append((match.group('key'), match.group('value')))
        logger.debug("decode_search, search patterns: %s", patterns)

        parameters = {}
        for t, s in patterns:
            t = t.lower()
            logger.debug("decode_search, searching for %s %s", t, s)

            if s.startswith('!'):
                s = {t: s[1:]}
                t = "$ne"

            parameters.update({t: s})

        return parameters

    @staticmethod
    def get_pagination_control(object_type, total, start=0, count=25, nb_max_items=5):
        """
        Build page navigation buttons as a list of elements containing:
        - button label
        - start element (None to create a disabled element)
        - count of elements
        - total number of elements
        - active element (True / False)

        Note that nb_max_items should be an odd number ... it will have a better look ;)

        The list contains:
        - fast forward and forward buttons if more than nb_max_items are left-hidden
        - fast backward and backward buttons if more than nb_max_items are right-hidden
        - nb_max_items page buttons to build a direct link to the corresponding pages
        """
        if count <= 0 or total <= 0:
            return []

        max_page = total // count + 1
        current_page = start // count + 1
        logger.debug(
            "Get navigation controls, total: %d, start: %d, count: %d, max items: %d",
            total, start, count, nb_max_items
        )
        logger.debug(
            "Get navigation controls, page: %d, count: %d, max page: %d",
            current_page, count, max_page
        )

        res = []
        # First element contains pagination global data
        res.append(
            (object_type, start, count, total, False)
        )
        if current_page > (nb_max_items / 2) + 1:
            # First page
            start = 0
            res.append(
                (_('<i class="fa fa-fast-backward"></i>'), start, count, total, False)
            )
            # Previous pages sequence
            start = int((current_page - nb_max_items - 1) * count)
            res.append(
                (_('<i class="fa fa-backward"></i>'), start, count, total, False)
            )

        # for i in xrange(current_page - (nb_max_items / 2), current_page + (nb_max_items / 2) + 1):
        start_page = max(1, current_page - (nb_max_items / 2) + 1)
        end_page = min(start_page + nb_max_items - 1, max_page)
        if end_page == max_page and (end_page - start_page) < nb_max_items:
            start_page = max(1, end_page - nb_max_items)
        logger.debug(
            "Get navigation controls, page sequence, from: %d to %d",
            start_page, end_page
        )
        page = start_page
        while page < end_page + 1:
            active = (page == current_page)
            res.append(
                (_('%d') % page, (page - 1) * count, count, total, active)
            )
            if (page * count) + 1 > total:
                break
            page += 1

        if current_page < max_page - ((nb_max_items / 2) + 1):
            # Next pages sequence
            start = int((current_page + nb_max_items - 1) * count)
            res.append(
                (_('<i class="fa fa-forward"></i>'), start, count, total, False)
            )
            # Last page
            start = int((max_page - 1) * count)
            res.append(
                (_('<i class="fa fa-fast-forward"></i>'), start, count, total, False)
            )

        return res
