%setdefault('debug', False)

%setdefault('mapStyle', "width: 100%; height: 100%;")

%from bottle import request
%search_string = request.query.get('search', '')

%# Add extra Css and Js for this page, and a callback function
%# No default refresh for this page
%css=["worldmap/static/leaflet/leaflet.css", "worldmap/static/css/MarkerCluster.css", "worldmap/static/css/MarkerCluster.Default.css", "worldmap/static/css/leaflet.label.css", "worldmap/static/css/worldmap.css"]
%js=["worldmap/static/leaflet/leaflet.js", "worldmap/static/js/leaflet.markercluster.js", "worldmap/static/js/leaflet.Icon.Glyph.js", "worldmap/static/js/leaflet.label.js", "worldmap/static/js/worldmap.js"]
%callback='initWorldmap'
%rebase("layout", title=title, js=js, css=css, callback=callback, pagination=pagination, page="/worldmap", refresh=False)

<!-- HTML map container -->
<div id="worldmap" class="card map_container" style="{{mapStyle}}">
   %if not hosts:
      <div class="panel-heading">
         <center class="alert-warning">
            <h3>{{_('We could not find any hosts to locate on a map.')}}</h3>
         </center>
      </div>
   %else:
      <div id="{{mapId}}">
         <div class="alert alert-info">
            <a href="#" class="alert-link">{{_('Loading map ...')}}</a>
         </div>
      </div>
   %end

   %include("_worldmap")
</div>
