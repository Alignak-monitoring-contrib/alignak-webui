<!-- Hosts widget -->

%rebase("_widget", js=[], css=[])

%from alignak_webui.utils.helper import Helper
%from alignak_webui.objects.item import Command

%if not hosts:
   <center>
      <h3>{{_('No hosts matching the filter...')}}</h3>
   </center>
%else:
   <table class="table table-condensed">
      <thead><tr>
         <th width="40px"></th>
         <th>{{_('Host name')}}</th>
         <th>{{_('Business impact')}}</th>
         <th>{{_('Check command')}}</th>
      </tr></thead>
      <tbody>
         %for host in hosts:
         %lv_host = datamgr.get_livestate_host({'where': {'host_name': host.id}})
         <tr id="#{{host.id}}">
            <td title="{{host.alias}}">
            %if lv_host:
               %label = "%s - %s (%s)" % (lv_host.status, Helper.print_duration(lv_host.last_check, duration_only=True, x_elts=0), lv_host.output)
               {{! lv_host.get_html_state(text=None, title=label)}}
            %else:
               {{! host.get_html_state(text=None, title=_('No livestate for this element'))}}
            %end
            </td>

            <td>
               <small>{{!host.html_link}}</small>
            </td>

            <td>
               <small>{{! Helper.get_html_business_impact(host.business_impact)}}</small>
            </td>

            <td>
               <small>{{! host.check_command.html_link}}</small>
            </td>
         </tr>
       %end
      </tbody>
   </table>
%end
