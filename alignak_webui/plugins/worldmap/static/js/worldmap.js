// Set true to activate javascript console logs
var debugMaps = false;
if (debugMaps && !window.console) {
    alert('Your web browser does not have any console object ... you should stop using IE ;-) !');
}
if (debugMaps) {
    console.log("Activated debug maps logs");
}

var defaultZoom = 12;
if (debugMaps) console.log('Default zoom: ', defaultZoom);
var defaultCenter = L.latLng(46.60611, 1.87528);
if (debugMaps) console.log('Default center: ', defaultCenter);

var actions = false;

// Markers ...
var allMaps = [];

// Hosts - positionned or not
var pos_hosts = []
var not_pos_hosts = []


function hostInfoContent() {
    return this.content;
}

function gpsLocation() {
    return L.latLng(this.lat, this.lng);
}

function markerIcon() {
    return "/static/plugins/worldmap/static/img/glyph-marker-icon-" + this.hostStatus().toLowerCase() + ".png";
}

function hostState() {
    return this.overallState;
}

function hostStatus() {
    return this.overallStatus;
}

function Host(id, name, alias, overallState, overallStatus, state, bi, content, lat, lng, services) {
    this.id = id;
    this.name = name;
    this.alias = alias;
    this.overallState = overallState;
    this.overallStatus = overallStatus;
    this.state = state;
    this.bi = bi;
    this.content = content;
    this.services = services;

    this.lat = lat;
    this.lng = lng;

    this.infoContent = hostInfoContent;
    this.location = gpsLocation;
    this.markerIcon = markerIcon;
    this.hostState = hostState;
    this.hostStatus = hostStatus;
}

function Service(hostId, id, name, alias, overallState, overallStatus, state, bi, content) {
    this.hostId = hostId;
    this.id = id;
    this.name = name;
    this.alias = alias;
    this.overallState = overallState;
    this.overallStatus = overallStatus;
    this.state = state;
    this.bi = bi;
    this.content = content;
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
markerCreate = function($map, host, markerCluster, draggable) {
    if (debugMaps) console.log("-> marker creation for " + host.name + ", state : " + host.hostStatus());

    var icon = L.icon.glyph({iconUrl: host.markerIcon(), prefix: 'fa', glyph: 'server'});

    var marker = L.marker(host.location(), {id:host.name, icon:icon, draggable:draggable})
                    .addTo(markerCluster)
                    .bindTooltip(host.name, {permanent: true, direction: 'center', offset: [0, -12]})
                    .bindPopup(host.infoContent())
                    .openPopup();
    marker.state = host.hostState();
    marker.state_text = host.hostStatus();
    marker.name = host.name;

    if (draggable == 'true') {
        marker.on('dragstart', function(event) {
            var marker = event.target;
            marker.opacity = 0.5;
        });

        marker.on('dragend', function(event){
            var marker = event.target;
            var position = marker.getLatLng();

            wait_message('Updating position...', true)

            $.ajax({
                url: "/host/" + host.name + "/form",
                type: "POST",
                data: {"location": ["latitude|"+position.lat, "longitude|"+position.lng]}
            })
            .done(function(data, textStatus, jqXHR) {
                // data is JSON formed with a _message field
                if (jqXHR.status != 200) {
                    console.error(jqXHR.status, data);
                    raise_message_ko(data._message);
                } else {
                    raise_message_info(data._message);
                    $.each(data, function(field, value){
                        if (field=='_message') return true;
                        if (field=='_errors') return true;
                        raise_message_ok("Updated " + field);
                    });

                    // Update marker
                    marker.setLatLng(position).update();
                    $map.panTo(position)
                }
            })
            .fail(function( jqXHR, textStatus, errorThrown ) {
                // data is JSON formed with a _message field
                if (jqXHR.status != 409) {
                    console.error(errorThrown, textStatus);
                } else {
                    raise_message_info(data._message);
                }
            })
            .always(function() {
                wait_message('', false)
            });
        });
    }

    return marker;
}

// ------------------------------------------------------------------------------
// Resize the map
// ------------------------------------------------------------------------------
mapResize = function($map, host) {
    if (typeof L !== 'undefined') {
        if (debugMaps)
            console.log("Map resize...", $map._leaflet_id);
        // Set map widht and height
        L.Util.requestAnimFrame($map.invalidateSize, $map, !1, $map._container);
        $("#hostsMap").height($("#worldmap").height()).width($("#worldmap").width());
        $map.invalidateSize();
    }
}

// ------------------------------------------------------------------------------
// Map initialization
// ------------------------------------------------------------------------------
mapInit = function(map_id, editable, callback) {
    if (debugMaps) console.log('Initialization function: mapInit for ', map_id);

    if  (pos_hosts.length < 1) {
        if (debugMaps) console.log('No hosts to display on the map.');
        return false;
    }

    $map = L.map(map_id, {zoom: defaultZoom, center: defaultCenter});
    if (debugMaps) console.log('Map object: ', map_id, $map)

    L.tileLayer('https://cartodb-basemaps-{s}.global.ssl.fastly.net/light_all/{z}/{x}/{y}.png', {attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors, &copy; <a href="http://cartodb.com/attributions">CartoDB</a>'}).addTo($map);

    // Build marker cluster
    var markerCluster = L.markerClusterGroup({
        spiderfyDistanceMultiplier: 2,
        iconCreateFunction: function(cluster) {
            // Manage markers in the cluster ...
            var markers = cluster.getAllChildMarkers();
            if (debugMaps) console.log("cluster markers, count : " + markers.length);

            var clusterState = 0, clusterStyle = 'ok';
            for (var i = 0; i < markers.length; i++) {
                var currentMarker = markers[i];
                if (debugMaps) console.log("marker, " + currentMarker.name + " state is: " + currentMarker.state_text);
                clusterState = Math.max(clusterState, currentMarker.state);
            }
            if (clusterState > 3) {
                clusterStyle = 'ko';
            } else if (clusterState > 0) {
                clusterStyle = 'warning';
            }
            if (debugMaps) console.log("cluster state:", clusterState, clusterStyle);
            return L.divIcon({
                html: '<div><span>' + markers.length + '</span></div>',
                className: 'marker-cluster marker-cluster-' + clusterStyle,
                iconSize: new L.Point(60, 60)
            });
        }
    }).addTo($map);

    // Markers ...
    var allMarkers = [];
    for (var i = 0; i < pos_hosts.length; i++) {
        var marker = markerCreate($map, pos_hosts[i], markerCluster, editable);

        //$map.addLayer(marker);
        allMarkers.push(marker);
    }
    markerCluster.addLayers(allMarkers);
    $map.addLayer(markerCluster);

//    var group = L.featureGroup(allMarkers); //add markers array to featureGroup
//    $map.fitBounds(group.getBounds());
    $map.fitBounds(markerCluster.getBounds());

    allMaps.push($map);

    $(window).on("resize", function() {
        mapResize($map);
    }).trigger("resize");

    if (typeof callback !== 'undefined' && $.isFunction(callback)) {
        if (debugMaps) console.log('Calling callback function ...');
        callback($map);
    }

    return true;
};
