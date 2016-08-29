%setdefault('debug', False)

%setdefault('type', 'Both')

%from bottle import request
%search_string = request.query.get('search', '')

%rebase("layout", title=title, js=[], css=[], pagination=pagination, page="/livestates")

%from alignak_webui.utils.helper import Helper
%from alignak_webui.objects.item_command import Command

%if not elts:
   <center>
      <h3>{{_('No elements matching the filter...')}}</h3>
   </center>
%else:
   <table class="table table-condensed">
      <thead><tr>
         <th style="width: 40px"></th>
         <th>{{_('Element')}}</th>
         <th>{{_('Business impact')}}</th>
         %if current_user.is_power():
         <th>{{_('Commands')}}</th>
         %end
         <th>{{_('Last check')}}</th>
         <th>{{_('State')}}</th>
         <th>{{_('State type')}}</th>
         <th>{{_('Acknowledged')}}</th>
         <th>{{_('In scheduled downtime')}}</th>
         <th>{{_('Output')}}</th>
         <th>{{_('Long output')}}</th>
      </tr></thead>
      <tbody>
         %for livestate in elts:
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

            <td>
               <small>{{! livestate.get_date(livestate.last_check)}}</small>
            </td>

            <td>
               <small>{{! livestate.status}}</small>
            </td>

            <td>
               <small>{{! livestate.state_type}}}}</small>
            </td>

            <td>
               <small>{{! Helper.get_on_off(livestate.acknowledged)}}</small>
            </td>

            <td>
               <small>{{! Helper.get_on_off(livestate.downtime)}}</small>
            </td>

            <td>
               <small>{{! livestate.output}}</small>
            </td>

            <td>
               <small>{{! livestate.long_output}}</small>
            </td>
         </tr>
       %end
      </tbody>
   </table>
%end
