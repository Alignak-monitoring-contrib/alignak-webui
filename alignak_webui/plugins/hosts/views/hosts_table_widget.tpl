<!-- Hosts table widget -->
%# embedded is True if the widget is got from an external application
%setdefault('embedded', False)
%from bottle import request
%setdefault('links', request.params.get('links', ''))
%setdefault('identifier', 'widget')
%setdefault('credentials', None)

%from alignak_webui.utils.helper import Helper
%from alignak_webui.objects.item_command import Command

%if not hosts:
   <center>
      <h3>{{_('No hosts matching the filter...')}}</h3>
   </center>
%else:
   <table class="table table-condensed">
      <thead><tr>
         <th style="width: 40px"></th>
         <th>{{_('Host name')}}</th>
         <th>{{_('Business impact')}}</th>
         <th>{{_('Check command')}}</th>
      </tr></thead>
      <tbody>
         %for host in hosts:
         <tr id="{{host.id}}">
            <td title="{{host.alias}}">
            %label = "%s - %s (%s)" % (host.status, Helper.print_duration(host.last_check, duration_only=True, x_elts=0), host.output)
            {{! host.get_html_state(text=None, title=label)}}
            </td>

            %if not embedded:
            <td>
               <small>{{! host.get_html_link(links)}}</small>
            </td>
            %else:
            <td>
               <small>{{! host.get_html_link(links) if links else host.alias}}</small>
            </td>
            %end

            <td>
               <small>{{! Helper.get_html_business_impact(host.business_impact)}}</small>
            </td>

            <td>
               <small>{{! host.check_command.get_html_link(links) if links else host.check_command.alias}}</small>
            </td>
         </tr>
       %end
      </tbody>
   </table>
%end
