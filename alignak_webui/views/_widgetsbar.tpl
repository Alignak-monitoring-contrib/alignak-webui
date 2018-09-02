%setdefault('debug', False)
%setdefault('debug_host', False)

%import json

<!-- Dashboard widgets bar -->
<li class="dropdown" data-toggle="tooltip" data-placement="bottom" title="{{_('Add a new widget')}}">
   <a class="navbar-link" href="#" class="dropdown-toggle" data-toggle="dropdown">
      <span class="caret hidden-xs"></span>
      <span class="fa fa-w fa-plug"></span>
      <span class="sr-only">{{_('Widgets')}}</span>
   </a>

   <ul class="dropdown-menu" role="menu" aria-labelledby="{{_('Widgets menu')}}">
      %for widget in webui.get_widgets_for('dashboard'):
      <li>
         <a href="#"
            class="dashboard-widget"
            data-widget-title="
                <button href='#' role='button'
                    data-action='add-widget'
                    data-widget-id='{{widget['id']}}'
                    data-widget-for='dashboard'
                    data-widget-name='{{widget['name']}}'
                    data-widget-template='{{widget['template']}}'
                    data-widget-icon='{{widget['icon']}}'
                    data-widget-picture='{{widget['picture']}}'
                    data-widget-uri='{{widget['base_uri']}}'
                    data-widget-options='{{json.dumps(widget['options'])}}'
                    class='btn btn-sm btn-success btn-raised'>
                    <span class='fa fa-plus'></span>
                    {{_('Add this widget to your dashboard')}}
                </button>"
            data-widget-description='{{!widget["description"]}} <hr/> <div class="center-block"><img style="max-width: 100%;" class="text-center" src="{{widget["picture"]}}"/></div>'
            >
            <span class="fa fa-{{widget['icon']}}"></span>
            {{widget['name']}}
         </a>
      </li>
      %end
   </ul>
</li>

%if debug:
   <li class="dropdown" data-toggle="tooltip" data-placement="right" title="{{_('External widgets')}}">
      <a class="navbar-link" href="#" class="dropdown-toggle" data-toggle="dropdown">
         <span class="caret"></span>
         <span class="fa fa-bug"></span>
         <span class="hidden-sm hidden-xs">{{_('External widgets')}}</span>
      </a>

      <ul class="dropdown-menu" role="menu">
         %for widget in webui.get_widgets_for('external'):
         <li>
            <a href="/external/widget/{{widget['id']}}?page&widget_id={{widget['id']}}">
               <span class="fa fa-fw fa-{{widget['icon']}}"></span>
               {{widget['name']}} <em>(id: {{widget['id']}})</em>
            </a>
         </li>
         %end
      </ul>
   </li>
   %debug_host = datamgr.get_host({'name': 'webui'})
   %if debug_host:
   <li class="dropdown" data-toggle="tooltip" data-placement="right" title="{{_('Hosts widgets')}}">
      <a class="navbar-link" href="#" class="dropdown-toggle" data-toggle="dropdown">
         <span class="caret"></span>
         <span class="fa fa-bug"></span>
         <span class="hidden-sm hidden-xs">{{_('Hosts widgets')}}</span>
      </a>

      <ul class="dropdown-menu" role="menu">
         %for widget in webui.get_widgets_for('host'):
         <li>
            <a href="/external/host/{{debug_host.id}}/{{widget['id']}}?page">
               <span class="fa fa-fw fa-{{widget['icon']}}"></span>
               {{widget['name']}} <em>(id: {{widget['id']}})</em>
            </a>
         </li>
         %end
      </ul>
   </li>
   %end
   <li class="dropdown" data-toggle="tooltip" data-placement="right" title="{{_('External tables')}}">
      <a class="navbar-link" href="#" class="dropdown-toggle" data-toggle="dropdown">
         <span class="caret"></span>
         <span class="fa fa-bug"></span>
         <span class="hidden-sm hidden-xs">{{_('External tables')}}</span>
      </a>

      <ul class="dropdown-menu" role="menu">
         %for table in webui.get_tables_for('external'):
         <li>
            <a href="/external/table/{{table['id']}}?page&table_id={{table['id']}}">
               <span class="fa fa-fw fa-{{table['icon']}}"></span>
               {{table['name']}} <em>(id: {{table['id']}})</em>
            </a>
         </li>
         %end
      </ul>
   </li>
%end
