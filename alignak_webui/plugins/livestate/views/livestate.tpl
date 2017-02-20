%setdefault('ls', None)
%from bottle import request

%setdefault('refresh', True)
%rebase("fullscreen", css=[], js=[], title=title)

%import json

<style>
    div.livestate-panel div.panel-heading{
        font-size: 1.5rem;
    }


    div[data-type="actions"] {
        margin: 0px;
    }

    div[data-type="actions"] ul.dropdown-menu {
        opacity: 1;
        background-color: light-grey;
    }

    div.pull-right a, div.pull-right div {
       margin-top: 0px; margin-bottom: 0px;
    }
</style>

<div id="livestate">
    <script type="text/javascript">
        // Panels user's preferences
        panels = {{ ! json.dumps(panels) }};
    </script>

    %if request.app.config.get('play_sound', 'no') == 'yes':
       %include("_sound_play.tpl")
    %end

    %include("_problems_synthesis.tpl", ls=ls)

    <div id="livestate-bi-5"></div>
    <div id="livestate-bi-4"></div>
    <div id="livestate-bi-3"></div>
    <div id="livestate-bi-2"></div>
    <div id="livestate-bi-1"></div>
    <div id="livestate-bi-0"></div>

    <script type="text/javascript">
        var debug_logs = true;
        
        // Function called on each page refresh ... update elements!
        function on_page_refresh(forced) {
            if (debug_logs) console.debug("livestate, on_page_refresh", forced);

            for (var bi = 5; bi >= 0; --bi) {
                // Request to update each possible Business impact ...
                if (debug_logs) console.debug("livestate, request Livestate for BI:", bi);
                $.ajax({
                    url: "/bi-livestate",
                    data: {
                        "bi": bi,
                        "search": null
                    },
                    method: "get",
                    dataType: "json"
                })
                .done(function(html, textStatus, jqXHR) {
                    /*
                        * Update page livestate
                    */

                    if (! html['livestate']) {
                        if (debug_logs) console.error("Bad data received, expected : html['livestate']");
                        return;
                    }

                    var bi = parseInt(html['livestate']['bi']);
                    var rows = html['livestate']['rows'];
                    /* Uncomment to filter the empty panels
                    if (! rows.length) {
                        if (debug_logs) console.debug("livestate, no data for BI:", bi);
                        return
                    }
                    */
                    if (debug_logs) console.debug("Received Livestate for BI:", bi);

                    if (! $('#livestate-bi-'+bi).length) {
                        if (debug_logs) console.debug("livestate, creating livestate panel for BI:", bi);
                        $('#livestate').append(html['livestate']['panel_bi']);

                        // Update table rows ...
                        $.each(html['livestate']['rows'], function( index, value ) {
                            // Update table rows
                            $('#livestate-bi-'+bi+' table tbody').append(value);
                        });
                    } else {
                        if (debug_logs) console.debug("livestate, updating livestate panel for BI:", bi);
                        $('#livestate-bi-'+bi).hide(function() {
                            // Replace existing panel ...
                            $('#livestate-bi-'+bi).replaceWith(html['livestate']['panel_bi']);

                            // Update table rows ...
                            $.each(html['livestate']['rows'], function( index, value ) {
                                // Update table rows
                                $('#livestate-bi-'+bi+' table tbody').append(value);
                            });

                            //$('#livestate-bi-'+bi).show(500);
                            $('#livestate-bi-'+bi);
                        });
                    }
                });
            }
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

                        %if current_user.is_power():
                        $('div[data-type="actions"]').each(function (index, child) {
                            if (debug_logs) console.debug("Hiding actions buttons...");
                            $(this).hide();
                        });
                        %end
                    } else {
                        $('a[data-action="fullscreen-request"]').show();

                        %if current_user.is_power():
                        $('div[data-type="actions"]').each(function (index, child) {
                            if (debug_logs) console.debug("Hiding actions buttons...");
                            $(this).show();
                        });
                        %end
                    }
                });
            }
        });

        // Panels collapse state
        $('#livestate').on('hidden.bs.collapse', 'div.livestate-panel', function (e) {
            if (debug_logs) console.debug("Hide:", $(this).attr('id'));
            /*
            if (e.target !== this)
                return;
            */
            wait_message('{{_('Saving configuration...')}}', true)

            try {
                panels[$(this).attr('id')].collapsed = true;
            } catch(e) {
                panels[$(this).attr('id')] = {'collapsed': true}
            }
            $(this).find('.fa-caret-down').removeClass('fa-caret-down').addClass('fa-caret-up');
            save_user_preference('livestate', JSON.stringify(panels), function() {
                wait_message('', false)
                // Page refresh required
                // refresh_required = true;
            });
        });
        $('#livestate').on('shown.bs.collapse', 'div.livestate-panel', function (e) {
            if (debug_logs) console.debug("Show:", $(this).attr('id'));
            /*
            if (e.target !== this)
                return;
            */

            wait_message('{{_('Saving configuration...')}}', true)

            try {
                panels[$(this).attr('id')].collapsed = false;
            } catch(e) {
                panels[$(this).attr('id')] = {'collapsed': false}
            }
            $(this).find('.fa-caret-up').removeClass('fa-caret-up').addClass('fa-caret-down');
            save_user_preference('livestate', JSON.stringify(panels), function() {
                wait_message('', false)
                // Page refresh required
                // refresh_required = true;
            });
        });
    </script>
</div>