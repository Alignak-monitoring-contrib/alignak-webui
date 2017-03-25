%setdefault('debug', False)

%from bottle import request
%search_string = request.query.get('search', '')

%rebase("layout", title=title, js=[], css=[], pagination=pagination, page="/hosts")

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
               %for host in elts:
               <div class="panel panel-default">
                  <div class="panel-heading">
                     <h4 class="panel-title">
                        <a data-toggle="collapse" href="#collapse_{{host.id}}"><i class="fa fa-bug"></i> {{host.name}}</a>
                     </h4>
                  </div>
                  <div id="collapse_{{host.id}}" class="panel-collapse collapse">
                     <dl class="dl-horizontal" style="height: 200px; overflow-y: scroll;">
                        %for k,v in sorted(host.__dict__.items()):
                           <dt>{{k}}</dt>
                           <dd>{{v}}</dd>
                        %end
                     </dl>
                  </div>
               </div>
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
               <th>{{_('Host name')}}</th>
               <th>{{_('Address')}}</th>
               <th>{{_('Check command')}}</th>
               <th>{{_('Active checks enabled')}}</th>
               <th>{{_('Passive checks enabled')}}</th>
               <th>{{_('Business impact')}}</th>
            </tr></thead>

            <tbody>
            %for host in elts:
               <tr id="#{{host.id}}">
                  <td title="{{host.alias}}">
                     %title = "%s - %s (%s)" % (host.state, Helper.print_duration(host.last_check, duration_only=True, x_elts=0), host.output)
                     {{! host.get_html_state(text=None, title=title)}}

                     {{! host.get_html_state(text=None, use_status=host.overall_status)}}
                  </td>

                  <td title="{{host.alias}}">
                     <small>{{!host.get_html_link()}}</small>
                  </td>

                  <td>
                     <small>{{host.address}}</small>
                  </td>

                  <td>
                     {{! host.check_command.get_html_state_link() if host.check_command != 'command' else ''}}
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
