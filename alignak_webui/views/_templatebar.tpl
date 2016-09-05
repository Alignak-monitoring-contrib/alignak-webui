%setdefault('templates_bar', False)

<!-- Templates actions bar -->
<li class="dropdown" data-toggle="tooltip" data-placement="bottom" title="{{_('Edition mode')}}">
   <a class="navbar-link" href="#" class="dropdown-toggle" data-toggle="dropdown">
      <span class="caret hidden-xs"></span>
      <span class="fa fa-clone"></span>
      <span class="sr-only">{{_('Edition')}}</span>
   </a>

   <ul class="dropdown-menu" role="menu" aria-labelledby="{{_('Edition mode menu')}}">
      <li data-toggle="tooltip" data-placement="bottom" title="{{_('Hosts templates')}}">
         <a href="{{ webui.get_url('Hosts templates') }}">
            <span class="fa fa-fw fa-server"></span>
            <span>{{_('Hosts templates')}}</span>
         </a>
      </li>
   </ul>
</li>
