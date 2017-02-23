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
import json
import traceback
from logging import getLogger, INFO

# from alignak_webui import _
from alignak_webui import get_app_config

# pylint: disable=invalid-name
logger = getLogger(__name__)
logger.setLevel(INFO)


class Helper(object):
    """
    Helper functions
    """

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

        """Give an enabled/disabled HTML state

            The returned HTML element is built from the configuration variables defined as:
            [on_off]
            ; Global element to be included in the HTML and including the items and the text
            on=<span title="##title##" class="fa fa-fw fa-check text-success">##message##</span>

            ; Element to be included for each BI count
            off=<span title="##title##" class="fa fa-fw fa-close text-danger">##message##</span>
        """

        if not title:
            title = _('Enabled') if status else _('Disabled')

        if isinstance(title, list):
            if status:
                title = title[0]
            else:
                title = title[1]

        # Get global configuration
        app_config = get_app_config()

        if status:
            element = app_config.get('on_off.on')
        else:
            element = app_config.get('on_off.off')

        element = element.replace("##title##", title)
        element = element.replace("##message##", message)
        return element

    @staticmethod
    def get_html_business_impact(business_impact, icon=True, text=False, less=0):

        """Give a business impact as text and stars if needed.
            If text=True, returns text+stars, else returns stars only ...

            The returned HTML element is built from the configuration variables defined as:
            [business_impact]
            ; Global element to be included in the HTML and including the items and the text
            global=<div><span>##items##</span><span>##text##</span></div>

            ; Element to be included for each BI count
            item=<span class="fa fa-star"></span>
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

        if not icon:
            return bi_texts.get(business_impact, _('Unknown'))

        # Get global configuration
        app_config = get_app_config()
        element = app_config.get('business_impact.global')
        star = app_config.get('business_impact.item')

        element = element.replace("##items##", star * max(0, business_impact - less))

        if not text:
            element = element.replace("##text##", "")
            return element

        element = element.replace("##text##", bi_texts.get(business_impact, _('Unknown')))
        return element

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

        """Build an html definition list for the timeperiod date ranges and exclusions.

            The returned HTML element is built from the configuration variables defined as:
            [timeperiods]

            ; Button to display the list
            button=<button class="btn btn-default btn-xs btn-block" type="button"
                    data-toggle="collapse" data-target="#html_tp_##id##" aria-expanded="false"
                    aria-controls="html_tp_##id##">##name##</button><div class="collapse"
                    id="html_tp_##id##"><div class="well">##content##</div></div>

            ; Global element to be included in the HTML for the list
            list=<ul class="list-group">##content##</ul>

            ; Each period element to be included in the HTML list (##period## is the name
            and ##range## is the date range)
            item=<li class="list-group-item"><span class="fa fa-hourglass">
                    &nbsp;##period## - ##range##</li>
        """

        if tp is None or len(tp.dateranges) == 0:
            return ''

        # Get global configuration
        app_config = get_app_config()

        element = app_config.get('timeperiods.button')
        element = element.replace("##id##", tp.id)
        element = element.replace("##name##", tp.name if not title else title)

        lists = ""

        # Build the included list ...
        if tp.dateranges:
            list_item = app_config.get('timeperiods.list')
            items = ""
            for daterange in tp.dateranges:
                for key in daterange.keys():
                    item = app_config.get('timeperiods.item')
                    item = item.replace("##period##", key)
                    item = item.replace("##range##", daterange[key])
                    items += item
            lists += list_item.replace("##content##", items)

        # Build the excluded list ...
        if tp.exclude:
            list_item = app_config.get('timeperiods.list')
            items = ""
            for daterange in tp.exclude:
                for key in daterange.keys():
                    item = app_config.get('timeperiods.item')
                    item = item.replace("##period##", key)
                    item = item.replace("##range##", daterange[key])
                    items += item
            lists += list_item.replace("##content##", items)

        element = element.replace("##content##", lists)

        return element

    @staticmethod
    def get_html_item_list(object_id, object_type, objects_list, title=None, max_items=10):

        """Build an html definition list for the items list

            The returned HTML element is built from the configuration variables defined as:
            [tables.lists]

            ; Button to display the list
            button=<button class="btn btn-xs btn-raised" data-toggle="collapse"
                    data-target="#list_##type##_##id##" aria-expanded="false">##title##
                    </button><div class="collapse" id="list_##type##_##id##">##content##</div>

            ; Global element to be included in the HTML for the list
            list=<ul class="list-group">##content##</ul>

            ; Each command element to be included in the HTML list
            item=<li class="list-group-item"><span class="fa fa-check">
                    &nbsp;##content##</span></li>

            ; Unique element to be included in the HTML list if the list contains only one element
            unique=##content##
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
            if bo_object.event_handler_enabled:
                button = app_config.get('buttons.livestate_command')
                button = button.replace("##id##", bo_object.id)
                button = button.replace("##type##", bo_object.get_type())
                button = button.replace("##name##", bo_object.name)
                button = button.replace("##action##", 'event_handler')
                button = button.replace("##title##", _('Try to fix this problem'))
                button = button.replace("##icon##", 'magic')
                if getattr(bo_object, 'state_id', 0) > 0:
                    button = button.replace("##disabled##", 'disabled="disabled"')
                else:
                    button = button.replace("##disabled##", '')
                buttons.append(button)

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
            if getattr(bo_object, 'active_checks_enabled', None) is not None:
                if not getattr(bo_object, 'active_checks_enabled'):
                    button = button.replace("##disabled##", 'disabled="disabled"')
            else:
                button = button.replace("##disabled##", 'disabled="disabled"')
            buttons.append(button)

            button = app_config.get('buttons.livestate_command')
            button = button.replace("##id##", bo_object.id)
            button = button.replace("##type##", bo_object.get_type())
            button = button.replace("##name##", bo_object.name)
            button = button.replace("##action##", 'downtime')
            button = button.replace("##title##", _('Schedule a downtime'))
            button = button.replace("##icon##", 'ambulance')
            if bo_object.downtimed:
                button = button.replace("##disabled##", 'disabled="disabled"')
            else:
                button = button.replace("##disabled##", '')
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

    @staticmethod
    def get_html_hosts_ls_history(hs, history, collapsed=False):

        """Build the HTML content for a live state history of the hosts

        :param hs: hosts livesynthesis as provided by the get_livesynthesis or
                   get_livesynthesis_history functions
        :param history: hosts livesynthesis history as provided by the
                        get_livesynthesis_history functions
        :param collapsed: True if the panel is collapsed
        :return:
        """

        # Get configuration
        app_config = get_app_config()
        states = app_config.get('currently.hh_states',
                                'up,down,unreachable,acknowledged,in_downtime')
        states = states.split(',')
        graph_height = int(app_config.get('currently.hh_height', '300'))
        if not states:
            return ""

        unmanaged_problems = hs['nb_problems'] - (hs['nb_acknowledged'] + hs['nb_in_downtime'])

        problems = _("(no unmanaged problems).")
        if hs['nb_problems'] == 0:
            problems = _("(no problems).")
        if unmanaged_problems != hs['nb_problems']:
            if unmanaged_problems == 0:
                problems = _("(#nb_problems# problems, all managed).")
            else:
                problems = _("(#nb_problems# problems, #nb_unmanaged_problems# unmanaged).")

        idx = len(history)
        labels = []
        for ls in history:
            labels.append(ls['_timestamp'])
            idx = idx - 1

        content = """
        <div id="panel_ls_history_hosts" class="panel panel-default">
            <div class="panel-heading clearfix">
                <strong>
                    <span class="fa fa-server"></span>
                    <span class="hosts-all text-%s"
                            data-count="#nb_elts#"
                            data-problems="#nb_problems#">
                        &nbsp; #nb_elts# hosts #problems#
                    </span>
                </strong>

                <div class="pull-right">
                    <a href="#p_plsh_hosts" class="btn btn-xs btn-raised" data-toggle="collapse">
                        <i class="fa fa-fw %s"></i>
                    </a>
                </div>
            </div>
            <div id="p_plsh_hosts" class="panel-collapse collapse %s">
              <div class="panel-body">
                  <div id="line-graph-hosts"><canvas width="100" height="%d"></canvas></div>
              </div>
            </div>
        </div>

        <script>
            // Hosts line chart
            // Graph labels
            var labels=%s
            // Graph data
        """ % ('white',
               'fa-caret-up' if collapsed else 'fa-caret-down',
               'in' if not collapsed else '',
               graph_height, json.dumps(labels))

        content = content.replace("#problems#", "%s" % problems)
        content = content.replace("#nb_elts#", "%d" % hs['nb_elts'])
        content = content.replace("#nb_problems#", "%d" % hs['nb_problems'])
        content = content.replace("#nb_unmanaged_problems#", "%d" % max(0, unmanaged_problems))
        content = content.replace("#nb_up#", "%d" % hs['nb_up'])
        content = content.replace("#nb_down#", "%d" % hs['nb_down'])
        content = content.replace("#nb_unreachable#", "%d" % hs['nb_unreachable'])
        content = content.replace("#nb_acknowledged#", "%d" % hs['nb_acknowledged'])
        content = content.replace("#nb_in_downtime#", "%d" % hs['nb_in_downtime'])

        data = {}
        # for state in ['up', 'unreachable', 'down', 'acknowledged', 'in_downtime']:
        for state in states:
            data[state] = []
            for elt in history:
                data[state].append(elt["hosts_synthesis"]["nb_" + state])
            logger.debug("Data state: %s %s", state, data[state])
            content += """
                var data_%s=%s;""" % (state, data[state])

        content += """
           var data = {
              labels: labels,
              datasets: ["""
        # do not consider unreachable hosts
        # for state in ['up', 'unreachable', 'down', 'acknowledged', 'in_downtime']:
        for state in states:
            content += """
                 {
                    label: g_hosts_states["%s"]['label'],
                    fill: false,
                    lineTension: 0.1,
                    borderWidth: 1,
                    borderColor: g_hosts_states["%s"]['color'],
                    backgroundColor: g_hosts_states["%s"]['background'],
                    pointBorderWidth: 1,
                    pointRadius: 1,
                    pointBorderColor: g_hosts_states["%s"]['color'],
                    pointBackgroundColor: g_hosts_states["%s"]['background'],
                    data: data_%s
                 },
                 """ % (state, state, state, state, state, state)
        content += """
              ]
           };

           new Chart($("#line-graph-hosts canvas"), {
              type: 'line',
              data: data,
              options: {
                 responsive: true,
                 maintainAspectRatio: false,
                 title: {
                    display: true,
                    text: "%s"
                 },
                 hover: {
                    mode: 'index',
                    intersect: true,
                 },
                 tooltip: {
                    mode: 'nearest',
                    intersect: true,
                 },
                 legend: {
                    display: true,
                    position: 'bottom'
                 },
                 scales: {
                    xAxes: [{
                       type: 'time',
                       ticks: {
                          fontSize: 10,
                          fontFamily: 'HelveticaNeue, HelveticaNeue, Roboto, ArialRounded',
                          autoSkip: true
                       },
                       time: {
                          parser: 'X',
                          tooltipFormat: 'LTS',
                          unit: 'minute',
                          displayFormats: {
                             second: 'LTS',
                             minute: 'LTS',
                             hour: 'LTS',
                             day: 'LTS'
                          }
                       }
                    }],
                    yAxes: [{
                       ticks: {
                          fontSize: 10,
                          fontFamily: 'HelveticaNeue, HelveticaNeue, Roboto, ArialRounded',
                          autoSkip: false
                       },
                       stacked: true
                    }]
                 }
              }
           });
        </script>
        """ % (_("Hosts states history, last %d minutes") % len(history))

        return content

    @staticmethod
    def get_html_services_ls_history(ss, history, collapsed=False):

        """Build the HTML content for a live state history of the services

        :param ss: services livesynthesis as provided by the get_livesynthesis or
                   get_livesynthesis_history functions
        :param history: services livesynthesis history as provided by the
                        get_livesynthesis_history functions
        :param collapsed: True if the panel is collapsed
        :return:
        """

        # Get configuration
        app_config = get_app_config()
        states = app_config.get('currently.sh_states',
                                'ok,warning,critical,unknown,acknowledged,in_downtime')
        states = states.split(',')
        graph_height = int(app_config.get('currently.sh_height', '300'))
        if not states:
            return ""

        unmanaged_problems = ss['nb_problems'] - (ss['nb_acknowledged'] + ss['nb_in_downtime'])

        problems = _("(no unmanaged problems).")
        if ss['nb_problems'] == 0:
            problems = _("(no problems).")
        if unmanaged_problems != ss['nb_problems']:
            if unmanaged_problems == 0:
                problems = _("(#nb_problems# problems, all managed).")
            else:
                problems = _("(#nb_problems# problems, #nb_unmanaged_problems# unmanaged).")

        idx = len(history)
        labels = []
        for ls in history:
            labels.append(ls['_timestamp'])
            idx = idx - 1

        content = """
        <div id="panel_ls_history_services" class="panel panel-default">
            <div class="panel-heading clearfix">
                <strong>
                    <span class="fa fa-cube"></span>
                    <span class="services-all text-%s"
                            data-count="#nb_elts#"
                            data-problems="#nb_problems#">
                        &nbsp; #nb_elts# services #problems#
                    </span>
                </strong>

                <div class="pull-right">
                    <a href="#p_plsh_services" class="btn btn-xs btn-raised" data-toggle="collapse">
                        <i class="fa fa-fw %s"></i>
                    </a>
                </div>
            </div>
          <div id="p_plsh_services" class="panel-collapse collapse %s">
            <div class="panel-body">
              <div id="line-graph-services"><canvas width="100" height="%d"></canvas></div>
            </div>
          </div>
        </div>

        <script>
            // Services line chart
            // Graph labels
            var labels=%s
            // Graph data
        """ % ('white',
               'fa-caret-up' if collapsed else 'fa-caret-down',
               'in' if not collapsed else '',
               graph_height, json.dumps(labels))

        content = content.replace("#problems#", "%s" % problems)
        content = content.replace("#nb_elts#", "%d" % ss['nb_elts'])
        content = content.replace("#nb_problems#", "%d" % ss['nb_problems'])
        content = content.replace("#nb_unmanaged_problems#", "%d" % max(0, unmanaged_problems))
        content = content.replace("#nb_ok#", "%d" % ss['nb_ok'])
        content = content.replace("#nb_warning#", "%d" % ss['nb_warning'])
        content = content.replace("#nb_critical#", "%d" % ss['nb_critical'])
        content = content.replace("#nb_unreachable#", "%d" % ss['nb_unreachable'])
        content = content.replace("#nb_unknown#", "%d" % ss['nb_unknown'])
        content = content.replace("#nb_acknowledged#", "%d" % ss['nb_acknowledged'])
        content = content.replace("#nb_in_downtime#", "%d" % ss['nb_in_downtime'])

        data = {}
        for state in states:
            data[state] = []
            for elt in history:
                data[state].append(elt["services_synthesis"]["nb_" + state])
            logger.debug("Data state: %s %s", state, data[state])
            content += """
                var data_%s=%s;""" % (state, data[state])

        content += """
           var data = {
              labels: labels,
              datasets: ["""
        for state in states:
            content += """
                 {
                    label: g_services_states["%s"]['label'],
                    fill: false,
                    lineTension: 0.1,
                    borderWidth: 1,
                    borderColor: g_services_states["%s"]['color'],
                    backgroundColor: g_services_states["%s"]['background'],
                    pointBorderWidth: 1,
                    pointRadius: 1,
                    pointBorderColor: g_services_states["%s"]['color'],
                    pointBackgroundColor: g_services_states["%s"]['background'],
                    data: data_%s
                 },
                 """ % (state, state, state, state, state, state)
        content += """
              ]
           };

           new Chart($("#line-graph-services canvas"), {
              type: 'line',
              data: data,
              options: {
                 responsive: true,
                 maintainAspectRatio: false,
                 title: {
                    display: true,
                    text: "%s"
                 },
                 hover: {
                    mode: 'index',
                    intersect: true,
                 },
                 tooltip: {
                    mode: 'index',
                    intersect: false,
                 },
                 legend: {
                    display: true,
                    position: 'bottom'
                 },
                 scales: {
                    xAxes: [{
                       type: 'time',
                       ticks: {
                          fontSize: 10,
                          fontFamily: 'HelveticaNeue, Roboto, ArialRounded',
                          autoSkip: true
                       },
                       time: {
                          parser: 'X',
                          tooltipFormat: 'LTS',
                          unit: 'minute',
                          displayFormats: {
                             second: 'LTS',
                             minute: 'LTS',
                             hour: 'LTS',
                             day: 'LTS'
                          }
                       }
                    }],
                    yAxes: [{
                       ticks: {
                          fontSize: 10,
                          fontFamily: 'HelveticaNeue, Roboto, ArialRounded',
                          autoSkip: false
                       },
                       //stacked: true
                    }]
                 }
              }
           });
        </script>
        """ % (_("Services states history, last %d minutes") % len(history))

        return content

    @staticmethod
    def get_html_hosts_count_panel(hs, url, collapsed=False, percentage=False):
        """

        :param hs: hosts livesynthesis as provided by the get_livesynthesis or
                   get_livesynthesis_history functions
        :param url: url to use for the links to an host table
        :param collapsed: True if the panel is collapsed
        :param percentage: True to build a percentage panel, else build a count panel
        :return:
        """
        content = ''

        sla = hs['pct_up']
        font = 'ok' if sla >= 95.0 else 'warning' if sla >= 90.0 else 'critical'
        unmanaged_problems = hs['nb_problems'] - (hs['nb_acknowledged'] + hs['nb_in_downtime'])

        problems = _("(no unmanaged problems).")
        if hs['nb_problems'] == 0:
            problems = _("(no problems).")
        if unmanaged_problems != hs['nb_problems']:
            if unmanaged_problems == 0:
                problems = _("(#nb_problems# problems, all managed).")
            else:
                problems = _("(#nb_problems# problems, #nb_unmanaged_problems# unmanaged).")

        if percentage:
            content = """
            <div id="panel_percentage_hosts" class="panel panel-default">
                <div class="panel-heading clearfix">
                <strong>
                    <span class="fa fa-server"></span>
                    <span class="hosts-all text-%s"
                            data-count="#nb_elts#"
                            data-problems="#nb_problems#">
                        &nbsp; #nb_elts# hosts #problems#
                    </span>
                </strong>

                    <div class="pull-right">
                        <a href="#p_ph" class="btn btn-xs btn-raised" data-toggle="collapse">
                            <i class="fa fa-fw %s"></i>
                        </a>
                    </div>
                </div>
                <div id="p_ph" class="panel-collapse collapse %s">
                  <div class="panel-body">
                    <div class="row">
                      <div class="col-xs-3 col-sm-3 text-center">
                        <div class="col-xs-12 text-center">
                          <a href="#hosts_table_url#" class="sla_hosts_%s">
                            <div>#pct_sla#%%</div>
                            <i class="fa fa-4x fa-server"></i>
                            <p>%s</p>
                          </a>
                        </div>
                      </div>

                      <div class="col-xs-9 col-sm-9 text-center">
                        <div class="row">
                          <div class="col-xs-4 text-center">
                            <a href="#hosts_table_url#?search=ls_state:UP"
                              class="item_host_up" title="Up">
                              <span class="hosts-count">#pct_up#%%</span>
                            </a>
                          </div>
                          <div class="col-xs-4 text-center">
                            <a href="#hosts_table_url#?search=ls_state:DOWN"
                              class="item_host_down" title="Down">
                              <span class="hosts-count">#pct_down#%%</span>
                            </a>
                          </div>
                          <div class="col-xs-4 text-center">
                            <a href="#hosts_table_url#?search=ls_state:UNREACHABLE"
                              class="item_host_unreachable" title="Unreachable">
                              <span class="hosts-count">#pct_unreachable#%%</span>
                            </a>
                          </div>
                        </div>
                        <div class="row">
                          <br/>
                        </div>
                        <div class="row">
                          <div class="col-xs-12 text-center">
                            <a href="#hosts_table_url#?search=ls_state:acknowledged"
                              class="item_host_acknowledged" title="Acknowledged">
                              <span class="hosts-count">#pct_acknowledged#%%</span>
                            </a>
                            <span>/</span>
                            <a href="#hosts_table_url#?search=ls_state:IN_DOWNTIME"
                              class="item_host_in_downtime" title="In downtime">
                              <span class="hosts-count">#pct_in_downtime#%%</span>
                            </a>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
            </div>
            """ % ('white',
                   'fa-caret-up' if collapsed else 'fa-caret-down',
                   'in' if not collapsed else '',
                   font, _('Hosts SLA'))

        else:
            content = """
            <div id="panel_counters_hosts" class="panel panel-default">
                <div class="panel-heading clearfix">
                <strong>
                    <span class="fa fa-server"></span>
                    <span class="hosts-all text-%s"
                            data-count="#nb_elts#"
                            data-problems="#nb_problems#">
                        &nbsp; #nb_elts# hosts #problems#
                    </span>
                </strong>

                    <div class="pull-right">
                        <a href="#p_ch" class="btn btn-xs btn-raised" data-toggle="collapse">
                            <i class="fa fa-fw %s"></i>
                        </a>
                    </div>
                </div>
                <div id="p_ch" class="panel-collapse collapse %s">
                  <div class="panel-body">
                    <div class="col-xs-12 col-sm-9 text-center">
                      <div class="col-xs-4 text-center">
                        <a href="#hosts_table_url#?search=ls_state:UP"
                          class="item_host_up" title="Up">
                          <span class="hosts-count">#nb_up#</span>
                        </a>
                      </div>
                      <div class="col-xs-4 text-center">
                        <a href="#hosts_table_url#?search=ls_state:DOWN"
                          class="item_host_down" title="Down">
                          <span class="hosts-count">#nb_down#</span>
                        </a>
                      </div>
                      <div class="col-xs-4 text-center">
                        <a href="#hosts_table_url#?search=ls_state:UNREACHABLE"
                          class="item_host_unreachable" title="Unreachable">
                          <span class="hosts-count">#nb_unreachable#</span>
                        </a>
                      </div>
                    </div>

                    <div class="col-xs-12 col-sm-3 text-center">
                      <a href="#hosts_table_url#?search=ls_state:acknowledged"
                        class="item_host_acknowledged" title="Acknowledged">
                        <span class="hosts-count">#nb_acknowledged#</span>
                      </a>
                      <span>/</span>
                      <a href="#hosts_table_url#?search=ls_state:IN_DOWNTIME"
                        class="item_host_in_downtime" title="In downtime">
                        <span class="hosts-count">#nb_in_downtime#</span>
                      </a>
                    </div>
                  </div>
                </div>
            </div>
            """ % ('white',
                   'fa-caret-up' if collapsed else 'fa-caret-down',
                   'in' if not collapsed else '')

        content = content.replace("#problems#", "%s" % problems)
        content = content.replace("#nb_elts#", "%d" % hs['nb_elts'])
        content = content.replace("#nb_problems#", "%d" % hs['nb_problems'])
        content = content.replace("#nb_unmanaged_problems#", "%d" % max(0, unmanaged_problems))
        content = content.replace("#nb_up#", "%d" % hs['nb_up'])
        content = content.replace("#nb_down#", "%d" % hs['nb_down'])
        content = content.replace("#nb_unreachable#", "%d" % hs['nb_unreachable'])
        content = content.replace("#nb_acknowledged#", "%d" % hs['nb_acknowledged'])
        content = content.replace("#nb_in_downtime#", "%d" % hs['nb_in_downtime'])
        content = content.replace("#pct_sla#", "%d" % sla)
        content = content.replace("#pct_up#", "%d" % hs['pct_up'])
        content = content.replace("#pct_down#", "%d" % hs['pct_down'])
        content = content.replace("#pct_unreachable#", "%d" % hs['pct_unreachable'])
        content = content.replace("#pct_acknowledged#", "%d" % hs['pct_acknowledged'])
        content = content.replace("#pct_in_downtime#", "%d" % hs['pct_in_downtime'])
        content = content.replace("#hosts_table_url#", url)

        return content

    @staticmethod
    def get_html_services_count_panel(ss, url, collapsed=False, percentage=False):
        """

        :param ss: services livesynthesis as provided by the get_livesynthesis or
                   get_livesynthesis_history functions
        :param url: url to use for the links to an host table
        :param collapsed: True if the panel is collapsed
        :param percentage: True to build a percentage panel, else build a count panel
        :return:
        """
        content = ''

        sla = ss['pct_ok']
        font = 'ok' if sla >= 95.0 else 'warning' if sla >= 90.0 else 'critical'
        unmanaged_problems = ss['nb_problems'] - (ss['nb_acknowledged'] + ss['nb_in_downtime'])

        problems = _("(no unmanaged problems).")
        if ss['nb_problems'] == 0:
            problems = _("(no problems).")
        if unmanaged_problems != ss['nb_problems']:
            if unmanaged_problems == 0:
                problems = _("(#nb_problems# problems, all managed).")
            else:
                problems = _("(#nb_problems# problems, #nb_unmanaged_problems# unmanaged).")

        if percentage:
            content = """
            <div id="panel_percentage_services" class="panel panel-default">
                <div class="panel-heading clearfix">
                <strong>
                    <span class="fa fa-cube"></span>
                    <span class="services-all text-%s"
                            data-count="#nb_elts#"
                            data-problems="#nb_problems#">
                        &nbsp; #nb_elts# services #problems#
                    </span>
                </strong>

                    <div class="pull-right">
                        <a href="#p_ps" class="btn btn-xs btn-raised" data-toggle="collapse">
                            <i class="fa fa-fw %s"></i>
                        </a>
                    </div>
                </div>
                <div id="p_ps" class="panel-collapse collapse %s">
                  <div class="panel-body">
                    <div class="row">
                      <div class="col-xs-3 col-sm-3 text-center">
                        <div class="col-xs-12 text-center">
                          <a href="#services_table_url#" class="sla_services_%s">
                            <div>#pct_ok#%%</div>
                            <i class="fa fa-4x fa-cube"></i>
                            <p>%s</p>
                          </a>
                        </div>
                      </div>

                      <div class="col-xs-9 col-sm-9 text-center">
                        <div class="row">
                          <div class="col-xs-4 text-center">
                            <a href="#services_table_url#?search=ls_state:OK"
                              class="item_service_ok" title="ok">
                              <span class="services-count">#pct_ok#%%</span>
                            </a>
                          </div>
                          <div class="col-xs-4 text-center">
                            <a href="#services_table_url#?search=ls_state:WARNING"
                              class="item_service_warning" title="warning">
                              <span class="services-count">#pct_warning#%%</span>
                            </a>
                          </div>
                          <div class="col-xs-4 text-center">
                            <a href="#services_table_url#?search=ls_state:CRITICAL"
                              class="item_service_critical" title="critical">
                              <span class="services-count">#pct_critical#%%</span>
                            </a>
                          </div>
                          <div class="col-xs-4 text-center">
                            <a href="#services_table_url#?search=ls_state:UNKNONW"
                              class="item_service_unknown" title="unknown">
                              <span class="services-count">#pct_unknown#%%</span>
                            </a>
                          </div>
                          <div class="col-xs-4 text-center">
                            <a href="#services_table_url#?search=ls_state:UNREACHABLE"
                              class="item_service_unreachable" title="unreachable">
                              <span class="services-count">#pct_unreachable#%%</span>
                            </a>
                          </div>
                        </div>
                        <div class="row">
                          <br/>
                        </div>
                        <div class="row">
                          <div class="col-xs-12 text-center">
                            <a href="#services_table_url#?search=ls_state:ACKNOWLEDGED"
                              class="item_service_acknowledged" title="acknowledged">
                              <span class="services-count">#pct_acknowledged#%%</span>
                            </a>
                            <span>/</span>
                            <a href="#services_table_url#?search=ls_state:IN_DOWNTIME"
                              class="item_service_in_downtime" title="in_downtime">
                              <span class="services-count">#pct_in_downtime#%%</span>
                            </a>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
            </div>
            """ % ('white',
                   'fa-caret-up' if collapsed else 'fa-caret-down',
                   'in' if not collapsed else '',
                   font, _('Services SLA'))

        else:
            content = """
            <div id="panel_counters_services" class="panel panel-default">
                <div class="panel-heading clearfix">
                <strong>
                    <span class="fa fa-cube"></span>
                    <span class="services-all text-%s"
                            data-count="#nb_elts#"
                            data-problems="#nb_problems#">
                        &nbsp; #nb_elts# services #problems#
                    </span>
                </strong>

                    <div class="pull-right">
                        <a href="#p_cs" class="btn btn-xs btn-raised" data-toggle="collapse">
                            <i class="fa fa-fw %s"></i>
                        </a>
                    </div>
                </div>
                <div id="p_cs" class="panel-collapse collapse %s">
                  <div class="panel-body">
                    <div class="col-xs-12 col-sm-9 text-center">
                      <div class="col-xs-2 text-center">
                        <a href="#services_table_url#?search=ls_state:OK"
                          class="item_service_ok" title="Ok">
                          <span class="services-count">#nb_ok#</span>
                        </a>
                      </div>
                      <div class="col-xs-2 text-center">
                        <a href="#services_table_url#?search=ls_state:WARNING"
                          class="item_service_critical" title="Warning">
                          <span class="services-count">#nb_warning#</span>
                        </a>
                      </div>
                      <div class="col-xs-2 text-center">
                        <a href="#services_table_url#?search=ls_state:CRITICAL"
                          class="item_service_critical" title="Critical">
                          <span class="services-count">#nb_critical#</span>
                        </a>
                      </div>
                      <div class="col-xs-2 text-center">
                        <a href="#services_table_url#?search=ls_state:UNKNOWN"
                          class="item_service_unknown" title="Unknown">
                          <span class="services-count">#nb_unknown#</span>
                        </a>
                      </div>
                      <div class="col-xs-2 text-center">
                        <a href="#services_table_url#?search=ls_state:UNREACHABLE"
                          class="item_service_unreachable" title="Unreachable">
                          <span class="services-count">#nb_unreachable#</span>
                        </a>
                      </div>
                    </div>

                    <div class="col-xs-12 col-sm-3 text-center">
                      <a href="#services_table_url#?search=ls_state:acknowledged"
                        class="item_service_acknowledged" title="Acknowledged">
                        <span class="services-count">#nb_acknowledged#</span>
                      </a>
                      <span>/</span>
                      <a href="#services_table_url#?search=ls_state:IN_DOWNTIME"
                        class="item_service_in_downtime" title="In downtime">
                        <span class="services-count">#nb_in_downtime#</span>
                      </a>
                    </div>
                  </div>
                </div>
            </div>
            """ % ('white',
                   'fa-caret-up' if collapsed else 'fa-caret-down',
                   'in' if not collapsed else '')

        content = content.replace("#problems#", "%s" % problems)
        content = content.replace("#nb_elts#", "%d" % ss['nb_elts'])
        content = content.replace("#nb_problems#", "%d" % ss['nb_problems'])
        content = content.replace("#nb_unmanaged_problems#", "%d" % max(0, unmanaged_problems))
        content = content.replace("#nb_ok#", "%d" % ss['nb_ok'])
        content = content.replace("#nb_warning#", "%d" % ss['nb_warning'])
        content = content.replace("#nb_critical#", "%d" % ss['nb_critical'])
        content = content.replace("#nb_unreachable#", "%d" % ss['nb_unreachable'])
        content = content.replace("#nb_unknown#", "%d" % ss['nb_unknown'])
        content = content.replace("#nb_acknowledged#", "%d" % ss['nb_acknowledged'])
        content = content.replace("#nb_in_downtime#", "%d" % ss['nb_in_downtime'])
        content = content.replace("#pct_sla#", "%d" % sla)
        content = content.replace("#pct_ok#", "%d" % ss['pct_ok'])
        content = content.replace("#pct_warning#", "%d" % ss['pct_warning'])
        content = content.replace("#pct_critical#", "%d" % ss['pct_critical'])
        content = content.replace("#pct_unknown#", "%d" % ss['pct_unknown'])
        content = content.replace("#pct_unreachable#", "%d" % ss['pct_unreachable'])
        content = content.replace("#pct_acknowledged#", "%d" % ss['pct_acknowledged'])
        content = content.replace("#pct_in_downtime#", "%d" % ss['pct_in_downtime'])
        content = content.replace("#services_table_url#", url)

        return content

    @staticmethod
    # pylint: disable=too-many-locals
    def get_html_livestate(datamgr, panels, bi=-1, search=None, actions=False):
        """
        Get HTML formatted live state

        If bi is -1 (default) then all the items are considered, else this
        function only considers the items with the provided BI.

        :param bi: business impact
        :type bi: int

        :return: hosts_states and services_states HTML strings in a dictionary
        :rtype: dict
        """
        logger.debug("get_html_livestate, BI: %d, search: '%s'", bi, search)
        if search is None or not isinstance(search, dict):
            search = {}
        if 'where' not in search:
            search.update({'where': {
                "ls_state_id": {"$nin": [0, 4]},
                'ls_acknowledged': False,
                'ls_downtimed': False
            }})
        if 'sort' not in search:
            search.update({'sort': '-ls_state_id, -ls_last_state_changed'})
        if bi != -1:
            search['where'].update({'business_impact': bi})
        else:
            search.update({'sort': '-business_impact, -ls_state_id, -ls_last_state_changed'})

        items = []
        # Copy because the search filter is updated by the function ...
        search_hosts = search.copy()
        logger.debug("get_html_livestate, BI: %d, hosts search: '%s'", bi, search_hosts)
        hosts = datamgr.get_hosts(search=search_hosts, embedded=False)
        items.extend(hosts)
        logger.debug("get_html_livestate, livestate %d (%s), %d hosts", bi, search, len(items))

        # Copy because the search filter is updated by the function ...
        if 'embedded' not in search:
            search.update({'embedded': {'host': 1}})
        search_services = search.copy()
        logger.debug("get_html_livestate, BI: %d, hosts search: '%s'", bi, search_services)
        services = datamgr.get_services(search=search_services, embedded=True)
        items.extend(services)
        logger.debug("get_html_livestate, livestate %d (%s), %d services", bi, search, len(items))

        rows = []
        problems_count = 0
        current_host = ''
        hosts_problems = -1
        services_problems = -1
        worst_hosts_state = 0
        worst_services_state = 0
        for item in items:
            logger.debug("get_html_livestate, item: %d / %d / %d / %s",
                         item.business_impact, item.state_id, item.last_state_changed, item)
            problems_count += 1

            if item.object_type == "service" and services_problems == -1:
                worst_services_state = max(worst_services_state, item.state_id)
                services_problems = item.get_total_count()
            if item.object_type == "host" and hosts_problems == -1:
                worst_hosts_state = max(worst_hosts_state, item.state_id)
                hosts_problems = item.get_total_count()

            host_url = ''
            if current_host != item.name:
                current_host = item.name
                host_url = item.html_link

            service_url = ''
            if item.object_type == "service":
                service_url = item.html_link
                host_url = item.host.html_link

            long_output = ''
            if item.long_output:
                long_output = """
                    <button
                        type="button"
                        class="btn btn-xs btn-info"
                        data-toggle="popover"
                        title="Long output"
                        data-content="Long check output ...">
                        %s
                        </button>
                """ % item.long_output

            extra = ''
            if item.acknowledged:
                extra += _(' and acknowledged')
            if item.downtimed:
                extra += _(' and in scheduled downtime')
            title = "%s - %s (%s)" \
                    % (item.status,
                       Helper.print_duration(item.last_check, duration_only=True, x_elts=0),
                       item.output)

            tr = """
            <tr>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td class="hidden-xs">%s</td>
                <td class="hidden-xs">%s</td>
                <td class="hidden-sm hidden-xs">%s: %s%s</td>
            </tr>""" % (
                item.get_html_state(text=None, title=title, extra=extra),
                Helper.get_html_commands_buttons(item, title=_("Actions")) if actions else '',
                Helper.get_html_business_impact(item.business_impact,
                                                icon=True, text=False, less=2),
                host_url,
                service_url,
                Helper.print_duration(item.last_state_changed, duration_only=True, x_elts=2),
                Helper.print_duration(item.last_check, duration_only=True, x_elts=2),
                Helper.print_date(item.last_state_changed),
                item.output, long_output
            )
            rows.append(tr)

        collapsed = False
        if 'livestate-bi-%d' % bi in panels:
            collapsed = panels['livestate-bi-%d' % bi]['collapsed']
        if not rows:
            collapsed = True

        panel_bi = """
        <div id="livestate-bi-#bi-id#" class="livestate-panel panel panel-default">
            <div class="panel-heading clearfix">
              <strong>
              <span class="fa fa-heartbeat"></span>
              <span class="livestate-all" data-count="#nb_problems#">
                &nbsp;#bi-text##problems#.
              </span>
              </strong>

              <div class="pull-right">
                <a href="#p_livestate-#bi-id#" class="btn btn-xs btn-raised"
                   data-toggle="collapse">
                   <i class="fa fa-fw %s"></i>
                </a>
              </div>
            </div>
            <div id="p_livestate-#bi-id#" class="panel-collapse collapse %s">
              <div class="panel-body">
        """ % ('fa-caret-up' if collapsed else 'fa-caret-down',
               'in' if not collapsed else '')

        if problems_count > 0:
            problems = _(" #nb_problems# problems")
            if hosts_problems > 0 and services_problems > 0:
                problems += _(" (hosts: #nb_hosts_problems# #alert_hosts_problems#, "
                              "services: #nb_services_problems# #alert_services_problems#)")
            elif hosts_problems > 0:
                problems += _(" (hosts: #nb_hosts_problems# #alert_hosts_problems#)")
            elif services_problems > 0:
                problems += _(" (services: #nb_services_problems# #alert_services_problems#)")
            panel_bi += """
            <table class="table table-invisible table-condensed" data-business-impact="#bi-id#" >
              <thead><tr>
                <th></th>
                <th></th>
                <th>%s</th>
                <th>%s</th>
                <th>%s</th>
                <th class="hidden-xs">%s</th>
                <th class="hidden-xs">%s</th>
                <th class="hidden-sm hidden-xs" >%s</th>
              </tr></thead>

              <tbody>
              </tbody>
            </table>
            """ % (
                _("Business impact"), _("Host"), _("Service"),
                _("Since"), _("Last check"), _("Output")
            )
        else:
            problems = _(" - no problems")
            panel_bi += """<div class="alert alert-success"><p>%s</p></div>""" % (_("No problems."))

        panel_bi += """
              </div>
            </div>
        </div>
        """

        # Update panel templating fields
        panel_bi = panel_bi.replace("#bi-id#", "%d" % (bi))
        if bi != -1:
            panel_bi = panel_bi.replace("#bi-text#",
                                        Helper.get_html_business_impact(bi, icon=True, text=True))
        else:
            panel_bi = panel_bi.replace("#bi-text#", "")
        panel_bi = panel_bi.replace("#problems#", "%s" % problems)
        panel_bi = panel_bi.replace("#nb_problems#", "%s" % problems_count)
        panel_bi = panel_bi.replace("#nb_hosts_problems#", "%s" % hosts_problems)
        panel_bi = panel_bi.replace("#nb_services_problems#", "%s" % services_problems)

        alert_hosts_problems = '<span class="fa fa-bolt"></span>' * worst_hosts_state
        alert_services_problems = '<span class="fa fa-bolt"></span>' * worst_services_state

        panel_bi = panel_bi.replace("#alert_hosts_problems#", "%s" % alert_hosts_problems)
        panel_bi = panel_bi.replace("#alert_services_problems#", "%s" % alert_services_problems)

        # Update title
        title = """<span class="fa fa-heartbeat"></span><span>&nbsp;#bi-text##problems#</span>"""

        problems = _(""" (#nb_problems# <span class="fa fa-bolt"></span>)""")
        if problems_count == 0:
            problems = ""

        title = title.replace("#bi-text#",
                              Helper.get_html_business_impact(bi, icon=True, text=False, less=2))
        title = title.replace("#problems#", "%s" % problems)
        title = title.replace("#nb_problems#", "%s" % problems_count)

        return {'bi': bi, 'rows': rows, 'title': title, 'panel_bi': panel_bi}
