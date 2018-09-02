%from bottle import request

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

    %if request.app.config.get('play_sound', 'no') == 'yes':
       %include("_sound_play.tpl")
    %end

    <div class="row">
        <div id="one-eye-hosts" class="col-xs-12 col-md-6">
          {{! panel_hosts }}
        </div>
        <div id="one-eye-services" class="col-xs-12 col-md-6">
          {{! panel_services }}
        </div>
    </div>

    <div class="row">
        <div id="ls-history-hosts" class="col-xs-12">
            {{! panel_ls_history_hosts }}
        </div>
        <div id="ls-history-services" class="col-xs-12">
            {{! panel_ls_history_services}}
        </div>
    </div>

    <script type="text/javascript">
        var debug_logs = false;

        // Function called on each page refresh...
        function on_page_refresh(forced) {
        };

        $(document).ready(function() {
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
        $('.panel').on('hidden.bs.collapse', function (e) {
            if (debug_logs) console.debug("Hide:", $(this).attr('id'));

            wait_message('{{_('Saving configuration...')}}', true)

            try {
                panels[$(this).attr('id')].collapsed = true;
            } catch(e) {
                panels[$(this).attr('id')] = {'collapsed': true}
            }
            $(this).find('.fa-caret-down').removeClass('fa-caret-down').addClass('fa-caret-up');
            save_user_preference('panels', JSON.stringify(panels), function() {
                wait_message('', false)
            });
        });
        $('.panel').on('shown.bs.collapse', function (e) {
            if (debug_logs) console.debug("Show:", $(this).attr('id'));

            wait_message('{{_('Saving configuration...')}}', true)

            try {
                panels[$(this).attr('id')].collapsed = false;
            } catch(e) {
                panels[$(this).attr('id')] = {'collapsed': false}
            }
            $(this).find('.fa-caret-up').removeClass('fa-caret-up').addClass('fa-caret-down');
            save_user_preference('panels', JSON.stringify(panels), function() {
                wait_message('', false)
            });
        });

        // Panels legend toggle
        $('[data-action="toggle-legend"]').on('click', function (e) {
            if (debug_logs) console.debug("Toggle legend:", $(this).attr('id'));

            wait_message('{{_('Saving configuration...')}}', true)

            if (dashboard_logs) console.debug('Toggle legend', graphs[$(this).data('graph')]);
            graphs[$(this).data('graph')]['display_states'][$(this).data('state')] = ! graphs[$(this).data('graph')]['display_states'][$(this).data('state')];
            if (graphs[$(this).data('graph')].legend) {
                $(this).children('i').show();
            } else {
                $(this).children('i').hide();
            }
            save_user_preference('currently_graphs', JSON.stringify(graphs), function() {
                wait_message('', false)
            });
        });
    </script>
</div>