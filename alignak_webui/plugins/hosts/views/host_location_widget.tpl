<!-- Hosts location widget -->
%# embedded is True if the widget is got from an external application
%setdefault('embedded', False)
%from bottle import request
%setdefault('links', request.params.get('links', ''))
%setdefault('identifier', 'widget')
%setdefault('credentials', None)

%setdefault('mapId', 'host_location_map')

%worldmap_plugin = webui.find_plugin('Worldmap')
%if not worldmap_plugin:
   <center>
      <h3>{{_('The worldmap plugin is not installed or enabled.')}}</h3>
   </center>
%else:
%hosts = [host]
%hosts = worldmap_plugin.get_map_elements(hosts)

<script>
   // Tabs management
   $('a[href="#host_tab_location"]').on("shown.bs.tab", function(e) {
      // Map resizing is bound to the window resize event...
      $(window).trigger("resize");
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

%include("_worldmap", load=True)
%end
