%setdefault('debug', False)
%setdefault('action_bar', False)
%setdefault('in_sidebar', False)

%action_bar = (len(webui.get_widgets_for('dashboard')) != 0)
%if action_bar:
%from bottle import request
%action_bar = request.route.name == 'Dashboard'
%end
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
      <li data-toggle="tooltip" data-placement="{{'bottom' if in_sidebar else 'right'}}" title="{{_('Livestate table')}}">
         <a class="navbar-link" href="{{ webui.get_url('Livestate table') + ('?target_user=' + target_user.get_username() if target_user else '') }}">
            <span class="fa fa-fw fa-heartbeat"></span>
            <span class="hidden-sm hidden-xs">{{_('Livestate')}}</span>
         </a>
      </li>
      <li data-toggle="tooltip" data-placement="{{'bottom' if in_sidebar else 'right'}}" title="{{_('Log table')}}">
         <a class="navbar-link" href="{{ webui.get_url('Log check result table') + ('?target_user=' + target_user.get_username() if target_user else '') }}">
            <span class="fa fa-fw fa-history"></span>
            <span class="hidden-sm hidden-xs">{{_('Log')}}</span>
         </a>
      </li>

      <!-- Items -->
      <li class="dropdown" data-toggle="tooltip" data-placement="top" title="{{_('Elements')}}">
         <a class="navbar-link" href="#" class="dropdown-toggle" data-toggle="dropdown">
            <span class="caret"></span>
            <span class="fa fa-wrench"></span>
            <span class="hidden-sm hidden-xs">{{_('Elements')}}</span>
         </a>

         <ul class="dropdown-menu" role="menu" aria-labelledby="{{_('Elements menu')}}">
            <li data-toggle="tooltip" data-placement="{{'bottom' if in_sidebar else 'right'}}" title="{{_('Hosts table')}}">
               <a class="navbar-link" href="{{ webui.get_url('Hosts table') + ('?target_user=' + target_user.get_username() if target_user else '') }}">
                  <span class="fa fa-fw fa-server"></span>
                  <span class="hidden-xs">{{_('Hosts')}}</span>
               </a>
            </li>
            <li data-toggle="tooltip" data-placement="{{'bottom' if in_sidebar else 'right'}}" title="{{_('Services table')}}">
               <a class="navbar-link" href="{{ webui.get_url('Services table') + ('?target_user=' + target_user.get_username() if target_user else '') }}">
                  <span class="fa fa-fw fa-cubes"></span>
                  <span class="hidden-xs">{{_('Services')}}</span>
               </a>
            </li>
            <li data-toggle="tooltip" data-placement="{{'bottom' if in_sidebar else 'right'}}" title="{{_('Users table')}}">
               <a class="navbar-link" href="{{ webui.get_url('Users table') + ('?target_user=' + target_user.get_username() if target_user else '') }}">
                  <span class="fa fa-fw fa-users"></span>
                  <span class="hidden-xs">{{_('Users')}}</span>
               </a>
            </li>

            <li class="divider"></li>

            <li data-toggle="tooltip" data-placement="{{'bottom' if in_sidebar else 'right'}}" title="{{_('Realms table')}}">
               <a class="navbar-link" href="{{ webui.get_url('Realms table') + ('?target_user=' + target_user.get_username() if target_user else '') }}">
                  <span class="fa fa-w fa-sitemap"></span>
                  <span class="hidden-xs">{{_('Realms')}}</span>
               </a>
            </li>
            <li data-toggle="tooltip" data-placement="{{'bottom' if in_sidebar else 'right'}}" title="{{_('Timeperiods table')}}">
               <a class="navbar-link" href="{{ webui.get_url('Timeperiods table') + ('?target_user=' + target_user.get_username() if target_user else '') }}">
                  <span class="fa fa-fw fa-calendar"></span>
                  <span class="hidden-xs">{{_('Timeperiods')}}</span>
               </a>
            </li>
            <li data-toggle="tooltip" data-placement="{{'bottom' if in_sidebar else 'right'}}" title="{{_('Commands table')}}">
               <a class="navbar-link" href="{{ webui.get_url('Commands table') + ('?target_user=' + target_user.get_username() if target_user else '') }}">
                  <span class="fa fa-fw fa-bolt"></span>
                  <span class="hidden-xs">{{_('Commands')}}</span>
               </a>
            </li>

            <li class="divider"></li>

            <li data-toggle="tooltip" data-placement="{{'bottom' if in_sidebar else 'right'}}" title="{{_('Users groups table')}}">
               <a class="navbar-link" href="{{ webui.get_url('Users groups table') + ('?target_user=' + target_user.get_username() if target_user else '') }}">
                  <span class="fa fa-w fa-sitemap"></span>
                  <span class="hidden-xs">{{_('Users groups')}}</span>
               </a>
            </li>
            <li data-toggle="tooltip" data-placement="{{'bottom' if in_sidebar else 'right'}}" title="{{_('Hosts groups table')}}">
               <a class="navbar-link" href="{{ webui.get_url('Hosts groups table') + ('?target_user=' + target_user.get_username() if target_user else '') }}">
                  <span class="fa fa-w fa-sitemap"></span>
                  <span class="hidden-xs">{{_('Hosts groups')}}</span>
               </a>
            </li>
            <li data-toggle="tooltip" data-placement="{{'bottom' if in_sidebar else 'right'}}" title="{{_('Services groups table')}}">
               <a class="navbar-link" href="{{ webui.get_url('Services groups table') + ('?target_user=' + target_user.get_username() if target_user else '') }}">
                  <span class="fa fa-w fa-sitemap"></span>
                  <span class="hidden-xs">{{_('Services groups')}}</span>
               </a>
            </li>
         </ul>
      </li>

      <!-- Tactical views -->
      <li class="dropdown" data-toggle="tooltip" data-placement="top" title="{{_('Tactical views')}}">
         <a class="navbar-link" href="#" class="dropdown-toggle" data-toggle="dropdown">
            <span class="caret"></span>
            <span class="fa fa-bar-chart"></span>
            <span class="hidden-sm hidden-xs">{{_('Tactical views')}}</span>
         </a>

         <ul class="dropdown-menu" role="menu" aria-labelledby="{{_('Tactical views menu')}}">
            <li data-toggle="tooltip" data-placement="{{'bottom' if in_sidebar else 'right'}}" title="{{_('Worldmap')}}">
               <a class="navbar-link" href="{{ webui.get_url('Worldmap') + ('?target_user=' + target_user.get_username() if target_user else '') }}">
                  <span class="fa fa-fw fa-globe"></span>
                  <span class="hidden-xs">{{_('Worldmap')}}</span>
               </a>
            </li>
            <li data-toggle="tooltip" data-placement="{{'bottom' if in_sidebar else 'right'}}" title="{{_('Minemap')}}">
               <a class="navbar-link" href="{{ webui.get_url('Minemap') + ('?target_user=' + target_user.get_username() if target_user else '') }}">
                  <span class="fa fa-fw fa-table"></span>
                  <span class="hidden-xs">{{_('Minemap')}}</span>
               </a>
            </li>
         </ul>
      </li>

      %if action_bar and in_sidebar and current_user.can_change_dashboard():
         <li role="separator" class="divider"></li>
         %include("_templatebar.tpl", in_sidebar=in_sidebar)
      %end

      %if action_bar and in_sidebar and current_user.can_change_dashboard():
         <li role="separator" class="divider"></li>
         %include("_actionbar.tpl", in_sidebar=in_sidebar)
      %end
   </ul>
</nav>

%if edition_mode and not in_sidebar:
   %include("_templatebar.tpl", in_sidebar=in_sidebar)
%end

%if action_bar and not in_sidebar and current_user.can_change_dashboard():
   %include("_actionbar.tpl", in_sidebar=in_sidebar)
%end
