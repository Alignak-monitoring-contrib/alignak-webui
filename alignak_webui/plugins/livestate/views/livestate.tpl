%setdefault('layout',  'table')
%setdefault('view_table',  True)
%setdefault('view_panels',  False)
%setdefault('view_tabs',  False)

%if layout.lower() == 'panels':
%view_table = False
%view_panels = True
%view_tabs = False
%end

%if layout.lower() == 'tabs':
%view_table = False
%view_panels = False
%view_tabs = True
%end

%setdefault('ls',  None)
%from bottle import request

%rebase("fullscreen",  css=[],  js=[],  title=title)

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

    div.pull-right a,  div.pull-right div {
       margin-top: 0px; margin-bottom: 0px;
    }
</style>

<div id="livestate">
    <script type="text/javascript">
        // Panels user's preferences
        panels = {{ ! json.dumps(panels) }};
    </script>

    %if request.app.config.get('play_sound',  'no') == 'yes':
       %include("_sound_play.tpl")
    %end

    %include("_problems_synthesis.tpl",  ls=ls)

    %if view_table:
        <div id="livestate-bi--1">
            <div class="alert alert-info text-center">
                <h2>
                    <span class="fa fa-spin fa-spinner"></span>
                    &nbsp;{{_("Fetching live state from the backend...")}}&nbsp;
                    <span class="fa fa-spin fa-spinner"></span>
                </h2>
            </div>
        </div>
    %end

    %if view_panels:
        %for index in [5, 4, 3, 2, 1, 0]:
            <div id="livestate-bi-{{index}}"> </div>
        %end
    %end

    %if view_tabs:
        <ul class="nav nav-tabs">
            %for index in [5, 4, 3, 2, 1, 0]:
            <li class="{{'active if index==0 else ''}}">
                <a href="#tab-bi-{{index}}" role="tab" data-toggle="tab" title="{{ index }}">
                    {{index}}&nbsp;<span class="fa fa-spin fa-spinner"></span>
                </a>
            </li>
            %end
        </ul>

        <div class="tab-content">
            %for index in [5, 4, 3, 2, 1, 0]:
            <div id="tab-bi-{{ index }}" class="tab-pane fade {{'active in' if index == 0 else ''}}" role="tabpanel">
                <div id="livestate-bi-{{index}}"></div>
            </div>
            %end
        </div>
    %end

    <script type="text/javascript">
        var debug_logs = false;

        // Function called on each page refresh ... update elements!
        function on_page_refresh(forced) {
            if (debug_logs) console.debug("livestate,  on_page_refresh",  forced);

            // Update problems synthesis
            $.ajax({
                url: "/ping?action=refresh&template=_problems_synthesis"
            })
            .done(function(content, textStatus, jqXHR) {
                $('#_header_states').html(content);
            });

            %if view_table:
                $.ajax({
                    url: "/bi-livestate",
                    data: {
                        "bi": -1,
                        "search": null
                    },
                    method: "get",
                    dataType: "json"
                })
                .done(function(html,  textStatus,  jqXHR) {
                    if (! html['livestate']) {
                        if (debug_logs) console.error("Bad data received,  expected : html['livestate']");
                        return;
                    }

                    var bi = parseInt(html['livestate']['bi']);
                    var rows = html['livestate']['rows'];
                    if (debug_logs) console.debug("Received Livestate for BI:",  bi);

                    if (debug_logs) console.debug("livestate,  updating livestate panel for BI:",  bi);
                    $('a[href="#tab-bi-'+ bi +'"]').html(html['livestate']['title']);

                    $('#livestate-bi-'+bi).hide(function() {
                        // Replace existing panel ...
                        $('#livestate-bi-'+bi).replaceWith(html['livestate']['panel_bi']);

                        $('#livestate-bi-'+bi).show(1000);

                        // Update table rows ...
                        $.each(html['livestate']['rows'],  function( index,  value ) {
                            // Update table rows
                            $('#livestate-bi-'+bi+' table tbody').append(value);
                        });
                    });
                });
            %end

            %if view_tabs or view_panels:
                for (var bi = 5; bi >= 0; --bi) {
                    // Request to update each possible Business impact ...
                    if (debug_logs) console.debug("livestate,  request Livestate for BI:",  bi);
                    $.ajax({
                        url: "/bi-livestate",
                        data: {
                            "bi": bi,
                            "search": null
                        },
                        method: "get",
                        dataType: "json"
                    })
                    .done(function(html,  textStatus,  jqXHR) {
                        if (! html['livestate']) {
                            if (debug_logs) console.error("Bad data received,  expected : html['livestate']");
                            return;
                        }

                        var bi = parseInt(html['livestate']['bi']);
                        var rows = html['livestate']['rows'];
                        if (debug_logs) console.debug("Received Livestate for BI:",  bi);

                        if (debug_logs) console.debug("livestate,  updating livestate panel for BI:",  bi);
                        %if view_tabs:
                        $('a[href="#tab-bi-'+ bi +'"]').html(html['livestate']['title']);
                        %end

                        $('#livestate-bi-'+bi).hide(function() {
                            // Replace existing panel ...
                            $('#livestate-bi-'+bi).replaceWith(html['livestate']['panel_bi']);

                            $('#livestate-bi-'+bi).show(500);

                            // Update table rows ...
                            $.each(html['livestate']['rows'],  function( index,  value ) {
                                // Update table rows
                                $('#livestate-bi-'+bi+' table tbody').append(value);
                            });
                        });
                    });
                }
            %end
        };

        $(document).ready(function(){
            on_page_refresh();

            // Date / time
            $('#clock').jclock({ format: '%H:%M:%S' });
            $('#date').jclock({ format: '%A,  %B %d' });

            %if message:
                raise_message_{{message.get('status', 'ko')}}("{{! message.get('message')}}");
            %end

            // Fullscreen management
            if (screenfull.enabled) {
                $('a[data-action="fullscreen-request"]').on('click',  function() {
                    screenfull.request();
                });

                // Fullscreen changed event
                document.addEventListener(screenfull.raw.fullscreenchange,  function () {
                    if (screenfull.isFullscreen) {
                        $('a[data-action="fullscreen-request"]').hide();

                        %if current_user.is_power():
                        $('div[data-type="actions"]').each(function (index,  child) {
                            if (debug_logs) console.debug("Hiding actions buttons...");
                            $(this).hide();
                        });
                        %end
                    } else {
                        $('a[data-action="fullscreen-request"]').show();

                        %if current_user.is_power():
                        $('div[data-type="actions"]').each(function (index,  child) {
                            if (debug_logs) console.debug("Hiding actions buttons...");
                            $(this).show();
                        });
                        %end
                    }
                });
            }
        });
    </script>
</div>