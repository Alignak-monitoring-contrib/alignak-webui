%setdefault('debug', False)
%setdefault('edition_mode', True)

%if debug:
<li class="dropdown">
   <a href="#" class="dropdown-toggle" data-original-title="Debug" data-toggle="dropdown">
      <span class="caret"></span>
      <span class="fa fa-bug"></span>
   </a>
   <ul class="dropdown-menu">
      <li>
         <div class="panel panel-default">
            <div class="panel-body">
               <ul class="list-group">
                  <li class="list-group-item"><small>Current user: {{current_user}}</small></li>
               </ul>
               <div class="panel-footer">Total: {{datamgr.get_objects_count('user')}} users</div>
            </div>
         </div>
      </li>
   </ul>
</li>
%end

<!-- User info -->
<li class="dropdown user user-menu" data-toggle="tooltip" data-placement="bottom" title="{{_('User')}}">
   <a href="#" class="dropdown-toggle" data-toggle="dropdown">
      <span class="caret"></span>
      <span class="fa fa-user"></span>
      <span class="username hidden-sm hidden-xs hidden-md">{{current_user.name}}</span>
      <span class="sr-only">{{_('User menu')}}</span>
   </a>

   <ul class="dropdown-menu" role="menu" aria-labelledby="{{_('User menu')}}">
      <li class="user-header hidden-xs hidden-sm">
         <div class="panel panel-default">
            <div class="panel-body">
               <!-- User image / name -->
               <p class="username">{{current_user.alias}}</p>
               <p class="usercategory">
                  <small>{{current_user.get_role(display=True)}}</small>
               </p>
               <img src="{{current_user.picture}}" class="img-circle user-logo" alt="{{_('Photo: %s') % current_user.name}}" title="{{_('Photo: %s') % current_user.name}}">
            </div>
         </div>
      </li>

      <li>
         <a href="/preferences/user" data-action="user-preferences" >
            <span class="fa fa-pencil"></span>
            <span>{{_('User preferences')}}</span>
         </a>
      </li>

      %if current_user.is_power():
      <li>
         %if edition_mode:
         <a href="#" data-action="edition-mode" data-state="on">
            <span class="text-warning fa fa-edit"></span>
            <span>{{_('Leave edition mode')}}</span>
         </a>
         %else:
         <a href="#" data-action="edition-mode" data-state="off">
            <span class="text-danger fa fa-edit"></span>
            <span>{{_('Enter edition mode')}}</span>
         </a>
         %end
      </li>
      <li class="divider">
      </li>
      %end

      <li>
         <a href="#" data-action="about-box">
            <span class="fa fa-question"></span>
            <span>{{_('About...')}}</span>
         </a>
      </li>
      <li>
         <a data-action="logout" href="/logout">
            <span class="fa fa-sign-out"></span>
            <span>{{_('Disconnect')}}</span>
         </a>
      </li>
   </ul>
</li>

