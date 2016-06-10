%setdefault('debug', False)

%from bottle import request
%search_string = request.query.get('search', '')

%rebase("layout", title=title, js=[], css=[], pagination=pagination, page="/timeperiods", elts_per_page=elts_per_page)

%from alignak_webui.utils.helper import Helper

<!-- timeperiods filtering and display -->
<div id="timeperiods">
   %if debug:
   <div class="panel-group">
      <div class="panel panel-default">
         <div class="panel-heading">
            <h4 class="panel-title">
               <a data-toggle="collapse" href="#collapse1"><i class="fa fa-bug"></i> Timeperiods as dictionaries</a>
            </h4>
         </div>
         <div id="collapse1" class="panel-collapse collapse">
            <ul class="list-group">
               %for timeperiod in timeperiods:
                  <li class="list-group-item"><small>Timeperiod: {{timeperiod}} - {{timeperiod.__dict__}}</small></li>
               %end
            </ul>
            <div class="panel-footer">{{len(timeperiods)}} elements</div>
         </div>
      </div>
   </div>
   %end

   <div class="panel panel-default">
      <div class="panel-body">
      %if not timeperiods:
         %include("_nothing_found.tpl", search_string=search_string)
      %else:

         %# First element for global data
         %object_type, start, count, total, dummy = pagination[0]
         <i class="pull-right small">{{_('%d elements out of %d') % (count, total)}}</i>

         <table class="table table-condensed">
            <thead><tr>
               <th width="40px"></th>
               <th>{{_('Timeperiod name')}}</th>
               <th>{{_('Alias')}}</th>
               <th>{{_('Date ranges and exclusions')}}</th>
            </tr></thead>

            <tbody>
               %for timeperiod in timeperiods:
               <tr id="#{{timeperiod.id}}">
                  <td>
                     {{! timeperiod.get_html_state()}}
                  </td>

                  <td>
                     <small>{{timeperiod.name}}</small>
                  </td>

                  <td>
                     <small>{{timeperiod.alias}}</small>
                  </td>

                  <td>
                     {{! Helper.get_html_timeperiod(timeperiod, title=_('Date ranges and exclusions'))}}
                  </td>
               </tr>
             %end
            </tbody>
         </table>
      %end
      </div>
   </div>
 </div>

 <script>
   $(document).ready(function(){
      set_current_page("{{ webui.get_url(request.route.name) }}");
   });
 </script>
