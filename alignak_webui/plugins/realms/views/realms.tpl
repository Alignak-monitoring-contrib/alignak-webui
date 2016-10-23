%setdefault('debug', False)

%from bottle import request
%search_string = request.query.get('search', '')

%rebase("layout", title=title, js=[], css=[], pagination=pagination, page="/realms")

%from alignak_webui.utils.helper import Helper
%from alignak_webui.objects.item_command import Command

<!-- hosts filtering and display -->
<div id="realms">
   %if debug:
   <div class="panel-group">
      <div class="panel panel-default">
         <div class="panel-heading">
            <h4 class="panel-title">
               <a data-toggle="collapse" href="#collapse1"><i class="fa fa-bug"></i> Realms as dictionaries</a>
            </h4>
         </div>
         <div id="collapse1" class="panel-collapse collapse">
            <ul class="list-group">
               %for realm in elts:
                  <li class="list-group-item"><small>Realm: {{realm}} - {{realm.__dict__}}</small></li>
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
               <th>{{_('Name')}}</th>
               <th>{{_('Alias')}}</th>
               <th>{{_('Default')}}</th>
               <th>{{_('Level')}}</th>
            </tr></thead>

            <tbody>
               %for realm in elts:
               <tr id="#{{realm.id}}">
                  <td title="{{realm.alias}}">
                     %(realm_state, realm_status) = datamgr.get_realm_overall_state(realm)
                     {{! realm.get_html_state(text=None, size="fa-2x", use_status=realm_status)}}
                  </td>

                  <td>
                     <small>{{!realm.get_html_link()}}</small>
                  </td>

                  <td>
                     <small>{{realm.alias}}</small>
                  </td>

                  <td>
                     <small>{{ ! Helper.get_on_off(realm.default) }}</small>
                  </td>

                  <td>
                     <small>{{realm.level}}</small>
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
