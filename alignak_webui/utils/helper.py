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

# from alignak_webui import _
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
        # self.config = get_app_config()

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
        stars = '<i class="fa fa-star"></i>' * business_impact

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
        # unmanaged_problems = hs['nb_problems'] - (hs['nb_acknowledged'] + hs['nb_in_downtime'])
        # pct_unmanaged_problems = round(100.0 * unmanaged_problems / hs['nb_elts'], 2) \
        #     if hs['nb_elts'] else -1
        # _('Unmanaged problems')

        if percentage:
            pp_h = """
            <div id="panel_percentage_hosts" class="panel panel-default">
                <div class="panel-heading clearfix">
                  <i class="fa fa-server"></i>
                  <span class="hosts-all"
                      data-count="#hs_nb_elts#"
                      data-problems="#hs_nb_problems#">
                    #hs_nb_elts# hosts (#hs_nb_problems# problems).
                    </span>

                  <div class="pull-right">
                    <a href="#p_pp_h" class="btn btn-xs btn-raised"
                       data-toggle="collapse">
                       <i class="fa fa-fw %s"></i>
                    </a>
                  </div>
                </div>
                <div id="p_pp_h" class="panel-collapse collapse %s">
                  <div class="panel-body">
                    <div class="row">
                      <div class="col-xs-3 col-sm-3 text-center">
                        <div class="col-xs-12 text-center">
                          <a href="#hosts_table_url#" class="sla_hosts_%s">
                            <div>#hs_pct_sla#%%</div>
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
                              <span class="hosts-count">#hs_pct_up#%%</span>
                            </a>
                          </div>
                          <div class="col-xs-4 text-center">
                            <a href="#hosts_table_url#?search=ls_state:DOWN"
                              class="item_host_down" title="Down">
                              <span class="hosts-count">#hs_pct_down#%%</span>
                            </a>
                          </div>
                          <div class="col-xs-4 text-center">
                            <a href="#hosts_table_url#?search=ls_state:UNREACHABLE"
                              class="item_host_unreachable" title="Unreachable">
                              <span class="hosts-count">#hs_pct_unreachable#%%</span>
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
                              <span class="hosts-count">#hs_pct_acknowledged#%%</span>
                            </a>
                            <span>/</span>
                            <a href="#hosts_table_url#?search=ls_state:IN_DOWNTIME"
                              class="item_host_in_downtime" title="In downtime">
                              <span class="hosts-count">#hs_pct_in_downtime#%%</span>
                            </a>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
            </div>
            """ % ('fa-caret-up' if collapsed else 'fa-caret-down',
                   'in' if not collapsed else '',
                   font, _('Hosts SLA'))

            pp_h = pp_h.replace("#hs_nb_elts#", "%d" % hs['nb_elts'])
            pp_h = pp_h.replace("#hs_nb_problems#", "%d" % hs['nb_problems'])
            pp_h = pp_h.replace("#hs_pct_sla#", "%d" % hs['pct_up'])
            pp_h = pp_h.replace("#hs_pct_up#", "%d" % hs['pct_up'])
            pp_h = pp_h.replace("#hs_pct_down#", "%d" % hs['pct_down'])
            pp_h = pp_h.replace("#hs_pct_unreachable#", "%d" % hs['pct_unreachable'])
            pp_h = pp_h.replace("#hs_pct_acknowledged#", "%d" % hs['pct_acknowledged'])
            pp_h = pp_h.replace("#hs_pct_in_downtime#", "%d" % hs['pct_in_downtime'])
            pp_h = pp_h.replace("#hosts_table_url#", url)
            content = pp_h
        else:
            pc_h = """
            <div id="panel_counters_hosts" class="panel panel-default">
                <div class="panel-heading clearfix">
                  <i class="fa fa-server"></i>
                  <span class="hosts-all"
                      data-count="#hs_nb_elts#"
                      data-problems="#hs_nb_problems#">
                    #hs_nb_elts# hosts (#hs_nb_problems# problems).
                    </span>

                  <div class="pull-right">
                    <a href="#p_pc_h" class="btn btn-xs btn-raised"
                       data-toggle="collapse">
                       <i class="fa fa-fw %s"></i>
                    </a>
                  </div>
                </div>
                <div id="p_pc_h" class="panel-collapse collapse %s">
                  <div class="panel-body">
                    <div class="col-xs-12 col-sm-9 text-center">
                      <div class="col-xs-4 text-center">
                        <a href="#hosts_table_url#?search=ls_state:UP"
                          class="item_host_up" title="Up">
                          <span class="hosts-count">#hs_nb_up#</span>
                        </a>
                      </div>
                      <div class="col-xs-4 text-center">
                        <a href="#hosts_table_url#?search=ls_state:DOWN"
                          class="item_host_down" title="Down">
                          <span class="hosts-count">#hs_nb_down#</span>
                        </a>
                      </div>
                      <div class="col-xs-4 text-center">
                        <a href="#hosts_table_url#?search=ls_state:UNREACHABLE"
                          class="item_host_unreachable" title="Unreachable">
                          <span class="hosts-count">#hs_nb_unreachable#</span>
                        </a>
                      </div>
                    </div>

                    <div class="col-xs-12 col-sm-3 text-center">
                      <a href="#hosts_table_url#?search=ls_state:acknowledged"
                        class="item_host_acknowledged" title="Acknowledged">
                        <span class="hosts-count">#hs_nb_acknowledged#</span>
                      </a>
                      <span>/</span>
                      <a href="#hosts_table_url#?search=ls_state:IN_DOWNTIME"
                        class="item_host_in_downtime" title="In downtime">
                        <span class="hosts-count">#hs_nb_in_downtime#</span>
                      </a>
                    </div>
                  </div>
                </div>
            </div>
            """ % ('fa-caret-up' if collapsed else 'fa-caret-down',
                   'in' if not collapsed else '')
            pc_h = pc_h.replace("#hs_nb_elts#", "%d" % hs['nb_elts'])
            pc_h = pc_h.replace("#hs_nb_problems#", "%d" % hs['nb_problems'])
            pc_h = pc_h.replace("#hs_nb_up#", "%d" % hs['nb_up'])
            pc_h = pc_h.replace("#hs_nb_down#", "%d" % hs['nb_down'])
            pc_h = pc_h.replace("#hs_nb_unreachable#", "%d" % hs['nb_unreachable'])
            pc_h = pc_h.replace("#hs_nb_acknowledged#", "%d" % hs['nb_acknowledged'])
            pc_h = pc_h.replace("#hs_nb_in_downtime#", "%d" % hs['nb_in_downtime'])
            pc_h = pc_h.replace("#hosts_table_url#", url)
            content = pc_h

        return content

    @staticmethod
    def get_html_services_count_panel(ss, url, collapsed=False, percentage=False):
        """

        :param hs: services livesynthesis as provided by the get_livesynthesis or
                   get_livesynthesis_history functions
        :param url: url to use for the links to an host table
        :param collapsed: True if the panel is collapsed
        :param percentage: True to build a percentage panel, else build a count panel
        :return:
        """
        content = ''

        logger.info("Services synthesis: %s", ss)
        sla = ss['pct_ok']
        font = 'ok' if sla >= 95.0 else 'warning' if sla >= 90.0 else 'critical'
        # unmanaged_problems = ss['nb_problems'] - (ss['nb_acknowledged'] + ss['nb_in_downtime'])
        # pct_unmanaged_problems = round(100.0 * unmanaged_problems / ss['nb_elts'], 2) \
        #     if ss['nb_elts'] else -1
        # _('Unmanaged problems')

        if percentage:
            pp_s = """
            <div id="panel_percentage_services" class="panel panel-default">
                <div class="panel-heading clearfix">
                  <i class="fa fa-server"></i>
                  <span class="services-all"
                      data-count="#ss_nb_elts#"
                      data-problems="#ss_nb_problems#">
                    #ss_nb_elts# services (#ss_nb_problems# problems).
                    </span>

                  <div class="pull-right">
                    <a href="#p_pp_s" class="btn btn-xs btn-raised"
                       data-toggle="collapse">
                       <i class="fa fa-fw %s"></i>
                    </a>
                  </div>
                </div>
                <div id="p_pp_s" class="panel-collapse collapse %s">
                  <div class="panel-body">
                    <div class="row">
                      <div class="col-xs-3 col-sm-3 text-center">
                        <div class="col-xs-12 text-center">
                          <a href="#services_table_url#" class="sla_services_%s">
                            <div>#ss_pct_ok#%%</div>
                            <i class="fa fa-4x fa-server"></i>
                            <p>%s</p>
                          </a>
                        </div>
                      </div>

                      <div class="col-xs-9 col-sm-9 text-center">
                        <div class="row">
                          <div class="col-xs-4 text-center">
                            <a href="#services_table_url#?search=ls_state:OK"
                              class="item_service_ok" title="ok">
                              <span class="services-count">#ss_pct_ok#%%</span>
                            </a>
                          </div>
                          <div class="col-xs-4 text-center">
                            <a href="#services_table_url#?search=ls_state:WARNING"
                              class="item_service_warning" title="warning">
                              <span class="services-count">#ss_pct_warning#%%</span>
                            </a>
                          </div>
                          <div class="col-xs-4 text-center">
                            <a href="#services_table_url#?search=ls_state:CRITICAL"
                              class="item_service_critical" title="critical">
                              <span class="services-count">#ss_pct_critical#%%</span>
                            </a>
                          </div>
                          <div class="col-xs-4 text-center">
                            <a href="#services_table_url#?search=ls_state:UNKNONW"
                              class="item_service_unknown" title="unknown">
                              <span class="services-count">#ss_pct_unknown#%%</span>
                            </a>
                          </div>
                          <div class="col-xs-4 text-center">
                            <a href="#services_table_url#?search=ls_state:UNREACHABLE"
                              class="item_service_unreachable" title="unreachable">
                              <span class="services-count">#ss_pct_unreachable#%%</span>
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
                              <span class="services-count">#ss_pct_acknowledged#%%</span>
                            </a>
                            <span>/</span>
                            <a href="#services_table_url#?search=ls_state:IN_DOWNTIME"
                              class="item_service_in_downtime" title="in_downtime">
                              <span class="services-count">#ss_pct_in_downtime#%%</span>
                            </a>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
            </div>
            """ % ('fa-caret-up' if collapsed else 'fa-caret-down',
                   'in' if not collapsed else '',
                   font, _('Services SLA'))

            pp_s = pp_s.replace("#ss_nb_elts#", "%d" % ss['nb_elts'])
            pp_s = pp_s.replace("#ss_nb_problems#", "%d" % ss['nb_problems'])
            pp_s = pp_s.replace("#ss_pct_ok#", "%d" % ss['pct_ok'])
            pp_s = pp_s.replace("#ss_pct_warning#", "%d" % ss['pct_warning'])
            pp_s = pp_s.replace("#ss_pct_critical#", "%d" % ss['pct_critical'])
            pp_s = pp_s.replace("#ss_pct_unknown#", "%d" % ss['pct_unknown'])
            pp_s = pp_s.replace("#ss_pct_unreachable#", "%d" % ss['pct_unreachable'])
            pp_s = pp_s.replace("#ss_pct_acknowledged#", "%d" % ss['pct_acknowledged'])
            pp_s = pp_s.replace("#ss_pct_in_downtime#", "%d" % ss['pct_in_downtime'])
            pp_s = pp_s.replace("#services_table_url#", url)
            content = pp_s
        else:
            pc_s = """
            <div id="panel_counters_services" class="panel panel-default">
                <div class="panel-heading clearfix">
                  <i class="fa fa-server"></i>
                  <span class="services-all"
                      data-count="#ss_nb_elts#"
                      data-problems="#ss_nb_problems#">
                    #ss_nb_elts# services (#ss_nb_problems# problems).
                    </span>

                  <div class="pull-right">
                    <a href="#p_pc_s" class="btn btn-xs btn-raised"
                       data-toggle="collapse">
                       <i class="fa fa-fw %s"></i>
                    </a>
                  </div>
                </div>
                <div id="p_pc_s" class="panel-collapse collapse %s">
                  <div class="panel-body">
                    <div class="col-xs-12 col-sm-9 text-center">
                      <div class="col-xs-2 text-center">
                        <a href="#services_table_url#?search=ls_state:OK"
                          class="item_service_ok" title="Ok">
                          <span class="services-count">#ss_nb_ok#</span>
                        </a>
                      </div>
                      <div class="col-xs-2 text-center">
                        <a href="#services_table_url#?search=ls_state:WARNING"
                          class="item_service_critical" title="Warning">
                          <span class="services-count">#ss_nb_warning#</span>
                        </a>
                      </div>
                      <div class="col-xs-2 text-center">
                        <a href="#services_table_url#?search=ls_state:CRITICAL"
                          class="item_service_critical" title="Critical">
                          <span class="services-count">#ss_nb_critical#</span>
                        </a>
                      </div>
                      <div class="col-xs-2 text-center">
                        <a href="#services_table_url#?search=ls_state:UNKNOWN"
                          class="item_service_unknown" title="Unknown">
                          <span class="services-count">#ss_nb_unknown#</span>
                        </a>
                      </div>
                      <div class="col-xs-2 text-center">
                        <a href="#services_table_url#?search=ls_state:UNREACHABLE"
                          class="item_service_unreachable" title="Unreachable">
                          <span class="services-count">#ss_nb_unreachable#</span>
                        </a>
                      </div>
                    </div>

                    <div class="col-xs-12 col-sm-3 text-center">
                      <a href="#services_table_url#?search=ls_state:acknowledged"
                        class="item_service_acknowledged" title="Acknowledged">
                        <span class="services-count">#ss_nb_acknowledged#</span>
                      </a>
                      <span>/</span>
                      <a href="#services_table_url#?search=ls_state:IN_DOWNTIME"
                        class="item_service_in_downtime" title="In downtime">
                        <span class="services-count">#ss_nb_in_downtime#</span>
                      </a>
                    </div>
                  </div>
                </div>
            </div>
            """ % ('fa-caret-up' if collapsed else 'fa-caret-down',
                   'in' if not collapsed else '')

            pc_s = pc_s.replace("#ss_nb_elts#", "%d" % ss['nb_elts'])
            pc_s = pc_s.replace("#ss_nb_problems#", "%d" % ss['nb_problems'])
            pc_s = pc_s.replace("#ss_nb_ok#", "%d" % ss['nb_ok'])
            pc_s = pc_s.replace("#ss_nb_warning#", "%d" % ss['nb_warning'])
            pc_s = pc_s.replace("#ss_nb_critical#", "%d" % ss['nb_critical'])
            pc_s = pc_s.replace("#ss_nb_unreachable#", "%d" % ss['nb_unreachable'])
            pc_s = pc_s.replace("#ss_nb_unknown#", "%d" % ss['nb_unknown'])
            pc_s = pc_s.replace("#ss_nb_acknowledged#", "%d" % ss['nb_acknowledged'])
            pc_s = pc_s.replace("#ss_nb_in_downtime#", "%d" % ss['nb_in_downtime'])
            pc_s = pc_s.replace("#services_table_url#", url)
            content = pc_s

        return content

    @staticmethod
    def get_html_id(obj_type, name):
        """
        Returns an host/service/contact ... HTML identifier

        If parameters are not valid, returns 'n/a'

        obj_type specifies object type
        name specifes the object name

        :param obj_type: host, service, contact
        :type obj_type: string
        :param name: object name
        :type name: string

        :return: valid HTML identifier
        :rtype: string
        """
        if not obj_type or not name:
            return 'n/a'

        return re.sub('[^A-Za-z0-9-_]', '', "%s-%s" % (obj_type, name))

    @staticmethod
    # pylint: disable=too-many-locals
    def get_html_livestate(datamgr, panels, bi=-1, search=None, actions=False):
        """
        Get HTML formatted live state

        Update system live synthesis and build header elements

        :param bi: business impact
        :type bi: int

        :return: hosts_states and services_states HTML strings in a dictionary
        :rtype: dict
        """
        logger.debug("get_html_livestate, BI: %d, search: '%s'", bi, search)
        if search is None or not isinstance(search, dict):
            search = {}
        if 'where' not in search:
            search.update({'where': {"ls_state_id": {"$ne": 0}}})
            search['where'].update({'ls_acknowledged': False})
            search['where'].update({'ls_downtimed': False})
        if 'sort' not in search:
            search.update({'sort': '-_overall_state_id'})
        if bi != -1:
            search['where'].update({'business_impact': bi})

        items = []
        # Copy because the search filter is updated by the function ...
        search_hosts = search.copy()
        hosts = datamgr.get_hosts(search=search_hosts, embedded=False)
        items.extend(hosts)
        logger.debug("get_html_livestate, livestate %d (%s), %d hosts", bi, search, len(items))

        # Copy because the search filter is updated by the function ...
        if 'embedded' not in search:
            search.update({'embedded': {'host': 1}})
        search_services = search.copy()
        services = datamgr.get_services(search=search_services, embedded=True)
        items.extend(services)
        logger.debug("get_html_livestate, livestate %d (%s), %d services", bi, search, len(items))

        rows = []
        problems_count = 0
        current_host = ''
        hosts_problems = -1
        services_problems = -1
        for item in items:
            logger.debug("get_html_livestate, item: %s", item)
            problems_count += 1
            if item.object_type == "service" and services_problems == -1:
                services_problems = item.get_total_count()
            if item.object_type == "host" and hosts_problems == -1:
                hosts_problems = item.get_total_count()

            elt_id = Helper.get_html_id("host", item.name)

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
            <tr data-toggle="collapse" data-target="#details-%s" class="accordion-toggle">
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td class="hidden-xs">%s</td>
                <td class="hidden-sm hidden-xs">%s%s</td>
            </tr>""" % (
                elt_id,
                item.get_html_state(text=None, title=title, extra=extra),
                Helper.get_html_commands_buttons(item, title=_("Actions")) if actions else '',
                host_url, service_url,
                Helper.print_duration(item.last_check, duration_only=True, x_elts=0),
                item.output, long_output
            )
            rows.append(tr)

            # tr2 = """
            # <tr id="details-%s" class="collapse">
            #     <td colspan="20">
            # """ % (elt_id)
            # tr2 += """
            # <div class="pull-left">
            # """
            # if item.passive_checks_enabled:
            #     tr2 += """
            #     <span>
            #         <span class="fa fa-arrow-left" title="Passive checks are enabled."></span>"""
            # if item.check_freshness:
            #     tr2 += """
            #         <span title="Freshness check is enabled">(Freshness: %s seconds)</span>
            #     </span>""" % (item.freshness_threshold)
            # else:
            #     tr2 += """</span>"""
            #
            # if item.active_checks_enabled:
            #     tr2 += """
            #     <span>
            #         <i class="fa fa-arrow-right" title="Active checks are enabled."></i>
            #         <i>
            #             Last check <strong>%s</strong>,
            #             next check in <strong>%s</strong>,
            #             attempt <strong>%d / %d</strong>
            #         </i>
            #     </span>""" % (
            #         Helper.print_duration(item.last_check, duration_only=True, x_elts=2),
            #         Helper.print_duration(item.next_check, duration_only=True, x_elts=2),
            #         int(item.current_attempt),
            #         int(item.max_attempts)
            #     )
            # tr2 += """
            # </div>
            # """
            #
            # tr2 += """
            #     </td>
            # </tr>"""
            #
            # rows.append(tr2)

        collapsed = False
        if 'livestate-bi-%d' % bi in panels:
            collapsed = panels['livestate-bi-%d' % bi]['collapsed']
        if not rows:
            collapsed = True

        panel_bi = """
        <div id="livestate-bi-#bi-id#" class="livestate-panel panel panel-default">
            <div class="panel-heading clearfix">
              <strong>
              <i class="fa fa-heartbeat"></i>
              <span class="livestate-all text-%s" data-count="#nb_problems#">
                &nbsp;#bi-text# - #problems#.
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
        """ % ('success' if problems_count == 0 else 'danger',
               'fa-caret-up' if collapsed else 'fa-caret-down',
               'in' if not collapsed else '')

        if problems_count > 0:
            problems = _("#nb_problems# problems")
            if hosts_problems > 0 and services_problems > 0:
                problems += _(" (hosts: #nb_hosts_problems#, services: #nb_services_problems#)")
            elif hosts_problems > 0:
                problems += _(" (hosts: #nb_hosts_problems#)")
            elif services_problems > 0:
                problems += _(" (services: #nb_services_problems#)")
            panel_bi += """
            <table class="table table-invisible table-condensed" data-business-impact="#bi-id#" >
              <thead><tr>
                <th width="10px"></th>
                <th width="30px"></th>
                <th width="60px">%s</th>
                <th width="90px">%s</th>
                <th width="30px">%s</th>
                <th class="hidden-sm hidden-xs" width="100%%">%s</th>
              </tr></thead>

              <tbody>
              </tbody>
            </table>
            """ % (
                _("Host"), _("Service"), _("Duration"), _("Output")
            )
        else:
            problems = _("no problems")
            panel_bi += """
            <div class="alert alert-success"><p>%s</p></div>
            """ % (_("No problems."))

        panel_bi += """
              </div>
            </div>
        </div>
        """

        # Update panel templating fields
        panel_bi = panel_bi.replace("#bi-id#", "%d" % (bi))
        panel_bi = panel_bi.replace("#bi-text#",
                                    Helper.get_html_business_impact(bi, icon=True, text=True))
        panel_bi = panel_bi.replace("#problems#", "%s" % problems)
        panel_bi = panel_bi.replace("#nb_problems#", "%s" % problems_count)
        panel_bi = panel_bi.replace("#nb_hosts_problems#", "%s" % hosts_problems)
        panel_bi = panel_bi.replace("#nb_services_problems#", "%s" % services_problems)

        return {'bi': bi, 'rows': rows, 'panel_bi': panel_bi}
