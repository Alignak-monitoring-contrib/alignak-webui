%setdefault('templates_bar', False)
%setdefault('object_plugin', None)

<!-- Templates actions bar -->
<li class="dropdown" data-toggle="tooltip" data-placement="bottom" title="{{_('Edition menu')}}">
   <a class="navbar-link" href="#" class="dropdown-toggle" data-toggle="dropdown">
      <span class="caret hidden-xs"></span>
      <span class="text-warning fa fa-w fa-edit"></span>
      <span class="sr-only">{{_('Templates menu')}}</span>
   </a>

   <ul class="dropdown-menu" role="menu" aria-labelledby="{{_('Edition mode menu')}}">
      <li>
         <a href="/realm_form/None">
            <span class="fa fa-fw fa-sitemap"></span>
            <span>{{_('Create a new realm')}}</span>
         </a>
      </li>
      <li>
         <a href="/hostgroup_form/None">
            <span class="fa fa-fw fa-sitemap"></span>
            <span>{{_('Create a new hostgroup')}}</span>
         </a>
      </li>
      <li>
         <a href="/hosts/templates">
            <span class="fa fa-fw fa-server"></span>
            <span>{{_('Create a new host')}}</span>
         </a>
      </li>

      %if object_plugin and object_plugin.table['_table']['editable']:
         <li class="divider"></li>
         %if not '_form' in request.urlparts.path:
         <li>
            <a href="{{ request.urlparts.path.replace(object_plugin.backend_endpoint, object_plugin.backend_endpoint + '_form') }}">
               <span class="fa fa-fw fa-edit"></span>
               <span>{{_('Edit this %s') % object_plugin.backend_endpoint}}</span>
            </a>
         </li>
         %else:
         <li>
            <a href="{{ request.urlparts.path.replace('_form', '') }}">
               <span class="fa fa-fw fa-square-o"></span>
               <span>{{_('View this %s') % object_plugin.backend_endpoint}}</span>
            </a>
         </li>
         %end
         %if '/host/' in request.urlparts.path:
         <li>
            <a href="/service_form/None">
               <span class="fa fa-fw fa-edit"></span>
               <span>{{_('Declare a new service for this host')}}</span>
            </a>
         </li>
         %end
      %end

      <li class="divider"></li>

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
