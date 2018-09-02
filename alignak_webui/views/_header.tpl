%setdefault('debug', False)

<script type="text/javascript">
   // Check header refresh period (seconds)
   var header_refresh_period = {{request.app.config.get('%s.header_refresh_period' % webui.name, '30')}};

   // Periodical header refresh ... this function is called by the global refresh handler.
   function header_refresh() {
      $.ajax({
         url: "/ping?action=refresh&template=_header_states"
      })
      .done(function(content, textStatus, jqXHR) {
         $('#_header_states').html(content);
      });
   }

   $(document).ready(function(){
      // Start refresh periodical check ... every header_refresh_period second
      if (header_refresh_period != 0) {
         setInterval("header_refresh();", header_refresh_period*1000);
      } else {
         console.log('Automatic header refresh disabled.');
         $('#overall-hosts-states').addClass('disabled text-muted');
         $('#overall-services-states').addClass('disabled text-muted');
      }
   });
</script>

<!-- Page header -->
<header>
   <nav id="topbar" class="navbar navbar-fixed-top">
      <div class="navbar-header">
         <button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#navbar-collapsible-part">
            <span class="sr-only">{{_('Toggle navigation')}}</span>
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
         </button>
         <a class="navbar-brand" href="/">
            <img
               src="{{request.app.config.get('app_logo', '/static/images/alignak_white_logo.png')}}"
               style="{{request.app.config.get('app_logo_css', '')}}"
               alt="{{_('Alignak WebUI logo')}}"
               title="{{request.app.config.get('app_logo_title', _('Alignak Web User Interface'))}}" />
         </a>

         <ul class="nav navbar-nav navbar-left" id="_header_states">
            %include("_header_states.tpl")
         </ul>
      </div>

      <!-- Right part ... -->
      <div id="navbar-collapsible-part" class="collapse navbar-collapse">
         %if current_user.skill_level > 0:
         %include("_menubar.tpl")
         %else:
         %include("_menubar_beginner.tpl")
         %end

         <ul class="nav navbar-nav navbar-left">
            <li class="hidden-xs" id="loading" style="display: none;">
               <a href="#">
                  <span class="fa fa-spinner fa-pulse fa-1x"></span>
                  <span class="sr-only">{{_('Loading...')}}</span>
               </a>
            </li>
         </ul>

         <ul class="nav navbar-nav navbar-right">
            %try:
            <li>
               <a data-action="display-currently"
                  data-toggle="tooltip" data-placement="bottom"
                  title="{{_('Display fullscreen one-eye view.')}}"
                  href="/currently">
                  <span class="fa fa-eye"></span>
               </a>
            </li>
            %except RouteBuildError:
            %print("Missing plugin Currently")
            %end

            %if request.app.config.get('play_sound', 'no') == 'yes':
            <li id="sound_alerting">
               <a data-action="toggle-sound-alert"
                  data-toggle="tooltip" data-placement="bottom"
                  title="{{_('Sound alert on/off')}}"
                  href="#">
                  <span class="fa fa-music"></span>
                  <span class="sr-only">{{_('Change sound playing state')}}</span>
               </a>
            </li>
            %end

            %if refresh:
            <li id="refresh_active">
               <a data-action="toggle-page-refresh"
                  data-toggle="tooltip" data-placement="bottom"
                  title="{{_('Refresh page every %d seconds.') % (int(request.app.config.get('refresh_period', '60')))}}"
                  href="#">
                  <span class="fa fa-refresh"></span>
                  <span class="sr-only">{{_('Change page refresh state')}}</span>
               </a>
            </li>
            %end

            %include("_header_user.tpl")
         </ul>
      </div>
   </nav>
</header>

%if request.app.config.get('play_sound', 'no') == 'yes':
   %include("_sound_play.tpl")
%end
