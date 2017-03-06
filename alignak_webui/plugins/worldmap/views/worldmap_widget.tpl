<!-- Hosts worldmap widget -->
%# embedded is True if the widget is got from an external application
%setdefault('embedded', False)
%from bottle import request
%setdefault('links', request.params.get('links', ''))
%setdefault('identifier', 'widget')
%setdefault('credentials', None)

%from alignak_webui.utils.helper import Helper

%# Add extra Css and Js for this page, and a callback function
%# No default refresh for this page
%css=["worldmap/static/leaflet/leaflet.css", "worldmap/static/css/MarkerCluster.css", "worldmap/static/css/MarkerCluster.Default.css", "worldmap/static/css/leaflet.label.css", "worldmap/static/css/worldmap.css"]
%js=["worldmap/static/leaflet/leaflet.js", "worldmap/static/js/worldmap.js"]
%callback='initWorldmap'
%setdefault('mapId', 'hosts_worldmap')

%hosts = elements
<!-- HTML map container -->
<div class="map_container_widget">
   %if not hosts:
      <div class="alert alert-danger">
         <center>
            <h3>{{_('We did not found any hosts to locate on the map.')}}</h3>
         </center>
      </div>
   %else:
      <div id="{{mapId}}" class="osm">
         <div class="alert alert-info">
            <a href="#" class="alert-link">{{_('Loading map ...')}}</a>
         </div>
      </div>
   %end

   %include("_worldmap")
</div>
