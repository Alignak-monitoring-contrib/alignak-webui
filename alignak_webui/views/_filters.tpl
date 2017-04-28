%from bottle import request

%setdefault('search_engine', False)
%setdefault('search_filters', {})

%search_action = request.urlparts.path
%search_query = request.urlparts.query
%search_string = request.query.get('search', '')
%if search_engine and search_filters:
<nav id="filter-bar" class="navbar">
   <div class="container-fluid">
      <ul class="nav navbar-nav">
         <li id="search-filters" class="dropdown">
            <a href="#" class="dropdown-toggle" data-original-title="{{_('Filters list')}}" data-toggle="dropdown">
            <span class="caret"></span>
            <span class="fa fa-filter"></span>
            <span class="hidden-xs"> {{_('Filters')}}</span>
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
            <li role="presentation" class="divider"></li>
            <li role="presentation" >
               <a role="menuitem" data-action="search-box">
                  <strong>{{! _('<span class="fa fa-question-circle"></span> Search syntax')}}</strong>
               </a>
            </li>
            </ul>
         </li>
      </ul>

      <form class="navbar-form" role="search" method="get" action="{{ search_action }}">
         <div class="form-group" style="display:inline;">
            <div class="input-group" style="display:table;">
               <span class="input-group-addon" style="width:1%;"><span class="glyphicon glyphicon-search"></span></span>
               <input class="form-control" id="search" name="search" value="{{ search_string }}"placeholder="{{_('search filter...')}}" autocomplete="off" autofocus="autofocus" type="search">
            </div>
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
   </div><!-- /.container-fluid -->
</nav>
%end
