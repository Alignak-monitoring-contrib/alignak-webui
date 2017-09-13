// Set true to activate javascript console logs
var debugMaps = true;
if (debugMaps && !window.console) {
    alert('Your web browser does not have any console object ... you should stop using IE ;-) !');
}
if (debugMaps) {
    console.log("Activated debug maps logs");
}

var positionHosts = false;

var defaultZoom = 12;
if (debugMaps) console.log('Default zoom: ', defaultZoom);
var defaultCenter = L.latLng(46.60611, 1.87528);
if (debugMaps) console.log('Default center: ', defaultCenter);

var actions = false;

// Geocoder
var geocoder_control;
var geocoder;
var geocoder_marker;

var selectedHosts = [];
var selectedHostIndex = -1;
var selectedPosition = null;

// Markers ...
var allMaps = [];

// Hosts - positioned or not
var pos_hosts = []


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

function Host(id, name, alias, overallState, overallStatus, state, bi, content, lat, lng, positioned, services) {
    this.id = id;
    this.name = name;
    this.alias = alias;
    this.overallState = overallState;
    this.overallStatus = overallStatus;
    this.state = state;
    this.bi = bi;
    this.content = content;
    this.services = services;

    this.positioned = positioned;
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

function setHostPosition(host, marker){
    var position = marker.getLatLng();

    wait_message('Updating position...', true)

    $.ajax({
        url: "/host_form/" + host.name,
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
};

function selectHost(host){
    if (debugMaps) console.log("Select an host: ", host.name);
    selectedHosts.push(host);
    var newElt = $('<li data-hostname="' + host.name + '"><a href="#" class="list-group-item">' + host.name + '</a></li>');
    newElt.on("click", function () {
        if (debugMaps) console.log("Unselect an host: ", $(this).data("hostname"));
        for (var i = 0; i < pos_hosts.length; i++) {
            if (pos_hosts[i].name == $(this).data("hostname")) {
                $('#selected_hosts li[data-hostname="' + pos_hosts[i].name + '"]').remove();

                if (! pos_hosts[i].positioned) {
                    var newElt = $('<li data-hostname="' + pos_hosts[i].name + '"><a href="#" class="list-group-item">' + pos_hosts[i].name + '</a></li>');
                    $("#not_positioned_hosts ul").append(newElt);
                }
            }
        }
    });
    $("#selected_hosts ul").append(newElt);
    if (debugMaps) console.log("Selected host: ", host.name);
};

//------------------------------------------------------------------------------
// Sequentially load necessary scripts to create map with markers
//------------------------------------------------------------------------------
/*
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
*/

// ------------------------------------------------------------------------------
// Create a marker for specified host
// ------------------------------------------------------------------------------
markerCreate = function($map, host, markerCluster, draggable) {
    if (debugMaps) console.log("-> marker creation for " + host.name + ", state : " + host.hostStatus());

    var icon = L.icon.glyph({iconUrl: host.markerIcon(), prefix: 'fa', glyph: 'server'});

    var marker = L.marker(host.location(), {id:host.name, icon:icon, draggable:draggable})
                    .bindTooltip(host.name, {permanent: true, direction: 'center', offset: [0, -12]})
                    .bindPopup(host.infoContent())
                    .openPopup();
    marker.state = host.hostState();
    marker.state_text = host.hostStatus();
    marker.name = host.name;
    marker.addTo(markerCluster)

    marker.on('click', function(event) {
        selectHost(host);
    });

    if (draggable == 'true') {
        marker.on('dragstart', function(event) {
            var marker = event.target;
            marker.opacity = 0.5;
        });

        marker.on('dragend', function(event) {
            setHostPosition(host, event.target);
        });
    }

    if (debugMaps) console.log("-> marker created: ", marker);
    return marker;
}

// ------------------------------------------------------------------------------
// Resize the map
// ------------------------------------------------------------------------------
mapResize = function($map, host) {
    if (typeof L !== 'undefined') {
        if (debugMaps) console.log("Map resize...", $map._leaflet_id);
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

    var map_object = $('#' + map_id);
    if (map_object && map_object._leaflet_id) {
        console.warning('Map is already initialized.');
        return false;
    }

    $map = L.map(map_id, {zoom: defaultZoom, center: defaultCenter});
    if (debugMaps) console.log('Map object: ', map_id, $map)

    L.tileLayer('https://cartodb-basemaps-{s}.global.ssl.fastly.net/light_all/{z}/{x}/{y}.png', {attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors, &copy; <a href="http://cartodb.com/attributions">CartoDB</a>'}).addTo($map);

    // Build marker cluster
    var markerCluster = L.markerClusterGroup({
        chunkedLoading: true,
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

    if (positionHosts) {
        // Geocoder
        geocoder_control = L.Control.geocoder({
            collapsed: false,
            position: "topright",
            placeholder: "Search...",
            errorMessage: "Nothing found :(",
            showResultIcons:true
        }).addTo($map);
        $map.on('click', function(e) {
            geocoder_control.geocoder.reverse(e.latlng, map.options.crs.scale(map.getZoom()), function(results) {
                var r = results[0];
                if (r) {
                    if (geocoder_marker) {
                        geocoder_marker.
                            setLatLng(r.center).
                            setPopupContent(r.html || r.name).
                            openPopup();
                    } else {
                        geocoder_marker = L.marker(r.center).bindPopup(r.name).addTo(map).openPopup();
                    }
                }
            })
        })
    }

    // Markers ...
    var allMarkers = [];
    var someHostsAreNotPositioned = false;
    for (var i = 0; i < pos_hosts.length; i++) {
        if (pos_hosts[i].positioned) {
            var marker = markerCreate($map, pos_hosts[i], markerCluster, editable);
            allMarkers.push(marker);
        } else {
            var newElt = $('<li data-hostname="' + pos_hosts[i].name + '"><a href="#" class="list-group-item">' + pos_hosts[i].name + '</a></li>');
            newElt.on("click", function () {
                if (debugMaps) console.log("Selected an unpositioned host: ", $(this).data("hostname"));
                if (! positionHosts) {
                    console.log("Positioning hosts on the map is not yet implemented. Feature is yet to come...");
                    return;
                }
                for (var i = 0; i < pos_hosts.length; i++) {
                    if (pos_hosts[i].name == $(this).data("hostname")) {
                        $('#not_positioned_hosts li[data-hostname="' + pos_hosts[i].name + '"]').remove();

                        if (selectedPosition) {
                            pos_hosts[i].lat = selectedPosition.lat;
                            pos_hosts[i].lng = selectedPosition.lng;
                            pos_hosts[i].positioned = true;
                            if (debugMaps) console.log("Position for host: ", pos_hosts[i].name, ", index:", i);

                            var marker = markerCreate($map, pos_hosts[i], markerCluster, editable);
                            allMarkers.push(marker);
                            setHostPosition(pos_hosts[i], marker);

                            raise_message_ok('Host: ' + pos_hosts[i].name + 'is now positioned.');
                            selectedPosition = null;
                        } else {
                            raise_message_info('Enter an address to position this host.');

                            selectHost(pos_hosts[i]);
                        }
                    }
                }
            });
            $("#not_positioned_hosts ul").append(newElt);
            someHostsAreNotPositioned = true;
        }
    }
    if (! positionHosts) {
        $("#selected_hosts").remove();
    }
    if (! someHostsAreNotPositioned) {
        $("#not_positioned_hosts").remove();
    }
    markerCluster.addLayers(allMarkers);
    $map.addLayer(markerCluster);

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
