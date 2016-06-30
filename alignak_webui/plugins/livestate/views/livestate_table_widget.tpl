<!-- livestates widget -->

%rebase("_widget", js=[], css=[])

%from alignak_webui.utils.helper import Helper
%from alignak_webui.objects.item import Command

%if not livestates:
   <center>
      <h3>{{_('No livestates matching the filter...')}}</h3>
   </center>
%else:
   <table class="table table-condensed">
      <thead><tr>
         <th style="width: 40px"></th>
         <th>{{_('livestate name')}}</th>
         <th>{{_('Business impact')}}</th>
         <th>{{_('Check command')}}</th>
      </tr></thead>
      <tbody>
         %livestates = sorted(livestates, key=lambda k: k['business_impact'], reverse=True)
         %for livestate in livestates:
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
               <small>{{!livestate.get_html_link()}}</small>
            </td>

            <td>
               <small>{{! Helper.get_html_business_impact(livestate.business_impact)}}</small>
            </td>

            <td>
               {{! Helper.get_html_commands_buttons(livestate, title='')}}
            </td>
         </tr>
       %end
      </tbody>
   </table>
%end
