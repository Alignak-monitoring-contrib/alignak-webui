%setdefault('debug', False)

%from bottle import request
%search_string = request.query.get('search', '')

%rebase("layout", title=title, js=[], css=[], pagination=pagination, page="/servicegroups")

%from alignak_webui.utils.helper import Helper
%from alignak_webui.objects.item_command import Command

<!-- hosts filtering and display -->
<div id="servicegroups">
   %if debug:
   <div class="panel-group">
      <div class="panel panel-default">
         <div class="panel-heading">
            <h4 class="panel-title">
               <a data-toggle="collapse" href="#collapse1"><i class="fa fa-bug"></i> Servicegroups as dictionaries</a>
            </h4>
         </div>
         <div id="collapse1" class="panel-collapse collapse">
            <ul class="list-group">
               %for servicegroup in elts:
                  <li class="list-group-item"><small>Servicegroup: {{servicegroup}} - {{servicegroup.__dict__}}</small></li>
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
               <th>{{_('Group')}}</th>
               <th>{{_('Alias')}}</th>
               <th>{{_('Notes')}}</th>
               <th>{{_('Parent')}}</th>
            </tr></thead>

            <tbody>
               %for servicegroup in elts:
               <tr id="#{{servicegroup.id}}">
                  <td title="{{servicegroup.alias}}">
                     {{! servicegroup.get_html_state(text=None, title=servicegroup.alias)}}
                  </td>

                  <td>
                     <small>{{!servicegroup.get_html_link()}}</small>
                  </td>

                  <td>
                     <small>{{servicegroup.alias}}</small>
                  </td>

                  <td>
                     <small>{{servicegroup.notes}}</small>
                  </td>

                  <td>
                     %if servicegroup._parent and servicegroup._parent != 'servicegroup':
                     {{servicegroup._parent.alias}}
                     %end
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
