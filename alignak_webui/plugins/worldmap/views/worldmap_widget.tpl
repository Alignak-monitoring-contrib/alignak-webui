<!-- Hosts worldmap widget -->
%# embedded is True if the widget is got from an external application
%setdefault('embedded', False)
%from bottle import request
%setdefault('links', request.params.get('links', ''))
%setdefault('identifier', 'widget')
%setdefault('credentials', None)

%from alignak_webui.utils.helper import Helper

%plugin = webui.find_plugin('Worldmap')
%(hosts, _) = plugin.get_map_elements(elements)
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
