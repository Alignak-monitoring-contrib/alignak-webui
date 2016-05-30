%setdefault('action_bar', False)
%setdefault('in_sidebar', False)

%if target_user.is_anonymous() or target_user.get_username() == current_user.get_username():
%target_user = None
%end

<!--Sidebar menu -->
<nav id="sidebar-menu" class="navbar navbar-default">
   <ul class="nav navbar-nav">
      <li data-toggle="tooltip" data-placement="{{'bottom' if in_sidebar else 'right'}}" title="{{_('Dashboard')}}">
         <a class="navbar-link" href="{{ webui.get_url('Dashboard') + ('?target_user=' + target_user.get_username() if target_user else '') }}">
            <span class="fa fa-fw fa-dashboard"></span>
            <span class="hidden-sm hidden-xs">{{_('Dashboard')}}</span>
         </a>
      </li>
      <li data-toggle="tooltip" data-placement="{{'bottom' if in_sidebar else 'right'}}" title="{{_('Hosts table')}}">
         <a class="navbar-link" href="{{ webui.get_url('Hosts table') + ('?target_user=' + target_user.get_username() if target_user else '') }}">
            <span class="fa fa-fw fa-table"></span>
            <span class="hidden-sm hidden-xs">{{_('Hosts table')}}</span>
         </a>
      </li>
      %if current_user.is_administrator():
      <li data-toggle="tooltip" data-placement="{{'bottom' if in_sidebar else 'right'}}" title="{{_('Users')}}">
         <a class="navbar-link" href="{{ webui.get_url('Users') + ('?target_user=' + target_user.get_username() if target_user else '') }}">
            <span class="fa fa-fw fa-users"></span>
            <span class="hidden-sm hidden-xs">{{_('Users')}}</span>
         </a>
      </li>
      %end
      <li data-toggle="tooltip" data-placement="{{'bottom' if in_sidebar else 'right'}}" title="{{_('Commands')}}">
         <a class="navbar-link" href="{{ webui.get_url('Commands') + ('?target_user=' + target_user.get_username() if target_user else '') }}">
            <span class="fa fa-fw fa-bolt"></span>
            <span class="hidden-sm hidden-xs">{{_('Commands')}}</span>
         </a>
      </li>
      %if action_bar and in_sidebar and current_user.can_change_dashboard():
         <li role="separator" class="divider"></li>
         %include("_actionbar.tpl", in_sidebar=in_sidebar)
      %end
   </ul>
</nav>

%if action_bar and not in_sidebar and current_user.can_change_dashboard():
   %include("_actionbar.tpl", in_sidebar=in_sidebar)
%end
