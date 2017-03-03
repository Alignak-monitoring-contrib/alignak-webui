<!-- Hosts location widget -->
%# embedded is True if the widget is got from an external application
%setdefault('embedded', False)
%from bottle import request
%setdefault('links', request.params.get('links', ''))
%setdefault('identifier', 'widget')
%setdefault('credentials', None)

%setdefault('mapId', 'host_location_map')

%worldmap_plugin = webui.find_plugin('Worldmap')
%hosts = [host]
%hosts = worldmap_plugin.get_valid_elements(hosts)

<script>
   var cssfiles=['/static/plugins/worldmap/static/css/leaflet.css', '/static/plugins/worldmap/static/css/MarkerCluster.css', '/static/plugins/worldmap/static/css/MarkerCluster.Default.css', '/static/plugins/worldmap/static/css/leaflet.label.css', '/static/plugins/worldmap/static/css/worldmap.css'];

   $.getCssFiles(cssfiles, function(){
      var jsfiles=['/static/plugins/worldmap/static/js/worldmap.js'];

      $.getJsFiles(jsfiles, function(){
      });
   });

   // Tabs management
   $('a[href="#host_tab_location"]').on("shown.bs.tab", function(e) {
      /*
      // Map height to be scaled inside the window
      var mapOffset = $('#{{mapId}}').offset().top;
      var footerOffset = $('footer').offset().top;
      $('#{{mapId}}').height(footerOffset - mapOffset - 35)

      mapResize_{{mapId}}();
      */
   });
   $('a[href="#host_tab_location"]').on("hidden.bs.tab", function(e) {
   });
</script>
<!-- HTML map container -->
<div class="map_container">
   %if not hosts:
      <center>
         <h3>{{_('We could not find any hosts to locate on a map.')}}</h3>
      </center>
   %else:
      <div id="{{mapId}}">
         <div class="alert alert-info">
           <a href="#" class="alert-link">{{_('Loading map ...')}}</a>
         </div>
      </div>
   %end
</div>

%include("_worldmap")
