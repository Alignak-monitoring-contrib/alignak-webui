%setdefault('debug', False)

%from bottle import request
%search_string = request.query.get('search', '')

%rebase("layout", title=title, js=[], css=[], pagination=pagination, page="/kiosks", elts_per_page=elts_per_page)

<!-- kiosks filtering and display -->
<div id="kiosks">
   %if debug:
   <div class="panel-group">
      <div class="panel panel-default">
         <div class="panel-heading">
            <h4 class="panel-title">
               <a data-toggle="collapse" href="#collapse1"><i class="fa fa-bug"></i> Kiosks as dictionaries</a>
            </h4>
         </div>
         <div id="collapse1" class="panel-collapse collapse">
            <ul class="list-group">
               %for kiosk in kiosks:
                  <li class="list-group-item"><small>Kiosk: {{kiosk}} - {{kiosk.__dict__}}</small></li>
               %end
            </ul>
            <div class="panel-footer">{{len(kiosks)}} elements</div>
         </div>
      </div>
   </div>
   %end

   <div class="panel panel-default">
      <div class="panel-body">
         %if not kiosks:
         <center>
            %if search_string:
               <h3>{{_('What a bummer! We couldn\'t find anything.')}}</h3>
               {{_('Use the filters or the bookmarks to find what you are looking for, or try a new search query.')}}
            %else:
               <h3>{{_('No elements found.')}}</h3>
            %end
         </center>
         %else:

         <i class="pull-right small">{{_('%d elements out of %d') % (count, total)}}</i>

         <table class="table table-condensed">
            <thead><tr>
               <th width="40px"></th>
               <th>{{_('Serial number')}}</th>
               <th>{{_('Model')}}</th>
               <th>{{_('Type')}}</th>
               <th>{{_('Group')}}</th>
               <th>{{_('Location')}}</th>
            </tr></thead>

            <tbody>
               %for kiosk in kiosks:
               <tr>
                  <td>
                     {{! kiosk.get_html_state()}}
                  </td>

                  <td class="align-left">
                     <small>{{kiosk.get_name()}}</small>
                  </td>

                  <td class="align-left">
                     <small>{{kiosk.model}}</small>
                  </td>
                  <td class="align-left">
                     <small>{{kiosk.type}}</small>
                  </td>

                  <td class="align-left">
                     <small>{{kiosk.entity_name}}</small>
                  </td>
                  <td class="align-left">
                     <small>{{kiosk.short_location}}</small>
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
