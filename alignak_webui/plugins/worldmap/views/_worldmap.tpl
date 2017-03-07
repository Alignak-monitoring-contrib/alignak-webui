%setdefault('load', False)

<script>
    %#Actions ?
    actions = {{ 'true' if current_user.is_power() else 'false' }};

    if (typeof debugMaps === 'undefined') debugMaps=false;

    function buildHosts() {
        // hosts is a global var defined in worldmaps.js
        %# List hosts and their services
        hosts = [
        %for host in hosts:
            new Host(
                '{{ host['id'] }}', '{{ host['name'] }}', '{{ host['alias'] }}',
                '{{ host['overall_state'] }}', '{{ host['overall_status'] }}',
                '{{ host['state_id'] }}', '{{ host['business_impact'] }}',
                '{{ ! host['content'] }}',
                {{ host['lat'] }}, {{ host['lng'] }},
                [
                    %for service in host['services']:
                        %status = service.get_html_state(text=None, use_status=service.overall_status)
                        %status = status.replace("'", " ")
                        new Service(
                            '{{ host['id'] }}',
                            '{{ service['id'] }}', '{{ service['name'] }}', '{{ service['alias'] }}',
                            '{{ service['overall_state'] }}', '{{ service['overall_status'] }}',
                            '{{ service['state_id'] }}', '{{ service['business_impact'] }}',
                            '{{ ! service['content'] }}'
                        ),
                    %end
                ]
            ),
        %end
        ]

        if (debugMaps) console.log("Hosts:", hosts);
        if (debugMaps) {
            for (var i = 0; i < hosts.length; i++) {
                var h = hosts[i];
                if (debugMaps) console.log("- services", h.services);
            }
        }
    }

    // Ok go initialize the map with all elements when it's loaded
    function initWorldmap() {
        // Build hosts list
        buildHosts();

        // Build map
        var mapCreated = mapInit('{{mapId}}', function($map) {
            // Map height to be scaled inside the window
            var mapOffset = $('#{{mapId}}').offset().top;
            var footerOffset = $('footer').offset().top;
            $('#{{mapId}}').height(footerOffset - mapOffset - 35)

            if (debugMaps) console.log('Resizing map:', $map.id)
            mapResize($map);
        });
        if (! mapCreated) {
            $('#{{mapId}}').html('<div class="alert alert-danger"><a href="#" class="alert-link">{{_('No hosts to display on the map')}}</a></div>');
        }
    }

    %if load:
        %# load is used for the host location widget to load on-demand the necessary map files
        var cssfiles=[];
        cssfiles.push('/static/plugins/worldmap/static/leaflet/leaflet.css');
        cssfiles.push('/static/plugins/worldmap/static/css/MarkerCluster.css');
        cssfiles.push('/static/plugins/worldmap/static/css/MarkerCluster.Default.css');
        cssfiles.push('/static/plugins/worldmap/static/css/leaflet.label.css');
        cssfiles.push('/static/plugins/worldmap/static/css/worldmap.css');

        $.getCssFiles(cssfiles, function(){
            var jsfiles=[];
            jsfiles.push('/static/plugins/worldmap/static/leaflet/leaflet.js');
            jsfiles.push('/static/plugins/worldmap/static/js/leaflet.markercluster.js');
            jsfiles.push('/static/plugins/worldmap/static/js/leaflet.Icon.Glyph.js');
            jsfiles.push('/static/plugins/worldmap/static/js/leaflet.label.js');
            jsfiles.push('/static/plugins/worldmap/static/js/worldmap.js');

            $.getJsFiles(jsfiles, function(){
                // Wait for a while to let the scripts get executed...
                window.setTimeout(function() {
                    initWorldmap();
                }, 1000);
            });
        });
    %end
</script>
