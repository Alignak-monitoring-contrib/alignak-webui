<!-- Hosts table widget -->
%# embedded is True if the widget is got from an external application
%setdefault('embedded', False)
%from bottle import request
%setdefault('links', request.params.get('links', ''))
%setdefault('identifier', 'widget')
%setdefault('credentials', None)

%from alignak_webui.utils.helper import Helper
%from alignak_webui.objects.item_command import Command

%if not services:
   <center>
      <h3>{{_('No services matching the filter...')}}</h3>
   </center>
%else:
   <table class="table table-condensed">
      <thead><tr>
         <th style="width: 40px"></th>
         <th>{{_('Service')}}</th>
         <th>{{_('Business impact')}}</th>
         <th>{{_('Check command')}}</th>
      </tr></thead>
      <tbody>
         %for service in services:
         %lv_service = datamgr.get_livestate_service({'where': {'service': service.id}})
         <tr id="{{service.id}}">
            <td title="{{service.alias}}">
            %if lv_service:
               %label = "%s - %s (%s)" % (lv_service.status, Helper.print_duration(lv_service.last_check, duration_only=True, x_elts=0), lv_service.output)
               {{! lv_service.get_html_state(text=None, title=label)}}
            %else:
               {{! service.get_html_state(text=None, title=_('No livestate for this element'))}}
            %end
            </td>

            <td>
               <small>{{! service.get_html_link(links) if links else service.alias}}</small>
            </td>

            <td>
               <small>{{! Helper.get_html_business_impact(service.business_impact)}}</small>
            </td>

            <td>
               <small>{{! service.check_command.get_html_link(links) if links else service.check_command.alias}}</small>
            </td>
         </tr>
       %end
      </tbody>
   </table>
%end
