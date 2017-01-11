<!-- User information widget -->
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
            <td>{{user.name}}</td>
         </tr>
         <tr>
            <td><strong>{{_('Alias:')}}</strong></td>
            <td>{{user.alias}}</td>
         </tr>
         <tr>
            <td></td>
            <td><img src="{{user.picture}}" class="img-circle user-logo" alt="{{_('Photo: %s') % user.name}}" title="{{_('Photo: %s') % user.name}}"></td>
         </tr>
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
            <th colspan="2">{{_('Rights:')}}</th>
         </tr>
      </thead>
      <tbody style="font-size:x-small;">
         <tr>
            <td><strong>{{_('Administrator')}}</strong></td>
            <td>{{! webui.helper.get_on_off(status=user.is_administrator())}}</td>
         </tr>
         <tr>
            <td><strong>{{_('Commands')}}</strong></td>
            <td>{{! webui.helper.get_on_off(user.is_power())}}</td>
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
            <th colspan="2">{{_('Hosts notifications configuration:')}}</th>
         </tr>
      </thead>
      <tbody style="font-size:x-small;">
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

   <table class="table table-condensed">
      <colgroup>
         <col style="width: 40%" />
         <col style="width: 60%" />
      </colgroup>
      <thead>
         <tr>
            <th colspan="2">{{_('Services notifications configuration:')}}</th>
         </tr>
      </thead>
      <tbody style="font-size:x-small;">
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
