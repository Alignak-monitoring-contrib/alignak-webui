%setdefault('worldmap_parameters', {'default_zoom': 6, 'default_lng': 1.87528, 'default_lat': 46.60611, 'hosts_level': [1, 2, 3, 4, 5], 'services_level': [1, 2, 3, 4, 5], 'layer': ''})

<script>
    // Set true to activate javascript console logs
    var debugMaps = false;
    if (debugMaps && !window.console) {
          alert('Your web browser does not have any console object ... you should stop using IE ;-) !');
    }

    var defaultZoom = {{ worldmap_parameters['default_zoom'] }};
    var defaultCenter = [{{ worldmap_parameters['default_lat'] }}, {{ worldmap_parameters['default_lng'] }}];
    var servicesLevel = {{ worldmap_parameters['services_level'] }};
    var hostsLevel = {{ worldmap_parameters['hosts_level'] }};

    %# List hosts and their services
    var hosts = [
    %for host in hosts:
        %pos = host.position
        %if 'type' not in pos or pos['type'] != 'Point':
        %continue
        %end
        %lat = pos['coordinates'][0]
        %lng = pos['coordinates'][1]
        %services = datamgr.get_services(search={'where': {'host':host.id}}, all_elements=True)
        new Host(
            '{{ host.id }}', '{{ host.name }}',
            '{{ host.status }}', '{{ ! host.get_html_state(text=None)}}',
            '{{ host.business_impact }}',
            '{{ ! Helper.get_html_business_impact(host.business_impact) }}',
            {{ lat }}, {{ lng }},
            {{ str(host.is_problem).lower() }},
            {{ str(host.is_problem).lower() }} && {{ str(host.acknowledged).lower() }},
            {{ str(host.downtime).lower() }},
            [
                %for service in services:
                    new Service(
                        '{{ host.id }}', '{{ host.name }}',
                        '{{ service.id }}', '{{ service.name }}',
                        '{{ service.status }}', '{{ ! service.get_html_state(text=None)}}',
                        '{{ service.business_impact }}', '{{ ! Helper.get_html_business_impact(service.business_impact) }}',
                        {{ str(service.is_problem).lower() }},
                        {{ str(service.is_problem).lower() }} && {{ str(service.acknowledged).lower() }},
                        {{ str(service.downtime).lower() }}
                    ),
                %end
            ]
        ),
    %end
    ]


    function hostInfoContent() {
        var text = '<div class="map-infoView" id="iw-' + this.name + '">' + this.stateIcon;
        text += '<span class="map-hostname"><a href="/host/' + this.id + '">' + this.name + '</a> ' + this.biIcon + '</span>';
        if (this.isDowntimed) {
            text += '<div><i class="fa fa-ambulance"></i> {{_('Currently in scheduled downtime.')}}</div>';
        }
        if (this.isProblem) {
             text += '<div>';
            if (this.isAcknowledged) {
                text += '<em><span class="fa fa-check"></span>' + "{{_('Problem has been acknowledged.')}}" + '</em>';
            } else {
                %if current_user.is_power():
                text += '<button class="btn btn-raised btn-xs"';
                text += 'data-type="action" data-action="acknowledge" data-toggle="tooltip" data-placement="top"';
                text += 'title="{{_('Acknowledge this problem')}}"';
                text += 'data-element_type="host" data-name="'+this.name+'" data-element="'+this.id+'">';
                text += '<i class="fa fa-check"></i></button>';
                %else:
                text += '<em><span class="fa fa-exclamation"></span>' + "{{_('Problem should be acknowledged.')}}" + '</em>';
                %end
            }
            text += '</div>';
        }
        text += '<hr/>';
        if (this.services.length > 0) {
             text += '<ul class="map-services">';
            for (var i = 0; i < this.services.length; i++) {
                text += this.services[i].infoContent();
            }
            text += '</ul>';
        }
        text += '</div>';
        return text;
    }

    function gpsLocation() {
        return L.latLng(this.lat, this.lng);
    }

    function markerIcon() {
        return "/static/plugins/worldmap/htdocs/img/" + '/glyph-marker-icon-' + this.hostState().toLowerCase() + '.png';
    }

    function hostState() {
        var hs = 'OK';
        switch (this.state.toUpperCase()) {
        case 'UP':
            break;
        case 'DOWN':
            if (this.isAcknowledged) {
                hs = 'ACK';
            } else {
                hs = 'KO';
            }
            break;
        default:
            if (this.isAcknowledged) {
                hs = 'ACK';
            } else {
                hs = 'WARNING';
            }
        }
        for (var i = 0; i < this.services.length; i++) {
            var s = this.services[i];
            if ($.inArray(s.bi, servicesLevel)) {
                switch (s.state.toUpperCase()) {
                case 'OK':
                    break;
                case 'CRITICAL':
                    if (hs == 'OK' || hs == 'WARNING' || hs == 'ACK') {
                        if (s.isAcknowledged) {
                            hs = 'ACK';
                        } else {
                            hs = 'KO';
                        }
                    }
                    break;
                default:
                    if (hs == 'OK' || hs == 'ACK') {
                        if (s.isAcknowledged) {
                            hs = 'ACK';
                        } else {
                            hs = 'WARNING';
                        }
                    }
                }
            }
        }
        return hs;
    }

    function Host(id, name, state, stateIcon, bi, biIcon, lat, lng, isProblem, isAcknowledged, isDowntimed, services) {
        this.id = id;
        this.name = name;
        this.state = state;
        this.stateIcon = stateIcon;
        this.bi = bi;
        this.biIcon = biIcon;
        this.lat = lat;
        this.lng = lng;
        this.isProblem = isProblem;
        this.isAcknowledged = isAcknowledged;
        this.isDowntimed = isDowntimed;
        this.services = services;

        this.infoContent = hostInfoContent;
        this.location = gpsLocation;
        this.markerIcon = markerIcon;
        this.hostState = hostState;
    }

    function serviceInfoContent() {
        var text = '<li>' + this.stateIcon + ' <a href="/service/' + this.id + '">' + this.name + '</a> ' + this.biIcon + '</li>';
        if (this.isDowntimed) {
            text += '<div><i class="fa fa-ambulance"></i> {{_('Currently in scheduled downtime.')}}</div>';
        }
        if (this.isProblem) {
            text += '<div>';
            if (this.isAcknowledged) {
                text += '<em><span class="fa fa-check"></span>' + "{{_('Problem has been acknowledged.')}}" + '</em>';
            } else {
                %if current_user.is_power():
                text += '<button class="btn btn-raised btn-xs" ';
                text += 'data-type="action" data-action="acknowledge" data-toggle="tooltip" data-placement="top"';
                text += 'title="{{_('Acknowledge this problem')}}"';
                text += 'data-element_type="service" data-name="'+this.name+'" data-element="'+this.id+'">';
                text += '<i class="fa fa-check"></i></button>';
                %else:
                text += '<em><span class="fa fa-exclamation"></span>' + "{{_('Problem should be acknowledged.')}}" + '</em>';
                %end
            }
            text += '</div>';
        }
        return text;
    }

    function Service(hostId, hostName, id, name, state, stateIcon, bi, biIcon, isProblem, isAcknowledged, isDowntimed) {
        this.hostId = hostId;
        this.hostName = hostName;
        this.id = id;
        this.name = name;
        this.state = state;
        this.stateIcon = stateIcon;
        this.bi = bi;
        this.biIcon = biIcon;
        this.isProblem = isProblem;
        this.isAcknowledged = isAcknowledged;
        this.isDowntimed = isDowntimed;

        this.infoContent = serviceInfoContent;
    }

    //------------------------------------------------------------------------------
    // Sequentially load necessary scripts to create map with markers
    //------------------------------------------------------------------------------
    loadScripts = function(scripts, complete) {
        var loadScript = function(src) {
            if (!src)
                return;
            if (debugMaps)
                console.log('Loading script: ', src);

            $.getScript(src, function(data, textStatus, jqxhr) {
                next = scripts.shift();
                if (next) {
                    loadScript(next);
                } else if (typeof complete == 'function') {
                    complete();
                }
            });
        };
        if (scripts.length) {
            loadScript(scripts.shift());
        } else if (typeof complete == 'function') {
            complete();
        }
    }

    // ------------------------------------------------------------------------------
    // Create a marker for specified host
    // ------------------------------------------------------------------------------
    markerCreate_{{mapId}} = function(host) {
        if (debugMaps)
            console.log("-> marker creation for " + host.name + ", state : " + host.hostState());

        var icon = L.icon.glyph({iconUrl: host.markerIcon(), prefix: 'fa', glyph: 'server'});

        var m = L.marker(host.location(), {icon: icon}).bindLabel(host.name, {
            noHide: true,
            direction: 'center',
            offset: [0, 0]
        }).bindPopup(host.infoContent()).openPopup();
        m.state = host.hostState();
        m.name = host.name;
        return m;
    }

    // ------------------------------------------------------------------------------
    // Resize the map
    // ------------------------------------------------------------------------------
    mapResize_{{mapId}} = function(host) {
        if (typeof L !== 'undefined') {
            if (debugMaps)
                console.log("Map resize...");
            L.Util.requestAnimFrame(map_{{mapId}}.invalidateSize, map_{{mapId}}, !1, map_{{mapId}}._container);
        }
    }

    // ------------------------------------------------------------------------------
    // Map initialization
    // ------------------------------------------------------------------------------
    var map_{{mapId}};
    mapInit_{{mapId}} = function() {
        if (debugMaps)
            console.log('Initialization function: mapInit_{{mapId}} ...');

        if  (hosts.length < 1) {
            if (debugMaps)
                console.log('No hosts to display on the map.');
            return false;
        }

        var scripts = [];
        scripts.push('/static/plugins/worldmap/htdocs/js/leaflet.markercluster.js');
        scripts.push('/static/plugins/worldmap/htdocs/js/leaflet.Icon.Glyph.js');
        scripts.push('/static/plugins/worldmap/htdocs/js/leaflet.label.js');
        loadScripts(scripts, function() {
            if (debugMaps)
                console.log('Scripts loaded !')

            map_{{mapId}} = L.map(
                '{{mapId}}',
                {
                    zoom: defaultZoom,
                    center: defaultCenter
                }
            );

            L.tileLayer('https://cartodb-basemaps-{s}.global.ssl.fastly.net/light_all/{z}/{x}/{y}.png', {attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors, &copy; <a href="http://cartodb.com/attributions">CartoDB</a>'}).addTo(map_{{mapId}});

            if (debugMaps)
                console.log('Map object ({{mapId}}): ', map_{{mapId}})

            // Markers ...
            var allMarkers_{{mapId}} = [];
            var bounds = new L.LatLngBounds();
            if (debugMaps)
                console.log("Initial map bounds:", bounds.isValid());
            for (var i = 0; i < hosts.length; i++) {
                var h = hosts[i];
                bounds.extend(h.location());
                allMarkers_{{mapId}}.push(markerCreate_{{mapId}}(h));
            }
            if (debugMaps)
                console.log("Extended map bounds:", bounds);
            if (debugMaps)
               console.log("Extended map bounds:", bounds.getNorth(), bounds.getSouth());

            // Zoom adaptation if bounds are a rectangle
            if (bounds.getNorth() != bounds.getSouth()) {
                map_{{mapId}}.fitBounds(bounds);
            }

            // Build marker cluster
            var markerCluster = L.markerClusterGroup({
                iconCreateFunction: function(cluster) {
                    // Manage markers in the cluster ...
                    var markers = cluster.getAllChildMarkers();
                    if (debugMaps)
                        console.log("marker, count : " + markers.length);
                    var clusterState = "ok";
                    for (var i = 0; i < markers.length; i++) {
                        var currentMarker = markers[i];
                        if (debugMaps)
                            console.log("marker, " + currentMarker.name + " state is: " + currentMarker.state);

                        switch (currentMarker.state) {
                        case "WARNING":
                            if (clusterState != "ko")
                                clusterState = "warning";
                            break;
                        case "KO":
                            clusterState = "ko";
                            break;
                        }
                    }
                    return L.divIcon({
                        html: '<div><span>' + markers.length + '</span></div>',
                        className: 'marker-cluster marker-cluster-' + clusterState,
                        iconSize: new L.Point(60, 60)
                    });
                }
            });
            markerCluster.addLayers(allMarkers_{{mapId}});
            map_{{mapId}}.addLayer(markerCluster);

            return true
        });
    };

    //<!-- Ok go initialize the map with all elements when it's loaded -->
    $(document).ready(function() {
        $.getScript("https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.0.0-rc.1/leaflet.js").done(function() {
            if (debugMaps)
                console.log("Leafletjs API loaded ...");
            if (! mapInit_{{mapId}}()) {
                $('#{{mapId}}').html('<div class="alert alert-danger"><a href="#" class="alert-link">{{_('No hosts to display on the map')}}</a></div>');
            }
        });
    });
</script>
