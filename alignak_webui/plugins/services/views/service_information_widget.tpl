<!-- Service information widget -->
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
            <td><strong>{{_('Host:')}}</strong></td>
            <td>{{! host.html_state_link}}</td>
         </tr>
         <tr>
            <td><strong>{{_('Name:')}}</strong></td>
            <td>{{service.name}}</td>
         </tr>
         <tr>
            <td><strong>{{_('Alias:')}}</strong></td>
            <td>{{service.alias}} {{! ("<em>(%s)</em>" % service.display_name) if service.display_name else ''}}</td>
         </tr>
         <tr>
            <td><strong>{{_('Importance:')}}</strong></td>
            <td>{{! Helper.get_html_business_impact(service.business_impact, icon=True, text=False)}}</td>
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
               %if service.acknowledged:
               %extra += _(' and acknowledged')
               %end
               %if service.downtime:
               %extra += _(' and in scheduled downtime')
               %end
               {{! service.get_html_state(extra=extra)}}
            </td>
         </tr>
         <tr>
            <td><strong>{{_('Since:')}}</strong></td>
            <td>
               {{! Helper.print_duration(service.last_state_changed, duration_only=True, x_elts=0)}}
            </td>
         </tr>
         <tr>
            <td><strong>{{_('Actions:')}}</strong></td>
            <td>
               %if current_user.is_power():
                  {{! Helper.get_html_commands_buttons(service, title='Buttons')}}
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
               {{! service.check_command.get_html_state_link(title=host.check_command.command_line)}}
            </td>
            <td>
            </td>
         </tr>

         <tr>
            <td><strong>{{_('Last check:')}}</strong></td>
            <td>
               {{Helper.print_duration(service.last_check, duration_only=False, x_elts=0)}}
            </td>
         </tr>
         <tr>
            <td><strong>{{_('Output:')}}</strong></td>
            <td>
               {{! service.output}}
            </td>
         </tr>
         %if service.long_output:
         <tr>
            <td><strong>{{_('Long output:')}}</strong></td>
            <td>
               {{! service.long_output}}
            </td>
         </tr>
         %end
         <tr>
            <td><strong>{{_('Performance data:')}}</strong></td>
            <td class="popover-dismiss popover-large ellipsis"
                  data-html="true" data-toggle="popover" data-trigger="hover" data-placement="bottom"
                  data-title="{{_('%s performance data') % service.perf_data}}"
                  data-content=" {{service.perf_data if service.perf_data else '(none)'}}"
                  >
                {{service.perf_data if service.perf_data else '(none)'}}
            </td>
         </tr>
         <tr>
            <td><strong>{{_('Check duration (latency):')}}</strong></td>
            <td>
               {{_('%.2f seconds (%.2f)') % (service.execution_time, service.latency) }}
            </td>
         </tr>

         <tr>
            <td><strong>{{_('Last state changed:')}}</strong></td>
            <td class="popover-dismiss"
                  data-html="true" data-toggle="popover" data-trigger="hover" data-placement="bottom"
                  data-title="{{service.name}}{{_('}} last state changed date')}}"
                  data-content="{{! Helper.print_duration(service.last_state_changed, duration_only=True, x_elts=0)}}"
                  >
                {{! Helper.print_duration(service.last_state_changed, duration_only=True, x_elts=0)}}
            </td>
         </tr>
         <tr>
            <td><strong>{{_('Current attempt:')}}</strong></td>
            <td>
               {{_('%s / %s %s state') % (service.current_attempt, service.max_attempts, service.state_type) }}
            </td>
         </tr>
         <tr>
            <td><strong>{{_('Next active check:')}}</strong></td>
            <td class="popover-dismiss"
                  data-html="true" data-toggle="popover" data-trigger="hover" data-placement="bottom"
                  data-title="{{service.name}}{{_('}} next check date')}}"
                  data-content="{{! Helper.print_duration(service.next_check, duration_only=True, x_elts=0)}}"
                  >
               {{! Helper.print_duration(service.next_check, duration_only=True, x_elts=0)}}
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
                  data-title='{{service.check_period}}'
                  data-content='{{service.check_period}}'
                  >
               {{! service.check_period.get_html_state_link()}}
            </td>
         </tr>

         %if service.maintenance_period is not None:
         <tr>
            <td><strong>{{_('Maintenance period:')}}</strong></td>
            <td data-name="maintenance_period" class="popover-dismiss"
                  data-html="true" data-toggle="popover" data-trigger="hover" data-placement="left"
                  data-title='{{service.maintenance_period}}'
                  data-content='{{service.maintenance_period}}'
                  >
               {{! service.maintenance_period.get_html_state_link()}}
            </td>
         </tr>
         %end

         <tr>
            <td><strong>{{_('Process performance data:')}}</strong></td>
            <td>
               {{! Helper.get_on_off(service.process_perf_data)}}
            </td>
         </tr>

         <tr>
            <td><strong>{{_('Active checks:')}}</strong></td>
            <td>
               {{! Helper.get_on_off(service.active_checks_enabled)}}
            </td>
         </tr>
         %if (service.active_checks_enabled):
         <tr>
            <td><strong>{{_('Check interval:')}}</strong></td>
            <td>{{service.check_interval}} minutes</td>
         </tr>
         <tr>
            <td><strong>{{_('Retry interval:')}}</strong></td>
            <td>{{service.retry_interval}} minutes</td>
         </tr>
         <tr>
            <td><strong>{{_('Max check attempts:')}}</strong></td>
            <td>{{service.max_check_attempts}}</td>
         </tr>
         %end
         <tr>
            <td><strong>{{_('Passive checks:')}}</strong></td>
            <td>
               {{! Helper.get_on_off(service.passive_checks_enabled)}}
            </td>
         </tr>
         %if (service.passive_checks_enabled):
         <tr>
            <td><strong>{{_('Freshness check:')}}</strong></td>
            <td>
               {{! Helper.get_on_off(service.check_freshness)}}
            </td>
         </tr>
         %if (service.check_freshness):
         <tr>
            <td><strong>{{_('Freshness threshold:')}}</strong></td>
            <td>{{service.freshness_threshold}} seconds</td>
         </tr>
         <tr>
            <td><strong>{{_('Freshness state:')}}</strong></td>
            <td>{{service.get_freshness_state()}}</td>
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
                      data-element="{{service.name}}" data-value="{{service.notifications_enabled}}"
                      {{'checked' if service.notifications_enabled else ''}}>
            </td>
         </tr>

         %if service.notifications_enabled and service.notification_period is not None:
            <tr>
               <td><strong>{{_('Notification period:')}}</strong></td>
               <td data-name="notification_period" class="popover-dismiss"
                     data-html="true" data-toggle="popover" data-trigger="hover" data-placement="left"
                     data-title='{{service.notification_period}}'
                     data-content='{{service.notification_period}}'
                     >
                  {{! service.notification_period.get_html_state_link()}}
               </td>
            </tr>
            %message = {}
            %message['w'] = {'title': _('Notifications enabled on Warning state'), 'message': _('WARNING')}
            %message['c'] = {'title': _('Notifications enabled on Critical state'), 'message': _('CRITICAL')}
            %message['u'] = {'title': _('Notifications enabled on Unknown state'), 'message': _('UNKNOWN')}
            %message['r'] = {'title': _('Notifications enabled on Recovery'), 'message': _('RECOVERY')}
            %message['f'] = {'title': _('Notifications enabled on Flapping'), 'message': _('FLAPPING')}
            %message['s'] = {'title': _('Notifications enabled on Downtime'), 'message': _('DOWNTIME')}
            %message['x'] = {'title': _('Notifications enabled on Unreachable'), 'message': _('UNREACHABLE')}
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
                     {{! Helper.get_on_off(m in service.notification_options, message[m]['title'], '&nbsp;' + message[m]['message'])}}
                  </td>
               </tr>
            %end
            <tr class="bg-danger">
               <td><strong>{{_('Last notification:')}}</strong></td>
               <td class="text-danger">Information not available!</td>
            </tr>
            <tr>
               <td><strong>{{_('Notification interval:')}}</strong></td>
               <td>{{service.notification_interval}} {{_('minutes')}}</td>
            </tr>
            <tr>
               <td><strong>{{_('Contacts:')}}</strong></td>
               <td>
                 %for user in service.users:
                 <a href="{{user.get_html_link()}}">{{ ! user.get_html_state_link() }}</a>,
                 %end
               </td>
            </tr>
            <tr>
               <td><strong>{{_('Contacts groups:')}}</strong></td>
               <td>
                 %for group in service.usergroups:
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
               {{! Helper.get_on_off(service.event_handler_enabled)}}
            </td>
         </tr>
         %if service.event_handler_enabled and service.event_handler:
         <tr>
            <td><strong>{{_('Event handler:')}}</strong></td>
            %if service.event_handler!='command':
            <td>
               <a href="/commands#{{service.event_handler.name}}">{{ service.event_handler.name }}</a>
            </td>
            %else:
            <td class="text-warning">{{_('No event handler is defined for this service. Alignak will use the globally defined event handler.')}}</td>
            %end
         </tr>
         %end
         %if service.event_handler_enabled and not service.event_handler:
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
                      data-element="{{service.name}}" data-value="{{service.flap_detection_enabled}}"
                      {{'checked' if service.flap_detection_enabled else ''}}>
            </td>
         </tr>
         %if service.flap_detection_enabled:
            %message = {}
            %message['o'] = {'title': _('Flapping enabled on Ok state'), 'message': _('OK')}
            %message['w'] = {'title': _('Flapping enabled on Down state'), 'message': _('WARNING')}
            %message['c'] = {'title': _('Flapping enabled on Unreachable state'), 'message': _('CRITICAL')}
            %message['u'] = {'title': _('Flapping enabled on Unreachable state'), 'message': _('UNKNOWN')}
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
                     {{! Helper.get_on_off(m in service.flap_detection_options, message[m]['title'], '&nbsp;' + message[m]['message'])}}
                  </td>
               </tr>
            %end
            <tr>
               <td><strong>Low threshold:</strong></td>
               <td>{{service.low_flap_threshold}}</td>
            </tr>
            <tr>
               <td><strong>High threshold:</strong></td>
               <td>{{service.high_flap_threshold}}</td>
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
            <td>{{', '.join(service.stalking_options)}}</td>
         </tr>
      </tbody>
   </table>
</div>
