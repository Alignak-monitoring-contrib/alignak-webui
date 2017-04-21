%setdefault('debug', False)

%setdefault('display_steps_form', False)

%setdefault('start', 0)
%setdefault('count', 25)
%setdefault('total', 0)

%from alignak_webui.utils.helper import Helper
%setdefault('pagination', Helper.get_pagination_control('unknown', total, start, count))

%from bottle import request

%if debug:
<div class="panel-group">
   <div class="panel panel-default">
      <div class="panel-heading">
         <h4 class="panel-title">
            <a data-toggle="collapse" href="#collapse_pagination"><i class="fa fa-bug"></i> Pagination</a>
         </h4>
      </div>
      <div id="collapse_pagination" class="panel-collapse collapse">
         <ul class="list-group">
            %for pagination_elt in pagination:
               <li class="list-group-item"><small>Element: {{pagination_elt}}</small></li>
            %end
         </ul>
         <div class="panel-footer">{{len(pagination)}} elements</div>
      </div>
   </div>
</div>
%end

%page_url, start, count, total, active = pagination[0]
%item_id = page_url.replace('/', '_')
%item_id = item_id.replace('#', '_')
<div id="pagination_{{item_id}}" class="elts_per_page btn-toolbar" role="toolbar" aria-label="{{_('Pages number sequence')}}">
   %if pagination and len(pagination) > 1:
      %if display_steps_form and elts_per_page is not None:
         <div class="input-group input-group-sm">
            <div class="input-group-btn">
               <button type="button" class="btn dropdown-toggle" data-toggle="dropdown" aria-expanded="false">
                  {{count}}&nbsp;#&nbsp;<span class="caret"></span>
               </button>
               <ul class="dropdown-menu" role="menu">
                  <li><a href="#" data-elts="5">{{_('%d elements') % 5}}</a></li>
                  <li><a href="#" data-elts="10">{{_('%d elements') % 10}}</a></li>
                  <li><a href="#" data-elts="25">{{_('%d elements') % 25}}</a></li>
                  <li><a href="#" data-elts="50">{{_('%d elements') % 50}}</a></li>
               </ul>
            </div>

            <ul class="pagination pagination-sm" >
               %from urllib import urlencode
               %first_element=False
               %next_page=False
               %for label, start, count, total, active in pagination:
                  %# Skip first element
                  %if not first_element:
                  %  first_element=True
                  %  continue
                  %end
                  %request.query['start'] = start
                  %request.query['count'] = count
                  <li class="{{'active' if active else ''}} {{'next_page' if next_page else ''}}">
                     <a href="{{page_url}}?{{urlencode(request.query)}}">{{!label}}
                        <span class="sr-only">{{!label}}</span>
                     </a>
                  </li>
                  %if active:
                  %  next_page=True
                  %else:
                     %if next_page:
                     %  next_page=False
                     %end
                  %end
               %end
            </ul>
         </div>

         <script>
         $("#pagination_{{item_id}} ul.dropdown-menu>li>a").on('click', function(e){
            var value = $(this).data('elts');

            // Build a new pagination request url
            var url = window.location.href.replace(window.location.search,'');
            url = url + '?start=0&count='+value;

            // Save user preference
            save_user_preference('elts_per_page', value, function() {
               // Force page reloading with new parameters
               document.location.href = url;
            });
         });
         </script>
      %end
   %end
</div>
