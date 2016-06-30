<!-- Hosts chart widget -->
%# embedded is True if the widget is got from an external application
%setdefault('embedded', False)
%setdefault('links', '')
%setdefault('identifier', 'widget')
%setdefault('credentials', None)

%rebase("_widget", js=[], css=[])

%from alignak_webui.utils.helper import Helper
%from alignak_webui.objects.item import Host

%if not hosts:
   <center>
      <h3>{{_('No hosts matching the filter...')}}</h3>
   </center>
%else:
   %hs = datamgr.get_livesynthesis()['hosts_synthesis']
   %if hs:
   <div id="hosts-states-popover-content" class="hidden">
      <table class="table table-invisible table-condensed">
         <tbody>
            <tr>
               %for state in 'up', 'unreachable', 'down':
               <td>
                 %label = "%s <i>(%s%%)</i>" % (hs["nb_" + state], hs["pct_" + state])
                 %label = "%s%%" % (hs["pct_" + state])
                 {{! Host({'status':state}).get_html_state(text=label, title=label, disabled=(not hs["nb_" + state]))}}
               </td>
               %end
            </tr>
         </tbody>
      </table>
   </div>
   %end
   <div class="panel panel-default">
      <div class="panel-body">
         <!-- Chart -->
         <div id="pie-graph-hosts">
            <div class="graph">
               <canvas></canvas>
            </div>
            <div class="title">
               <div class="text-center">
                  <h4>Hosts states</h4>
                  <span class="text-muted">-/-</span>
               </div>
            </div>
            <div class="legend">
               <div class="pull-left well well-sm" style="margin-bottom: 0px">
                  <span class="legend hidden-sm hidden-xs"></span>
               </div>
            </div>
         </div>
      </div>
   </div>
%end
<script>
   var title = true;
   var legend = true;

   /*
    * Expert configuration for page graphs.
    * ------------------------------------------
    * Based on: http://www.chartjs.org/docs/
    */
   Chart.defaults.global = {
      // Boolean - Whether to animate the chart
      animation: true,

      // Number - Number of animation steps
      animationSteps: 60,

      // String - Animation easing effect
      // Possible effects are:
      // [easeInOutQuart, linear, easeOutBounce, easeInBack, easeInOutQuad,
      //  easeOutQuart, easeOutQuad, easeInOutBounce, easeOutSine, easeInOutCubic,
      //  easeInExpo, easeInOutBack, easeInCirc, easeInOutElastic, easeOutBack,
      //  easeInQuad, easeInOutExpo, easeInQuart, easeOutQuint, easeInOutCirc,
      //  easeInSine, easeOutExpo, easeOutCirc, easeOutCubic, easeInQuint,
      //  easeInElastic, easeInOutSine, easeInOutQuint, easeInBounce,
      //  easeOutElastic, easeInCubic]
      animationEasing: "easeOutQuart",

      // Boolean - If we should show the scale at all
      showScale: true,

      // Boolean - If we want to override with a hard coded scale
      scaleOverride: false,

      // ** Required if scaleOverride is true **
      // Number - The number of steps in a hard coded scale
      scaleSteps: null,
      // Number - The value jump in the hard coded scale
      scaleStepWidth: null,
      // Number - The scale starting value
      scaleStartValue: null,

      // String - Colour of the scale line
      scaleLineColor: "rgba(0,0,0,.1)",

      // Number - Pixel width of the scale line
      scaleLineWidth: 1,

      // Boolean - Whether to show labels on the scale
      scaleShowLabels: true,

      // Interpolated JS string - can access value
      scaleLabel: "<%=value%>",

      // Boolean - Whether the scale should stick to integers, not floats even if drawing space is there
      scaleIntegersOnly: true,

      // Boolean - Whether the scale should start at zero, or an order of magnitude down from the lowest value
      scaleBeginAtZero: false,

      // String - Scale label font declaration for the scale label
      scaleFontFamily: "'Helvetica Neue', 'Helvetica', 'Arial', sans-serif",

      // Number - Scale label font size in pixels
      scaleFontSize: 12,

      // String - Scale label font weight style
      scaleFontStyle: "normal",

      // String - Scale label font colour
      scaleFontColor: "#666",

      // Boolean - whether or not the chart should be responsive and resize when the browser does.
      responsive: true,

      // Boolean - whether to maintain the starting aspect ratio or not when responsive, if set to false, will take up entire container
      maintainAspectRatio: true,

      // Boolean - Determines whether to draw tooltips on the canvas or not
      showTooltips: true,

      // Function - Determines whether to execute the customTooltips function instead of drawing the built in tooltips (See [Advanced - External Tooltips](#advanced-usage-custom-tooltips))
      customTooltips: function(tooltip) {
         if (! tooltip) return;
      },

      // Array - Array of string names to attach tooltip events
      tooltipEvents: ["mousemove", "touchstart", "touchmove"],

      // String - Tooltip background colour
      tooltipFillColor: "rgba(0,0,0,0.8)",

      // String - Tooltip label font declaration for the scale label
      tooltipFontFamily: "'Helvetica Neue', 'Helvetica', 'Arial', sans-serif",

      // Number - Tooltip label font size in pixels
      tooltipFontSize: 14,

      // String - Tooltip font weight style
      tooltipFontStyle: "normal",

      // String - Tooltip label font colour
      tooltipFontColor: "#fff",

      // String - Tooltip title font declaration for the scale label
      tooltipTitleFontFamily: "'Helvetica Neue', 'Helvetica', 'Arial', sans-serif",

      // Number - Tooltip title font size in pixels
      tooltipTitleFontSize: 14,

      // String - Tooltip title font weight style
      tooltipTitleFontStyle: "bold",

      // String - Tooltip title font colour
      tooltipTitleFontColor: "#fff",

      // Number - pixel width of padding around tooltip text
      tooltipYPadding: 6,

      // Number - pixel width of padding around tooltip text
      tooltipXPadding: 6,

      // Number - Size of the caret on the tooltip
      tooltipCaretSize: 8,

      // Number - Pixel radius of the tooltip border
      tooltipCornerRadius: 6,

      // Number - Pixel offset from point x to tooltip edge
      tooltipXOffset: 10,

      // String - Template string for single tooltips
      tooltipTemplate: "<%if (label){%><%=label%>: <%}%><%= value %>",

      // String - Template string for multiple tooltips
      multiTooltipTemplate: "<%= value %>",

      // Function - Will fire on animation progression.
      onAnimationProgress: function(){},

      // Function - Will fire on animation completion.
      onAnimationComplete: function(){}
   };

   var pie_graph_hosts_parameters = {
     "up": {
         color:"#5bb75b",
         highlight: "#5AD3D1",
         label: "Up"
     },
     "unreachable": {
         color: "#faa732",
         highlight: "#5AD3D1",
         label: "Unreachable"
     },
     "down": {
         color: "#da4f49",
         highlight: "#5AD3D1",
         label: "Down"
     }
   };
   var pie_graph_hosts_options = {
      legendTemplate: [
         '<div id="pie_graph_hosts_legend">',
             '<% for (var i=0; i<segments.length; i++)\{\%>',
                 '<div>',
                     '<span style="background-color:<%=segments[i].fillColor%>; display: inline-block; width: 12px; height: 12px; margin-right: 5px;"></span>',
                     '<small>',
                     '<%=segments[i].label%>',
                     '<%if(segments[i].value)\{\%>',
                         ' (<%=segments[i].value%>)',
                     '<%\}\%>',
                     '</small>',
                 '</div>',
             '<%}%>',
         '</div>'
      ].join('')
   };

   $(document).ready(function() {
      var data = [];
      %for state in 'up', 'unreachable', 'down':
         // Update table rows
         row = pie_graph_hosts_parameters['{{state}}'];
         row['value'] = {{hs["nb_" + state]}};
         data.push(row)
      %end

      // Update graph
      var ctx = $("#pie-graph-hosts canvas").get(0).getContext("2d");
      var myPieChart = new Chart(ctx).Doughnut(data, pie_graph_hosts_options);
      if (title) {
         $("#pie-graph-hosts .title").show();
         $("#pie-graph-hosts .title span").html({{hs["nb_elts"]}} + " hosts").show();
      } else {
         $("#pie-graph-hosts .title").hide();
      }
      if (legend) {
         if (pie_graph_hosts_options) {
             $("#pie-graph-hosts .legend").show();
             if ($("#pie-graph-hosts span.legend").length) {
                 if (! $("#pie_graph_hosts_legend").length) {
                     $("#pie-graph-hosts .legend span").append(myPieChart.generateLegend());
                 }
                 // TODO: Update ...
             }
         }
      } else {
         $("#pie-graph-hosts .legend").hide();
      }
   });
</script>