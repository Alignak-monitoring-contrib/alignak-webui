%from bottle import RouteBuildError

%setdefault('debug', False)
%setdefault('widgets_bar', False)

%if widgets_bar:
%from bottle import request
%widgets_bar = (request.route.name == 'Dashboard')
%end

<!-- Application menu -->
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

   %try:
   <li data-toggle="tooltip" data-placement="bottom" title="{{_('Hosts table')}}">
      <a href="{{ webui.get_url('Hosts table') }}">
         <span class="fa fa-fw fa-server"></span>
         <span class="sr-only">{{_('Hosts')}}</span>
      </a>
   </li>
   %except RouteBuildError:
   %print("Missing plugin Hosts")
   %end

   %try:
   <li data-toggle="tooltip" data-placement="bottom" title="{{_('Services table')}}">
      <a href="{{ webui.get_url('Services table') }}">
         <span class="fa fa-fw fa-cubes"></span>
         <span class="sr-only">{{_('Services')}}</span>
      </a>
   </li>
   %except RouteBuildError:
   %print("Missing plugin Services")
   %end

   %try:
   <li data-toggle="tooltip" data-placement="bottom" title="{{_('Livestate')}}">
      <a href="{{ webui.get_url('Livestate') }}">
         <span class="fa fa-fw fa-heartbeat"></span>
         <span class="sr-only">{{_('Livestate')}}</span>
      </a>
   </li>
   %except RouteBuildError:
   %print("Missing plugin Livestate")
   %end

   %try:
   <li data-toggle="tooltip" data-placement="bottom" title="{{_('Worldmap')}}">
      <a href="{{ webui.get_url('Worldmap') }}">
         <span class="fa fa-fw fa-globe"></span>
         <span class="sr-only">{{_('Worldmap')}}</span>
      </a>
   </li>
   %except RouteBuildError:
   %print("Missing plugin Worldmap")
   %end

   %try:
   <li data-toggle="tooltip" data-placement="bottom" title="{{_('Minemap')}}">
      <a href="{{ webui.get_url('Minemap') }}">
         <span class="fa fa-fw fa-table"></span>
         <span class="sr-only">{{_('Minemap')}}</span>
      </a>
   </li>
   %except RouteBuildError:
   %print("Missing plugin Minemap")
   %end

   %if widgets_bar and current_user.can_change_dashboard():
      %include("_widgetsbar.tpl")
   %end
</ul>
