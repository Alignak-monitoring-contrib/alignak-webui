%setdefault('debug', False)
%# When layout is False, this template is embedded
%setdefault('layout', True)

%from bottle import request
%search_string = request.query.get('search', '')

%if layout:
%rebase("layout", title=title, js=[], css=[], pagination=pagination, page="/logcheckresults")
%end

%from alignak_webui.utils.helper import Helper
%from alignak_webui.objects.item_command import Command
%from alignak_webui.objects.item_host import Host

<!-- logcheckresults filtering and display -->
<div id="logcheckresults">
   %if debug:
   <div class="panel-group">
      <div class="panel panel-default">
         <div class="panel-heading">
            <h4 class="panel-title">
               <a data-toggle="collapse" href="#collapse_logcheckresults"><i class="fa fa-bug"></i> logcheckresults as dictionaries</a>
            </h4>
         </div>
         <div id="collapse_logcheckresults" class="panel-collapse collapse">
            <ul class="list-group">
               %for logcheckresult in logcheckresults:
                  <li class="list-group-item"><small>logcheckresult: {{logcheckresult}} - {{logcheckresult.__dict__}}</small></li>
               %end
            </ul>
            <div class="panel-footer">{{len(logcheckresults)}} elements</div>
         </div>
      </div>
   </div>
   %end

   <div class="panel panel-default">
      <div class="panel-body">
      %if not logcheckresults:
         %include("_nothing_found.tpl", search_string=search_string)
      %else:
         %# First element for global data
         %object_type, start, count, total, dummy = pagination[0]
         <i class="pull-right small">{{_('%d elements out of %d') % (count, total)}}</i>

         <table class="table table-condensed" style="width: 100%">
            <thead><tr>
               <th class="col-md-1"></th>
               <th class="col-md-2">{{! _('<span class="fa fa-clock-o"></span>')}}</th>
               <th>{{_('Host')}}</th>
               <th>{{_('Service')}}</th>
               <th>{{_('State')}}</th>
               <th>{{_('State type')}}</th>
               <th>{{_('Last state')}}</th>
               <th>{{_('Acknowledged')}}</th>
               <th>{{_('Latency')}}</th>
               <th>{{_('Execution time')}}</th>
               <th>{{_('Output')}}</th>
               <th>{{_('Long output')}}</th>
               <th>{{_('Performance data')}}</th>
            </tr></thead>

            <tbody>
               %for lcr in logcheckresults:
               %css = 'success' if lcr.state == 'OK' else ''
               <tr id="#{{lcr.id}}" class="{{css}}">
                  <td title="{{lcr.alias}}">
                  {{! lcr.get_html_state(text=None, title=_('No livestate for this element'))}}
                  </td>

                  <td title="{{! lcr.get_check_date()}}">
                     <small>
                     {{! lcr.get_check_date(duration=True)}}
                     </small>
                  </td>

                  <td>
                     <small>{{! lcr.host.get_html_link()}}</small>
                  </td>

                  <td>
                     <small>{{! lcr.service.get_html_link() if lcr.service and lcr.service!='service' else ''}}</small>
                  </td>

                  <td>
                     <small>{{! lcr.state}}</small>
                  </td>

                  <td>
                     <small>{{! lcr.state_type}}</small>
                  </td>

                  <td>
                     <small>{{! lcr.last_state}}</small>
                  </td>

                  <td>
                     <small>{{! Helper.get_on_off(lcr.acknowledged)}}</small>
                  </td>

                  <td>
                     <small>{{! lcr.latency}}</small>
                  </td>

                  <td>
                     <small>{{! lcr.execution_time}}</small>
                  </td>

                  <td>
                     <small>{{! lcr.output}}</small>
                  </td>

                  <td>
                     <small>{{! lcr.long_output}}</small>
                  </td>

                  <td>
                     <small>{{! lcr.perf_data}}</small>
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
