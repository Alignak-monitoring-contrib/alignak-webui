<!-- Hosts information widget -->
%# embedded is True if the widget is got from an external application
%setdefault('embedded', False)
%from bottle import request
%setdefault('links', request.params.get('links', ''))
%setdefault('identifier', 'widget')
%setdefault('credentials', None)

%import time
%from alignak_webui.utils.helper import Helper
%from alignak_webui.utils.perfdata import PerfDatas

<div class="col-sm-6">
   <table class="table table-condensed table-overview">
      <colgroup>
         <col style="width: 40%" />
         <col style="width: 60%" />
      </colgroup>
      <thead>
         <tr>
            <th colspan="2">{{_('Overview:')}}</th>
         </tr>
      </thead>
      <tbody>
         <tr>
            <td><strong>{{_('Name:')}}</strong></td>
            <td>{{! host.get_html_link()}}{{_(' (%s)') % host.address if host.address else ''}}</td>
         </tr>
         <tr>
            <td><strong>{{_('Alias:')}}</strong></td>
            <td>{{host.alias}}</td>
         </tr>
         <tr>
            <td><strong>{{_('Importance:')}}</strong></td>
            <td>{{! Helper.get_html_business_impact(host.business_impact, icon=True, text=False)}}</td>
         </tr>
      </tbody>
   </table>

   <table class="table table-condensed table-status">
      <colgroup>
         <col style="width: 40%" />
         <col style="width: 60%" />
      </colgroup>
      <thead>
         <tr>
            <th colspan="2">{{_('Status:')}}</th>
         </tr>
      </thead>
      <tbody>
         <tr>
            <td><strong>{{_('Status:')}}</strong></td>
            <td>
               %extra=''
               %if host.acknowledged:
               %extra += _(' and acknowledged')
               %end
               %if host.downtimed:
               %extra += _(' and in scheduled downtime')
               %end
               {{! host.get_html_state(extra=extra)}}
            </td>
         </tr>
         <tr>
            <td><strong>{{_('Since:')}}</strong></td>
            <td>
               {{! Helper.print_duration(host.last_state_changed, duration_only=True, x_elts=0)}}
            </td>
         </tr>
         <tr>
            <td><strong>{{_('Actions:')}}</strong></td>
            <td>
               %if current_user.is_power():
                  {{! Helper.get_html_commands_buttons(host, _('Actions'))}}
               %end
            </td>
         </tr>
      </tbody>
   </table>

   <table class="table table-condensed table-nowrap table-check-result">
      <colgroup>
         <col style="width: 40%" />
         <col style="width: 60%" />
      </colgroup>
      <thead>
         <tr>
            <th colspan="2">{{_('Last check:')}}</th>
         </tr>
      </thead>
      <tbody>
         <tr>
            <td><strong>{{_('Check command:')}}</strong></td>
            <td>
               %if host.check_command != 'command':
               {{! host.check_command.get_html_state_link(title=getattr(host.check_command, 'command_line', ''))}}
               %else:
               {{ host.check_command }}
               %end
            </td>
            <td>
            </td>
         </tr>

         %if host.last_check:
         <tr>
            <td><strong>{{_('When:')}}</strong></td>
            <td>
               {{Helper.print_duration(host.last_check, duration_only=False, x_elts=0)}}
            </td>
         </tr>
         %else:
         <tr>
            <td></td>
            <td class="text-danger"><strong>{{_('Not yet checked!')}}</strong></td>
         </tr>
         %end
         %if host.output:
         <tr>
            <td><strong>{{_('Output:')}}</strong></td>
            <td>
               {{! host.html_output}}
            </td>
         </tr>
         %end
         %if host.long_output:
         <tr>
            <td><strong>{{_('Long output:')}}</strong></td>
            <td>
               {{! host.html_long_output}}
            </td>
         </tr>
         %end
         %if host.perf_data:
         <tr>
            <td><strong>{{_('Performance data:')}}</strong></td>
            <td>
                {{! host.html_perf_data if host.perf_data else '(none)'}}
            </td>
         </tr>
         %end
         %if host.execution_time:
         <tr>
            <td><strong>{{_('Check duration (latency):')}}</strong></td>
            <td>
               {{_('%.2f seconds (%.2f)') % (host.execution_time, host.latency) }}
            </td>
         </tr>
         %end

         <tr>
            <td><strong>{{_('Last state changed:')}}</strong></td>
            <td>
                {{! Helper.print_duration(host.last_state_changed, duration_only=True, x_elts=0)}}
            </td>
         </tr>
         <tr>
            <td><strong>{{_('Current attempt:')}}</strong></td>
            <td>
               {{_('%s / %s %s state') % (host.current_attempt, host.max_attempts, host.state_type) }}
            </td>
         </tr>
         <tr>
            <td><strong>{{_('Next active check:')}}</strong></td>
            <td>
               {{! Helper.print_duration(host.next_check, duration_only=False, x_elts=0)}}
            </td>
         </tr>
         %if host.active_checks_enabled and current_user.is_power():
         <tr>
            <td></td>
            <td>
            {{! Helper.get_html_command_button(host, 'recheck', _('Re-check this host'), 'refresh', unique=True)}}
            </td>
         </tr>
         %end
      </tbody>
   </table>

   <table class="table table-condensed table-check">
      <colgroup>
         <col style="width: 40%" />
         <col style="width: 60%" />
      </colgroup>
      <thead>
         <tr>
            <th colspan="2">{{_('Checks configuration:')}}</th>
         </tr>
      </thead>
      <tbody>
         <tr>
            <td><strong>{{_('Check period:')}}</strong></td>
            <td>
               {{! host.check_period.get_html_state_link()}}
            </td>
         </tr>

         %if host.maintenance_period is not None:
         <tr>
            <td><strong>{{_('Maintenance period:')}}</strong></td>
            <td>
               {{! host.maintenance_period.get_html_state_link()}}
            </td>
         </tr>
         %end

         <tr>
            <td><strong>{{_('Process performance data:')}}</strong></td>
            <td>
               {{! Helper.get_on_off(host.process_perf_data)}}
            </td>
         </tr>

         <tr>
            <td><strong>{{_('Active checks:')}}</strong></td>
            <td>
               %if not current_user.is_power():
                  {{! Helper.get_on_off(host.active_checks_enabled, message=_('Enabled') if host.active_checks_enabled else _('Disabled'))}}
               %else:
               <div class="togglebutton">
                  <label>
                     <input type="checkbox"
                            data-action="command" data-type="host" data-name="{{host.name}}"
                            data-element="{{host.id}}" data-command="{{'disable_host_check' if host.active_checks_enabled else 'enable_host_check'}}"
                            {{ 'checked="checked"' if host.active_checks_enabled else ''}}>
                     <small>{{_('Enabled') if host.active_checks_enabled else _('Disabled') }}</small>
                  </label>
               </div>
               %end
            </td>
         </tr>
         %if (host.active_checks_enabled):
         <tr>
            <td><strong>{{_('Check interval:')}}</strong></td>
            <td>{{host.check_interval}} minutes</td>
         </tr>
         <tr>
            <td><strong>{{_('Retry interval:')}}</strong></td>
            <td>{{host.retry_interval}} minutes</td>
         </tr>
         <tr>
            <td><strong>{{_('Max check attempts:')}}</strong></td>
            <td>{{host.max_check_attempts}}</td>
         </tr>
         %end
         <tr>
            <td><strong>{{_('Passive checks:')}}</strong></td>
            <td>
               %if not current_user.is_power():
                  {{! Helper.get_on_off(host.passive_checks_enabled, message=_('Enabled') if host.passive_checks_enabled else _('Disabled'))}}
               %else:
               <div class="togglebutton">
                  <label>
                     <input type="checkbox"
                            data-action="command" data-type="host" data-name="{{host.name}}"
                            data-element="{{host.id}}" data-command="{{'disable_passive_host_checks' if host.passive_checks_enabled else 'enable_passive_host_checks'}}"
                            {{ 'checked="checked"' if host.passive_checks_enabled else ''}}>
                     <small>{{_('Enabled') if host.passive_checks_enabled else _('Disabled') }}</small>
                  </label>
               </div>
               %end
            </td>
         </tr>
         %if (host.passive_checks_enabled):
         <tr>
            <td><strong>{{_('Freshness check:')}}</strong></td>
            <td>
               %if not current_user.is_power():
                  {{! Helper.get_on_off(host.check_freshness, message=_('Enabled') if host.check_freshness else _('Disabled'))}}
               %else:
               <div class="togglebutton">
                  <label>
                     <input type="checkbox"
                            data-action="command" data-type="host" data-name="{{host.name}}"
                            data-element="{{host.id}}" data-command="{{'disable_host_freshness_checks' if host.check_freshness else 'enable_host_freshness_checks'}}"
                            {{ 'checked="checked"' if host.check_freshness else ''}}>
                     <small>{{_('Enabled') if host.check_freshness else _('Disabled') }}</small>
                  </label>
               </div>
               %end
            </td>
         </tr>
         %if (host.check_freshness):
         <tr>
            <td><strong>{{_('Freshness threshold:')}}</strong></td>
            <td>{{host.freshness_threshold}} seconds</td>
         </tr>
         <tr>
            <td><strong>{{_('Freshness state:')}}</strong></td>
            <td>{{host.get_freshness_state()}}</td>
         </tr>
         %end
         %end
      </tbody>
   </table>
</div>

<div class="col-sm-6">
   <table class="table table-condensed table-notifications">
      <colgroup>
         <col style="width: 40%" />
         <col style="width: 60%" />
      </colgroup>
      <thead>
         <tr>
            <th colspan="2">{{_('Notifications:')}}</th>
         </tr>
      </thead>
      <tbody>
         <tr>
            <td><strong>{{_('State:')}}</strong></td>
            <td>
               %if not current_user.is_power():
                  {{! Helper.get_on_off(host.notifications_enabled, message=_('Enabled') if host.notifications_enabled else _('Disabled'))}}
               %else:
               <div class="togglebutton">
                  <label>
                     <input type="checkbox" id="notifications_enabled" name="notifications_enabled"
                            data-action="command" data-type="host" data-name="{{host.name}}"
                            data-element="{{host.id}}" data-command="{{'disable_host_notifications' if host.notifications_enabled else 'enable_host_notifications'}}"
                            {{ 'checked="checked"' if host.notifications_enabled else ''}}>
                     <small>{{_('Enabled') if host.notifications_enabled else _('Disabled') }}</small>
                  </label>
               </div>
               %end
            </td>
         </tr>

         %if host.notifications_enabled and host.notification_period is not None:
            <tr>
               <td><strong>{{_('Notification period:')}}</strong></td>
               <td>
                  {{! host.notification_period.get_html_state_link()}}
               </td>
            </tr>
            %message = {}
            %message['d'] = {'title': _('Notifications enabled on Down state'), 'message': _('DOWN')}
            %message['x'] = {'title': _('Notifications enabled on Unreachable state'), 'message': _('UNREACHABLE')}
            %message['r'] = {'title': _('Notifications enabled on Recovery'), 'message': _('RECOVERY')}
            %message['f'] = {'title': _('Notifications enabled on Flapping'), 'message': _('FLAPPING')}
            %message['s'] = {'title': _('Notifications enabled on Downtime'), 'message': _('DOWNTIME')}
            %message['n'] = {'title': _('Notifications disabled'), 'message': _('NONE')}
            %first=True
            %for m in message:
               <tr>
                  %if first:
                     <td><strong>{{_('Options:')}}</strong></td>
                     %first=False
                  %else:
                     <td></td>
                  %end
                  <td>
                     {{! Helper.get_on_off(m in host.notification_options, message[m]['title'], '&nbsp;' + message[m]['message'])}}
                  </td>
               </tr>
            %end
            <tr class="bg-danger">
               <td><strong>{{_('Last notification:')}}</strong></td>
               <td class="text-danger">{{_('Information not available!')}}</td>
            </tr>
            <tr>
               <td><strong>{{_('Notification interval:')}}</strong></td>
               <td>{{host.notification_interval}} {{_('minutes')}}</td>
            </tr>
            <tr>
               <td><strong>{{_('Contacts:')}}</strong></td>
               <td>
                 %for user in host.users:
                 <a href="{{user.get_html_link()}}">{{ ! user.get_html_state_link() }}</a>,
                 %end
               </td>
            </tr>
            <tr>
               <td><strong>{{_('Contacts groups:')}}</strong></td>
               <td>
                 %for group in host.usergroups:
                 <a href="{{group.get_html_link()}}">{{ ! group.get_html_state_link() }}</a>,
                 %end
               </td>
            </tr>
         %end
      </tbody>
   </table>

   <table class="table table-condensed table-event-handler">
      <colgroup>
         <col style="width: 40%" />
         <col style="width: 60%" />
      </colgroup>
      <thead>
         <tr>
            <th colspan="2">{{_('Event handling:')}}</th>
         </tr>
      </thead>
      <tbody>
         <tr>
            <td><strong>{{_('State:')}}</strong></td>
            <td>
               %if not current_user.is_power():
                  {{! Helper.get_on_off(host.event_handler_enabled, message=_('Enabled') if host.event_handler_enabled else _('Disabled'))}}
               %else:
               <div class="togglebutton">
                  <label>
                     <input type="checkbox" id="event_handler_enabled" name="event_handler_enabled"
                            data-action="command" data-type="host" data-name="{{host.name}}"
                            data-element="{{host.id}}" data-command="{{'disable_host_event_handler' if host.event_handler_enabled else 'enable_host_event_handler'}}"
                            {{ 'checked="checked"' if host.event_handler_enabled else ''}}>
                     <small>{{_('Enabled') if host.event_handler_enabled else _('Disabled') }}</small>
                  </label>
               </div>
               %end
            </td>
         </tr>
         %if host.event_handler_enabled:
         %if host.event_handler:
         <tr>
            <td><strong>{{_('Event handler:')}}</strong></td>
            %if host.event_handler!='command':
            <td>
               <a href="/commands#{{host.event_handler.name}}">{{ host.event_handler.name }}</a>
            </td>
            %else:
            <td class="text-warning">{{_('No event handler is defined for this host. Alignak will use the globally defined event handler.')}}</td>
            %end
         </tr>
         %else:
         <tr>
            <td></td>
            <td><strong>{{_('No event handler defined.')}}</strong></td>
         </tr>
         %end
         %end
      </tbody>
   </table>

   <table class="table table-condensed table-flapping">
      <colgroup>
         <col style="width: 40%" />
         <col style="width: 60%" />
      </colgroup>
      <thead>
         <tr>
            <th colspan="2">{{_('Flapping detection:')}}</th>
         </tr>
      </thead>
      <tbody>
         <tr>
            <td><strong>{{_('State:')}}</strong></td>
            <td>
               %if not current_user.is_power():
                  {{! Helper.get_on_off(host.flap_detection_enabled, message=_('Enabled') if host.flap_detection_enabled else _('Disabled'))}}
               %else:
               <div class="togglebutton">
                  <label>
                     <input type="checkbox" id="flap_detection_enabled" name="flap_detection_enabled"
                            data-action="command" data-type="host" data-name="{{host.name}}"
                            data-element="{{host.id}}" data-command="{{'disable_host_flap_detection' if host.flap_detection_enabled else 'enable_host_flap_detection'}}"
                            {{ 'checked="checked"' if host.flap_detection_enabled else ''}}>
                     <small>{{_('Enabled') if host.flap_detection_enabled else _('Disabled') }}</small>
                  </label>
               </div>
               %end
            </td>
         </tr>
         %if host.flap_detection_enabled:
            %message = {}
            %message['o'] = {'title': _('Flapping enabled on Up state'), 'message': _('UP')}
            %message['d'] = {'title': _('Flapping enabled on Down state'), 'message': _('DOWN')}
            %message['x'] = {'title': _('Flapping enabled on Unreachable state'), 'message': _('UNREACHABLE')}
            %first=True
            %for m in message:
               <tr>
                  %if first:
                     <td><strong>{{_('Options:')}}</strong></td>
                     %first=False
                  %else:
                     <td></td>
                  %end
                  <td>
                     {{! Helper.get_on_off(m in host.flap_detection_options, message[m]['title'], '&nbsp;' + message[m]['message'])}}
                  </td>
               </tr>
            %end
            <tr>
               <td><strong>Low threshold:</strong></td>
               <td>{{host.low_flap_threshold}}</td>
            </tr>
            <tr>
               <td><strong>High threshold:</strong></td>
               <td>{{host.high_flap_threshold}}</td>
            </tr>
         %end
      </tbody>
   </table>

   %if not host.stalking_options:
   <table class="table table-condensed table-stalking">
      <colgroup>
         <col style="width: 40%" />
         <col style="width: 60%" />
      </colgroup>
      <thead>
         <tr>
            <th colspan="2">{{_('Stalking options:')}}</th>
         </tr>
      </thead>
      <tbody>
         %message = {}
         %message['o'] = {'title': _('Log enabled on Up state'), 'message': _('UP')}
         %message['d'] = {'title': _('Log enabled on Down state'), 'message': _('DOWN')}
         %message['x'] = {'title': _('Log enabled on Unreachable state'), 'message': _('UNREACHABLE')}
         %first=True
         %for m in message:
            <tr>
               %if first:
                  <td><strong>{{_('Options:')}}</strong></td>
                  %first=False
               %else:
                  <td></td>
               %end
               <td>
                  {{! Helper.get_on_off(m in host.stalking_options, message[m]['title'], '&nbsp;' + message[m]['message'])}}
               </td>
            </tr>
         %end
      </tbody>
   </table>
   %end
</div>
