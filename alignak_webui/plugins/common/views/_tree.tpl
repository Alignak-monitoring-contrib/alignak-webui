%import json

%setdefault('debug', False)
%setdefault('selectable', True)
%setdefault('context_menu', True)

%from bottle import request
%search_string = request.query.get('search', '')

%# jsTree js and css are included in the page layout
%rebase("layout", title=title, page="/{{tree_type}}/tree")

%from alignak_webui.utils.helper import Helper

<style>
   // Get sure that jsTree context menu is visible ...
   .jstree-contextmenu {
       z-index: 1000;
   }

.vcenter {
    display: inline-block;
    vertical-align: middle;
    height: 40px;
}
</style>

<!-- Tree display -->
<div id="{{tree_type}}s_tree_view">
   %if debug:
   <div class="panel-group">
      <div class="panel panel-default">
         <div class="panel-heading">
            <h4 class="panel-title">
               <a data-toggle="collapse" href="#{{tree_type}}_tree_collapse"><i class="fa fa-bug"></i> Elements as dictionaries</a>
            </h4>
         </div>
         <div id="{{tree_type}}_tree_collapse" class="panel-collapse collapse">
            <ul class="list-group">
               %for item in elts:
                  <li class="list-group-item">
                     <small>Element: {{item}} - {{item.__dict__}}</small>
                  </li>
               %end
            </ul>
            <div class="panel-footer">{{len(elts)}} elements</div>
         </div>
      </div>
   </div>
   %end

   %if not elts:
      %include("_nothing_found.tpl", search_string=search_string)
   %else:
      <div class="panel panel-default">
         <div class="panel-heading clearfix">
            <div class="pull-left">
               <button type="button" class="btn btn-xs btn-raised"
                  data-action="navigate-table" data-element="{{tree_type}}">
                  <span class="fa fa-table"></span>
               </button>
            </div>
            <h4 class="pull-left">
               &nbsp;{{title}}
            </h4>

            <div class="pull-right">
               <form class="hidden-xs navbar-form navbar-right" role="search">
                  <span class="fa fa-search"></span>&nbsp;
                  <input id="searchfield" type="text" placeholder="{{_('search...')}}">
               </form>
            </div>
         </div>

         <div class="panel-body">
            <div class="row">
               <div class="col-sm-6 col-xs-12">
                  <!-- Tree structure to display items -->
                  <div id="{{tree_type}}_tree"></div>
               </div>
               <div id="members_list" class="col-sm-6 col-xs-12">
                  <div class="alert alert-info">
                     {{_('Select an item in the left tree to display some elements.')}}
                  </div>
               </div>
            </div>
         </div>
      </div>
   %end
</div>

<script>
   var debugTree = true;

   // Navigate to the table view
   $('[data-action="navigate-table"][data-element="{{tree_type}}"]').on("click", function () {
      var elt_id = $(this).data('element');
      window.setTimeout(function(){
         window.location.href = "/{{tree_type}}s/table";
      }, 50);
   });

   // Build tree data...
   var jsTreeData = [];
   %for item in elts:
      %parent='#'
      %if 'parent' in item.__dict__:
      %  parent=item.parent.id
      %end
      %level=item.__dict__.get('level', 0)
      jsTreeData.push( {
         "id": '{{item.id}}',
         "parent" : '{{'#' if parent=='#' else item.parent.id}}',
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
      });
      if (debugTree) console.log('Added: ', '{{item.id}}', '{{item.name}}', '{{level}}', '{{parent}}');
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
            $("#{{tree_type}}_tree").jstree(true).search(v);
         }, 250);
      });

      $("#{{tree_type}}_tree")
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
                  if (debugTree) console.log('Calling context menu for: ', node);

                  // Non terminating node ...
                  if (node.children.length && !node.host_name) {
                     return;
                  }

                  var tree = $("#{{tree_type}}_tree").jstree(true);
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
            var o_{{tree_type}}_tree = $("#{{tree_type}}_tree").jstree(true);
            if (debugTree) console.log('Tree ready!');
         })

         %if selectable:
         .bind('select_node.jstree', function(node, selectedNodes) {
            if (debugTree) console.log('Selection :', selectedNodes);
         })
         %end

         .bind('changed.jstree', function(event, action) {
            if (debugTree) console.log('Changed :', action.action, action.node);

            if (action.action == 'select_node') {
               if (debugTree) console.log('Selected :', action.node);

               $.ajax( {
                  "url": "/{{tree_type}}/members/" + action.node.id,
                  "dataType": "json",
                  "type": "GET",
                  "success": function (data) {
                     if (debugTree) console.debug("Got data:", data);

                     $("#members_list").slideUp('fast', function() {
                        $(this).empty();

                        $(data).each(function(idx, elt){
                           if (debugTree) console.debug("Element:", elt);

                           $('<div id="member_' + elt.id + '" />')
                              .append(elt.icon)
                              .append(elt.url)
                              .appendTo('#members_list');
                        });

                        $("#members_list")
                           .slideDown('slow');
                     });

                  },
                  "error": function (jqXHR, textStatus, errorThrown) {
                     console.error("Get list error: ", textStatus, jqXHR);
                  }
               });
            }
            if (action.node.children.length === 0 && action.node.host_name) {
               // Node has no child...
            } else {
               // Node has children ...
               $.each(action.node.children, function (index, child) {
                  var childNode = $('#{{tree_type}}_tree').jstree(true).get_node(child);
                  if (debugTree) console.log('Child:', childNode);
               });
            }
         });
   });
 </script>
