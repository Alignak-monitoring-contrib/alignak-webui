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
    Plugin actions - define Alignak external commands
"""

# pylint: disable=invalid-name
commands = {
    'process_host_check_result': {
        'global': False, 'elements_type': 'host',
        'title': _("Send an host check result"),
        "parameters": ["ls_state_id", "ls_output"]
    },
    'process_host_output': {
        'global': False, 'elements_type': 'host',
        'title': _("Send an host check output"),
        "parameters": ["ls_output"]
    },
    'del_all_host_downtimes': {
        'global': False, 'elements_type': 'host',
        'title': _("Delete all host downtimes"),
        "parameters": []
    },
    'process_service_check_result': {
        'global': False, 'elements_type': 'service',
        'title': _("Send a service check result"),
        "parameters": ["ls_state_id", "ls_output"]
    },
    'process_service_output': {
        'global': False, 'elements_type': 'service',
        'title': _("Send a service check output"),
        "parameters": ["ls_output"]
    },
    'del_all_svc_downtimes': {
        'global': False, 'elements_type': 'service',
        'title': _("Delete all service downtimes"),
        "parameters": []
    },
}

# Hereunder are all the Alignak knonw external commands. They need to be prepared and updated
# as the `commands` defined before!
alignak_commands = {
    'change_contact_modsattr':
        {'global': True, 'args': ['contact', None]},
    'change_contact_modhattr':
        {'global': True, 'args': ['contact', None]},
    'change_contact_modattr':
        {'global': True, 'args': ['contact', None]},
    'change_contact_host_notification_timeperiod':
        {'global': True, 'args': ['contact', 'time_period']},
    'add_svc_comment':
        {'global': False, 'args': ['service', 'obsolete', 'author', None]},
    'add_host_comment':
        {'global': False, 'args': ['host', 'obsolete', 'author', None]},
    'acknowledge_svc_problem':
        {'global': False, 'args': ['service', 'to_int', 'to_bool', 'obsolete', 'author', None]},
    'acknowledge_host_problem':
        {'global': False, 'args': ['host', 'to_int', 'to_bool', 'obsolete', 'author', None]},
    'acknowledge_svc_problem_expire':
        {'global': False, 'args': ['service', 'to_int', 'to_bool',
                                   'obsolete', 'to_int', 'author', None]},
    'acknowledge_host_problem_expire':
        {'global': False,
         'args': ['host', 'to_int', 'to_bool', 'obsolete', 'to_int', 'author', None]},
    'change_contact_svc_notification_timeperiod':
        {'global': True, 'args': ['contact', 'time_period']},
    'change_custom_contact_var':
        {'global': True, 'args': ['contact', None, None]},
    'change_custom_host_var':
        {'global': False, 'args': ['host', None, None]},
    'change_custom_svc_var':
        {'global': False, 'args': ['service', None, None]},
    'change_global_host_event_handler':
        {'global': True, 'args': ['command']},
    'change_global_svc_event_handler':
        {'global': True, 'args': ['command']},
    'change_host_check_command':
        {'global': False, 'args': ['host', 'command']},
    'change_host_check_timeperiod':
        {'global': False, 'args': ['host', 'time_period']},
    'change_host_event_handler':
        {'global': False, 'args': ['host', 'command']},
    'change_host_snapshot_command':
        {'global': False, 'args': ['host', 'command']},
    'change_host_modattr':
        {'global': False, 'args': ['host', 'to_int']},
    'change_max_host_check_attempts':
        {'global': False, 'args': ['host', 'to_int']},
    'change_max_svc_check_attempts':
        {'global': False, 'args': ['service', 'to_int']},
    'change_normal_host_check_interval':
        {'global': False, 'args': ['host', 'to_int']},
    'change_normal_svc_check_interval':
        {'global': False, 'args': ['service', 'to_int']},
    'change_retry_host_check_interval':
        {'global': False, 'args': ['host', 'to_int']},
    'change_retry_svc_check_interval':
        {'global': False, 'args': ['service', 'to_int']},
    'change_svc_check_command':
        {'global': False, 'args': ['service', 'command']},
    'change_svc_check_timeperiod':
        {'global': False, 'args': ['service', 'time_period']},
    'change_svc_event_handler':
        {'global': False, 'args': ['service', 'command']},
    'change_svc_snapshot_command':
        {'global': False, 'args': ['service', 'command']},
    'change_svc_modattr':
        {'global': False, 'args': ['service', 'to_int']},
    'change_svc_notification_timeperiod':
        {'global': False, 'args': ['service', 'time_period']},
    'delay_host_notification':
        {'global': False, 'args': ['host', 'to_int']},
    'delay_svc_notification':
        {'global': False, 'args': ['service', 'to_int']},
    'del_all_contact_downtimes':
        {'global': False, 'args': ['contact']},
    'del_all_host_comments':
        {'global': False, 'args': ['host']},
    'del_all_host_downtimes':
        {'global': False, 'args': ['host']},
    'del_all_svc_comments':
        {'global': False, 'args': ['service']},
    'del_all_svc_downtimes':
        {'global': False, 'args': ['service']},
    'del_contact_downtime':
        {'global': True, 'args': [None]},
    'del_host_comment':
        {'global': True, 'args': [None]},
    'del_host_downtime':
        {'global': True, 'args': [None]},
    'del_svc_comment':
        {'global': True, 'args': [None]},
    'del_svc_downtime':
        {'global': True, 'args': [None]},
    'disable_all_notifications_beyond_host':
        {'global': False, 'args': ['host']},
    'disable_contactgroup_host_notifications':
        {'global': True, 'args': ['contact_group']},
    'disable_contactgroup_svc_notifications':
        {'global': True, 'args': ['contact_group']},
    'disable_contact_host_notifications':
        {'global': True, 'args': ['contact']},
    'disable_contact_svc_notifications':
        {'global': True, 'args': ['contact']},
    'disable_event_handlers':
        {'global': True, 'args': []},
    'disable_failure_prediction':
        {'global': True, 'args': []},
    'disable_flap_detection':
        {'global': True, 'args': []},
    'disable_hostgroup_host_checks':
        {'global': True, 'args': ['host_group']},
    'disable_hostgroup_host_notifications':
        {'global': True, 'args': ['host_group']},
    'disable_hostgroup_passive_host_checks':
        {'global': True, 'args': ['host_group']},
    'disable_hostgroup_passive_svc_checks':
        {'global': True, 'args': ['host_group']},
    'disable_hostgroup_svc_checks':
        {'global': True, 'args': ['host_group']},
    'disable_hostgroup_svc_notifications':
        {'global': True, 'args': ['host_group']},
    'disable_host_and_child_notifications':
        {'global': False, 'args': ['host']},
    'disable_host_check':
        {'global': False, 'args': ['host']},
    'disable_host_event_handler':
        {'global': False, 'args': ['host']},
    'disable_host_flap_detection':
        {'global': False, 'args': ['host']},
    'disable_host_freshness_checks':
        {'global': True, 'args': []},
    'disable_host_notifications':
        {'global': False, 'args': ['host']},
    'disable_host_svc_checks':
        {'global': False, 'args': ['host']},
    'disable_host_svc_notifications':
        {'global': False, 'args': ['host']},
    'disable_notifications':
        {'global': True, 'args': []},
    'disable_passive_host_checks':
        {'global': False, 'args': ['host']},
    'disable_passive_svc_checks':
        {'global': False, 'args': ['service']},
    'disable_performance_data':
        {'global': True, 'args': []},
    'disable_servicegroup_host_checks':
        {'global': True, 'args': ['service_group']},
    'disable_servicegroup_host_notifications':
        {'global': True, 'args': ['service_group']},
    'disable_servicegroup_passive_host_checks':
        {'global': True, 'args': ['service_group']},
    'disable_servicegroup_passive_svc_checks':
        {'global': True, 'args': ['service_group']},
    'disable_servicegroup_svc_checks':
        {'global': True, 'args': ['service_group']},
    'disable_servicegroup_svc_notifications':
        {'global': True, 'args': ['service_group']},
    'disable_service_flap_detection':
        {'global': False, 'args': ['service']},
    'disable_service_freshness_checks':
        {'global': True, 'args': []},
    'disable_svc_check':
        {'global': False, 'args': ['service']},
    'disable_svc_event_handler':
        {'global': False, 'args': ['service']},
    'disable_svc_flap_detection':
        {'global': False, 'args': ['service']},
    'disable_svc_notifications':
        {'global': False, 'args': ['service']},
    'enable_all_notifications_beyond_host':
        {'global': False, 'args': ['host']},
    'enable_contactgroup_host_notifications':
        {'global': True, 'args': ['contact_group']},
    'enable_contactgroup_svc_notifications':
        {'global': True, 'args': ['contact_group']},
    'enable_contact_host_notifications':
        {'global': True, 'args': ['contact']},
    'enable_contact_svc_notifications':
        {'global': True, 'args': ['contact']},
    'enable_event_handlers':
        {'global': True, 'args': []},
    'enable_failure_prediction':
        {'global': True, 'args': []},
    'enable_flap_detection':
        {'global': True, 'args': []},
    'enable_hostgroup_host_checks':
        {'global': True, 'args': ['host_group']},
    'enable_hostgroup_host_notifications':
        {'global': True, 'args': ['host_group']},
    'enable_hostgroup_passive_host_checks':
        {'global': True, 'args': ['host_group']},
    'enable_hostgroup_passive_svc_checks':
        {'global': True, 'args': ['host_group']},
    'enable_hostgroup_svc_checks':
        {'global': True, 'args': ['host_group']},
    'enable_hostgroup_svc_notifications':
        {'global': True, 'args': ['host_group']},
    'enable_host_and_child_notifications':
        {'global': False, 'args': ['host']},
    'enable_host_check':
        {'global': False, 'args': ['host']},
    'enable_host_event_handler':
        {'global': False, 'args': ['host']},
    'enable_host_flap_detection':
        {'global': False, 'args': ['host']},
    'enable_host_freshness_checks':
        {'global': True, 'args': []},
    'enable_host_notifications':
        {'global': False, 'args': ['host']},
    'enable_host_svc_checks':
        {'global': False, 'args': ['host']},
    'enable_host_svc_notifications':
        {'global': False, 'args': ['host']},
    'enable_notifications':
        {'global': True, 'args': []},
    'enable_passive_host_checks':
        {'global': False, 'args': ['host']},
    'enable_passive_svc_checks':
        {'global': False, 'args': ['service']},
    'enable_performance_data':
        {'global': True, 'args': []},
    'enable_servicegroup_host_checks':
        {'global': True, 'args': ['service_group']},
    'enable_servicegroup_host_notifications':
        {'global': True, 'args': ['service_group']},
    'enable_servicegroup_passive_host_checks':
        {'global': True, 'args': ['service_group']},
    'enable_servicegroup_passive_svc_checks':
        {'global': True, 'args': ['service_group']},
    'enable_servicegroup_svc_checks':
        {'global': True, 'args': ['service_group']},
    'enable_servicegroup_svc_notifications':
        {'global': True, 'args': ['service_group']},
    'enable_service_freshness_checks':
        {'global': True, 'args': []},
    'enable_svc_check':
        {'global': False, 'args': ['service']},
    'enable_svc_event_handler':
        {'global': False, 'args': ['service']},
    'enable_svc_flap_detection':
        {'global': False, 'args': ['service']},
    'enable_svc_notifications':
        {'global': False, 'args': ['service']},
    'process_file':
        {'global': True, 'args': [None, 'to_bool']},
    'process_host_check_result':
        {'global': False, 'args': ['host', 'to_int', None]},
    'process_host_output':
        {'global': False, 'args': ['host', None]},
    'process_service_check_result':
        {'global': False, 'args': ['service', 'to_int', None]},
    'process_service_output':
        {'global': False, 'args': ['service', None]},
    'read_state_information':
        {'global': True, 'args': []},
    'remove_host_acknowledgement':
        {'global': False, 'args': ['host']},
    'remove_svc_acknowledgement':
        {'global': False, 'args': ['service']},
    'restart_program':
        {'global': True, 'internal': True, 'args': []},
    'reload_config':
        {'global': True, 'internal': True, 'args': []},
    'save_state_information':
        {'global': True, 'args': []},
    'schedule_and_propagate_host_downtime':
        {'global': False, 'args': ['host', 'to_int', 'to_int', 'to_bool',
                                   'to_int', 'to_int', 'author', None]},
    'schedule_and_propagate_triggered_host_downtime':
        {'global': False, 'args': ['host', 'to_int', 'to_int', 'to_bool',
                                   'to_int', 'to_int', 'author', None]},
    'schedule_contact_downtime':
        {'global': True, 'args': ['contact', 'to_int', 'to_int', 'author', None]},
    'schedule_forced_host_check':
        {'global': False, 'args': ['host', 'to_int']},
    'schedule_forced_host_svc_checks':
        {'global': False, 'args': ['host', 'to_int']},
    'schedule_forced_svc_check':
        {'global': False, 'args': ['service', 'to_int']},
    'schedule_hostgroup_host_downtime':
        {'global': True, 'args': ['host_group', 'to_int', 'to_int',
                                  'to_bool', None, 'to_int', 'author', None]},
    'schedule_hostgroup_svc_downtime':
        {'global': True, 'args': ['host_group', 'to_int', 'to_int', 'to_bool',
                                  None, 'to_int', 'author', None]},
    'schedule_host_check':
        {'global': False, 'args': ['host', 'to_int']},
    'schedule_host_downtime':
        {'global': False, 'args': ['host', 'to_int', 'to_int', 'to_bool',
                                   None, 'to_int', 'author', None]},
    'schedule_host_svc_checks':
        {'global': False, 'args': ['host', 'to_int']},
    'schedule_host_svc_downtime':
        {'global': False, 'args': ['host', 'to_int', 'to_int', 'to_bool',
                                   None, 'to_int', 'author', None]},
    'schedule_servicegroup_host_downtime':
        {'global': True, 'args': ['service_group', 'to_int', 'to_int', 'to_bool',
                                  None, 'to_int', 'author', None]},
    'schedule_servicegroup_svc_downtime':
        {'global': True, 'args': ['service_group', 'to_int', 'to_int', 'to_bool',
                                  None, 'to_int', 'author', None]},
    'schedule_svc_check':
        {'global': False, 'args': ['service', 'to_int']},
    'schedule_svc_downtime':
        {'global': False, 'args': ['service', 'to_int', 'to_int',
                                   'to_bool', None, 'to_int', 'author', None]},
    'send_custom_host_notification':
        {'global': False, 'args': ['host', 'to_int', 'author', None]},
    'send_custom_svc_notification':
        {'global': False, 'args': ['service', 'to_int', 'author', None]},
    'set_host_notification_number':
        {'global': False, 'args': ['host', 'to_int']},
    'set_svc_notification_number':
        {'global': False, 'args': ['service', 'to_int']},
    'shutdown_program':
        {'global': True, 'args': []},
    'start_accepting_passive_host_checks':
        {'global': True, 'args': []},
    'start_accepting_passive_svc_checks':
        {'global': True, 'args': []},
    'start_executing_host_checks':
        {'global': True, 'args': []},
    'start_executing_svc_checks':
        {'global': True, 'args': []},
    'start_obsessing_over_host':
        {'global': False, 'args': ['host']},
    'start_obsessing_over_host_checks':
        {'global': True, 'args': []},
    'start_obsessing_over_svc':
        {'global': False, 'args': ['service']},
    'start_obsessing_over_svc_checks':
        {'global': True, 'args': []},
    'stop_accepting_passive_host_checks':
        {'global': True, 'args': []},
    'stop_accepting_passive_svc_checks':
        {'global': True, 'args': []},
    'stop_executing_host_checks':
        {'global': True, 'args': []},
    'stop_executing_svc_checks':
        {'global': True, 'args': []},
    'stop_obsessing_over_host':
        {'global': False, 'args': ['host']},
    'stop_obsessing_over_host_checks':
        {'global': True, 'args': []},
    'stop_obsessing_over_svc':
        {'global': False, 'args': ['service']},
    'stop_obsessing_over_svc_checks':
        {'global': True, 'args': []},
    'launch_svc_event_handler':
        {'global': False, 'args': ['service']},
    'launch_host_event_handler':
        {'global': False, 'args': ['host']},
    # Now internal calls
    'add_simple_host_dependency':
        {'global': False, 'args': ['host', 'host']},
    'del_host_dependency':
        {'global': False, 'args': ['host', 'host']},
    'add_simple_poller':
        {'global': True, 'internal': True, 'args': [None, None, None, None]},
}
