%setdefault('debug', False)

%setdefault('action_bar', False)

%from bottle import request
%rebase("layout", js=['dashboard/htdocs/js/lodash.js', 'dashboard/htdocs/js/jquery.ui.touch-punch.min.js', 'dashboard/htdocs/js/gridstack.min.js'], css=['dashboard/htdocs/css/dashboard.css', 'dashboard/htdocs/css/gridstack.min.css'], title=title)

<div id="dashboard">
   <table class="table table-invisible table-condensed">
      <tbody>
         <tr>
            %hs = datamgr.get_livesynthesis()['hosts_synthesis']
            %if hs:
            %font='critical' if hs['pct_problems'] >= hs['critical_threshold'] else 'warning' if hs['pct_problems'] >= hs['warning_threshold'] else 'ok'
            <td>
               <center>
                  <a href="{{ webui.get_url('Hosts') }}" class="btn btn-sm">
                     <i class="fa fa-4x fa-server font-greyed"></i>
                     <span class="badger-title"><i class="fa fa-plus" style="color: #ccc"></i>&nbsp;{{_('Hosts')}}</span>
                     <span class="badger-big badger-left badger-info" title="{{_('Number of monitored hosts')}}">{{hs["nb_elts"]}}</span>
                     <span class="badger-big badger-right badger-{{font}}" title="{{_('Number of hosts in problem')}}">{{hs["nb_problems"]}}</span>
                  </a>
               </center>
            </td>
            %end

            %ss = datamgr.get_livesynthesis()['services_synthesis']
            %if ss:
            %font='critical' if ss['pct_problems'] >= ss['critical_threshold'] else 'warning' if ss['pct_problems'] >= ss['warning_threshold'] else 'ok'
            <td>
               <center>
                  <a href="{{ webui.get_url('Services') }}" class="btn btn-sm">
                     <i class="fa fa-4x fa-cubes font-greyed"></i>
                     <span class="badger-title"><i class="fa fa-plus" style="color: #ccc"></i>&nbsp;{{_('Services')}}</span>
                     <div class="badger-big badger-left badger-info" title="{{_('Number of hosts up')}}">{{ss["nb_elts"]}}</div>
                     <div class="badger-big badger-right badger-{{font}}" title="{{_('Number of services in problems')}}">{{ss["nb_problems"]}}</div>
                  </a>
               </center>
            </td>
            %end

            %if hs and ss:
            %problems = hs['nb_problems'] + ss['nb_problems']
            %elements = hs['nb_elts'] + ss['nb_elts']
            %pct_problems = round(100.0 * problems / elements, 2) if elements else 0.0
            %font='critical' if pct_problems >= hs['global_critical_threshold'] else 'warning' if pct_problems >= hs['global_warning_threshold'] else 'ok'
            <td>
               <center>
                  <a href="{{ webui.get_url('Livestate table') }}" class="btn btn-sm">
                     <i class="fa fa-4x fa-exclamation-triangle font-greyed"></i>
                     <span class="badger-title"><i class="fa fa-plus" style="color: #ccc"></i>&nbsp;{{_('Problems')}}</span>
                     <span class="badger-big badger-left badger-info" title="{{_('Number of monitored items')}}">{{hs["nb_elts"] + ss["nb_elts"]}}</span>
                     <span class="badger-big badger-right badger-{{font}}" title="{{_('Number of problems')}}">{{hs["nb_problems"] + ss["nb_problems"]}}</span>
                  </a>
               </center>
            </td>
            %end

            %if hs and ss:

            %# TO BE REPLACED WITH IMPACTS DATA ...

            %problems = hs['nb_problems'] + ss['nb_problems']
            %elements = hs['nb_elts'] + ss['nb_elts']
            %pct_problems = round(100.0 * problems / elements, 2) if elements else 0.0
            %font='critical' if pct_problems >= hs['global_critical_threshold'] else 'warning' if pct_problems >= hs['global_warning_threshold'] else 'ok'
            <td>
               <center>
                  <a href="{{ webui.get_url('Livestate table') }}" class="btn btn-sm">
                     <i class="fa fa-4x fa-bolt font-greyed"></i>
                     <span class="badger-title"><i class="fa fa-plus" style="color: #ccc"></i>&nbsp;{{_('Impacts')}}</span>
                     <span class="badger-big badger-left badger-info" title="{{_('Number of monitored items')}}">{{hs["nb_elts"] + ss["nb_elts"]}}</span>
                     <span class="badger-big badger-right badger-{{font}}" title="{{_('Number of problems')}}">{{hs["nb_problems"] + ss["nb_problems"]}}</span>
                  </a>
               </center>
            </td>
            %end
         </tr>
      </tbody>
   </table>

   %if current_user.can_change_dashboard() and not len(dashboard_widgets):
   <div class="panel panel-default alert-warning" id="propose-widgets" style="margin:10px; display:none">
      <div class="panel-body" style="padding-bottom: -10">
         <center>
            <h3>{{_('You do not have any widgets yet ...')}}</h3>
         </center>
         <hr/>
         <p>
            {{_('Click the ')}}
            <strong>{{_('Add a new widget')}}</strong>
            {{_(' buttton in the menu to list all the available widgets.')}}
         </p>
         <p>
            {{_('Select a proposed widget to view its description.')}}
         </p>
         <p>
            {{_('Click the ')}}
            <strong>{{_('Add widget')}}</strong>
            {{_(' button on top of the description to include the widget in your dashboard.')}}
         </p>
      </div>
   </div>
   %end

   <div class="container-fluid">
      <!-- Widgets loading indicator -->
      <div id="widgets_loading" style="position: absolute; top: 0px; left: 0px;"></div>

      <div class="well well-sm">
         <div class="grid-stack">
            %for widget in dashboard_widgets:
               <div class="grid-stack-item"
                     id="{{widget['id']}}"
                     data-name="{{widget['name']}}"
                     data-uri="{{widget['uri']}}"

                     data-gs-id="{{widget['id']}}"
                     data-gs-x="{{widget['x']}}"
                     data-gs-y="{{widget['y']}}"
                     data-gs-width="{{widget['width']}}"
                     data-gs-min-width="{{widget['minWidth']}}"
                     data-gs-max-width="{{widget['maxWidth']}}"
                     data-gs-height="{{widget['height']}}"
                     data-gs-min-height="{{widget['minHeight']}}"
                     data-gs-max-height="{{widget['maxHeight']}}"
                     >
                  <div class="grid-stack-item-content">
                  </div>
               </div>
            %end
         </div>
      </div>
   </div>
</div>
<script type="text/javascript">
   var dashboard_logs = false;

   $('.grid-stack').on('change', function (e, items) {
      console.log("Grid layout changed:", items);
      if (items === undefined) return;
      var widgets = [];
      for (i = 0; i < items.length; i++) {
         console.log($('#'+items[i].id));
         var widget = {
            'id': items[i].id,
            'name': $('#'+items[i].id).data('name'),
            'uri': $('#'+items[i].id).data('uri'),
            'x': items[i].x,
            'y': items[i].y,
            'width': items[i].width,
            'minWidth': items[i].minWidth,
            'maxWidth': items[i].maxWidth,
            'height': items[i].height,
            'minHeight': items[i].minHeight,
            'maxHeight': items[i].maxHeight
         };
         var found = widgets.some(function (el) {
            return el.id === widget.id;
         });
         if (!found) {
            widgets.push(widget);
         }
      }
      if (widgets.length > 0) {
         var to_save = {'widgets': widgets}
         save_user_preference('{{widgets_place}}_widgets', JSON.stringify(to_save), function(){
            console.log("Saved {{widgets_place}} widgets grid", to_save)
         });
      }
   });

   $('body').on("submit", 'form[data-action="save-options"]', function (evt) {
      console.debug('Submit form data: ', $(this));
      console.debug('Form item/action: ', $(this).data("widget"), $(this).data("action"));
      console.debug('Form data: ', $(this).serializeArray());

      // Do not automatically submit ...
      evt.preventDefault();

      $('#widgets_loading').show();

      $.ajax({
         url: $(this).attr('action'),
         type: $(this).attr('method'),
         data: $(this).serialize()
      })
      .done(function( data, textStatus, jqXHR ) {
         if (jqXHR.status != 200) {
            raise_message_ko(jqXHR.status, data);
         } else {
            $("#" + $(this).data("widget") + " div.grid-stack-item-content").html(data);
            raise_message_ok("{{_('Widget options saved')}}");
         }
      })
      .fail(function( jqXHR, textStatus, errorThrown ) {
         raise_message_ko(jqXHR.responseJSON['message']);
      })
     .always(function() {
         $('#widgets_loading').hide();
      });
   });

   $(document).ready(function(){
      set_current_page("{{ webui.get_url(request.route.name) }}");

      %if not len(dashboard_widgets):
         // Show the widgets proposal area.
         $('#propose-widgets').show();
      %else:
         // Hide the widgets proposal area ...
         $('#propose-widgets').hide();

         // Loading indicator ...
         $("#widgets_loading").
            html('<i class="fa fa-spinner fa-spin fa-3x"></i> <span class="lead">{{_('Loading widgets ... ')}}</span>').
            show();

         nb_widgets_loading = 0;
      %end

      var options = {
         float: false,
         cellHeight: 20,
         disableDrag: false,
         disableResize: false,
         removable: true,
         verticalMargin: 20
      };
      $('.grid-stack').gridstack(options);

      %for widget in dashboard_widgets:
         // We are saying to the user that we are loading a widget with
         // a spinner
         nb_widgets_loading += 1;

         console.log("Load: {{widget['uri']}}")
         $("#{{widget['id']}} div.grid-stack-item-content").load(
            "{{widget['uri']}}",
            {
               %for (key, v) in widget['options'].iteritems():
                  {{key}}: '{{v.get('value', '')}}',
               %end
               widget_id: '{{widget['id']}}'
            },
            function(response, status, xhr) {
               //console.log(status, response)
               nb_widgets_loading -= 1;
               if (nb_widgets_loading==0){
                  $('#widgets_loading').hide();
               }

               if ( status == "error" ) {
                  raise_message_ko(status, data);
               }
            }
         );

      %end
   });
</script>
