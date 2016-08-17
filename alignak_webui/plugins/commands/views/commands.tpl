%setdefault('debug', False)

%from bottle import request
%search_string = request.query.get('search', '')

%rebase("layout", title=title, js=[], css=[], pagination=pagination, page="/commands")

%from alignak_webui.utils.helper import Helper

<!-- commands filtering and display -->
<div id="commands">
   %if debug:
   <div class="panel-group">
      <div class="panel panel-default">
         <div class="panel-heading">
            <h4 class="panel-title">
               <a data-toggle="collapse" href="#collapse1"><i class="fa fa-bug"></i> Commands as dictionaries</a>
            </h4>
         </div>
         <div id="collapse1" class="panel-collapse collapse">
            <ul class="list-group">
               %for command in elts:
                  <li class="list-group-item"><small>Command: {{command}} - {{command.__dict__}}</small></li>
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
               <th>{{_('Command name')}}</th>
               <th>{{_('Command line')}}</th>
               <th>{{_('Timeout')}}</th>
               <th>{{_('Environment macros')}}</th>
               <th>{{_('Poller tag')}}</th>
               <th>{{_('Reactionner tag')}}</th>
            </tr></thead>

            <tbody>
               %for command in elts:
               <tr id="#{{command.id}}">
                  <td>
                     {{! command.get_html_state()}}
                  </td>

                  <td>
                     <small>{{command.name}}</small>
                  </td>

                  <td>
                     <small>{{command.command_line}}</small>
                  </td>

                  <td>
                     <small>{{command.timeout}}</small>
                  </td>

                  <td>
                     <small>{{ ! Helper.get_on_off(command.enable_environment_macros) }}</small>
                  </td>

                  <td>
                     <small>{{command.poller_tag}}</small>
                  </td>

                  <td>
                     <small>{{command.reactionner_tag}}</small>
                  </td>
               </tr>
             %end
            </tbody>
         </table>
      </div>
   </div>
   %end
 </div>

 <script>
   $(document).ready(function(){
      set_current_page("{{ webui.get_url(request.route.name) }}");
   });
 </script>
