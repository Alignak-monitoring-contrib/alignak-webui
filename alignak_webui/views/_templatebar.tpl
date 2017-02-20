%setdefault('templates_bar', False)

<!-- Templates actions bar -->
<li class="dropdown" data-toggle="tooltip" data-placement="bottom" title="{{_('Edition mode')}}">
   <a class="navbar-link" href="#" class="dropdown-toggle" data-toggle="dropdown">
      <span class="caret hidden-xs"></span>
      <span class="fa fa-clone"></span>
      <span class="sr-only">{{_('Edition')}}</span>
   </a>

   <ul class="dropdown-menu" role="menu" aria-labelledby="{{_('Edition mode menu')}}">
      %try:
      <li>
         <a href="{{ webui.get_url('Hosts templates table') }}">
            <span class="fa fa-fw fa-server"></span>
            <span>{{_('Hosts templates')}}</span>
         </a>
      </li>
      %except RouteBuildError:
      %print("Missing plugin Hosts")
      %end
      %try:
      <li>
         <a href="{{ webui.get_url('Services templates table') }}">
            <span class="fa fa-fw fa-cube"></span>
            <span>{{_('Services templates')}}</span>
         </a>
      </li>
      %except RouteBuildError:
      %print("Missing plugin Services")
      %end
      %try:
      <li>
         <a href="{{ webui.get_url('Users templates table') }}">
            <span class="fa fa-fw fa-user"></span>
            <span>{{_('Users templates')}}</span>
         </a>
      </li>
      %except RouteBuildError:
      %print("Missing plugin Users")
      %end
   </ul>
</li>
