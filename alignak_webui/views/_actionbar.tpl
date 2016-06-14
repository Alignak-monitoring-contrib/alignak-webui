%setdefault('in_sidebar', False)

<!-- Dashboard actions bar -->
%if not in_sidebar:
<nav id="actionbar-menu" class="navbar navbar-default" >
   <ul class="nav navbar-nav navbar-left">
%end
      <li class="dropdown" data-toggle="tooltip" data-placement="right" title="{{_('Add a new widget')}}">
         <a class="navbar-link" href="#" class="dropdown-toggle" data-toggle="dropdown">
            <span class="caret"></span>
            <span class="fa fa-leaf"></span>
            <span class="hidden-sm hidden-xs">{{_('Add a new widget')}}</span>
         </a>

         <ul class="dropdown-menu" role="menu" aria-labelledby="Widgets bar menu">
            %for widget in webui.get_widgets_for('dashboard'):
            <li>
               <a href="#"
                  class="dashboard-widget"
                  data-widget-title="
                      <button href='#' role='button'
                          data-action='add-widget'
                          data-widget-id='{{widget['id']}}'
                          data-widget-name='{{widget['name']}}'
                          data-widget-template='{{widget['template']}}'
                          data-widget-uri='{{widget['base_uri']}}'
                          class='btn btn-sm btn-success'>
                          <span class='fa fa-plus'></span>
                          {{_('Add this widget to your dashboard')}}
                      </button>"
                  data-widget-description='{{!widget["description"]}} <hr/> <div class="center-block"><img class="text-center" src="{{widget["picture"]}}"/></div>'
                  >
                  <span class="fa fa-{{widget['icon']}}"></span>
                  {{widget['name']}}
               </a>
            </li>
            %end
         </ul>
      </li>
%if not in_sidebar:
   </ul>
</nav>
%end