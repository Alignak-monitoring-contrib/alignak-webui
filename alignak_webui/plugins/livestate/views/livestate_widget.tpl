<!-- Livestate table widget -->
%# embedded is True if the widget is got from an external application
%setdefault('embedded', False)
%from bottle import request
%setdefault('links', request.params.get('links', ''))
%setdefault('identifier', 'widget')
%setdefault('credentials', None)

%setdefault('ls',  None)

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

<div id="livestate_widget">
    <div id="livestate-bi--1">
    </div>

    <script type="text/javascript">
        var debug_logs = false;

        // Function called on each page refresh ... update elements!
        function on_page_refresh(forced) {
            if (debug_logs) console.debug("livestate,  on_page_refresh",  forced);

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
        };

        $(document).ready(function(){
            on_page_refresh();
        });
    </script>
</div>