%setdefault('debug', False)

%from bottle import request
%search_string = request.query.get('search', '')

%rebase("layout", title=title, js=[], css=[], pagination=pagination, page="/hosts", elts_per_page=elts_per_page)

%from alignak_webui.utils.helper import Helper

<!-- hosts filtering and display -->
<div id="hosts">
   %if debug:
   <div class="panel-group">
      <div class="panel panel-default">
         <div class="panel-heading">
            <h4 class="panel-title">
               <a data-toggle="collapse" href="#collapse1"><i class="fa fa-bug"></i> Hosts as dictionaries</a>
            </h4>
         </div>
         <div id="collapse1" class="panel-collapse collapse">
            <ul class="list-group">
               %for host in hosts:
                  <li class="list-group-item"><small>Host: {{host}} - {{host.__dict__}}</small></li>
               %end
            </ul>
            <div class="panel-footer">{{len(hosts)}} elements</div>
         </div>
      </div>
   </div>
   %end

   <div class="panel panel-default">
      <div class="panel-body">
      %if not hosts:
         %include("_nothing_found.tpl", search_string=search_string)
      %else:

         <i class="pull-right small">{{_('%d elements out of %d') % (count, total)}}</i>

         <table class="table table-condensed">
            <thead><tr>
               <th width="40px"></th>
               <th>{{_('Host name')}}</th>
               <th>{{_('Alias')}}</th>
               <th>{{_('Display name')}}</th>
               <th>{{_('Address')}}</th>
               <th>{{_('Check command')}}</th>
               <th>{{_('Active checks enabled')}}</th>
               <th>{{_('Passive checks enabled')}}</th>
               <th>{{_('Business impact')}}</th>
            </tr></thead>

            <tbody>
               %for host in hosts:
                  <tr data-toggle="collapse" data-target="#details-{{host.get_id()}}" class="accordion-toggle">
                     <td>
                        {{! host.get_html_state()}}
                     </td>

                     <td>
                        <small>{{host.name}}</small>
                     </td>

                     <td>
                        <small>{{host.alias}}</small>
                     </td>

                     <td>
                        <small>{{host.display_name}}</small>
                     </td>

                     <td>
                        <small>{{host.address}}</small>
                     </td>

                     <td>
                        <small>{{host.check_command}}</small>
                     </td>

                     <td>
                        <small>{{! Helper.get_on_off(host.active_checks_enabled)}}</small>
                     </td>

                     <td>
                        <small>{{! Helper.get_on_off(host.passive_checks_enabled)}}</small>
                     </td>

                     <td>
                        <small>{{host.business_impact}}</small>
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
