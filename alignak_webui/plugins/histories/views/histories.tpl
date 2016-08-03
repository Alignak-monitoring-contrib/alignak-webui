%setdefault('debug', False)
%# When layout is False, this template is embedded
%setdefault('layout', True)

%from bottle import request
%search_string = request.query.get('search', '')

%if layout:
%rebase("layout", title=title, js=[], css=[], pagination=pagination, page="/histories")
%end

%from alignak_webui.utils.helper import Helper
%from alignak_webui.objects.item_command import Command
%from alignak_webui.objects.item_host import Host

<!-- histories filtering and display -->
<div id="histories">
   %if debug:
   <div class="panel-group">
      <div class="panel panel-default">
         <div class="panel-heading">
            <h4 class="panel-title">
               <a data-toggle="collapse" href="#collapse_histories"><i class="fa fa-bug"></i> histories as dictionaries</a>
            </h4>
         </div>
         <div id="collapse_histories" class="panel-collapse collapse">
            <ul class="list-group">
               %for history in histories:
                  <li class="list-group-item"><small>history: {{history}} - {{history.__dict__}}</small></li>
               %end
            </ul>
            <div class="panel-footer">{{len(histories)}} elements</div>
         </div>
      </div>
   </div>
   %end

   <div class="panel panel-default">
      <div class="panel-body">
      %if not histories:
         %include("_nothing_found.tpl", search_string=search_string)
      %else:
         %# First element for global data
         %object_type, start, count, total, dummy = pagination[0]
         <i class="pull-right small">{{_('%d elements out of %d') % (count, total)}}</i>

         <table class="table table-condensed" style="width: 100%">
            <thead><tr>
               <th class="col-md-1"></th>
               <th class="col-md-1">{{! _('<span class="fa fa-clock-o"></span>')}}</th>
               <th>{{_('Host')}}</th>
               <th>{{_('Service')}}</th>
               <th>{{_('User')}}</th>
               <th>{{_('Message')}}</th>
               <th></th>
            </tr></thead>

            <tbody>
               %for lcr in histories:
               %if filter and lcr.type not in filter:
               %continue
               %end
               %css = 'success' if lcr.status == 'OK' else ''
               <tr id="#{{lcr.id}}" class="{{css}}">
                  <td title="{{lcr.alias}}">
                  {{! lcr.get_html_state(text=None)}}
                  </td>

                  <td title="{{! lcr.get_check_date()}}">
                     <small>
                     {{! lcr.get_check_date(duration=True)}}
                     </small>
                  </td>

                  <td>
                     <small>{{! lcr.host.get_html_link()}}</small>
                  </td>

                  <td>
                     <small>{{! lcr.service.get_html_link() if lcr.service and lcr.service!='service' else ''}}</small>
                  </td>

                  <td>
                     <small>{{! lcr.user.get_html_link() if lcr.user and lcr.user!='user' else ''}}</small>
                  </td>

                  <td>
                     %message = lcr.message
                     %if lcr.type == 'check.result':
                     %message = "%s - %s" % (lcr.logcheckresult.get_html_state(text=None), lcr.logcheckresult.output)
                     %end
                     <small>{{! message}}</small>
                  </td>
               </tr>
             %end
            </tbody>
         </table>
      %end
      </div>
   </div>
 </div>

%if layout:
 <script>
   $(document).ready(function(){
      set_current_page("{{ webui.get_url(request.route.name) }}");
   });
 </script>
%end
