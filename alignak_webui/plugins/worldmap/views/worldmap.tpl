%setdefault('debug', False)

%setdefault('mapStyle', "width: 100%; height: 100%;")

%from bottle import request
%search_string = request.query.get('search', '')

%# Add extra Css and Js for this page, and a callback function
%css=["worldmap/static/leaflet/leaflet.css", "worldmap/static/css/MarkerCluster.css", "worldmap/static/css/MarkerCluster.Default.css", "worldmap/static/css/worldmap.css", "worldmap/static/geocoder/Control.OSMGeocoder.css", "worldmap/static/geocoder2/Control.Geocoder.css"]
%js=["worldmap/static/leaflet/leaflet.js", "worldmap/static/geocoder/Control.OSMGeocoder.js", "worldmap/static/geocoder2/Control.Geocoder.js", "worldmap/static/js/leaflet.markercluster.js", "worldmap/static/js/leaflet.Icon.Glyph.js", "worldmap/static/js/worldmap.js"]
%callback='initWorldmap'

%# No default refresh for this page
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

   <div class="dropup" id="selected_hosts">
      <button id="dd_selected" class="btn btn-default dropdown-toggle" type="button" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
         <span class="fa-stack" style="font-size:0.63em;"><i class="fa fa-check"></i><i class="fa fa-ban fa-stack-2x text-danger"></i></span>{{_('Selected hosts')}}
         <span class="caret"></span>
      </button>
      <ul class="dropdown-menu" aria-labelledby="dd_selected">
      </ul>
   </div>


   <div class="dropup" id="not_positioned_hosts">
      <button id="dd_notpositioned" class="btn btn-default dropdown-toggle" type="button" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
         <span class="fa-stack" style="font-size:0.63em;"><i class="fa fa-globe"></i><i class="fa fa-ban fa-stack-2x text-danger"></i></span>{{_('Hosts not positioned on the map.')}}
         <span class="caret"></span>
      </button>
      <ul class="dropdown-menu" aria-labelledby="dd_notpositioned">
      </ul>
   </div>

   %include("_worldmap")
</div>
