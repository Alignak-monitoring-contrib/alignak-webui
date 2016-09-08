%setdefault('debug', False)

%from bottle import request
%search_string = request.query.get('search', '')

%rebase("layout", title=title, js=[], css=[], pagination=pagination, page="/hostgroups")

%from alignak_webui.utils.helper import Helper
%from alignak_webui.objects.item_command import Command

<!-- hosts filtering and display -->
<div id="hostgroups">
   %if debug:
   <div class="panel-group">
      <div class="panel panel-default">
         <div class="panel-heading">
            <h4 class="panel-title">
               <a data-toggle="collapse" href="#collapse1"><i class="fa fa-bug"></i> Hostgroups as dictionaries</a>
            </h4>
         </div>
         <div id="collapse1" class="panel-collapse collapse">
            <ul class="list-group">
               %for hostgroup in elts:
                  <li class="list-group-item"><small>Hostgroup: {{hostgroup}} - {{hostgroup.__dict__}}</small></li>
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
               <th>{{_('Level')}}</th>
               <th>{{_('Parent')}}</th>
            </tr></thead>

            <tbody>
               %real_state_to_status = ['ok', 'acknowledged', 'in_downtime', 'warning', 'critical']
               %for hostgroup in elts:
                  %hostgroup.status = 'unknown'
                  %real_state = 0
                  %for host in hostgroup.members:
                     %if isinstance(host, basestring):
                        %continue
                     %end
                     %real_state = max(real_state, datamgr.get_host_real_state(host.id))
                     %hostgroup.status = real_state_to_status[real_state]
                  %end
               %end

               %for hostgroup in elts:
                  <tr id="#{{hostgroup.id}}">
                     <td title="{{hostgroup.alias}}">
                        {{! hostgroup.get_html_state(text=None)}}
                     </td>

                     <td>
                        <small>{{!hostgroup.get_html_link()}}</small>
                     </td>

                     <td>
                        <small>{{hostgroup.alias}}</small>
                     </td>

                     <td>
                        <small>{{hostgroup.level}}</small>
                     </td>

                     <td>
                        %if hostgroup._parent and hostgroup._parent != 'hostgroup':
                        <small>{{hostgroup._parent.alias}}</small>
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
