%setdefault('debug', False)

%from bottle import request
%search_string = request.query.get('search', '')

%rebase("layout", title=title, js=[], css=[], refresh=False, pagination=None, page="/hosts/templates")

%from alignak_webui.utils.helper import Helper

<style>
   .well .form-group {
      margin-bottom: 20px;
   }
</style>
<!-- hosts filtering and display -->
<div id="hosts-templates">
   %if debug:
   <div class="panel-group">
      <div class="panel panel-default">
         <div class="panel-heading">
            <h4 class="panel-title">
               <a data-toggle="collapse" href="#collapse1"><i class="fa fa-bug"></i> Hosts as dictionaries</a>
            </h4>
         </div>
         <div id="collapse1" class="panel-collapse collapse">
            <ul class="list-group">
               %for host in elts:
               <div class="panel panel-default">
                  <div class="panel-heading">
                     <h4 class="panel-title">
                        <a data-toggle="collapse" href="#collapse_{{host.id}}"><i class="fa fa-bug"></i> {{host.name}}</a>
                     </h4>
                  </div>
                  <div id="collapse_{{host.id}}" class="panel-collapse collapse">
                     <dl class="dl-horizontal" style="height: 200px; overflow-y: scroll;">
                        %for k,v in sorted(host.__dict__.items()):
                           <dt>{{k}}</dt>
                           <dd>{{v}}</dd>
                        %end
                     </dl>
                  </div>
               </div>
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
      <div class="panel-body">
         %if edition_mode:
         <form role="form" data-element="None" class="element_form" method="post" action="/host_form/None">
            <div class="well page">
            <fieldset>
               <legend>{{_('Creating a new host:')}}</legend>

               <div class="alert alert-dismissible alert-info">
                  <button type="button" class="close" data-dismiss="alert">×</button>
                  <h4>{{_('Creating a new host:')}}</h4>
                  <hr/>
                  <p>{{_('You must define a name for your new host. It must match the computer hostname.')}}</p>
                  <p>{{_('You can define an alias (friendly name) for your new host.')}}</p>
                  <p>{{_('Specify if the new host is a template and / or if it is based upon one (or several) template(s).')}}</p>
               </div>
               <script>
                  window.setTimeout(function() { $("div.alert-dismissible").alert('close'); }, 10000);
               </script>

               <div class="form-group">
                   <label class="control-label" for="name">{{_('Host name:')}}</label>
                   <input class="form-control" type="text" id="name" name="name" placeholder="{{_('Host name')}}"  value="">
                   <p class="help-block">{{_('The host name must be unique in the whole monitored system.')}}</p>
               </div>

               <div class="form-group">
                  <label class="control-label" for="name">{{_('Host alias:')}}</label>
                  <input class="form-control" type="text" id="alias" alias="alias" placeholder="{{_('Host alias')}}"  value="">
                  <p class="help-block">{{_('The host alias is used as a friendly name for the host in the Web UI.')}}</p>
               </div>

               <div class="form-group">
                  <label class="control-label" for="address">{{_('Host address:')}}</label>
                  <input class="form-control" type="text" id="address" name="address" placeholder="{{_('0.0.0.0')}}"  value="">
                  <p class="help-block">{{_('The host address is not mandatory and it can be an IP address or a name resolved thanks to DNS.')}}</p>
               </div>

               <div class="form-group">
                   <label class="control-label" for="realm">{{_('Realm:')}}</label>
                   <input class="form-control" type="text" id="realm" realm="realm" placeholder="{{_('Host realm')}}"  value="">
                   <p class="help-block">{{_('The host realm must be unique in the whole monitored system.')}}</p>
               </div>

               <div class="form-group">
                  <div class="checkbox">
                     <div class="togglebutton col-xs-8">
                        <label for="_is_template">
                           <input type="checkbox" id="_is_template" name="_is_template"> {{_('Host is a template:')}}
                           <p class="help-block">
                              {{_('Indicate if the host to be created is a template or a real host.')}}
                           </p>
                        </label>
                     </div>
                  </div>
               </div>
            </fieldset>
            </div>

            <div class="well form-group">
               <button type="reset" class="btn btn-default pull-left">{{_('Cancel')}}</button>
               <button type="submit" class="btn btn-primary pull-right">{{_('Submit')}}</button>
               <div class="clearfix"></div>
            </div>

         <div class="well page">
         <fieldset>
            <legend>{{_('Choose the inherited templates:')}}</legend>
         %end

         %# First element for global data
         %object_type, start, count, total, dummy = pagination[0]
         <i class="pull-right small">{{_('%d elements out of %d') % (count, total)}}</i>

         <table class="table table-condensed">
            <thead><tr>
               <th>{{_('Template name')}}</th>
               <th>{{_('Inherits from')}}</th>
               <th>{{_('Notes / description')}}</th>
            </tr></thead>

            <tbody>
            %for elt in elts:
               <tr id="#{{elt.id}}">
                  %if edition_mode:
                  <td>
                     <div class="input-group input-group-sm" title="{{_('Check this to select the template')}}">
                        <div class="togglebutton">
                           <label>
                              %if edition_mode:
                              <input id="{{elt.name}}" name="{{elt.name}}" type="checkbox" data-linked="{{','.join([t.name for t in elt._templates])}}" data-id="{{elt.id}}">
                              %end
                           </label>
                           {{elt.alias}} (<small>{{elt.name}}</small>)
                        </div>
                     </div>
                  </td>
                  %end
                  <td>
                     %for tpl in elt._templates:
                     <small>{{!tpl.get_html_link()}}</small>
                     %end
                  </td>

                  <td>
                     <small>{{elt.notes}}</small>
                  </td>
               </tr>
            %end
            </tbody>
         </table>

         %if edition_mode:
         </fieldset>
         </div>
         </form>
         %end
      </div>
   </div>
   %end
</div>

<script>
   $(document).ready(function(){
      set_current_page("{{ webui.get_url(request.route.name) }}");

      %icon=''
      %from alignak_webui.objects.element_state import ElementState
      %icon = ElementState().get_icon_state('realm', 'unknown')
      %icon=icon['icon'] if icon else ''
      $('#realm').selectize({
         'plugins': ["remove_button"],

         valueField: 'id',
         labelField: 'name',
         searchField: 'name',
         create: false,

         render: {
            option: function(item, escape) {
               return '<div>' +
                  %if icon:
                  '<i class="fa fa-{{icon}}"></i>&nbsp;' +
                  %end
                  (item.name ? '<span class="name">' + escape(item.name) + '</span>' : '') +
                  (item.alias ? '<small><em><span class="alias"> (' + escape(item.alias) + ')</span></em></small>' : '') +
               '</div>';
            },
            item: function(item, escape) {
               return '<div>' +
                  %if icon:
                  '<i class="fa fa-{{icon}}"></i>&nbsp;' +
                  %end
                  (item.name ? '<span class="name">' + escape(item.name) + '</span>' : '') +
               '</div>';
            }
         },

         preload: true,
         openOnFocus: true,
         load: function(query, callback) {
            $.ajax({
               url: "/realms/list",
               type: 'GET',
               error: function() {
                  callback();
               },
               success: function(res) {
                  // 10 first items only...
                  // callback(res.slice(0, 10));
                  callback(res);
               }
            });
         },

         maxItems: 1,
         closeAfterSelect: true,

         hideSelected: true,
         allowEmptyOption: true
      });
      // Add selected options / items to the control...
      var selectize = $('#realm').selectize();
   });

   %if edition_mode:
      function change_linked_recursively(links, check_state) {
         if (links == undefined) return false;
         $.each(links.split(','), function(idx, link) {
            if (link == undefined) return false;
            $('#'+link).prop('checked', check_state);

            var linked = $('#'+link).data("linked");
            if (linked != '') {
               change_linked_recursively(linked, check_state);
            }
         });
      }

      $('div.togglebutton input').on('click', function(e) {
         var check_state = $(this).is(":checked");
         $(this).prop('checked', check_state);

         var linked = $(this).data("linked");
         if (linked != '') {
            change_linked_recursively(linked, check_state);
         }
      });

      $('form[data-element="None"]').on("submit", function (evt) {
         // Do not automatically submit ...
         evt.preventDefault();

         var templates = [];
         $('div.togglebutton input').each(function(idx, box) {
            var check_state = $(box).is(":checked");
            if (check_state) {
               templates.push($(box).data('id'));
            }
         });
         if (templates.join(',') == '') {
            templates = [];
         }

         // Submitting message
         wait_message('{{_('Submitting form...')}}', true)

         $.ajax({
            url: $(this).attr('action'),
            type: $(this).attr('method'),
            data: {
               "name": $("#name").val(),
               "_realm": $("#realm").val(),
               "address": $("#address").val(),
               "alias": $("#alias").val(),
               "_is_template": $("#_is_template").prop('checked'),
               "_templates": templates
            }
         })
         .done(function(data, textStatus, jqXHR) {
            console.log(data);
            // data is JSON formed with a _message field
            if (jqXHR.status != 200) {
               console.error(jqXHR.status, data);
               raise_message_ko(data._message);
            } else {
               if (data._errors) {
                  raise_message_ko(data._message);
                  $.each(data._errors, function(field, value){
                     $('#'+field).parents("div.form-group").addClass("has-error");
                     raise_message_ko(field + ":" + value);
                  })
               } else {
                  raise_message_info(data._message);

                  $.each(data, function(field, value) {
                     if (field=='_message') return true;
                     if (field=='_errors') return true;
                     $('#'+field).parents("div.form-group").addClass("has-success");
                     raise_message_ok("Updated " + field);
                  });

                  // Navigate to the new element edition form
                  var url = document.location.href;
                  url = url.replace("None", data['_id']);
                  window.setTimeout(function(){
                     window.location.href = url;
                  }, 3000);
               }
            }
         })
         .fail(function( jqXHR, textStatus, errorThrown ) {
            // data is JSON formed with a _message field
            if (jqXHR.status != 409) {
               console.error(errorThrown, textStatus);
            } else {
               raise_message_info(data._message);
               $.each(data, function(field, value){
                  if (field=='_message') return true;
                  $('#'+field).parents("div.form-group").addClass("has-success");
                  raise_message_ok("Updated " + field);
               })
            }
         })
        .always(function() {
            wait_message('', false)
         });
      });
   %end
</script>
