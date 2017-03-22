%from bottle import request

%setdefault('search_engine', False)
%setdefault('search_filters', {})

%search_action = request.urlparts
%search_query = request.urlparts.query
%search_string = request.query.get('search', '')
%if search_engine and search_filters:
   <li id="search-filters" class="dropdown">
      <a href="#" class="dropdown-toggle" data-original-title="{{_('Filters list')}}" data-toggle="dropdown">
         <span class="caret"></span>
         <span class="fa fa-filter"></span>
         <span class="hidden-sm hidden-xs"> {{_('Filters')}}</span>
      </a>
      <ul class="dropdown-menu" role="menu" aria-labelledby="filters_menu">
         <li role="presentation">
            <a role="menuitem" data-action="filter" data-filter="">{{_('Clear filter')}}</a>
         </li>
         <li role="presentation" class="divider"></li>
         %for k in sorted(search_filters.keys()):
            %title,filter = search_filters[k]
            %if not title:
            <li class="divider"/>
            %else:
            <li role="presentation">
               <a role="menuitem" data-action="filter" data-filter="{{filter}}">{{title}}</a>
            </li>
            %end
         %end
         <li role="presentation" class="divider hidden-xs hidden-sm"></li>
         <li role="presentation" >
            <a role="menuitem" data-action="search-box">
               <strong>{{! _('<span class="fa fa-question-circle"></span> Search syntax')}}</strong>
            </a>
         </li>
      </ul>
   </li>
   <form class="navbar-form navbar-left" role="search" method="get" action="{{ search_action }}">
      <label class="sr-only" for="search">{{_('Filter input field')}}</label>
      <div class="input-group">
         <input class="form-control" type="search" id="search" name="search" value="{{ search_string }}" placeholder="{{_('search filter...')}}">
      </div>
   </form>
   <script>
      $('a[data-action="filter"]').on('click', function(e){
         var filter = $(this).data('filter');
         if (filter == undefined) return;

         // Build a new request url
         var url = window.location.href.replace(window.location.search,'');
         if (filter == '') {
            // Empty filter clears the filter
         } else {
            url = url + '?search=' + filter;
         }
         // Force page reloading with new parameters
         document.location.href = url;
      });
   </script>
%end
