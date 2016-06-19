%import json

%setdefault('debug', False)
%setdefault('selectable', True)
%setdefault('context_menu', True)

%from bottle import request
%# jsTree js and css are included in the page layout
%rebase("layout", title=title, page="/{{object_type}}_tree")

%from alignak_webui.utils.helper import Helper

<style>
   // Get sure that jsTree context menu is visible ...
   .jstree-contextmenu {
       z-index: 1000;
   }
</style>

<!-- Tree display -->
<div id="{{object_type}}_tree_view">
   %if debug:
   <div class="panel-group">
      <div class="panel panel-default">
         <div class="panel-heading">
            <h4 class="panel-title">
               <a data-toggle="collapse" href="#{{object_type}}_tree_collapse"><i class="fa fa-bug"></i> Elements as dictionaries</a>
            </h4>
         </div>
         <div id="{{object_type}}_tree_collapse" class="panel-collapse collapse">
            <ul class="list-group">
               %for item in items:
                  <li class="list-group-item">
                     <small>Host: {{item}} - {{item.__dict__}}</small>
                  </li>
               %end
            </ul>
            <div class="panel-footer">{{len(items)}} elements</div>
         </div>
      </div>
   </div>
   %end

   %if not items:
      %include("_nothing_found.tpl", search_string=search_string)
   %else:
      <div class="panel panel-default">
         <div class="panel-heading">
            <h4 class="panel-title">
               {{title}}
               <div class="pull-right">
                  <span class="fa fa-search"></span>&nbsp;
                  <input id="searchfield" type="text" placeholder="{{_('search...')}}">
               </div>
            </h4>
         </div>
         <div class="panel-body">
            <!-- Tree structure to display items -->
            <div id="{{object_type}}_tree"></div>
         </div>
      </div>
   %end
</div>

<script>
   debugJs = true;
   // Build tree data...
   var jsTreeData = [];
   %for item in items:
      jsTreeData.push( {
         "id": '{{item.id}}',
         "parent" : '{{'#' if item._level == 0 else item._tree_parents[0]}}',
         "text": '{{item.alias}}',
         "icon": '{{item.get_state()}}',
         "state": {
            "opened": true,
            "selected": false,
            "disabled": false
         },
         "data": {
            %for key in item.__dict__:
            %try:
            "{{key}}": {{! json.dumps(item[key])}},
            %except TypeError:
            %pass
            %end
            %end
         },
         li_attr: {
            "item_id" : '{{item.id}}'
         },
         a_attr: {
         }
      } );
   %end

   $(document).ready(function(){
      set_current_page("{{ webui.get_url(request.route.name) }}");

      var to=null;
      $('#searchfield').keyup(function () {
         if (to) {
            window.clearTimeout(to);
         }
         to = setTimeout(function () {
            var v = $('#searchfield').val();
            $("#{{object_type}}_tree").jstree(true).search(v);
         }, 250);
      });

      $("#{{object_type}}_tree")
         .jstree({
            "core" : {
               "check_callback" : true,
               "data" : jsTreeData
            },
            "plugins" : [
               "sort",
               %if selectable:
               "checkbox",
               %end
               "search",
               %if context_menu:
               "contextmenu"
               %end
            ],
            "search": { "show_only_matches": true },
            %if context_menu:
            "contextmenu": {
               "items": function(node) {
                  if (debugJs) console.debug('Calling context menu for: ', node);

                  // Non terminating node ...
                  if (node.children.length && !node.host_name) {
                     return;
                  }

                  var tree = $("#{{object_type}}_tree").jstree(true);
                  return ({
                  %for action in context_menu['actions']:
                     "{{action}}": {
                        "label": "{{context_menu['actions'][action]['label']}}",
                        "icon": "{{context_menu['actions'][action]['icon']}}",
                        "action": {{! context_menu['actions'][action]['action']}}
                     },
                  %end
                  });
               }
            }
            %end
         })
         .bind('ready.jstree', function(e, data) {
            var o_{{object_type}}_tree = $("#{{object_type}}_tree").jstree(true);
            console.debug('Ready!');
         })

         %if selectable:
         .bind('select_node.jstree', function(node, selectedNodes) {
            if (debugJs) console.debug('Selection :', selectedNodes);
         })
         %end

         .bind('changed.jstree', function(event, action) {
            if (debugJs) console.debug('Changed :', action.action, action.node);

            if (action.node.children.length === 0 && action.node.host_name) {
               // Node has no child...
            } else {
               // Node has children ...
               $.each(action.node.children, function (index, child) {
                  var childNode = $('#{{object_type}}_tree').jstree(true).get_node(child);
                  if (debugJs) console.debug('Child:', childNode);
               });
            }
         });
   });
 </script>
