%setdefault('debug', False)

%from bottle import request
%search_string = request.query.get('search', '')

%# No default refresh for this page
%rebase("layout", title=title, js=[], css=['worldmap/htdocs/css/worldmap.css', 'worldmap/htdocs/css/leaflet.css', 'worldmap/htdocs/css/MarkerCluster.css', 'worldmap/htdocs/css/MarkerCluster.Default.css', 'worldmap/htdocs/css/leaflet.label.css'], pagination=pagination, page="/worldmap", refresh=False)

%from alignak_webui.utils.helper import Helper

<script>
   $(document).ready(function() {
      // Map height to be scaled inside the window
      var mapOffset = $('#{{mapId}}').offset().top;
      var footerOffset = $('footer').offset().top;
      $('#{{mapId}}').height(footerOffset - mapOffset - 35)

      mapResize_{{mapId}}();
   });
</script>

<!-- HTML map container -->
<div id="worldmap" class="card map_container" style="padding:10px; margin-top: 10px">
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
