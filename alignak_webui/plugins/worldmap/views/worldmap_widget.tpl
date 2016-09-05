<!-- Hosts worldmap widget -->
%# embedded is True if the widget is got from an external application
%setdefault('embedded', False)
%from bottle import request
%setdefault('links', request.params.get('links', ''))
%setdefault('identifier', 'widget')
%setdefault('credentials', None)

%from alignak_webui.utils.helper import Helper

%setdefault('mapId', 'hosts_worldmap')

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
