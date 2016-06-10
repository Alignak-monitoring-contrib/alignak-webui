%debug=False

%# Fetch page count preference for user, default is 25
%elts_per_page = datamgr.get_user_preferences(username, 'elts_per_page', 25)

<script type="text/javascript">
   // Check header refresh period (seconds)
   var header_refresh_period = 10;

   // Periodical header refresh ... this function is called by the global refresh handler.
   function header_refresh() {
      $.ajax({
         url: "/ping?action=refresh&template=_header_hosts_state"
      })
      .done(function(content, textStatus, jqXHR) {
         $('#overall-hosts-states').html(content);
      });

      $.ajax({
         url: "/ping?action=refresh&template=_header_services_state"
      })
      .done(function(content, textStatus, jqXHR) {
         $('#overall-services-states').html(content);
      });
   }

   $(document).ready(function(){
      // Start refresh periodical check ... every header_refresh_period second
      // header_refresh_period is defined in alignak_webui_refresh.js
      setInterval("header_refresh();", header_refresh_period*1000);
   });
</script>


<!-- Page header -->
<header>
   <nav id="topbar-menu" class="navbar navbar-default navbar-fixed-top">
      <div class="container-fluid">
         <div class="navbar-header">
            <button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#navbar-collapsible-part">
               <span class="sr-only">{{_('Toggle navigation')}}</span>
               <span class="icon-bar"></span>
               <span class="icon-bar"></span>
               <span class="icon-bar"></span>
            </button>
            <a class="navbar-brand" href="/">
               <img src="/static/images/{{request.app.config.get('company_logo', 'default_company.png')}}" alt="{{_('Company logo')}}" />
            </a>
         </div>

         <!-- Right part ... -->
         <div id="navbar-collapsible-part" class="collapse navbar-collapse">
            <div class="hidden-xs">
               <!-- Page filtering ... -->
               %include("_filters.tpl")
            </div>

            <ul class="nav navbar-nav navbar-right">
               <li id="overall-hosts-states">
                  %include("_header_hosts_state.tpl")
               </li>

               <li id="overall-services-states">
                  %include("_header_services_state.tpl")
               </li>

               <li>
                  <a data-action="display-currently" data-toggle="tooltip" data-placement="bottom" title="{{_('Display fullscreen one-eye view.')}}" href="/currently">
                     <span class="fa fa-eye"></span>
                  </a>
               </li>

               %if request.app.config.get('play_sound', 'no') == 'yes':
               <li class="hidden-xs">
                  <a data-action="toggle-sound-alert" data-toggle="tooltip" data-placement="bottom" title="{{_('Sound alert on/off')}}" href="#">
                     <span id="sound_alerting" class="fa-stack" style="margin-top: -4px">
                       <i class="fa fa-music fa-stack-1x"></i>
                       <i class="fa fa-ban fa-stack-2x text-danger"></i>
                     </span>
                  </a>
               </li>
               %end

               %if refresh:
               <li>
                  <a data-action="toggle-page-refresh" data-toggle="tooltip" data-placement="bottom" title="{{_('Refresh page every %d seconds.') % (int(request.app.config.get('refresh_period', '60')))}}" href="#">
                     <span id="header_loading" class="fa fa-refresh"></span>
                  </a>
               </li>
               %end

               %if debug:
               <li class="dropdown">
                  <a href="#" class="dropdown-toggle" data-original-title="Debug" data-toggle="dropdown">
                     <span class="fa fa-bug"></span>
                     <span class="caret"></span>
                  </a>
                  <ul class="dropdown-menu">
                     <li>
                        <div class="panel panel-default">
                           <div class="panel-body">
                              <ul class="list-group">
                                 <li class="list-group-item"><small>Current user: {{current_user}}</small></li>
                                 <li class="list-group-item"><small>Target user: {{target_user}}</small></li>
                              </ul>
                              <div class="panel-footer">Total: {{datamgr.get_objects_count('user')}} users</div>
                           </div>
                        </div>
                     </li>
                  </ul>
               </li>
               %end

               <!-- User info -->
               <li class="dropdown user user-menu hidden-xs">
                  <a href="#" class="dropdown-toggle" data-original-title="{{_('User menu')}}" data-toggle="dropdown">
                     <i class="fa fa-user"></i>
                        %if request.app.config.get('target_user', 'no') == 'yes':
                        %if not target_user.is_anonymous() and current_user.get_username() != target_user.get_username():
                        <span class="label label-warning" style="position:relative; left: 0px">{{target_user.get_username()}}</span>
                        %end
                        %end
                        <span class="username hidden-sm hidden-xs hidden-md">{{current_user.name}}</span>
                        <i class="caret"></i>
                  </a>

                  <ul class="dropdown-menu">
                     %if request.app.config.get('target_user', 'no') == 'yes':
                     <li class="user-header">
                        %include("_select_target_user")
                     </li>
                     %end
                     <li class="user-header">
                        <div class="panel panel-info" id="user_info">
                           <div class="panel-body panel-default">
                              <!-- User image / name -->
                              <p class="username">{{current_user.name}}</p>
                              <p class="usercategory">
                                 <small>{{current_user.get_role(display=True)}}</small>
                              </p>
                              <img src="{{current_user.picture}}" class="img-circle user-logo" alt="{{_('Photo: %s') % current_user.name}}" title="{{_('Photo: %s') % current_user.name}}">
                           </div>
                           <div class="panel-footer">
                              <div class="btn-group" role="group">
                                 <a class="btn btn-default" href="#"
                                    data-action="about-box"
                                    title="{{_('Display application information')}}"
                                    >
                                    <span class="fa fa-question"></span>
                                 </a>
                                 %if current_user.is_administrator():
                                 <a class="btn btn-default" href="/preferences/user"
                                    title="{{_('Show all the stored user preferences')}}">
                                    <span class="fa fa-pencil"></span>
                                 </a>
                                 %end
                                 <a class="btn btn-default" href="/logout"
                                    title="{{_('Disconnect from the application')}}">
                                    <span class="fa fa-sign-out"></span>
                                 </a>
                              </div>
                           </div>
                        </div>
                     </li>
                  </ul>
               </li>
               <li class="col-xs-1 hidden-sm hidden-md hidden-lg">
                  <a data-action="logout"
                     data-toggle="tooltip" data-placement="bottom" title="{{_('Sign out')}}"
                     href="/logout">
                     <i class="fa fa-sign-out"></i>
                  </a>
               </li>
            </ul>

            <div class="col-xs-10 col-sm-offset-1 col-sm-10 hidden-md hidden-lg">
               <!-- Sidebar menu is included in the header for small devices -->
               %include("_sidebar.tpl", action_bar=True, in_sidebar=True)
            </div>
         </div>
      </div>
   </nav>
</header>


%if request.app.config.get('play_sound', 'no') == 'yes':
   <audio id="alert-sound" volume="1.0">
      <source src="/static/sound/alert.wav" type="audio/wav">
      Your browser does not support the <code>HTML5 Audio</code> element.
      <EMBED src="/static/sound/alert.wav" autostart=true loop=false volume=100 >
   </audio>

   <script type="text/javascript">
      get_user_preference('sound', function(data) {
         // Toggle sound icon...
         if (data.value == 'no') {
            sound_activated = false;
            $('#sound_alerting i.fa-ban').addClass('hidden');
         } else {
            sound_activated = true;
            $('#sound_alerting i.fa-ban').removeClass('hidden');
         }
         $('[data-action="toggle-sound-alert"]').on('click', function (e, data) {
            get_user_preference('sound', function(data) {
               if (data.value == 'no') {
                  save_user_preference('sound', JSON.stringify('yes'), function(){
                     sound_activated = false;
                     $('#sound_alerting i.fa-ban').removeClass('hidden');
                  });
               } else {
                  save_user_preference('sound', JSON.stringify('no'), function() {
                     sound_activated = true;
                     playAlertSound();
                     $('#sound_alerting i.fa-ban').addClass('hidden');
                  });
               }
            });
         });
      }, 'yes');
   </script>
%end
