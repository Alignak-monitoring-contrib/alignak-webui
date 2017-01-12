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
    This module contains helper functions used in HTML application templates.

    An ``helper`` object linked to the application is created by this module to be used in all
    the application.
"""
import re
import time
import traceback
from logging import getLogger, INFO

from alignak_webui import _
from alignak_webui import get_app_config

# pylint: disable=invalid-name
logger = getLogger(__name__)
logger.setLevel(INFO)


class Helper(object):
    """
    Helper functions
    """
    def __init__(self):
        """ Empty ... """
        self.config = get_app_config()

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

        :param ts_is_duration:
        :param x_elts:
        :param duration_only:
        :param timestamp: unix timestamp
        :type timestamp: long int
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
        if seconds < 3:
            if 0 > seconds > -4:
                return _('Very soon')
            if seconds >= 0:
                return _('Just now')

        in_future = False

        # Remember if it's in the future or not
        if seconds < 0:
            in_future = True

        # Now manage all case like in the past
        seconds = abs(seconds)

        seconds = int(round(seconds))
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)
        weeks, days = divmod(days, 7)
        months, weeks = divmod(weeks, 4)
        years, months = divmod(months, 12)

        minutes = int(minutes)
        hours = int(hours)
        days = int(days)
        weeks = int(weeks)
        months = int(months)
        years = int(years)

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

        # Maybe the user just wants the duration
        if duration_only:
            return ' '.join(duration)

        # Now manage the future or not print
        if in_future:
            return _('in ') + ' '.join(duration)
        else:
            return _(' ') + ' '.join(duration) + _(' ago')

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

        # nb_stars = max(0, business_impact - 2)
        stars = '<i class="fa fa-star text-primary"></i>' * business_impact

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
                        '<a href="%s" target="_blank" role="button" data-toggle="popover urls" '
                        'data-container="body" '
                        'data-html="true" data-content="%s" data-trigger="hover focus" '
                        'data-placement="bottom"><i class="fa fa-%s"></i>&nbsp;%s</a>' % (
                            url, description, icon, title
                        )
                    )
                else:
                    result.append(
                        '<span data-toggle="popover urls" data-html="true" data-content="%s" '
                        'data-container="body" '
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
                    notes.append("%s,," % item)
                else:
                    notes_url = obj.notes_url.split('|')
                    if len(notes_url) > i:
                        notes.append("%s,,%s" % (item, notes_url[i]))
                    else:
                        notes.append("%s,," % item)
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

            if '|' in s:
                s = {t: s.split('|')}
                t = "$in"

            elif s.startswith('!'):
                s = {t: s[1:]}
                t = "$ne"

            parameters.update({t: s})

        logger.debug("decode_search, parameters: %s", parameters)
        return parameters

    @staticmethod
    def get_pagination_control(page_url, total, start=0, count=25, nb_max_items=5):
        """
        Build page navigation buttons as a list of elements containing:
        - button label
        - start element (None to create a disabled element)
        - count of elements
        - total number of elements
        - active element (True / False)

        The first element in the list contains:
        - page_url, the current page main URL
        - start
        - count
        - total

        Note that nb_max_items should be an odd number ... it will have a better look ;)

        The list contains:
        - fast forward and forward buttons if more than nb_max_items are left-hidden
        - fast backward and backward buttons if more than nb_max_items are right-hidden
        - nb_max_items page buttons to build a direct link to the corresponding pages
        """
        if count <= 0 or total <= 0:
            return [(page_url, start, count, total, False)]

        max_page = (total // count) + 1
        current_page = (start // count) + 1
        logger.debug(
            "Get navigation controls, total: %d, start: %d, count: %d, max items: %d",
            total, start, count, nb_max_items
        )
        logger.debug(
            "Get navigation controls, page: %d, count: %d, max page: %d",
            current_page, count, max_page
        )

        # First element contains pagination global data
        res = [(page_url, start, count, total, False)]
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

    @staticmethod
    def get_html_timeperiod(tp, title=None):
        """
        Build an html definition list for the timeperiod date ranges and exclusions.
        """
        if tp is None or len(tp.dateranges) == 0:
            return ''

        content = '<button class="btn btn-default btn-xs btn-block" type="button"' \
                  'data-toggle="collapse" data-target="#html_tp_%s" aria-expanded="false" ' \
                  'aria-controls="html_tp_%s">%s</button>' \
                  '<div class="collapse" id="html_tp_%s"><div class="well">' % (
                      tp.id, tp.id, tp.name if not title else title, tp.id
                  )

        # Build the included list ...
        if tp.dateranges:
            content += '''<ul class="list-group">'''
            for daterange in tp.dateranges:
                for key in daterange.keys():
                    content += \
                        '<li class="list-group-item">'\
                        '<span class="fa fa-check">&nbsp;%s - %s</li>' % (
                            key, daterange[key]
                        )
            content += '''</ul>'''

        # Build the excluded list ...
        if tp.exclude:
            content += '<ul class="list-group">'
            for daterange in tp.exclude:
                for key in daterange.keys():
                    content += \
                        '<li class="list-group-item">'\
                        '<span class="fa fa-close">&nbsp;%s - %s</li>''' % (
                            key, daterange[key]
                        )
            content += '</ul>'

        content += '</div></div>'

        return content

    @staticmethod
    def get_html_item_list(object_id, object_type, objects_list, title=None, max_items=10):
        """
        Build an html definition list for the items list
        """
        if not objects_list or not isinstance(objects_list, list):
            return ''

        # Get global configuration
        app_config = get_app_config()

        content = ''
        if len(objects_list) == 1:
            item = objects_list[0]
            list_item = app_config.get('tables.lists.unique')
            if isinstance(item, basestring):
                content = list_item.replace("##content##", item)
            elif isinstance(item, dict):
                content = list_item.replace("##content##", str(item))
            elif hasattr(item, '_type'):
                content = list_item.replace("##content##", item.get_html_state_link())
            else:
                content = list_item.replace("##content##", item)
            return content

        button = app_config.get('tables.lists.button')
        button = button.replace("##id##", object_id)
        button = button.replace("##type##", object_type)
        button = button.replace("##title##", object_type if not title else title)

        items_list = app_config.get('tables.lists.list')

        if len(objects_list) > max_items:
            objects_list = objects_list[:max_items]
            list_item = app_config.get('tables.lists.item')
            content += list_item.replace("##content##", _('Only %d items...') % max_items)
            content += list_item.replace("##content##", _('-- / --'))

        for item in objects_list:
            list_item = app_config.get('tables.lists.item')
            if isinstance(item, basestring):
                content += list_item.replace("##content##", item)
            elif isinstance(item, dict):
                content += list_item.replace("##content##", str(item))
            elif hasattr(item, '_type'):
                content = list_item.replace("##content##", item.get_html_state_link())
            else:
                content = list_item.replace("##content##", item)

        content = items_list.replace("##content##", content)
        content = button.replace("##content##", content)

        return content

    @classmethod
    def get_html_commands_buttons(cls, bo_object, title=''):
        """
        Build an html button bar for a livestate element
        """
        if not bo_object:
            return ''

        content = ''
        try:
            # Get global configuration
            app_config = get_app_config()

            buttons = []
            button = app_config.get('buttons.livestate_command')
            button = button.replace("##id##", bo_object.id)
            button = button.replace("##type##", bo_object.get_type())
            button = button.replace("##name##", bo_object.name)
            button = button.replace("##action##", 'acknowledge')
            button = button.replace("##title##", _('Acknowledge this problem'))
            button = button.replace("##icon##", 'check')
            if getattr(bo_object, 'state_id', 0) > 0:
                if bo_object.acknowledged:
                    button = button.replace("##disabled##", 'disabled="disabled"')
                else:
                    button = button.replace("##disabled##", '')
            else:
                button = button.replace("##disabled##", 'disabled="disabled"')
            buttons.append(button)

            button = app_config.get('buttons.livestate_command')
            button = button.replace("##id##", bo_object.id)
            button = button.replace("##type##", bo_object.get_type())
            button = button.replace("##name##", bo_object.name)
            button = button.replace("##action##", 'recheck')
            button = button.replace("##title##", _('Re-check this element'))
            button = button.replace("##icon##", 'refresh')
            buttons.append(button)

            button = app_config.get('buttons.livestate_command')
            button = button.replace("##id##", bo_object.id)
            button = button.replace("##type##", bo_object.get_type())
            button = button.replace("##name##", bo_object.name)
            button = button.replace("##action##", 'downtime')
            button = button.replace("##title##", _('Schedule a downtime'))
            button = button.replace("##icon##", 'ambulance')
            if getattr(bo_object, 'state_id', 0) > 0:
                if bo_object.downtime:
                    button = button.replace("##disabled##", 'disabled="disabled"')
                else:
                    button = button.replace("##disabled##", '')
            else:
                button = button.replace("##disabled##", 'disabled="disabled"')
            buttons.append(button)

            content = app_config.get('buttons.livestate_commands')
            content = content.replace("##title##", title)
            content = content.replace("##commands##", ''.join(buttons))
            logger.debug("Content: %s", content)
            logger.debug("get_html_commands_buttons, content: %s", content)
        except Exception as e:
            logger.error("get_html_commands_buttons, exception: %s", str(e))
            logger.error("traceback: %s", traceback.format_exc())

        return content
