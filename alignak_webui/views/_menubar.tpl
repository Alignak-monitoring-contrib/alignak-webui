%setdefault('debug', False)
%setdefault('action_bar', False)
%setdefault('in_sidebar', False)

%action_bar = (len(webui.get_widgets_for('dashboard')) != 0)
%if action_bar:
%from bottle import request
%action_bar = (request.route.name == 'Dashboard')
%end
%if target_user.is_anonymous() or target_user.get_username() == current_user.get_username():
%target_user = None
%end

<!-- Application menu -->
<nav id="menu-bar">
   <ul class="nav navbar-nav">
      <li data-toggle="tooltip" data-placement="bottom" title="{{_('Dashboard')}}">
         <a class="navbar-link" href="{{ webui.get_url('Dashboard') + ('?target_user=' + target_user.get_username() if target_user else '') }}">
            <span class="fa fa-fw fa-dashboard"></span>
            <span class="sr-only">{{_('Dashboard')}}</span>
         </a>
      </li>
      <li data-toggle="tooltip" data-placement="bottom" title="{{_('Livestate table')}}">
         <a class="navbar-link" href="{{ webui.get_url('Livestate table') + ('?target_user=' + target_user.get_username() if target_user else '') }}">
            <span class="fa fa-fw fa-heartbeat"></span>
            <span class="sr-only">{{_('Livestate')}}</span>
         </a>
      </li>
      <li data-toggle="tooltip" data-placement="bottom" title="{{_('Log table')}}">
         <a class="navbar-link" href="{{ webui.get_url('Log check result table') + ('?target_user=' + target_user.get_username() if target_user else '') }}">
            <span class="fa fa-fw fa-history"></span>
            <span class="sr-only">{{_('Log')}}</span>
         </a>
      </li>

      <!-- Items -->
      <li class="dropdown" data-toggle="tooltip" data-placement="bottom" title="{{_('Elements')}}">
         <a href="#" class="dropdown-toggle" data-toggle="dropdown">
            <span class="caret"></span>
            <span class="fa fa-cube"></span>
            <span class="sr-only">{{_('Elements')}}</span>
         </a>

         <ul class="dropdown-menu" role="menu" aria-labelledby="{{_('Elements menu')}}">
            <li>
               <a href="{{ webui.get_url('Hosts table') + ('?target_user=' + target_user.get_username() if target_user else '') }}">
                  <span class="fa fa-fw fa-server"></span>
                  <span>{{_('Hosts')}}</span>
               </a>
            </li>
            <li>
               <a href="{{ webui.get_url('Services table') + ('?target_user=' + target_user.get_username() if target_user else '') }}">
                  <span class="fa fa-fw fa-cubes"></span>
                  <span>{{_('Services')}}</span>
               </a>
            </li>
            <li>
               <a href="{{ webui.get_url('Users table') + ('?target_user=' + target_user.get_username() if target_user else '') }}">
                  <span class="fa fa-fw fa-users"></span>
                  <span>{{_('Users')}}</span>
               </a>
            </li>

            <li class="divider"></li>

            <li>
               <a href="{{ webui.get_url('Hosts dependencies table') + ('?target_user=' + target_user.get_username() if target_user else '') }}">
                  <span class="fa fa-fw fa-arrows-v"></span>
                  <span>{{_('Hosts dependencies')}}</span>
               </a>
            </li>

            <li class="divider"></li>

            <li>
               <a href="{{ webui.get_url('Realms table') + ('?target_user=' + target_user.get_username() if target_user else '') }}">
                  <span class="fa fa-w fa-sitemap"></span>
                  <span>{{_('Realms')}}</span>
               </a>
            </li>
            <li>
               <a href="{{ webui.get_url('Timeperiods table') + ('?target_user=' + target_user.get_username() if target_user else '') }}">
                  <span class="fa fa-fw fa-calendar"></span>
                  <span>{{_('Timeperiods')}}</span>
               </a>
            </li>
            <li>
               <a href="{{ webui.get_url('Commands table') + ('?target_user=' + target_user.get_username() if target_user else '') }}">
                  <span class="fa fa-fw fa-bolt"></span>
                  <span>{{_('Commands')}}</span>
               </a>
            </li>

            <li class="divider"></li>

            <li>
               <a href="{{ webui.get_url('Users groups table') + ('?target_user=' + target_user.get_username() if target_user else '') }}">
                  <span class="fa fa-w fa-sitemap"></span>
                  <span>{{_('Users groups')}}</span>
               </a>
            </li>
            <li>
               <a href="{{ webui.get_url('Hosts groups table') + ('?target_user=' + target_user.get_username() if target_user else '') }}">
                  <span class="fa fa-w fa-sitemap"></span>
                  <span>{{_('Hosts groups')}}</span>
               </a>
            </li>
            <li>
               <a href="{{ webui.get_url('Services groups table') + ('?target_user=' + target_user.get_username() if target_user else '') }}">
                  <span class="fa fa-w fa-sitemap"></span>
                  <span>{{_('Services groups')}}</span>
               </a>
            </li>
         </ul>
      </li>

      <!-- Tactical views -->
      <li class="dropdown" data-toggle="tooltip" data-placement="bottom" title="{{_('Tactical views')}}">
         <a href="#" class="dropdown-toggle" data-toggle="dropdown">
            <span class="caret"></span>
            <span class="fa fa-bar-chart"></span>
            <span class="sr-only">{{_('Tactical views')}}</span>
         </a>

         <ul class="dropdown-menu" role="menu" aria-labelledby="{{_('Tactical views menu')}}">
            <li data-toggle="tooltip" data-placement="bottom" title="{{_('Worldmap')}}">
               <a href="{{ webui.get_url('Worldmap') + ('?target_user=' + target_user.get_username() if target_user else '') }}">
                  <span class="fa fa-fw fa-globe"></span>
                  <span>{{_('Worldmap')}}</span>
               </a>
            </li>
            <li data-toggle="tooltip" data-placement="bottom" title="{{_('Minemap')}}">
               <a href="{{ webui.get_url('Minemap') + ('?target_user=' + target_user.get_username() if target_user else '') }}">
                  <span class="fa fa-fw fa-table"></span>
                  <span>{{_('Minemap')}}</span>
               </a>
            </li>
         </ul>
      </li>

      %if action_bar and in_sidebar and current_user.can_change_dashboard():
         %include("_templatebar.tpl", in_sidebar=in_sidebar)
      %end

      %if action_bar and in_sidebar and current_user.can_change_dashboard():
         %include("_actionbar.tpl", in_sidebar=in_sidebar)
      %end
   </ul>
</nav>