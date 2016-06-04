%setdefault('debug', False)
%# When layout is False, this template is embedded
%setdefault('layout', True)

%from bottle import request
%search_string = request.query.get('search', '')

%if layout:
%rebase("layout", title=title, js=[], css=[], pagination=pagination, page="/services")
%end

%from alignak_webui.utils.helper import Helper
%from alignak_webui.objects.item import Command, Host

<!-- services filtering and display -->
<div id="services">
   %if debug:
   <div class="panel-group">
      <div class="panel panel-default">
         <div class="panel-heading">
            <h4 class="panel-title">
               <a data-toggle="collapse" href="#collapse_services"><i class="fa fa-bug"></i> Services as dictionaries</a>
            </h4>
         </div>
         <div id="collapse_services" class="panel-collapse collapse">
            <ul class="list-group">
               %for service in services:
                  <li class="list-group-item"><small>Service: {{service}} - {{service.__dict__}}</small></li>
               %end
            </ul>
            <div class="panel-footer">{{len(services)}} elements</div>
         </div>
      </div>
   </div>
   %end

   <div class="panel panel-default">
      <div class="panel-body">
      %if not services:
         %include("_nothing_found.tpl", search_string=search_string)
      %else:
         %# First element for global data
         %object_type, start, count, total, dummy = pagination[0]
         <i class="pull-right small">{{_('%d elements out of %d') % (count, total)}}</i>

         <table class="table table-condensed">
            <thead><tr>
               <th width="40px"></th>
               <th>{{_('Service description')}}</th>
               <th>{{_('Alias')}}</th>
               <th>{{_('Display name')}}</th>
               <th>{{_('Host name')}}</th>
               <th>{{_('Check command')}}</th>
               <th>{{_('Active checks enabled')}}</th>
               <th>{{_('Passive checks enabled')}}</th>
               <th>{{_('Business impact')}}</th>
            </tr></thead>

            <tbody>
               %for service in services:
                  <tr data-toggle="collapse" data-target="#details-{{service.get_id()}}" class="accordion-toggle">
                     <td>
                        {{! service.get_html_state()}}
                     </td>

                     <td>
                        <small>{{service.name}}</small>
                     </td>

                     <td>
                        <small>{{service.alias}}</small>
                     </td>

                     <td>
                        <small>{{service.display_name}}</small>
                     </td>

                     <td>
                        %host = service.host_name
                        <small>{{! '<a href="host/%s">%s</a>' % (host.get_id(), host.get_html_state(label=host.get_name()))}}</small>
                     </td>

                     <td>
                        %command = service.check_command
                        <small>{{! '<a href="command/%s">%s</a>' % (command.get_id(), command.get_html_state(label=command.get_name()))}}</small>
                     </td>

                     <td>
                        <small>{{! Helper.get_on_off(service.active_checks_enabled)}}</small>
                     </td>

                     <td>
                        <small>{{! Helper.get_on_off(service.passive_checks_enabled)}}</small>
                     </td>

                     <td>
                        <small>{{service.business_impact}}</small>
                     </td>
                  </tr>
             %end
            </tbody>
         </table>
      %end
      </div>
   </div>
 </div>

%if layout:
 <script>
   $(document).ready(function(){
      set_current_page("{{ webui.get_url(request.route.name) }}");
   });
 </script>
%end
