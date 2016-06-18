%setdefault('debug', True)

%from bottle import request
%rebase("layout", title=title, js=['realms/htdocs/js/jstree/jstree.min.js'], css=['realms/htdocs/css/default/style.min.css'], page="/realm")

%from alignak_webui.utils.helper import Helper

<style>
   // Get sure that jsTree context menu is visible ...
   .jstree-contextmenu {
       z-index: 1000;
   }
</style>

<!-- Realm view -->
<div id="realm">
   %if debug:
   <div class="panel-group">
      <div class="panel panel-default">
         <div class="panel-heading">
            <h4 class="panel-title">
               <a data-toggle="collapse" href="#collapse1"><i class="fa fa-bug"></i> Realms as dictionaries</a>
            </h4>
         </div>
         <div id="collapse1" class="panel-collapse collapse">
            <ul class="list-group">
               %for realm in realms:
                  <li class="list-group-item">
                     <small>Host: {{realm}} - {{realm.__dict__}}</small>
                  </li>
               %end
            </ul>
            <div class="panel-footer">{{len(realms)}} elements</div>
         </div>
      </div>
   </div>
   %end

   <div class="panel panel-default">
      <div class="panel-body">
      %if not realms:
         %include("_nothing_found.tpl", search_string=search_string)
      %else:

         <!-- Tree structure to display realms -->
         <div id="realmsTree"></div>

         %# First element for global data
         %object_type, start, count, total, dummy = pagination[0]
         <i class="pull-right small">{{_('%d elements out of %d') % (count, total)}}</i>

         <table class="table table-condensed">
            <thead><tr>
               <th width="40px"></th>
               <th>{{_('Realm name')}}</th>
               <th>{{_('Level')}}</th>
               <th>{{_('Check command')}}</th>
               <th>{{_('Active checks enabled')}}</th>
               <th>{{_('Passive checks enabled')}}</th>
               <th>{{_('Business impact')}}</th>
            </tr></thead>

            <tbody>
               %for realm in realms:
               <tr id="#{{realm.id}}">
                  <td title="{{realm.alias}}">
                     {{! realm.get_html_state(text=None, title=_('No livestate for this element'))}}
                  </td>

                  <td>
                     <small>{{!realm.html_link}}</small>
                  </td>

                  <td>
                     <small>{{realm._level}}</small>
                  </td>

               </tr>
             %end
            </tbody>
         </table>
      %end
      </div>
   </div>
 </div>

 <script>
   debugJs = true;
   // Build tree data...
   var jsTreeData = [];
   %for realm in realms:
      jsTreeData.push( {
         "id": '{{realm.id}}',
         "parent" : '{{'#' if realm._level == 0 else realm._tree_parents[0]}}',
         "text": '{{realm.alias}}',
         "icon": "",
         "state": {
            "opened": true,
            "selected": false,
            "disabled": false
         },
         li_attr: {
            "realm_id" : '{{realm.id}}'
         },
         a_attr: {
         }
      } );
   %end

dc = {
   tree: {
    // Include hosts in tree view
    hosts: true,
    // Hosts filter
    // '' for no filtering
    hostsFilter: '',
    // Maximum hosts
    maxHosts: 2000,
    hostsStateFilter: ['DOWN', 'UP', 'UNREACHABLE'],

    // Include services in tree view
    services: true,
    // Services filter (list of services to display)
    // '*' for all services
    // '' for no services
    servicesFilter: '*',
    servicesStateFilter: ['WARNING', 'CRITICAL'],

    "contextmenu" : {
      "active" : true
    },

    // Host / services icon types
    "types" : {
      "default" : {
        "icon" : "ion-navicon text-teal"
      },

      // Depending upon host global state
      "hostUP" : {
        "icon" : "ion-checkmark text-green"
        , "display": true
      },
      "hostDOWN" : {
        "icon" : "ion-close text-red"
        , "display": true
      },
      "hostUNREACHABLE" : {
        "icon" : "ion-minus text-yellow"
        , "display": true
      },
      "hostPENDING" : {
        "icon" : "ion-minus text-teal"
        , "display": true
      },
      "hostACK" : {
        "icon" : "ion-medkit text-blue"
        , "display": true
      },

      // All services of the host are Ok
      "hostServicesOK" : {
        "icon" : "ion-plus text-teal"
        , "display": true
      },

      // Depending upon service state
      "serviceOK" : {
        "icon" : "ion-checkmark text-green"
        , "display": false
      },
      "serviceCRITICAL" : {
        "icon" : "ion-close hostDOWN text-red"
        , "display": true
      },
      "serviceWARNING" : {
        "icon" : "ion-alert text-yellow"
        , "display": true
      },
      "servicePENDING" : {
        "icon" : "ion-minus text-teal"
      },
      "serviceUNKNOWN" : {
        "icon" : "ion-minus text-teal"
        , "display": true
      },
      "serviceACK" : {
        "icon" : "ion-medkit text-blue"
        , "display": true
      }
    }
  }
};

   $(document).ready(function(){
      set_current_page("{{ webui.get_url(request.route.name) }}");

      // Realms tree ...
      $('#realm div.panel-body').prepend('<hr>');
      $('#realm div.panel-body').prepend('<input id="searchfield" type="text">');
      $('#realm div.panel-body').prepend(dc.loader);

      var to=null;
      $('#searchfield').keyup(function () {
        if(to) { window.clearTimeout(to); }
        to = setTimeout(function () {
          var v = $('#searchfield').val();
          $("#realmsTree").jstree(true).search(v);
        }, 250);
      });

      $("#realmsTree")
         .jstree({
            "core" : {
               "check_callback" : true,
               "data" : jsTreeData
            },
            "plugins" : [
               dc.tree.types ? "types" : null,
               dc.tree.contextmenu ? "contextmenu" : null,
               "checkbox",
               "sort",
               "search"
            ],
            "search": { "show_only_matches": true },
            "types" : dc.tree.types,
            "contextmenu": {
            "items": function(node) {
              if (debugJs) console.debug('Calling context menu for: ', node);
              // Non terminating node ...
              if (node.children.length && !node.host_name) {
                // Should deal here with hostgroup acknowledge ...
                return;
              }

              var tree = $("#realmsTree").jstree(true);

              return ({
                "Acknowledge": ((node.service_state != "OK") && ((! node.service_ack))) ? {
                  "label": (node.service_name) ? "Acquitter le problème" : "Acquitter tous les problèmes de la borne",
                  "icon": node.service_name ? "ion-cube" : "ion-monitor",
                  "action": function (obj) {
                    if (node.service_name) {
                      if (! node.service_ack) {
                        $.when(
                          /* Interface WS :
                           * - hostname
                           * - service
                           * - comment
                           * - operation : add (delete)
                           * - sticky: 1 (0)
                           * - notify: 1 (0)
                           * - persistent: 1 (0)
                          */
                          wsCall('kiosks.ackService', {
                            hostname: node.host_name,
                            host_id: node.host_id,
                            service: node.service_name,
                            service_id: node.service_id,
                            comment: "Problème acquitté depuis le dashboard"
                          })
                        )
                        .done( function( response ) {
                          if (response.ok) {
                            console.info('Problem acknowledgement success: ', response);
                            // Set node type
                            $("#realmsTree").jstree(true).set_type(node.id, 'serviceACK');
                            userNotification("Acquittement", node.host_name+'/'+node.service_name, "success", 5000);
                            // alert('Le problème du service' + node.host_name + '/' + node.service_name + ' a été pris en compte.');
                          } else {
                            console.error('Problem acknowledgement error: ', response);
                            userNotification("Acquittement", response.error, "error", 5000);
                            alert('Le problème du service' + node.host_name + '/' + node.service_name + ' n\'a pas été pris en compte !');
                          }
                        })
                        .fail(function(jqXHR, textStatus) {
                          console.error('Problem acknowledgement error: ', response);
                        });
                      } else {
                        alert('Le problème du service' + node.host_name + '/' + node.service_name + ' est déjà pris en compte !');
                      }
                    } else {
                      if (! node.host_ack) {
                        $.when(
                          /* Interface WS :
                           * - hostname
                           * - service
                           * - comment
                           * - operation : add (delete)
                           * - sticky: 1 (0)
                           * - notify: 1 (0)
                           * - persistent: 1 (0)
                          */
                          wsCall('kiosks.ackService', {
                            hostname: node.host_name,
                            host_id: node.host_id,
                            comment: "Problème acquitté depuis le dashboard"
                          })
                        )
                        .done( function( response ) {
                          if (response.ok) {
                            // Set node type
                            $("#realmsTree").jstree(true).set_type(node.id, 'hostACK');
                            userNotification("Acquittement", node.host_name, "success", 5000);
                            // Set children type
                            $.each(node.children, function (index, child) {
                              $("#realmsTree").jstree(true).set_type(child, 'serviceACK');
                              userNotification("Acquittement", node.host_name+'/'+ $("#realmsTree").jstree("get_text", child), "success", 5000);
                            });
                            // for each services ...
                            console.info('Problem acknowledgement success: ', response);
                            // alert('Le problème de la borne ' + node.host_name + ' a été pris en compte.');
                          } else {
                            console.error('Problem acknowledgement error: ', response);
                            userNotification("Acquittement", response, "error", 5000);
                            alert('Le problème de la borne ' + node.host_name + ' n\'a pas été pris en compte !');
                          }
                        })
                        .fail(function(jqXHR, textStatus) {
                          console.error('Problem acknowledgement error: ', response);
                        });
                      } else {
                        alert('Le problème de la borne ' + node.host_name + ' est déjà pris en compte !');
                      }
                    }
                  }
                } : null,
                "Downtime": {
                  "label": "Programmer une maintenance pour "+node.host_name,
                  "icon": "ion-monitor",
                  "action": function (obj) {
                    $.when(
                      /* Interface WS :
                       * - hostname
                       * - comment
                       * - operation : add (delete)
                      */
                      wsCall('kiosks.downtimeHost', {
                        hostname: node.host_name,
                        host_id: node.host_id,
                        comment: "Maintenance dashboard"
                      })
                    )
                    .done( function( response ) {
                      if (response.ok) {
                        console.info('Downtime schedule success: ', response);
                        // Go to ticket page
                        $(':mobile-pagecontainer').pagecontainer('change', '#loginPage');

                        userNotification("Maintenance", node.host_name, "success", 5000);
                        // Set children type
                        $.each(node.children, function (index, child) {
                          $("#realmsTree").jstree(true).set_type(child, 'serviceACK');
                          userNotification("Maintenance", node.host_name+'/'+ $("#realmsTree").jstree("get_text", child), "success", 5000);
                        });
                      } else {
                        console.error('Downtime schedule error: ', response);
                        alert('La maintenance de la borne ' + node.host_name + ' n\'a pas pu être programmée.');
                      }
                    })
                    .fail(function(jqXHR, textStatus) {
                      console.error('Downtime schedule error: ', response);
                    });
                  }
                }
              });
            }
          }
         })

         .bind('ready.jstree', function(e, data) {
            if (! dc.tree.hosts) return;

            var o_realmsTree = $("#realmsTree").jstree(true);
            console.log('ready.jstree', $("#realmsTree").jstree(true), $("#realmsTree").jstree("get_node", "#"));
            /*
            // Iterates through first level nodes ...
            $.each($("#realmsTree").jstree("get_node", "#").children, function (index, child) {
               console.log('ready.jstree, root node child', child);
               var entitiesList = [];
               var node = o_realmsTree.get_node(child);
               var parent =node.li_attr.parent;

               if (o_realmsTree.is_parent(child)) {
                  // Not direct site realm ...
                  $.each(node.children, function (index, child) {
                     var node = o_realmsTree.get_node(child);
                     var parent =node.li_attr.parent;
                     entitiesList.push(parent);
                  });
               } else {
                  // Direct site realm ...
                  entitiesList.push(parent);
               }
            });
            */
            $('#treePage div.loader').remove();
        })

         .bind('select_node.jstree', function(node, selectedNodes) {
            console.debug('Selection :', selectedNodes);
         });

   });
 </script>
