%setdefault('debug', True)
%setdefault('in_sidebar', False)

<!-- Templates actions bar -->
%if not in_sidebar:
<nav id="templatebar-menu" class="navbar navbar-default" >
   <ul class="nav navbar-nav navbar-left">
%end
      <li class="{{'dropdown' if in_sidebar else 'dropup'}}" data-toggle="tooltip" data-placement="right" title="{{_('Edition mode')}}">
         <a class="navbar-link" href="#" class="dropdown-toggle" data-toggle="dropdown">
            <span class="caret"></span>
            <span class="fa fa-clone"></span>
            <span class="hidden-sm hidden-xs">{{_('Edition mode')}}</span>
         </a>

         <ul class="dropdown-menu" role="menu" aria-labelledby="{{_('Edition mode menu')}}">
            <li data-toggle="tooltip" data-placement="{{'bottom' if in_sidebar else 'right'}}" title="{{_('Hosts templates')}}">
               <a class="navbar-link" href="{{ webui.get_url('Hosts templates') }}">
                  <span class="fa fa-fw fa-server"></span>
                  <span>{{_('Hosts templates')}}</span>
               </a>
            </li>
         </ul>
      </li>

%if not in_sidebar:
   </ul>
</nav>
%end