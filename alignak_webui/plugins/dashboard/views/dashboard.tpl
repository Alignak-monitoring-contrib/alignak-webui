%setdefault('ls', None)
%setdefault('debug', False)

%import json

%from bottle import request
%rebase("layout", js=['dashboard/static/js/lodash.js', 'dashboard/static/js/jquery.ui.touch-punch.min.js', 'dashboard/static/js/gridstack.min.js'], css=['dashboard/static/css/dashboard.css', 'dashboard/static/css/gridstack.min.css'], title=title)


<style type="text/css">
    .grid-stack {
        background-color: transparent;
    }

    .grid-stack-item-content {
        background-color: transparent;
    }
</style>

<div id="dashboard">
%if debug:
    <div class="panel-group">
      <div class="panel panel-default">
         <div class="panel-heading">
            <h4 class="panel-title">
               <a data-toggle="collapse" href="#collapse_widgets"><i class="fa fa-bug"></i> Dashboard installed widgets</a>
            </h4>
         </div>
         <div id="collapse_widgets" class="panel-collapse collapse">
            %for widget in dashboard_widgets:
            <h4>{{widget['name']}}</h4>
            <dl class="dl-horizontal" style="height: 200px; overflow-y: scroll;">
               %for k,v in sorted(widget.items()):
                  <dt>{{k}}</dt>
                  <dd>{{v}}</dd>
               %end
            </dl>
            %end
         </div>
      </div>
   </div>
%end
    %include("_problems_synthesis.tpl", ls=ls)

    %if current_user.can_change_dashboard() and not len(dashboard_widgets):
    <div id="propose-widgets" class="panel panel-warning" style="display:none">
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
        <!-- Widgets loading indicator
        <div id="widgets_loading"></div>
        -->

        <!-- Widgets grid -->
        <div class="grid-stack">
         %for widget in dashboard_widgets:
            <div class="grid-stack-item"
                  id="{{widget['id']}}"
                  data-uri="{{widget['uri']}}"
                  data-name="{{widget['name']}}"
                  data-icon="{{widget['icon']}}"
                  data-template="{{widget['template']}}"

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
               <div class="grid-stack-item-content card" style="padding:5px">
               </div>
            </div>
         %end
      </div>
    </div>
</div>
<script type="text/javascript">
    var dashboard_logs = false;

    $('.grid-stack').on('change', function (e, items) {
        if (dashboard_logs) console.log("Grid layout changed:", items);
        if (items === undefined) {
            // No more widgets
            wait_message('{{_('Saving configuration...')}}', true)

            var to_save = []
            save_user_preference('{{widgets_place}}_widgets', JSON.stringify(to_save), function(){
                if (dashboard_logs) console.log("Saved {{widgets_place}} widgets grid", to_save)

                wait_message('', false)
            });
            return;
        }

        var widgets = [];
        for (i = 0; i < items.length; i++) {
            if (dashboard_logs) console.log("Grid item: ", $('#'+items[i].id));
            var widget = {
                'id': items[i].id,
                'uri': $('#'+items[i].id).data('uri'),
                'name': $('#'+items[i].id).data('name'),
                'icon': $('#'+items[i].id).data('icon'),
                'template': $('#'+items[i].id).data('template'),
                'picture': $('#'+items[i].id).data('picture'),
                //'options': $('#'+items[i].id).data('options'),
                'x': items[i].x,
                'y': items[i].y,
                'width': items[i].width,
                'minWidth': items[i].minWidth,
                'maxWidth': items[i].maxWidth,
                'height': items[i].height,
                'minHeight': items[i].minHeight,
                'maxHeight': items[i].maxHeight
            };
            if (dashboard_logs) console.log("Widget item: ", widget);
            var found = widgets.some(function (el) {
                return el.id === widget.id;
            });
            if (!found) {
                widgets.push(widget);
            }
        }
        if (widgets.length > 0) {
            wait_message('{{_('Saving configuration...')}}', true)

            var to_save = widgets
            save_user_preference('{{widgets_place}}_widgets', JSON.stringify(to_save), function(){
                if (dashboard_logs) console.log("Saved {{widgets_place}} widgets grid", to_save)

                wait_message('', false)
            });
        }
    });

    $('.grid-stack').on('removed', function(event, items) {
        for (var i = 0; i < items.length; i++) {
            if (dashboard_logs) console.log('Item removed from grid:', items[i]);
        }
        // Page refresh required
        refresh_required = true;
    });

    $('.grid-stack').on('added', function(event, items) {
        for (var i = 0; i < items.length; i++) {
            if (dashboard_logs) console.log('Item added to grid:', items[i]);
        }
        // Page refresh required
        refresh_required = true;
    });

    $(document).ready(function(){
        set_current_page("{{ webui.get_url(request.route.name) }}");

        %if message:
            raise_message_{{message.get('status', 'ko')}}("{{! message.get('message')}}");
        %end

        %if not len(dashboard_widgets):
            // Show the widgets proposal area.
            $('#propose-widgets').show();
        %else:
            // Hide the widgets proposal area ...
            $('#propose-widgets').hide();

            // Loading indicator ...
            // wait_message('{{_('Loading dashboard widgets...')}}', true)

            nb_widgets_loading = 0;
        %end

        var options = {
            float: false,
            animate: true,
            cellHeight: 20,
            disableDrag: false,
            disableResize: false,
            removable: true,
            verticalMargin: 20,
            alwaysShowResizeHandle: /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent),
            resizable: {
                handles: 'e, se, s, sw, w'
            }
        };
        $('.grid-stack').gridstack(options);

        %for widget in dashboard_widgets:
            nb_widgets_loading += 1;

            if (dashboard_logs) console.log("Widget: ", {{! json.dumps(widget)}})
            if (dashboard_logs) console.log("Load: {{widget['uri']}} for {{widget['id']}}")
            raise_message_info("{{_('Loading widget: %s' % widget['name'])}}");
            $("#{{widget['id']}} div.grid-stack-item-content").load(
                "{{widget['uri']}}",
                {
                %if 'options' in widget:
                %for option in widget['options'].split('|'):
                    %option=option.split('=')
                    %if len(option) > 1:
                    {{option[0]}}: '{{option[1]}}',
                    %end
                %end
                %end
                title: '{{widget['name']}}',
                widget_template: '{{widget['template']}}',
                widget_id: '{{widget['id']}}'
                },
                function(response, status, xhr) {
                    nb_widgets_loading -= 1;
                    if (nb_widgets_loading==0){
                        wait_message('', false)
                    }

                    if (status == "error") {
                        //raise_message_ko("{{_('Error when loading a widget: %s' % widget['name'])}}");
                        console.error(response, status, xhr);
                    } else {
                        raise_message_ok("{{_('Loaded widget: %s' % widget['name'])}}");
                    }
                }
            );

        %end
    });
</script>
