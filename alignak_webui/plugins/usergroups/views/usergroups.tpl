%setdefault('debug', False)

%from bottle import request
%search_string = request.query.get('search', '')

%rebase("layout", title=title, js=[], css=[], pagination=pagination, page="/usergroups")

%from alignak_webui.utils.helper import Helper
%from alignak_webui.objects.item_command import Command

<!-- hosts filtering and display -->
<div id="usergroups">
   %if debug:
   <div class="panel-group">
      <div class="panel panel-default">
         <div class="panel-heading">
            <h4 class="panel-title">
               <a data-toggle="collapse" href="#collapse1"><i class="fa fa-bug"></i> Usergroups as dictionaries</a>
            </h4>
         </div>
         <div id="collapse1" class="panel-collapse collapse">
            <ul class="list-group">
               %for usergroup in elts:
                  <li class="list-group-item"><small>Usergroup: {{usergroup}} - {{usergroup.__dict__}}</small></li>
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
               %for usergroup in elts:
               <tr id="#{{usergroup.id}}">
                  <td title="{{usergroup.alias}}">
                     {{! usergroup.get_html_state(text=None, size="fa-2x", title=usergroup.alias)}}
                  </td>

                  <td>
                     <small>{{!usergroup.get_html_link()}}</small>
                  </td>

                  <td>
                     <small>{{usergroup.alias}}</small>
                  </td>

                  <td>
                     <small>{{usergroup.notes}}</small>
                  </td>

                  <td>
                     %if usergroup._parent and usergroup._parent != 'usergroup':
                     {{usergroup._parent.alias}}
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
