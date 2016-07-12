%setdefault('debug', False)

%setdefault('page', 'unknown')

%setdefault('display_steps_form', False)

%setdefault('start', 0)
%setdefault('count', 25)
%setdefault('total', 0)

%from alignak_webui.utils.helper import Helper
%setdefault('pagination', Helper.get_pagination_control(page, total, start, count))

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
%# First element for global data
%# page_url start, count and total
%page_url, start, count, total, active = pagination[0]
<div id="pagination_{{page_url.replace('/', '_')}}" class="elts_per_page btn-toolbar" role="toolbar" aria-label="{{_('Pages number sequence')}}">
   %if pagination and len(pagination) > 1:
      %if display_steps_form and elts_per_page is not None:
      <form id="elts_per_page" class="form-inline">
         <div class="input-group">
            <div class="input-group-btn">
               <button type="button" class="btn btn-default dropdown-toggle" data-toggle="dropdown" aria-expanded="false">
                  #&nbsp;<span class="caret"></span>
               </button>
               <ul class="dropdown-menu" role="menu">
                  <li><a href="#" data-elts="5">{{_('%d elements') % 5}}</a></li>
                  <li><a href="#" data-elts="10">{{_('%d elements') % 10}}</a></li>
                  <li><a href="#" data-elts="25">{{_('%d elements') % 25}}</a></li>
                  <li><a href="#" data-elts="50">{{_('%d elements') % 50}}</a></li>
                  <li><a href="#" data-elts="100">{{_('%d elements') % 100}}</a></li>
                  <li><a href="#" data-elts="0">{{_('All elements (%d)' % total)}}</a></li>
               </ul>
            </div>
            <input type="number" class="form-control" aria-label="{{_('Elements per page')}}" placeholder="{{_('Elements per page')}}" value="{{elts_per_page}}">
         </div>
      </form>
      <script>
      $("#elts_per_page li a").click(function(e){
         var value = $(this).data('elts');

         // Save user preference
         save_user_preference('elts_per_page', value);

         // Force page reloading
         location.reload();
      });
      $('#elts_per_page').submit(function(e){
         var value = $('#elts_per_page input').val();

         if (value == parseInt(value)) {
            // Update input field
            save_user_preference('elts_per_page', value);
         } else {
            $('#elts_per_page input').val(value);
         }

         // Force page reloading
         location.reload();
      });
      $('#elts_per_page input').blur(function(e){
         var value = $('#elts_per_page input').val();

         if (value == parseInt(value)) {
            // Update input field
            save_user_preference('elts_per_page', value);
         } else {
            $('#elts_per_page input').val(value);
         }

         // Force page reloading
         location.reload();
      });
      </script>
      %end

      <div class="btn-group" role="group" aria-label="{{_('Pages sequence')}}">
      %from urllib import urlencode
      %first_element=False
      %next_page=False
      %for label, start, count, total, active in pagination:
         %# Skip first element
         %if not first_element:
         %first_element=True
         %continue
         %end
         %request.query['start'] = start
         %request.query['count'] = count
         <a class="btn btn-default {{'active' if active else ''}} {{'next_page' if next_page else ''}}"
            href="{{page_url}}?{{urlencode(request.query)}}">{{!label}}<span class="sr-only">{{!label}}</span></a>
         %if active:
         %next_page=True
         %else:
            %if next_page:
            %next_page=False
            %end
         %end
      %end
      </div>
   %end
</div>
