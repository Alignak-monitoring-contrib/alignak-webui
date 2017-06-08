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
    # Global commands
    'disable_event_handlers': {
        'global': True, 'elements_type': None,
        'title': _("Disable event handlers"),
        'parameters': []
    },
    'enable_event_handlers': {
        'global': True, 'elements_type': None,
        'title': _("Enable event handlers"),
        'parameters': []
    },
    'disable_flap_detection': {
        'global': True, 'elements_type': None,
        'title': _("Disable flapping detection"),
        'parameters': []
    },
    'enable_flap_detection': {
        'global': True, 'elements_type': None,
        'title': _("Enable flapping detection"),
        'parameters': []
    },
    'disable_notification': {
        'global': True, 'elements_type': None,
        'title': _("Disable notification"),
        'parameters': []
    },
    'enable_notification': {
        'global': True, 'elements_type': None,
        'title': _("Enable notification"),
        'parameters': []
    },
    'disable_performance_data': {
        'global': True, 'elements_type': None,
        'title': _("Disable performance data"),
        'parameters': []
    },
    'enable_performance_data': {
        'global': True, 'elements_type': None,
        'title': _("Enable performance data"),
        'parameters': []
    },

    # Hostgroup commands
    'disable_hostgroup_host_checks': {
        'global': False, 'elements_type': 'hostgroup',
        'title': _("Disable hosts active checks for an hostgroup"),
        'parameters': []
    },
    'enable_hostgroup_host_checks': {
        'global': False, 'elements_type': 'hostgroup',
        'title': _("Enable hosts active checks for an hostgroup"),
        'parameters': []
    },
    'disable_hostgroup_svc_checks': {
        'global': False, 'elements_type': 'hostgroup',
        'title': _("Disable services active checks for an hostgroup"),
        'parameters': []
    },
    'enable_hostgroup_svc_checks': {
        'global': False, 'elements_type': 'hostgroup',
        'title': _("Enable services active checks for an hostgroup"),
        'parameters': []
    },
    'disable_hostgroup_passive_host_checks': {
        'global': False, 'elements_type': 'hostgroup',
        'title': _("Disable hosts passive checks for an hostgroup"),
        'parameters': []
    },
    'enable_hostgroup_passive_host_checks': {
        'global': False, 'elements_type': 'hostgroup',
        'title': _("Enable hosts passive checks for an hostgroup"),
        'parameters': []
    },
    'disable_hostgroup_passive_svc_checks': {
        'global': False, 'elements_type': 'hostgroup',
        'title': _("Disable services passive checks for an hostgroup"),
        'parameters': []
    },
    'enable_hostgroup_passive_svc_checks': {
        'global': False, 'elements_type': 'hostgroup',
        'title': _("Enable services passive checks for an hostgroup"),
        'parameters': []
    },
    'disable_hostgroup_host_notifications': {
        'global': False, 'elements_type': 'hostgroup',
        'title': _("Disable hosts notifications for an hostgroup"),
        'parameters': []
    },
    'enable_hostgroup_host_notifications': {
        'global': False, 'elements_type': 'hostgroup',
        'title': _("Enable hosts notifications for an hostgroup"),
        'parameters': []
    },
    'disable_hostgroup_svc_notifications': {
        'global': False, 'elements_type': 'hostgroup',
        'title': _("Disable services notifications for an hostgroup"),
        'parameters': []
    },
    'enable_hostgroup_svc_notifications': {
        'global': False, 'elements_type': 'hostgroup',
        'title': _("Enable services notifications for an hostgroup"),
        'parameters': []
    },

    # Host commands
    'process_host_check_result': {
        'global': False, 'elements_type': 'host',
        'title': _("Send an host check result"),
        "parameters": ["ls_state_id", "ls_output", "ls_long_output", "ls_perf_data"]
    },
    'process_host_output': {
        'global': False, 'elements_type': 'host',
        'title': _("Send an host check output"),
        'parameters': ["ls_output"]
    },
    'disable_host_check': {
        'global': False, 'elements_type': 'host',
        'title': _("Disable active host checks"),
        'parameters': []
    },
    'enable_host_check': {
        'global': False, 'elements_type': 'host',
        'title': _("Enable active host checks"),
        'parameters': []
    },
    'disable_passive_host_checks': {
        'global': False, 'elements_type': 'host',
        'title': _("Disable passive host checks"),
        'parameters': []
    },
    'enable_passive_host_checks': {
        'global': False, 'elements_type': 'host',
        'title': _("Enable passive host checks"),
        'parameters': []
    },
    'disable_host_freshness_checks': {
        'global': False, 'elements_type': 'service',
        'title': _("Disable passive host freshness checks"),
        'parameters': []
    },
    'enable_host_freshness_checks': {
        'global': False, 'elements_type': 'service',
        'title': _("Enable passive host freshness checks"),
        'parameters': []
    },
    'del_all_host_downtimes': {
        'global': False, 'elements_type': 'host',
        'title': _("Delete all host downtimes"),
        'parameters': []
    },
    'disable_host_notifications': {
        'global': False, 'elements_type': 'host',
        'title': _("Disable host notifications"),
        'parameters': []
    },
    'enable_host_notifications': {
        'global': False, 'elements_type': 'host',
        'title': _("Enable host notifications"),
        'parameters': []
    },
    'disable_host_event_handler': {
        'global': False, 'elements_type': 'host',
        'title': _("Disable host event handler"),
        'parameters': []
    },
    'enable_host_event_handler': {
        'global': False, 'elements_type': 'host',
        'title': _("Enable host event handler"),
        'parameters': []
    },
    'disable_host_flap_detection': {
        'global': False, 'elements_type': 'host',
        'title': _("Disable host flapping detection"),
        'parameters': []
    },
    'enable_host_flap_detection': {
        'global': False, 'elements_type': 'host',
        'title': _("Enable host flapping detection"),
        'parameters': []
    },
    'disable_host_svc_checks': {
        'global': False, 'elements_type': 'host',
        'title': _("Disable host services active checks"),
        'parameters': []
    },
    'enable_host_svc_checks': {
        'global': False, 'elements_type': 'host',
        'title': _("Enable host services active checks"),
        'parameters': []
    },
    'disable_host_svc_notifications': {
        'global': False, 'elements_type': 'host',
        'title': _("Disable host services notifications"),
        'parameters': []
    },
    'enable_host_svc_notifications': {
        'global': False, 'elements_type': 'host',
        'title': _("Enable host services notifications"),
        'parameters': []
    },

    # Service commands
    'process_service_check_result': {
        'global': False, 'elements_type': 'service',
        'title': _("Send a service check result"),
        'parameters': ["ls_state_id", "ls_output"]
    },
    'process_service_output': {
        'global': False, 'elements_type': 'service',
        'title': _("Send a service check output"),
        'parameters': ["ls_output"]
    },
    'disable_svc_check': {
        'global': False, 'elements_type': 'service',
        'title': _("Disable active service checks"),
        'parameters': []
    },
    'enable_svc_check': {
        'global': False, 'elements_type': 'service',
        'title': _("Enable active service checks"),
        'parameters': []
    },
    'disable_passive_svc_checks': {
        'global': False, 'elements_type': 'service',
        'title': _("Disable passive service checks"),
        'parameters': []
    },
    'enable_passive_svc_checks': {
        'global': False, 'elements_type': 'service',
        'title': _("Enable passive service checks"),
        'parameters': []
    },
    'disable_service_freshness_checks': {
        'global': False, 'elements_type': 'service',
        'title': _("Disable passive service freshness checks"),
        'parameters': []
    },
    'enable_service_freshness_checks': {
        'global': False, 'elements_type': 'service',
        'title': _("Enable passive service freshness checks"),
        'parameters': []
    },
    'del_all_svc_downtimes': {
        'global': False, 'elements_type': 'service',
        'title': _("Delete all service downtimes"),
        'parameters': []
    },
    'disable_svc_notifications': {
        'global': False, 'elements_type': 'service',
        'title': _("Disable service notifications"),
        'parameters': []
    },
    'enable_svc_notifications': {
        'global': False, 'elements_type': 'service',
        'title': _("Enable service notifications"),
        'parameters': []
    },
    'disable_svc_event_handler': {
        'global': False, 'elements_type': 'service',
        'title': _("Disable service event handler"),
        'parameters': []
    },
    'enable_svc_event_handler': {
        'global': False, 'elements_type': 'service',
        'title': _("Enable service event handler"),
        'parameters': []
    },
    'disable_svc_flap_detection': {
        'global': False, 'elements_type': 'service',
        'title': _("Disable service flapping detection"),
        'parameters': []
    },
    'enable_svc_flap_detection': {
        'global': False, 'elements_type': 'service',
        'title': _("Enable service flapping detection"),
        'parameters': []
    },

    # User commands
    'disable_contact_host_notifications': {
        'global': False, 'elements_type': 'user',
        'title': _("Disable hosts notifications"),
        'parameters': []
    },
    'enable_contact_host_notifications': {
        'global': False, 'elements_type': 'user',
        'title': _("Enable hosts notifications"),
        'parameters': []
    },
    'disable_contact_svc_notifications': {
        'global': False, 'elements_type': 'user',
        'title': _("Disable services notifications"),
        'parameters': []
    },
    'enable_contact_svc_notifications': {
        'global': False, 'elements_type': 'user',
        'title': _("Enable services notifications"),
        'parameters': []
    },
}

# Hereunder are all the Alignak known external commands. They need to be prepared and updated
# as the `commands` defined before!
alignak_commands = {
    'change_contact_host_notification_timeperiod':
        {'global': True, 'args': ['contact', 'time_period']},

    # Start - To replace posting on alignak backend
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
    # Stop - To replace posting on alignak backend

    'delay_host_notification':
        {'global': False, 'args': ['host', 'to_int']},
    'delay_svc_notification':
        {'global': False, 'args': ['service', 'to_int']},

    # Delete downtimes, acks, ...
    'del_all_contact_downtimes':
        {'global': False, 'args': ['contact']},
    'del_contact_downtime':
        {'global': True, 'args': [None]},

    'del_all_host_comments':
        {'global': False, 'args': ['host']},
    'del_all_host_downtimes':
        {'global': False, 'args': ['host']},
    'del_all_svc_comments':
        {'global': False, 'args': ['service']},
    'del_all_svc_downtimes':
        {'global': False, 'args': ['service']},

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

    'disable_host_and_child_notifications':
        {'global': False, 'args': ['host']},

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
    'enable_all_notifications_beyond_host':
        {'global': False, 'args': ['host']},
    'enable_contactgroup_host_notifications':
        {'global': True, 'args': ['contact_group']},
    'enable_contactgroup_svc_notifications':
        {'global': True, 'args': ['contact_group']},

    'enable_host_and_child_notifications':
        {'global': False, 'args': ['host']},
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

    'stop_accepting_passive_host_checks':
        {'global': True, 'args': []},
    'stop_accepting_passive_svc_checks':
        {'global': True, 'args': []},
    'stop_executing_host_checks':
        {'global': True, 'args': []},
    'stop_executing_svc_checks':
        {'global': True, 'args': []},

    'launch_svc_event_handler':
        {'global': False, 'args': ['service']},
    'launch_host_event_handler':
        {'global': False, 'args': ['host']},
}
