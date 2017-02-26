%from bottle import RouteBuildError

%setdefault('debug', False)
%setdefault('widgets_bar', False)

%if widgets_bar:
%from bottle import request
%widgets_bar = (request.route.name == 'Dashboard')
%end

<!-- Application menu -->
<nav id="menu-bar">
   <ul class="nav navbar-nav">
      %try:
      <li data-toggle="tooltip" data-placement="bottom" title="{{_('Dashboard')}}">
         <a class="navbar-link" href="{{ webui.get_url('Dashboard') }}">
            <span class="fa fa-fw fa-dashboard"></span>
            <span class="sr-only">{{_('Dashboard')}}</span>
         </a>
      </li>
      %except RouteBuildError:
      %print("Missing plugin Dashboard")
      %end

      <!-- Items -->
      <li class="dropdown" data-toggle="tooltip" data-placement="bottom" title="{{_('Elements')}}">
         <a href="#" class="dropdown-toggle" data-toggle="dropdown">
            <span class="caret"></span>
            <span class="fa fa-cube"></span>
            <span class="sr-only">{{_('Elements')}}</span>
         </a>

         <ul class="dropdown-menu" role="menu" aria-labelledby="{{_('Elements menu')}}">
            %try:
            <li>
               <a href="{{ webui.get_url('Hosts table') }}">
                  <span class="fa fa-fw fa-server"></span>
                  <span>{{_('Hosts')}}</span>
               </a>
            </li>
            %except RouteBuildError:
            %print("Missing plugin Hosts")
            %end

            %try:
            <li>
               <a href="{{ webui.get_url('Services table') }}">
                  <span class="fa fa-fw fa-cubes"></span>
                  <span>{{_('Services')}}</span>
               </a>
            </li>
            %except RouteBuildError:
            %print("Missing plugin Services")
            %end

            %try:
            <li>
               <a href="{{ webui.get_url('Users table') }}">
                  <span class="fa fa-fw fa-users"></span>
                  <span>{{_('Users')}}</span>
               </a>
            </li>
            %except RouteBuildError:
            %print("Missing plugin Users")
            %end

            <li class="divider"></li>

            %try:
            <li>
               <a href="{{ webui.get_url('Hosts dependencies table') }}">
                  <span class="fa fa-fw fa-arrows-v"></span>
                  <span>{{_('Hosts dependencies')}}</span>
               </a>
            </li>
            %except RouteBuildError:
            %print("Missing plugin Hosts dependencies")
            %end

            %try:
            <li>
               <a href="{{ webui.get_url('Services dependencies table') }}">
                  <span class="fa fa-fw fa-arrows-v"></span>
                  <span>{{_('Services dependencies')}}</span>
               </a>
            </li>
            %except RouteBuildError:
            %print("Missing plugin Services dependencies")
            %end

            <li class="divider"></li>

            %try:
            <li>
               <a href="{{ webui.get_url('Realms table') }}">
                  <span class="fa fa-w fa-sitemap"></span>
                  <span>{{_('Realms')}}</span>
               </a>
            </li>
            %except RouteBuildError:
            %print("Missing plugin Realms")
            %end

            %try:
            <li>
               <a href="{{ webui.get_url('Timeperiods table') }}">
                  <span class="fa fa-fw fa-calendar"></span>
                  <span>{{_('Timeperiods')}}</span>
               </a>
            </li>
            %except RouteBuildError:
            %print("Missing plugin Timeperiods")
            %end

            %try:
            <li>
               <a href="{{ webui.get_url('Commands table') }}">
                  <span class="fa fa-fw fa-bolt"></span>
                  <span>{{_('Commands')}}</span>
               </a>
            </li>
            %except RouteBuildError:
            %print("Missing plugin Commands")
            %end

            <li class="divider"></li>

            %try:
            <li>
               <a href="{{ webui.get_url('Users groups table') }}">
                  <span class="fa fa-w fa-sitemap"></span>
                  <span>{{_('Users groups')}}</span>
               </a>
            </li>
            %except RouteBuildError:
            %print("Missing plugin Users groups")
            %end

            %try:
            <li>
               <a href="{{ webui.get_url('Hosts groups table') }}">
                  <span class="fa fa-w fa-sitemap"></span>
                  <span>{{_('Hosts groups')}}</span>
               </a>
            </li>
            %except RouteBuildError:
            %print("Missing plugin Hosts groups")
            %end

            %try:
            <li>
               <a href="{{ webui.get_url('Services groups table') }}">
                  <span class="fa fa-w fa-sitemap"></span>
                  <span>{{_('Services groups')}}</span>
               </a>
            </li>
            %except RouteBuildError:
            %print("Missing plugin Services groups")
            %end
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
            %try:
            <li>
               <a href="{{ webui.get_url('Livestate') }}">
                  <span class="fa fa-fw fa-heartbeat"></span>
                  <span>{{_('Livestate')}}</span>
               </a>
            </li>
            %except RouteBuildError:
            %print("Missing plugin Livestate")
            %end

            %try:
            <li>
               <a href="{{ webui.get_url('Log check results table') }}">
                  <span class="fa fa-fw fa-history"></span>
                  <span>{{_('Log')}}</span>
               </a>
            </li>
            %except RouteBuildError:
            %print("Missing plugin Logs")
            %end

            <li class="divider"></li>

            %try:
            <li>
               <a href="{{ webui.get_url('Worldmap') }}">
                  <span class="fa fa-fw fa-globe"></span>
                  <span>{{_('Worldmap')}}</span>
               </a>
            </li>
            %except RouteBuildError:
            %print("Missing plugin Worldmap")
            %end

            %try:
            <li>
               <a href="{{ webui.get_url('Minemap') }}">
                  <span class="fa fa-fw fa-table"></span>
                  <span>{{_('Minemap')}}</span>
               </a>
            </li>
            %except RouteBuildError:
            %print("Missing plugin Minemap")
            %end

            <li class="divider"></li>

            %try:
            <li>
               <a href="{{ webui.get_url('Realms tree') }}">
                  <span class="fa fa-w fa-sitemap"></span>
                  <span>{{_('Realms')}}</span>
               </a>
            </li>
            %except RouteBuildError:
            %print("Missing plugin Realms")
            %end

            %try:
            <li>
               <a href="{{ webui.get_url('Hosts groups tree') }}">
                  <span class="fa fa-w fa-sitemap"></span>
                  <span>{{_('Hosts groups')}}</span>
               </a>
            </li>
            %except RouteBuildError:
            %print("Missing plugin Hosts groups")
            %end

            <li class="divider"></li>

            %try:
            <li>
               <a href="{{ webui.get_url('Alignak status') }}">
                  <span class="fa fa-w fa-sitemap"></span>
                  <span>{{_('Alignak status')}}</span>
               </a>
            </li>
            %except RouteBuildError:
            %print("Missing plugin Alignak")
            %end
         </ul>
      </li>

      %if edition_mode:
         %include("_templatebar.tpl")
      %end

      %if widgets_bar and current_user.can_change_dashboard():
         %include("_widgetsbar.tpl")
      %end
   </ul>
</nav>