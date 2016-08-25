%from bottle import request
%# If current page defines its own search criteria...
%search_filters = {}
%if 'search_engine' in request.route.config and request.route.config['search_engine']:
%search_action = request.fullpath
%search_prefix = request.route.config['search_prefix']
%search_filters = request.route.config['search_filters']
%search_name = request.route.name
%search_string = request.query.get('search', '')
%if search_prefix not in search_string:
%search_string = search_prefix + ' ' + search_string
%end
%end

%if search_filters:
   <li class="dropdown">
      <a href="#" class="dropdown-toggle" data-original-title="{{_('Filters  menu')}}" data-toggle="dropdown">
         <span class="caret"></span>
         <i class="fa fa-filter"></i>
         <span class="hidden-sm hidden-xs"> {{_('Filters')}}</span>
      </a>
      <ul class="dropdown-menu" role="menu" aria-labelledby="filters_menu">
         <li role="presentation">
            <a role="menuitem" href="{{search_action}}?search=">{{_('All')}}</a>
         </li>
         <li role="presentation" class="divider"></li>
         %for k in sorted(search_filters.keys()):
            %title,filter = search_filters[k]
            %if not title:
            <li class="divider"/>
            %else:
            <li role="presentation">
               <a role="menuitem" href="{{search_action}}?search={{filter}}">{{title}}</a>
            </li>
            %end
         %end
      </ul>
   </li>
   <form class="hidden-xs hidden-sm navbar-form navbar-left" role="search" method="get" action="{{ search_action }}">
      <div class="form-group">
         <label class="sr-only" for="search">{{_('Filter')}}</label>
         <div class="input-group">
            <span class="input-group-addon hidden-xs hidden-sm"><i class="fa fa-search"></i></span>
            <input class="form-control" type="search" id="search" name="search" value="{{ search_string }}" placeholder="{{_('filter...')}}">
         </div>
      </div>
   </form>
%end
