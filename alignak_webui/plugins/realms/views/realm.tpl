%setdefault('debug', True)

%rebase("layout", title=title, js=[realms/htdocs/js/jstree.min.js], css=[], page="/realm")

%from alignak_webui.utils.helper import Helper

<style>
   // Get sure that jsTree context menu is visible ...
   .jstree-contextmenu {
       z-index: 1000;
   }
</style>

<!-- Realm view -->
<div id="realm">
   %realm_id = realm.id
   %#services = datamgr.get_services(search={'where': {'realm':realm_id}})
   %#livestate = datamgr.get_livestate(search={'where': {'type': 'realm', 'name':'%s' % realm.name}})
   %#livestate = livestate[0] if livestate else None

   %if debug:
   <div class="panel-group">
      <div class="panel panel-default">
         <div class="panel-heading">
            <h4 class="panel-title">
               <a data-toggle="collapse" href="#collapse_{{realm_id}}"><i class="fa fa-bug"></i> Realm as dictionary</a>
            </h4>
         </div>
         <div id="collapse_{{realm_id}}" class="panel-collapse collapse">
            <dl class="dl-horizontal" style="height: 200px; overflow-y: scroll;">
               %for k,v in sorted(realm.__dict__.items()):
                  <dt>{{k}}</dt>
                  <dd>{{v}}</dd>
               %end
            </dl>
         </div>
      </div>
   </div>
   %end

 </div>
