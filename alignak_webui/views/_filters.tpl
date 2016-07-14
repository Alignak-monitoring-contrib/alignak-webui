%setdefault("common_bookmarks", datamgr.get_user_preferences('common', 'bookmarks', []))
%setdefault("user_bookmarks", datamgr.get_user_preferences(current_user.get_username(), 'bookmarks', []))

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
<form class="navbar-form navbar-left" method="get" action="{{ search_action }}">
   <div class="dropdown form-group text-left">
      <button id="filters_menu" class="btn btn-default dropdown-toggle" type="button" data-toggle="dropdown" aria-expanded="true">
         <i class="fa fa-filter"></i>
         <span class="hidden-sm"> {{_('Filters')}}</span>
         <span class="caret"></span>
      </button>
      <ul class="dropdown-menu" role="menu" aria-labelledby="filters_menu">
         <li role="presentation">
            <a role="menuitem" href="{{search_action}}?search=">{{_('All')}}</a>
         </li>
         <li role="presentation" class="divider"></li>
         %for k,v in sorted(search_filters.items()):
            <li role="presentation">
               <a role="menuitem" href="{{search_action}}?search={{v}}">{{k}}</a>
            </li>
         %end
      </ul>
   </div>
   <div class="form-group">
      <label class="sr-only" for="search">{{_('Filter')}}</label>
      <div class="input-group">
         <span class="input-group-addon hidden-xs hidden-sm"><i class="fa fa-search"></i> {{ search_name }}</span>
         <input class="form-control" type="search" id="search" name="search" value="{{ search_string }}">
      </div>
   </div>
   %if ('value' in user_bookmarks and user_bookmarks['value']) or ('value' in common_bookmarks and common_bookmarks['value']):
   <div class="dropdown form-group text-left">
      <button class="btn btn-default dropdown-toggle" type="button" id="bookmarks_menu" data-toggle="dropdown" aria-expanded="true">
         <i class="fa fa-bookmark"></i>
         <span class="hidden-sm hidden-xs hidden-md"> {{_('Bookmarks')}}</span>
         <span class="caret"></span>
      </button>
      <ul class="dropdown-menu dropdown-menu-right" role="menu" aria-labelledby="bookmarks_menu">
      <script type="text/javascript">
         %for b in user_bookmarks['value']:
            declare_bookmark("{{!b['name']}}","{{!b['uri']}}");
         %end
         %for b in common_bookmarks['value']:
            declare_bookmarksro("{{!b['name']}}","{{!b['uri']}}");
         %end
         </script>
      </ul>
   </div>
   %end
</form>
%end
