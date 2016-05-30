%setdefault("common_bookmarks", webui.prefs_module.get_common_bookmarks())
%setdefault("user_bookmarks", webui.prefs_module.get_user_bookmarks(current_user.get_username()))

%from bottle import request
%if 'search_engine' in request.route.config and request.route.config['search_engine']:
%search_action = request.fullpath
%search_prefix = request.route.config['search_prefix']
%search_filters = request.route.config['search_filters']
%search_name = request.route.name
%else:
%search_action = '/all'
%search_prefix = ''
%search_filters = {}
%search_name = ''
%end
%search_string = request.query.get('search', '')
%if search_prefix not in search_string:
%search_string = search_prefix + ' ' + search_string
%end

<form class="navbar-form navbar-left" method="get" action="{{ search_action }}">
   %if search_filters:
   <div class="dropdown form-group text-left">
      <button id="filters_menu" class="btn btn-default dropdown-toggle" type="button" data-toggle="dropdown" aria-expanded="true">
         <i class="fa fa-filter"></i>
         <span class="hidden-sm"> {{_('Filters')}}</span>
         <span class="caret"></span>
      </button>
      <ul class="dropdown-menu" role="menu" aria-labelledby="filters_menu">
         <li role="presentation"><a role="menuitem" href="{{search_action}}?search={{search_prefix}}&title={{'%s %s' % (_('All '), search_name)}}">{{_('All')}}</a></li>
         <li role="presentation" class="divider"></li>
         %for k,v in search_filters.items():
            <li role="presentation"><a role="menuitem" href="{{search_action}}?search={{v}}">{{k}}</a></li>
         %end
      </ul>
   </div>
   %end
   <div class="form-group">
      <label class="sr-only" for="search">{{_('Filter')}}</label>
      <div class="input-group">
         <span class="input-group-addon hidden-xs hidden-sm"><i class="fa fa-search"></i> {{ search_name }}</span>
         <input class="form-control" type="search" id="search" name="search" value="{{ search_string }}">
      </div>
   </div>
   <!--
   <div class="dropdown form-group text-left">
      <button class="btn btn-default dropdown-toggle" type="button" id="bookmarks_menu" data-toggle="dropdown" aria-expanded="true">
         <i class="fa fa-bookmark"></i>
         <span class="hidden-sm hidden-xs hidden-md"> {{_('Bookmarks')}}</span>
         <span class="caret"></span>
      </button>
      <ul class="dropdown-menu dropdown-menu-right" role="menu" aria-labelledby="bookmarks_menu">
      <script type="text/javascript">
         %for b in user_bookmarks:
            declare_bookmark("{{!b['name']}}","{{!b['uri']}}");
         %end
         %for b in common_bookmarks:
            declare_bookmarksro("{{!b['name']}}","{{!b['uri']}}");
         %end
         </script>
      </ul>
   </div>
   -->
</form>
