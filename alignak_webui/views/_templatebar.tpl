%setdefault('templates_bar', False)
%setdefault('plugin', None)

<!-- Templates actions bar -->
<li class="dropdown" data-toggle="tooltip" data-placement="bottom" title="{{_('Templates menu')}}">
   <a class="navbar-link" href="#" class="dropdown-toggle" data-toggle="dropdown">
      <span class="caret hidden-xs"></span>
      <span class="fa fa-clone"></span>
      <span class="sr-only">{{_('Templates menu')}}</span>
   </a>

   <ul class="dropdown-menu" role="menu" aria-labelledby="{{_('Edition mode menu')}}">
      %try:
      <li>
         <a href="/hosts/templates">
            <span class="fa fa-fw fa-server"></span>
            <span>{{_('Declare a new host')}}</span>
         </a>
      </li>
      <li class="divider"></li>
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

      <li class="divider"></li>
      %#try:
      <li>
         <a href="/realm/None/form">
            <span class="fa fa-fw fa-sitemap"></span>
            <span>{{_('Create a new realm')}}</span>
         </a>
      </li>
      %#except RouteBuildError:
      %#print("Missing plugin Realms")
      %#end

      %if plugin and plugin.table['_table']['editable']:
      <li class="divider"></li>
      <li>
         <a href="{{ request.urlparts.path + '/form' }}">
            <span class="fa fa-fw fa-edit"></span>
            <span>{{_('Edition form for the %s') % plugin.backend_endpoint}}</span>
         </a>
      </li>
      %elif plugin:
      <li>
         <a href="{{ request.urlparts.path }}">
            <span class="fa fa-fw fa-edit"></span>
            <span>{{_('No edition form for the %s') % plugin.backend_endpoint}}</span>
         </a>
      </li>
      %end
   </ul>
</li>
