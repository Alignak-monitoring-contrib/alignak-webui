%setdefault('debug', True)

%setdefault('display_steps_form', False)
%setdefault('div_class', "")
%setdefault('ul_class', "")
%setdefault('div_style', "")
%setdefault('size', 'btn-lg')

%from bottle import request

%if pagination:
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
   %name, start, end, total, active = pagination[0]
%end
<div class="btn-toolbar" role="toolbar" aria-label="{{_('Pages number sequence')}}">
   %if pagination and len(pagination) > 1:
      %if display_steps_form and elts_per_page is not None:
      <ul class="steps_form pull-left" style="margin-left: -35px">
         <li>
         <form id="elts_per_page" class="pull-left">
          <div class="input-group" style="width:120px">
            <div class="input-group-btn">
              <button type="button" class="btn btn-default dropdown-toggle" data-toggle="dropdown" aria-expanded="false">#&nbsp;<span class="caret"></span></button>
              <ul class="dropdown-menu" role="menu">
                <li><a href="#" data-elts="5">{{_('%d elements') % 5}}</a></li>
                <li><a href="#" data-elts="10">{{_('%d elements') % 10}}</a></li>
                <li><a href="#" data-elts="25">{{_('%d elements') % 25}}</a></li>
                <li><a href="#" data-elts="50">{{_('%d elements') % 50}}</a></li>
                <li><a href="#" data-elts="100">{{_('%d elements') % 100}}</a></li>
                <li><a href="#" data-elts="0">{{_('All elements (%d)' % total)}}</a></li>
              </ul>
            </div>
            <input type="number" class="form-control" aria-label="{{_('Elements per page')}}" placeholder="{{_('Elements per page')}}" value="{{elts_per_page}}" style="max-width: 100px;">
          </div>
         </form>
         </li>
         <script>
         var current_elts_per_page = {{elts_per_page}};
         $("#elts_per_page li a").click(function(e){
            var value = $(this).data('elts');

            // Save user preference
            save_user_preference('elts_per_page', value);

            // Update input field
            $('#elts_per_page input').val(value);

            current_elts_per_page = value;

            e.preventDefault();

            refresh_required = true;
         });
         $('#elts_per_page form').submit(function(e){
            var value = $('#elts_per_page input').val();

            if (value == parseInt(value)) {
               // Update input field
               save_user_preference('elts_per_page', value);
               current_elts_per_page = value;
            } else {
               $('#elts_per_page input').val(current_elts_per_page);
            }

            e.preventDefault();

            refresh_required = true;
         });
         $('#elts_per_page input').blur(function(e){
            var value = $('#elts_per_page input').val();

            if (value == parseInt(value)) {
               // Update input field
               save_user_preference('elts_per_page', value);
               current_elts_per_page = value;
            } else {
               $('#elts_per_page input').val(current_elts_per_page);
            }

            e.preventDefault();

            refresh_required = true;
         });
         </script>
      </ul>
      %end

      <div class="btn-group" role="group" aria-label="{{_('Pages sequence')}}">
      %from urllib import urlencode
      %for label, start, count, total, active in pagination:
         %request.query['start'] = start
         %request.query['count'] = count
         <a class="btn btn-default {{'active' if active else ''}}"
            href="{{page}}?{{urlencode(request.query)}}">
            {{!label}}
            <span class="sr-only">{{!label}}</span>
         </a>
      %end
      </div>
   %end
</div>
