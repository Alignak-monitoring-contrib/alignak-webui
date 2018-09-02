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

   .member {
      background-color: #eee;
   }

   #tree_search {
      color: black !important;
   }

   .tree_state{
      width: 20px;
   }
   .tree_url{
      width: 200px;
   }
   .tree_bi{
      width: 40px;
   }
   .tree_lc{
      width: 60px;
   }
   .tree_lsc{
      width: 60px;
   }
   .tree_output{
      width: 100%;
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
                  <input id="tree_search" type="text" placeholder="{{_('search...')}}">
               </form>
            </div>
         </div>

         <div class="panel-body">
            <div class="row">
               %if tree_items:
               <div class="col-md-4 col-sm-6 col-xs-12">
                  <!-- Tree structure to display items -->
                  <div id="{{tree_type}}_tree"></div>
               </div>
               <div id="right_panel" class="col-md-8 col-sm-6 col-xs-12">
                  <div class="card alert alert-dismissible alert-info">
                     <button type="button" class="close" data-dismiss="alert">×</button>
                     <h4>{{_('Select an item in the left tree to display more elements.')}}</h4>
                  </div>
                  <script>
                     window.setTimeout(function() { $("#right_panel div.alert-dismissible").alert('close'); }, 3000);
                  </script>
               </div>
               %else:
                  <div class="card alert alert-dismissible alert-danger">
                     <button type="button" class="close" data-dismiss="alert">×</button>
                     <h4>{{_('No available tree view for those elements.')}}</h4>
                  </div>
               %end
            </div>
         </div>
      </div>
   %end
</div>

<script>
   var debugTree = {{'true' if debug else 'false'}};

   // Navigate to the table view
   $('[data-action="navigate-table"][data-element="{{tree_type}}"]').on("click", function () {
      var elt_id = $(this).data('element');
      window.setTimeout(function(){
         window.location.href = "/{{tree_type}}s/table";
      }, 50);
   });

   // Build tree data...
   var jsTreeData = [];
   %for item in tree_items:
      jsTreeData.push({{! json.dumps(item)}})
      if (debugTree) console.log('Added: {{! json.dumps(item)}}');
   %end

   $(document).ready(function(){
      set_current_page("{{ webui.get_url(request.route.name) }}");

      var to=null;
      $('#tree_search').keyup(function () {
         if (to) {
            window.clearTimeout(to);
         }
         to = setTimeout(function () {
            var v = $('#tree_search').val();
            $("#{{tree_type}}_tree").jstree(true).search(v);
         }, 250);
      });

      $("#{{tree_type}}_tree")
         .jstree({
            "core" : {
               "check_callback" : true,   // Allow to change the tree
               "data" : jsTreeData
            },
            "plugins" : [
               "state",
               "sort",
               %if selectable:
               //"checkbox",
               %end
               "search",
               %if context_menu:
               "contextmenu"
               %end
            ],
            "state": {
               "key": "{{tree_type}}_tree",
               "filter": function(state) {
                  if (debugTree) console.log('Restoring saved state: ', state);
               }
            },
            "search": {
               "show_only_matches": true
            },
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
            if (debugTree) console.log('{{tree_type}} tree ready!');
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

               if (action.node.data.type == '{{tree_type}}') {
                  wait_message('{{_('Loading members data...')}}', true);

                  // Try to get node members
                  $.ajax( {
                     "url": "/{{tree_type}}/members/" + action.node.id,
                     "dataType": "json",
                     "type": "GET",
                     "success": function (data) {
                        if (debugTree) console.debug("Got data:", data);

                        $("#right_panel").slideUp(50, function() {
                           $(this).empty();

                           var o = null;

                           $(data).each(function(idx, elt){
                              if (debugTree) console.debug("Element:", elt);

                              if (elt.id == -1) {
                                 o = $(elt.tr).appendTo('#right_panel');
                                 return true;
                              }

                              // Iterates through the selected node children...
                              var found = false;
                              $.each(action.node.children, function (index, child) {
                                 var node = $('#{{tree_type}}_tree').jstree(true).get_node(child);
                                 if (node.id == elt.id) found = true;
                              });
                              if (! found) {
                                 // Create a new child node
                                 var nodeID = $('#{{tree_type}}_tree').jstree(true).create_node(
                                    action.node,
                                    {
                                       "id": elt.id,
                                       "icon": elt.icon,
                                       "text": elt.alias,
                                       "data": elt
                                    },
                                    "last",
                                    function (node) {
                                       if (debugTree) console.log('Created :', node);
                                 });
                              }

                              if (o) {
                                 $('#right_panel table tbody').append(elt.tr);
                              }
                           });

                           $("#right_panel")
                              .slideDown('slow');
                        });

                        wait_message('', false)
                     },
                     "error": function (jqXHR, textStatus, errorThrown) {
                        console.error("Get list error: ", textStatus, jqXHR);
                        wait_message('', false)
                     }
                  });
               } else {
                  $("#right_panel").slideUp(50, function() {
                     $(this).empty();

                     var o = $('<div class="card" style="padding:10px;">')
                        .appendTo('#right_panel');

                     $.ajax({
                        url: '/external/'+action.node.data.type+'/'+action.node.id+'/information'
                     })
                     .done(function(content, textStatus, jqXHR) {
                        $('#right_panel div.card').html(content);

                        $("#right_panel")
                           .slideDown('slow');
                     })
                     .fail(function( jqXHR, textStatus, errorThrown ) {
                        console.error('get tree element, error: ', jqXHR, textStatus, errorThrown);
                        raise_message_ko(errorThrown + ': '+ textStatus);
                     });
                  });
               }
            }
            if (action.node.children.length === 0) {
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
