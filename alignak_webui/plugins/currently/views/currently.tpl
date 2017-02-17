%from bottle import request

%setdefault('refresh', True)
%rebase("fullscreen", css=[], js=[], title=title)

%import json

<style>
div.pull-right a, div.pull-right div {
   margin-top: 0px; margin-bottom: 0px;
}
.hosts-count, .services-count {
   font-size: 24px;
}
.hosts-state, .services-state {
   font-size: 12px;
}
</style>

<div id="currently">
    <script type="text/javascript">
        // Application globals
        dashboard_currently = true;

        // Panels user's preferences
        panels = {{ ! json.dumps(panels) }};
    </script>

    <nav id="topbar" class="navbar navbar-fixed-top">
       <div id="one-eye-toolbar" class="col-xs-12">
          <ul class="nav navbar-nav navbar-left">
             <li>
                <a tabindex="0" role="button"
                   data-toggle="tooltip" data-placement="bottom"
                   title="{{_('Go back to the dashboard')}}" href="/dashboard">
                   <span class="fa fa-home"></span>
                   <span class="sr-only">{{_('Go back to the main dashboard')}}</span>
                </a>
             </li>
             <li>
                <a tabindex="0" role="button"
                   data-action="fullscreen-request"
                   data-toggle="tooltip" data-placement="bottom"
                   title="{{_('Fullscreen page')}}" href="#">
                   <span class="fa fa-desktop"></span>
                   <span class="sr-only">{{_('Fullscreen page')}}</span>
                </a>
             </li>
             %if request.app.config.get('play_sound', 'no') == 'yes':
             <li id="sound_alerting">
                <a tabindex="0" role="button"
                   data-action="toggle-sound-alert"
                   data-toggle="tooltip" data-placement="bottom"
                   title="{{_('Sound alert on/off')}}" href="#">
                   <span class="fa fa-music"></span>
                   <span class="sr-only">{{_('Change sound playing state')}}</span>
                </a>
             </li>
             %end
          </ul>

          <ul class="nav navbar-nav navbar-right">
             <li>
                <p class="navbar-text font-darkgrey">
                   <span id="date"></span>&nbsp;&hyphen;&nbsp;<span id="clock"></span>
                </p>
             </li>
          </ul>
       </div>
    </nav>

    %if request.app.config.get('play_sound', 'no') == 'yes':
       %include("_sound_play.tpl")
    %end

    <div class="row" style="margin-top:60px;">
        <div id="one-eye-hosts-counters" class="col-xs-12 col-md-6">
          {{! panel_counters_hosts }}
        </div>
        <div id="one-eye-services-counters" class="col-xs-12 col-md-6">
          {{! panel_counters_services }}
        </div>

        <div id="one-eye-hosts-percentages" class="col-xs-12 col-md-6">
          {{! panel_percentage_hosts }}
        </div>
        <div id="one-eye-services-percentages" class="col-xs-12 col-md-6">
          {{! panel_percentage_services }}
        </div>
    </div>

    <div class="row" style="margin-top:60px;">
        <div id="livestate" class="col-xs-12">
        </div>
    </div>

    <div class="row" style="margin-top:60px;">
        <div id="livestate-graphs" class="col-xs-12">
        </div>
    </div>

    <script type="text/javascript">
        // Function called on each page refresh ... update graphs!
        function on_page_refresh(forced) {
        };

        $(document).ready(function(){
            on_page_refresh();

            // Date / time
            $('#clock').jclock({ format: '%H:%M:%S' });
            $('#date').jclock({ format: '%A, %B %d' });

            // Fullscreen management
            if (screenfull.enabled) {
                $('a[data-action="fullscreen-request"]').on('click', function() {
                    screenfull.request();
                });

                // Fullscreen changed event
                document.addEventListener(screenfull.raw.fullscreenchange, function () {
                    if (screenfull.isFullscreen) {
                        $('a[data-action="fullscreen-request"]').hide();
                    } else {
                        $('a[data-action="fullscreen-request"]').show();
                    }
                });
            }
        });

        // Panels collapse state
        $('.panel').on('hidden.bs.collapse', function () {
            wait_message('{{_('Saving configuration...')}}', true)

            panels[$(this).parent().attr('id')].collapsed = true;
            $(this).find('.fa-caret-up').removeClass('fa-caret-up').addClass('fa-caret-down');
            save_user_preference('panels', JSON.stringify(panels), function() {
                wait_message('', false)
                // Page refresh required
                refresh_required = true;
            });
        });
        $('.panel').on('shown.bs.collapse', function () {
            wait_message('{{_('Saving configuration...')}}', true)

            panels[$(this).parent().attr('id')].collapsed = false;
            $(this).find('.fa-caret-down').removeClass('fa-caret-down').addClass('fa-caret-up');
            save_user_preference('panels', JSON.stringify(panels), function() {
                wait_message('', false)
                // Page refresh required
                refresh_required = true;
            });
        });
    </script>

    <script type="text/javascript">
       var bi;
       for (bi = 5; bi >= 0; --bi) {
          // Request to update each possible Business impact ...
          $.ajax({
             url: "/livestate",
             data: {
                "bi": bi,
                "search": null
             },
             method: "get",
             dataType: "json"
          })
          .done(function(html, textStatus, jqXHR) {
             if (refresh_logs) console.debug("Livestate:", html);
             /*
              * Update page header : live synthesis
              */
             if (! html['livestate']) {
                if (refresh_logs) console.error("Bad data received, expected : html['livestate']");
                return
             }

             var bi = parseInt(html['livestate']['bi']);
             var rows = html['livestate']['rows'];
             if (! rows.length) {
                if (refresh_logs) console.debug("No data for BI:", bi);
                return
             }
             if (refresh_logs) console.debug("Received Livestate for BI:", bi);

             if (! $('#livestate-bi-'+bi).length) {
                $('#livestate').append(html['livestate']['panel_bi']);

                // Update table rows ...
                $.each(html['livestate']['rows'], function( index, value ) {
                   // Update table rows
                   $('#livestate-bi-'+bi+' table tbody').append(value);
                });
             } else {
                $('#livestate-bi-'+bi).hide(1000, function() {
                   // Replace existing panel ...
                   $('#livestate-bi-'+bi).replaceWith(html['livestate']['panel_bi']);

                   // Update table rows ...
                   $.each(html['livestate']['rows'], function( index, value ) {
                      // Update table rows
                      $('#livestate-bi-'+bi+' table tbody').append(value);
                   });

                   $('#livestate-bi-'+bi).show(500);
                });
             }
          });
       }
    </script>
</div>