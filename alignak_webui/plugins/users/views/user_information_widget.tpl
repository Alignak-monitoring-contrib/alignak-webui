<!-- User information widget -->
%# embedded is True if the widget is got from an external application
%setdefault('embedded', False)
%from bottle import request
%setdefault('links', request.params.get('links', ''))
%setdefault('identifier', 'widget')
%setdefault('credentials', None)

%from alignak_webui.utils.helper import Helper
%from alignak_webui.utils.perfdata import PerfDatas

<div class="row">
   <div class="col-sm-6">
      <table class="table table-condensed table-rights">
         <colgroup>
            <col style="width: 40%" />
            <col style="width: 60%" />
         </colgroup>
         <thead>
            <tr>
               <th colspan="2">{{_('Rights:')}}</th>
            </tr>
         </thead>
         <tbody>
            <tr>
               <td><strong>{{_('Administrator')}}</strong></td>
               <td>{{! webui.helper.get_on_off(status=user.is_administrator())}}</td>
            </tr>
            <tr>
               <td><strong>{{_('Commands')}}</strong></td>
               <td>{{! webui.helper.get_on_off(user.is_power())}}</td>
            </tr>
            <tr>
               <td><strong>{{_('Skill level')}}</strong></td>
               %skill,title = user.get_skill_level()
               <td title="{{title}}">{{skill}}</td>
            </tr>
            <tr>
               <td><strong>{{_('Password')}}</strong></td>
               <td>
                  <a class="btn btn-default btn-xs btn-raised" href="#"
                     data-action="change-user-password"
                     data-element_type="user" data-name="{{user.name}}" data-element="{{user.id}}"
                     data-message="{{_('User preference deleted')}}"
                     data-toggle="tooltip" data-placement="top"
                     title="{{_('Change my password')}}">
                        <span class="fa fa-user-secret"></span>
                   </a>
               </td>
            </tr>
         </tbody>
      </table>
   </div>
   <div class="col-sm-6">
      <table class="table table-condensed table-notes">
         <colgroup>
            <col style="width: 40%" />
            <col style="width: 60%" />
         </colgroup>
         <thead>
            <tr>
               <th colspan="2">{{_('Notes:')}}</th>
            </tr>
         </thead>
         <tbody>
            <tr>
               <td><strong>{{_('Alias')}}</strong></td>
               <td>{{ user.alias }}</td>
            </tr>
            <tr>
               <td><strong>{{_('Notes')}}</strong></td>
               <td>{{ user.notes }}</td>
            </tr>
            %if current_user.is_super_administrator() or current_user.is_administrator():
            <tr>
               <td><strong>{{_('Login')}}</strong></td>
               <td>{{ user.name }}</td>
            </tr>
            <tr>
               <td><strong>{{_('Token')}}</strong></td>
               <td>{{ user.token }}</td>
            </tr>
            %end
         </tbody>
      </table>
   </div>
</div>

<div class="row">
   <div class="col-sm-6">
   <table class="table table-condensed table-hosts-notifications">
      <colgroup>
         <col style="width: 40%" />
         <col style="width: 60%" />
      </colgroup>
      <thead>
         <tr>
            <th colspan="2">{{_('Hosts notifications configuration:')}}</th>
         </tr>
      </thead>
      <tbody>
         <tr>
            <td><strong>{{_('State:')}}</strong></td>
            <td>
               %if not current_user.is_power():
                  {{! Helper.get_on_off(user.host_notifications_enabled, message=_('Enabled') if user.host_notifications_enabled else _('Disabled'))}}
               %else:
               <div class="togglebutton">
                  <label>
                     <input type="checkbox" id="hosts_notifications_enabled" name="notifications_enabled"
                            data-action="command" data-type="user" data-name="{{user.name}}"
                            data-element="{{user.id}}" data-command="{{'disable_contact_host_notifications' if user.host_notifications_enabled else 'enable_contact_host_notifications'}}"
                            {{ 'checked="checked"' if user.host_notifications_enabled else ''}}>
                     <small>{{_('Enabled') if user.host_notifications_enabled else _('Disabled') }}</small>
                  </label>
               </div>
               %end
            </td>
         </tr>

         <tr>
            <td><strong>{{_('Notification period:')}}</strong></td>
            <td data-name="host_notification_period" class="popover-dismiss"
                  data-html="true" data-toggle="popover" data-trigger="hover" data-placement="left"
                  data-title='{{user.host_notification_period}}'
                  data-content='{{user.host_notification_period}}'
                  >
               {{! user.host_notification_period.get_html_state_link()}}
            </td>
         </tr>

         <tr>
            <td><strong>{{_('Notifications enabled:')}}</strong></td>
            <td>
               {{! Helper.get_on_off(user.host_notifications_enabled)}}
            </td>
         </tr>

         <tr>
            <td><strong>{{_('Notifications commands:')}}</strong></td>
            %if not user.host_notification_commands:
            <td>
               {{_('No notification commands defined.')}}
            </td>
            %else:
            %first = True
            %for command in user.host_notification_commands:
               %if not first:
               <tr>
               <td></td>
               %else:
               %first = False
               %end
               <td>
                  {{! command.get_html_state_link()}}
               </td>
               </tr>
            %end
            %end
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
                  {{! Helper.get_on_off(m in user.host_notification_options, message[m]['title'], '&nbsp;' + message[m]['message'])}}
               </td>
            </tr>
         %end
      </tbody>
   </table>
   </div>

   <div class="col-sm-6">
   <table class="table table-condensed table-services-notifications">
      <colgroup>
         <col style="width: 40%" />
         <col style="width: 60%" />
      </colgroup>
      <thead>
         <tr>
            <th colspan="2">{{_('Services notifications configuration:')}}</th>
         </tr>
      </thead>
      <tbody>
         <tr>
            <td><strong>{{_('State:')}}</strong></td>
            <td>
               %if not current_user.is_power():
                  {{! Helper.get_on_off(user.service_notifications_enabled, message=_('Enabled') if user.service_notifications_enabled else _('Disabled'))}}
               %else:
               <div class="togglebutton">
                  <label>
                     <input type="checkbox" id="services_notifications_enabled" name="notifications_enabled"
                            data-action="command" data-type="user" data-name="{{user.name}}"
                            data-element="{{user.id}}" data-command="{{'disable_contact_svc_notifications' if user.service_notifications_enabled else 'enable_contact_svc_notifications'}}"
                            {{ 'checked="checked"' if user.service_notifications_enabled else ''}}>
                     <small>{{_('Enabled') if user.service_notifications_enabled else _('Disabled') }}</small>
                  </label>
               </div>
               %end
            </td>
         </tr>

         <tr>
            <td><strong>{{_('Notification period:')}}</strong></td>
            <td data-name="service_notification_period" class="popover-dismiss"
                  data-html="true" data-toggle="popover" data-trigger="hover" data-placement="left"
                  data-title='{{user.service_notification_period}}'
                  data-content='{{user.service_notification_period}}'
                  >
               {{! user.service_notification_period.get_html_state_link()}}
            </td>
         </tr>

         <tr>
            <td><strong>{{_('Notifications enabled:')}}</strong></td>
            <td>
               {{! Helper.get_on_off(user.service_notifications_enabled)}}
            </td>
         </tr>

         <tr>
            <td><strong>{{_('Notifications commands:')}}</strong></td>
            %if not user.service_notification_commands:
            <td>
               {{_('No notification commands defined.')}}
            </td>
            %else:
            %first = True
            %for command in user.service_notification_commands:
               %if not first:
               <tr>
               <td></td>
               %else:
               %first = False
               %end
               <td>
                  {{! command.get_html_state_link()}}
               </td>
               </tr>
            %end
            %end
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
                  {{! Helper.get_on_off(m in user.service_notification_options, message[m]['title'], '&nbsp;' + message[m]['message'])}}
               </td>
            </tr>
         %end
      </tbody>
   </table>
   </div>
</div>
