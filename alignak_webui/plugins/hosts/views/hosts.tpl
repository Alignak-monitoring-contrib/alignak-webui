%setdefault('debug', False)

%from bottle import request
%search_string = request.query.get('search', '')

%rebase("layout", title=title, js=[], css=[], pagination=pagination, page="/hosts")

%from alignak_webui.utils.helper import Helper
%from alignak_webui.objects.item_command import Command

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
               %for host in elts:
                  <li class="list-group-item"><small>Host: {{host}} - {{host.__dict__}}</small></li>
               %end
            </ul>
            <div class="panel-footer">{{len(elts)}} elts</div>
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
               <th>{{_('Host name')}}</th>
               <th>{{_('Address')}}</th>
               <th>{{_('Check command')}}</th>
               <th>{{_('Active checks enabled')}}</th>
               <th>{{_('Passive checks enabled')}}</th>
               <th>{{_('Business impact')}}</th>
            </tr></thead>

            <tbody>
               %for host in elts:
               %lv_host = datamgr.get_livestates({'where': {'host': host.id}})
               %lv_host = lv_host[0]
               <tr id="#{{host.id}}">
                  <td title="{{host.alias}}">
                  %if lv_host:
                     %title = "%s - %s (%s)" % (lv_host.status, Helper.print_duration(lv_host.last_check, duration_only=True, x_elts=0), lv_host.output)
                     {{! lv_host.get_html_state(text=None, title=title)}}
                  %else:
                     {{! host.get_html_state(text=None, title=_('No livestate for this element'))}}
                  %end
                  </td>

                  <td>
                     <small>{{!host.get_html_link()}}</small>
                  </td>

                  <td>
                     <small>{{host.address}}</small>
                  </td>

                  <td>
                     <small>{{! host.check_command.get_html_state_link()}}</small>
                  </td>

                  <td>
                     <small>{{! Helper.get_on_off(host.active_checks_enabled)}}</small>
                  </td>

                  <td>
                     <small>{{! Helper.get_on_off(host.passive_checks_enabled)}}</small>
                  </td>

                  <td>
                     <small>{{! Helper.get_html_business_impact(host.business_impact)}}</small>
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
