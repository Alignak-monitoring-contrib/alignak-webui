<!-- Hosts information widget -->
%# embedded is True if the widget is got from an external application
%setdefault('embedded', False)
%from bottle import request
%setdefault('links', request.params.get('links', ''))
%setdefault('identifier', 'widget')
%setdefault('credentials', None)

%from alignak_webui.utils.helper import Helper
%from alignak_webui.utils.perfdata import PerfDatas

<div class="col-md-6">
   <table class="table table-condensed">
      <colgroup>
         <col style="width: 40%" />
         <col style="width: 60%" />
      </colgroup>
      <thead>
         <tr>
            <th colspan="2">{{_('Overview:')}}</th>
         </tr>
      </thead>
      <tbody style="font-size:x-small;">
         <tr>
            <td><strong>{{_('Name:')}}</strong></td>
            <td>{{host.name}} ({{host.address}})</td>
         </tr>
         <tr>
            <td><strong>{{_('Alias:')}}</strong></td>
            <td>{{host.alias}} {{! ("<em>(%s)</em>" % host.display_name) if host.display_name else ''}}</td>
         </tr>
         <tr>
            <td><strong>{{_('Importance:')}}</strong></td>
            <td>{{! Helper.get_html_business_impact(host.business_impact, icon=True, text=False)}}</td>
         </tr>
      </tbody>
   </table>

   <table class="table table-condensed">
      <colgroup>
         <col style="width: 40%" />
         <col style="width: 60%" />
      </colgroup>
      <thead>
         <tr>
            <th colspan="2">{{_('Status:')}}</th>
         </tr>
      </thead>
      <tbody style="font-size:x-small;">
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

   <table class="table table-condensed table-nowrap">
      <colgroup>
         <col style="width: 40%" />
         <col style="width: 60%" />
      </colgroup>
      <thead>
         <tr>
            <th colspan="2">{{_('Last check:')}}</th>
         </tr>
      </thead>
      <tbody style="font-size:x-small;">
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

         <tr>
            <td><strong>{{_('Last check:')}}</strong></td>
            <td>
               {{Helper.print_duration(host.last_check, duration_only=False, x_elts=0)}}
            </td>
         </tr>
         <tr>
            <td><strong>{{_('Output:')}}</strong></td>
            <td>
               {{! host.output}}
            </td>
         </tr>
         %if host.long_output:
         <tr>
            <td><strong>{{_('Long output:')}}</strong></td>
            <td>
               {{! host.long_output}}
            </td>
         </tr>
         %end
         <tr>
            <td><strong>{{_('Performance data:')}}</strong></td>
            <td>
                {{host.perf_data if host.perf_data else '(none)'}}
            </td>
         </tr>
         <tr>
            <td><strong>{{_('Check duration (latency):')}}</strong></td>
            <td>
               {{_('%.2f seconds (%.2f)') % (host.execution_time, host.latency) }}
            </td>
         </tr>

         <tr>
            <td><strong>{{_('Last state changed:')}}</strong></td>
            <td class="popover-dismiss"
                  data-html="true" data-toggle="popover" data-trigger="hover" data-placement="bottom"
                  data-title="{{host.name}}{{_('}} last state changed date')}}"
                  data-content="{{! Helper.print_duration(host.last_state_changed, duration_only=True, x_elts=0)}}"
                  >
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
            <td class="popover-dismiss"
                  data-html="true" data-toggle="popover" data-trigger="hover" data-placement="bottom"
                  data-title="{{host.name}}{{_('}} next check date')}}"
                  data-content="{{! Helper.print_duration(host.next_check, duration_only=True, x_elts=0)}}"
                  >
               {{! Helper.print_duration(host.next_check, duration_only=True, x_elts=0)}}
            </td>
         </tr>
      </tbody>
   </table>

   <table class="table table-condensed">
      <colgroup>
         <col style="width: 40%" />
         <col style="width: 60%" />
      </colgroup>
      <thead>
         <tr>
            <th colspan="2">{{_('Checks configuration:')}}</th>
         </tr>
      </thead>
      <tbody style="font-size:x-small;">
         <tr>
            <td><strong>{{_('Check period:')}}</strong></td>
            <td data-name="check_period" class="popover-dismiss"
                  data-html="true" data-toggle="popover" data-trigger="hover" data-placement="left"
                  data-title='{{host.check_period}}'
                  data-content='{{host.check_period}}'
                  >
               {{! host.check_period.get_html_state_link()}}
            </td>
         </tr>

         %if host.maintenance_period is not None:
         <tr>
            <td><strong>{{_('Maintenance period:')}}</strong></td>
            <td data-name="maintenance_period" class="popover-dismiss"
                  data-html="true" data-toggle="popover" data-trigger="hover" data-placement="left"
                  data-title='{{host.maintenance_period}}'
                  data-content='{{host.maintenance_period}}'
                  >
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
               {{! Helper.get_on_off(host.active_checks_enabled)}}
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
               {{! Helper.get_on_off(host.passive_checks_enabled)}}
            </td>
         </tr>
         %if (host.passive_checks_enabled):
         <tr>
            <td><strong>{{_('Freshness check:')}}</strong></td>
            <td>
               {{! Helper.get_on_off(host.check_freshness)}}
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

<div class="col-md-6">
   <table class="table table-condensed">
      <colgroup>
         <col style="width: 40%" />
         <col style="width: 60%" />
      </colgroup>
      <thead>
         <tr>
            <th colspan="2">{{_('Notifications:')}}</th>
         </tr>
      </thead>
      <tbody style="font-size:x-small;">
         <tr>
            <td><strong>{{_('Notifications:')}}</strong></td>
            <td>
               <input type="checkbox" class="switch"
                      data-size="mini" data-on-color="success" data-off-color="danger"
                      data-type="action" action="toggle-notifications"
                      data-element="{{host.name}}" data-value="{{host.notifications_enabled}}"
                      {{'checked' if host.notifications_enabled else ''}}>
            </td>
         </tr>

         %if host.notifications_enabled and host.notification_period is not None:
            <tr>
               <td><strong>{{_('Notification period:')}}</strong></td>
               <td data-name="notification_period" class="popover-dismiss"
                     data-html="true" data-toggle="popover" data-trigger="hover" data-placement="left"
                     data-title='{{host.notification_period}}'
                     data-content='{{host.notification_period}}'
                     >
                  {{! host.notification_period.get_html_state_link()}}
               </td>
            </tr>
            %message = {}
            %message['d'] = {'title': _('Notifications enabled on Down state'), 'message': _('DOWN')}
            %message['u'] = {'title': _('Notifications enabled on Unreachable state'), 'message': _('UNREACHABLE')}
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
               <td class="text-danger">Information not available!</td>
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

   <table class="table table-condensed">
      <colgroup>
         <col style="width: 40%" />
         <col style="width: 60%" />
      </colgroup>
      <thead>
         <tr>
            <th colspan="2">{{_('Event handler:')}}</th>
         </tr>
      </thead>
      <tbody style="font-size:x-small;">
         <tr>
            <td><strong>{{_('Event handler enabled:')}}</strong></td>
            <td>
               {{! Helper.get_on_off(host.event_handler_enabled)}}
            </td>
         </tr>
         %if host.event_handler_enabled and host.event_handler:
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
         %end
         %if host.event_handler_enabled and not host.event_handler:
         <tr>
            <td></td>
            <td><strong>{{_('No event handler defined.')}}</strong></td>
         </tr>
         %end
      </tbody>
   </table>

   <table class="table table-condensed">
      <colgroup>
         <col style="width: 40%" />
         <col style="width: 60%" />
      </colgroup>
      <thead>
         <tr>
            <th colspan="2">{{_('Flapping detection:')}}</th>
         </tr>
      </thead>
      <tbody style="font-size:x-small;">
         <tr>
            <td><strong>{{_('Flapping detection:')}}</strong></td>
            <td>
               <input type="checkbox" class="switch"
                      data-size="mini" data-on-color="success" data-off-color="danger"
                      data-type="action" action="toggle-flap-detection"
                      data-element="{{host.name}}" data-value="{{host.flap_detection_enabled}}"
                      {{'checked' if host.flap_detection_enabled else ''}}>
            </td>
         </tr>
         %if host.flap_detection_enabled:
            %message = {}
            %message['o'] = {'title': _('Flapping enabled on Up state'), 'message': _('UP')}
            %message['d'] = {'title': _('Flapping enabled on Down state'), 'message': _('DOWN')}
            %message['u'] = {'title': _('Flapping enabled on Unreachable state'), 'message': _('UNREACHABLE')}
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

   <table class="table table-condensed">
      <colgroup>
         <col style="width: 40%" />
         <col style="width: 60%" />
      </colgroup>
      <thead>
         <tr>
            <th colspan="2">{{_('Stalking options:')}}</th>
         </tr>
      </thead>
      <tbody style="font-size:x-small;">
         <tr>
            <td><strong>{{_('Stalking options:')}}</strong></td>
            <td>{{', '.join(host.stalking_options)}}</td>
         </tr>
      </tbody>
   </table>
</div>
