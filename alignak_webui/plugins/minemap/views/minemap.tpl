%setdefault('debug', False)

%from bottle import request
%search_string = request.query.get('search', '')

%# No default refresh for this page
%rebase("layout", title=title, js=['minemap/htdocs/js/jquery.floatThead.min.js'], css=['minemap/htdocs/css/minemap.css'], pagination=pagination, page="/minemap", refresh=False)

%from alignak_webui.utils.helper import Helper

<div id="minemap" class="card" style="padding:10px; margin-top: 10px">
   %if not minemap:
      %include("_nothing_found.tpl", search_string=search_string)
   %else:

      <table class="table table-striped table-header-rotated table-fixed-header">
         <thead>
            <tr>
               <th>&nbsp;</th>
               %if debug:
               <th><i class="fa fa-bug"></i></th>
               %end
               %for service in columns:
                  <th class="rotate-45">
                     <div><span>
                        <a href="{{ webui.get_url('Services table') }}?search=name:{{service}}">{{service}}</a>
                     </span></div>
                  </th>
               %end
            </tr>
         </thead>
         <tbody>
            %for minemap_row in minemap:
               %host = minemap_row['host_check']
               <tr>
                  %title = "%s - %s - %s (%s)" % (host.name, host.status, Helper.print_duration(host.last_check, duration_only=True, x_elts=0), host.output)
                  <td title="{{title}}">
                     <a href="{{! host.endpoint}}">
                        {{ ! host.get_html_state(text=host.alias, title=title)}}
                     </a>
                  </td>
                  %if debug:
                     <td class="text-center">
                        <button class="btn btn-default btn-xs btn-block" type="button" data-toggle="collapse" data-target="#html_rows_{{host.id}}" aria-expanded="false" aria-controls="html_rows_{{host.id}}">{{host.name}}</button>

                        <div class="collapse" id="html_rows_{{host.id}}"><div class="well">
                        <ul class="list-group">
                        %for check in minemap_row:
                           <li class="list-group-item">
                              {{check}}
                           </li>
                        %end
                        </ul>
                        </div></div>
                     </td>
                  %end
                  %for column in columns:
                     %if column in minemap_row:
                        %service = minemap_row[column]
                        %title = "%s - %s - %s (%s)" % (service.name, service.status, Helper.print_duration(service.last_check, duration_only=True, x_elts=0), service.output)
                        <td title="{{title}}">
                           <a href="{{! service.endpoint}}">
                              {{ ! service.get_html_state(text=None, title=title)}}
                           </a>
                        </td>
                     %else:
                        <td>&nbsp;</td>
                     %end
                  %end
               </tr>
            %end
         </tbody>
      </table>

      <script language="javascript" type="text/javascript" >
         $(document).ready(function(){
            $('table.table-fixed-header').floatThead({
               top: $('#topbar').outerHeight(),
               zIndex: 101
            });
         });
      </script>
   %end
 </div>
