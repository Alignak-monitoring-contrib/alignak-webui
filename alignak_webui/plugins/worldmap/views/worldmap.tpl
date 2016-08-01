%setdefault('debug', False)

%from bottle import request
%search_string = request.query.get('search', '')

%# No default refresh for this page
%rebase("layout", title=title, js=[], css=['worldmap/htdocs/css/worldmap.css', 'worldmap/htdocs/css/leaflet.css', 'worldmap/htdocs/css/MarkerCluster.css', 'worldmap/htdocs/css/MarkerCluster.Default.css', 'worldmap/htdocs/css/leaflet.label.css'], pagination=pagination, page="/worldmap", refresh=False)

%from alignak_webui.utils.helper import Helper

<!-- HTML map container -->
<div class="map_container">
   %if not hosts:
   <div class="panel-heading">
      <center class="alert-warning">
         <h3>We couldn't find any hosts to locate on a map.</h3>
      </center>
   </div>
   %else:
     <div id="{{mapId}}" class="osm">
       <div class="alert alert-info">
          <a href="#" class="alert-link">Loading map ...</a>
       </div>
     </div>
   %end

   %include("_worldmap")
</div>
