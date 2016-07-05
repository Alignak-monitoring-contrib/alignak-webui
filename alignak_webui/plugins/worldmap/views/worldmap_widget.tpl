<!-- Hosts chart widget -->
%# embedded is True if the widget is got from an external application
%setdefault('embedded', False)
%from bottle import request
%setdefault('links', request.params.get('links', ''))
%setdefault('identifier', 'widget')
%setdefault('credentials', None)

%from alignak_webui.utils.helper import Helper

%setdefault('mapId', 'hosts_worldmap')
%setdefault('params', {'default_zoom': 16, 'default_lng': 5.080625, 'default_lat': 45.054148, 'hosts_level': [1, 2, 3, 4, 5], 'services_level': [1, 2, 3, 4, 5], 'layer': ''})

%hosts = elements
<script>
   var cssfiles=['/static/plugins/worldmap/htdocs/css/worldmap.css', '/static/plugins/worldmap/htdocs/css/leaflet.css', '/static/plugins/worldmap/htdocs/css/MarkerCluster.css', '/static/plugins/worldmap/htdocs/css/MarkerCluster.Default.css', '/static/plugins/worldmap/htdocs/css/leaflet.label.css'];

   $.getCssFiles(cssfiles, function(){
       // do something, e.g.
       // console.log('Loaded all CSS files!');
   });
</script>
<!-- HTML map container -->
<div class="map_container_widget">
   %if not hosts:
      <center>
         <h3>We couldn't find any hosts to locate on a map.</h3>
      </center>
      <hr/>
      <p><strong>1. </strong>If you used a filter in the widget, change the filter to try a new search query.</p>
      <p><strong>2. </strong>Only the hosts having GPS coordinates may be located on the map. If you do not have any, add hosts GPS coordinates in the configuration file: </p>
      <code>
      <p># GPS</p>
      <p>_LOC_LAT             45.054700</p>
      <p>_LOC_LNG             5.080856</p>
      </code>
   %else:
      <div id="{{mapId}}" class="osm">
        <div class="alert alert-info">
           <a href="#" class="alert-link">Loading map ...</a>
        </div>
      </div>
   %end
</div>

%include("_worldmap")
