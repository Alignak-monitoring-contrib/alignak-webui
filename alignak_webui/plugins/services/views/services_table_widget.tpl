<!-- Hosts table widget -->
%# embedded is True if the widget is got from an external application
%setdefault('embedded', False)
%from bottle import request
%setdefault('links', request.params.get('links', ''))
%setdefault('identifier', 'widget')
%setdefault('credentials', None)

%from alignak_webui.utils.helper import Helper
%from alignak_webui.objects.item_command import Command

%if not elements:
   <center>
      <h4>{{_('No services matching the filter...')}}</h4>
   </center>
%else:
   <table class="table table-condensed">
      <thead><tr>
         <th style="width: 40px"></th>
         <th>{{_('Host')}}</th>
         <th>{{_('Service')}}</th>
         <th>{{_('Business impact')}}</th>
         <th>{{_('Check command')}}</th>
      </tr></thead>
      <tbody>
         %for service in elements:
         <tr id="{{service.id}}">
            <td title="{{service.alias}}">
            %label = "%s - %s (%s)" % (service.status, Helper.print_duration(service.last_check, duration_only=True, x_elts=0), service.output)
            {{! service.get_html_state(text=None, title=label)}}
            </td>

            %if not embedded:
            <td>
               <small>{{! service.host.get_html_link(links)}}</small>
            </td>

            <td>
               <small>{{! service.get_html_link(links)}}</small>
            </td>
            %else:
            <td>
               <small>{{! service.host.alias}}</small>
            </td>

            <td>
               <small>{{! service.alias}}</small>
            </td>
            %end

            <td>
               <small>{{! Helper.get_html_business_impact(service.business_impact)}}</small>
            </td>

            <td>
               %if service.check_command and service.check_command != 'command':
               <small>{{! service.check_command.get_html_link(links) if links else service.check_command.alias}}</small>
               %else:
               {{_('Command not fetched from the backend')}}
               %end
            </td>
         </tr>
       %end
      </tbody>
   </table>
%end
