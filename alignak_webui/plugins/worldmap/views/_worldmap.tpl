<script>
   // Set true to activate javascript console logs
   var debugMaps = false;
   if (debugMaps && !window.console) {
      alert('Your web browser does not have any console object ... you should stop using IE ;-) !');
   }

   var servicesLevel = {{ params['services_level'] }};

   %# List hosts and their services
   var hosts = [
   %for host in hosts:
      %services = datamgr.get_services(search={'where': {'host':host.id}})
      %livestate = datamgr.get_livestate(search={'where': {'type': 'host', 'name':'%s' % host.name}})
      %livestate = livestate[0] if livestate else None
      %if not livestate:
      %continue
      %end
      new Host(
         '{{ host.id }}', '{{ host.name }}',
         '{{ livestate.status }}', '{{ ! livestate.get_html_state(text=None)}}',
         '{{ host.business_impact }}', '{{ ! Helper.get_html_business_impact(host.business_impact) }}',
         {{ float(host.customs.get('_LOC_LAT')) }}, {{ float(host.customs.get('_LOC_LNG')) }},
         '{{ livestate.id }}',
         {{ str(livestate.is_problem).lower() }},
         {{ str(livestate.is_problem).lower() }} && {{ str(livestate.acknowledged).lower() }},
         {{ str(livestate.downtime).lower() }},
         [
            %for service in services:
            %livestate = datamgr.get_livestate(search={'where': {'type': 'service', 'name':'%s/%s' % (host.name, service.name)}})
            %livestate = livestate[0] if livestate else None
            %if not livestate:
            %continue
            %end
            new Service(
               '{{ livestate.id }}', '{{ host.name }}',
               '{{ service.id }}', '{{ service.name }}',
               '{{ livestate.status }}', '{{ ! livestate.get_html_state(text=None)}}',
               '{{ service.business_impact }}', '{{ ! Helper.get_html_business_impact(service.business_impact) }}',
               '{{ livestate.id }}',
               {{ str(livestate.is_problem).lower() }},
               {{ str(livestate.is_problem).lower() }} && {{ str(livestate.acknowledged).lower() }},
               {{ str(livestate.downtime).lower() }}
            ),
            %end
         ]
      ),
   %end
   ]


   function hostInfoContent() {
      var text = '<div class="map-infoView" id="iw-' + this.name + '">' + this.stateIcon;
      text += '<span class="map-hostname"><a href="/livestate/' + this.lvId + '">' + this.name + '</a> ' + this.biIcon + '</span>';
      if (this.scheduledDowntime) {
         text += '<div><i class="fa fa-ambulance"></i> {{_('Currently in scheduled downtime.')}}</div>';
      }
      if (this.isProblem) {
         text += '<div>';
         if (this.isAcknowledged) {
            text += '<em><span class="fa fa-check"></span>' + "{{_('Problem has been acknowledged.')}}" + '</em>';
         } else {
            %if current_user.is_power():
            text += '<button class="btn btn-default btn-xs" data-type="action" data-action="acknowledge" data-toggle="tooltip" data-placement="top" title="{{_('Acknowledge this problem')}}" data-name="'+this.name+'" data-element="'+this.lvId+'"><i class="fa fa-check"></i></button>';
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

   function Host(id, name, state, stateIcon, bi, biIcon, lat, lng, lvId, isProblem, isAcknowledged, scheduledDowntime, services) {
      this.id = id;
      this.name = name;
      this.state = state;
      this.stateIcon = stateIcon;
      this.bi = bi;
      this.biIcon = biIcon;
      this.lat = lat;
      this.lng = lng;
      this.lvId = lvId;
      this.isProblem = isProblem;
      this.isAcknowledged = isAcknowledged;
      this.scheduledDowntime = scheduledDowntime;
      this.services = services;

      this.infoContent = hostInfoContent;
      this.location = gpsLocation;
      this.markerIcon = markerIcon;
      this.hostState = hostState;
   }

   function serviceInfoContent() {
      var text = '<li>' + this.stateIcon + ' <a href="/livestate/' + this.lvId + '">' + this.name + '</a> ' + this.biIcon + '</li>';
      if (this.scheduledDowntime) {
         text += '<div><i class="fa fa-ambulance"></i> {{_('Currently in scheduled downtime.')}}</div>';
      }
      if (this.isProblem) {
         text += '<div>';
         if (this.isAcknowledged) {
            text += '<em><span class="fa fa-check"></span>' + "{{_('Problem has been acknowledged.')}}" + '</em>';
         } else {
            %if current_user.is_power():
            text += '<button class="btn btn-default btn-xs" data-type="action" data-action="acknowledge" data-toggle="tooltip" data-placement="top" title="{{_('Acknowledge this problem')}}" data-name="'+this.name+'" data-element="'+this.lvId+'"><i class="fa fa-check"></i></button>';
            %else:
            text += '<em><span class="fa fa-exclamation"></span>' + "{{_('Problem should be acknowledged.')}}" + '</em>';
            %end
         }
         text += '</div>';
      }
      return text;
   }

   function Service(hostId, hostName, id, name, state, stateIcon, bi, biIcon, lvId, isProblem, isAcknowledged, scheduledDowntime) {
      this.hostId = hostId;
      this.hostName = hostName;
      this.id = id;
      this.name = name;
      this.state = state;
      this.stateIcon = stateIcon;
      this.bi = bi;
      this.biIcon = biIcon;
      this.lvId = lvId;
      this.isProblem = isProblem;
      this.isAcknowledged = isAcknowledged;
      this.scheduledDowntime = scheduledDowntime;

      this.infoContent = serviceInfoContent;
   }

   var map_{{mapId}};

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
  // Create a marker on specified position for specified host/state with IW content
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
  // Map initialization
  // ------------------------------------------------------------------------------
   mapInit_{{mapId}} = function() {
      if (debugMaps)
         console.log('mapInit_{{mapId}} ...');

      var scripts = [];
      scripts.push('/static/plugins/worldmap/htdocs/js/leaflet.markercluster.js');
      scripts.push('/static/plugins/worldmap/htdocs/js/Leaflet.Icon.Glyph.js');
      scripts.push('/static/plugins/worldmap/htdocs/js/leaflet.label.js');
      loadScripts(scripts, function() {
         if (debugMaps)
            console.log('Scripts loaded !')

         map_{{mapId}} = L.map('{{mapId}}');
         L.tileLayer('https://cartodb-basemaps-{s}.global.ssl.fastly.net/light_all/{z}/{x}/{y}.png', {attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors, &copy; <a href="http://cartodb.com/attributions">CartoDB</a>'}).addTo(map_{{mapId}});
         var bounds = new L.LatLngBounds();

         if (debugMaps)
            console.log('Map object ({{mapId}}): ', map_{{mapId}})

         // Markers ...
         var allMarkers_{{mapId}} = [];
         for (var i = 0; i < hosts.length; i++) {
            var h = hosts[i];
            bounds.extend(h.location());
            allMarkers_{{mapId}}.push(markerCreate_{{mapId}}(h));
         }

         // Zoom
         map_{{mapId}}.fitBounds(bounds);

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
      });
   };

   //<!-- Ok go initialize the map with all elements when it's loaded -->
   $(document).ready(function() {
      $.getScript("https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.0.0-rc.1/leaflet.js").done(function() {
         if (debugMaps)
            console.log("Leafletjs API loaded ...");
         mapInit_{{mapId}}();
      });
   });
</script>
