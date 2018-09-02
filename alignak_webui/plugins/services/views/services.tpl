%setdefault('debug', False)
%# When layout is False, this template is embedded
%setdefault('layout', True)
%# When in_host_view is True, list the services in the host view (do not include the host column)
%setdefault('in_host_view', False)

%from bottle import request
%search_string = request.query.get('search', '')

%if layout:
%rebase("layout", title=title, js=[], css=[], pagination=pagination, page="/services")
%end

%from alignak_webui.utils.helper import Helper
%from alignak_webui.objects.item_command import Command
%from alignak_webui.objects.item_host import Host

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
               %for service in elts:
                  <li class="list-group-item"><small>Service: {{service}} - {{service.__dict__}}</small></li>
               %end
            </ul>
            <div class="panel-footer">{{len(elts)}} elements</div>
         </div>
      </div>
   </div>
   %end

   %if not elts:
      %include("_nothing_found.tpl", search_string=search_string)
   %else:
   <div class="panel panel-default">
      <div class="panel-body">
         %# First element for global data
         %object_type, start, count, total, dummy = pagination[0]
         <i class="pull-right small">{{_('%d elements out of %d') % (count, total)}}</i>

         <table class="table table-condensed">
            <thead><tr>
               <th style="width: 40px"></th>
               %if not in_host_view:
               <th>{{_('Host')}}</th>
               %end
               <th>{{_('Service')}}</th>
               <th>{{_('Business impact')}}</th>
               <th></th>
               <th>{{_('Check command')}}</th>
               <th>{{_('Last check output')}}</th>
            </tr></thead>

            <tbody>
               %for service in elts:
               <tr id="#service-{{service.id}}">
                  <td title="{{service.alias}}">
                     %extra=''
                     %if service.acknowledged:
                     %extra += _(' and acknowledged')
                     %end
                     %if service.downtimed:
                     %extra += _(' and in scheduled downtime')
                     %end
                     %title = "%s - %s (%s)" % (service.state, Helper.print_duration(service.last_check, duration_only=True, x_elts=0), service.output)
                     {{! service.get_html_state(text=None, title=title, extra=extra, use_status=service.overall_status)}}
                  </td>

                  %if not in_host_view:
                  <td>
                     %if service.host != 'host':
                     <small>{{! service.host.get_html_link()}}</small>
                     %else:
                     <small>{{_('Unknown host')}} - {{service.host}}</small>
                     %end
                  </td>
                  %end

                  <td>
                     <small>{{! service.get_html_link()}}</small>
                  </td>

                  <td>
                     <small>{{! Helper.get_html_business_impact(service.business_impact)}}</small>
                  </td>

                  <td>
                     %if current_user.is_power():
                        {{! Helper.get_html_commands_buttons(service, 'Actions')}}
                     %end
                  </td>

                  <td>
                     %if service.check_command != 'command':
                     <small>{{! service.check_command.get_html_link()}}</small>
                     %else:
                     <small>{{_('Unknown command')}}</small>
                     %end
                  </td>

                  <td>
                     <small>{{! service.output}}</small>
                  </td>
               </tr>
             %end
            </tbody>
         </table>
      </div>
   </div>
   %end
 </div>

%if layout:
 <script>
   $(document).ready(function(){
      set_current_page("{{ webui.get_url(request.route.name) }}");
   });
 </script>
%end
