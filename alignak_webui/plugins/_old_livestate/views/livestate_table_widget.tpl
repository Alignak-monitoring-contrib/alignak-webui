<!-- Livestate table widget -->
%# embedded is True if the widget is got from an external application
%setdefault('embedded', False)
%from bottle import request
%setdefault('links', request.params.get('links', 'yes'))
%setdefault('identifier', 'widget')
%setdefault('credentials', None)

%from alignak_webui.utils.helper import Helper
%from alignak_webui.objects.item_command import Command

%if not elements:
   <center>
      <h3>{{_('No elements matching the filter...')}}</h3>
   </center>
%else:
   <table class="table table-condensed">
      <thead><tr>
         <th style="width: 40px"></th>
         <th>{{_('Livestate element')}}</th>
         <th>{{_('Business impact')}}</th>
         %if current_user.is_power():
         <th>{{_('Commands')}}</th>
         %end
      </tr></thead>
      <tbody>
         %for livestate in elements:
         <tr id="#{{livestate.id}}">
            <td title="{{livestate.alias}}">
               %label = "%s - %s (%s)" % (livestate.status, Helper.print_duration(livestate.last_check, duration_only=True, x_elts=0), livestate.output)
               %extra=''
               %if livestate.acknowledged:
               %extra += _(' and acknowledged')
               %end
               %if livestate.downtime:
               %extra += _(' and in scheduled downtime')
               %end
               {{! livestate.get_html_state(text=None, title=label, extra=extra)}}
            </td>

            <td>
               <small>{{!livestate.get_html_link(prefix=request.params.get('links'))}}</small>
            </td>

            <td>
               <small>{{! Helper.get_html_business_impact(livestate.business_impact)}}</small>
            </td>

            %if current_user.is_power():
            <td>
               {{! Helper.get_html_commands_buttons(livestate, title='')}}
            </td>
            %end
         </tr>
       %end
      </tbody>
   </table>
%end
