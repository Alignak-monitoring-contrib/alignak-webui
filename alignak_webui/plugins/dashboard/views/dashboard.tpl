%setdefault('action_bar', False)

%from bottle import request
%rebase("layout", js=['dashboard/htdocs/js/widgets.js', 'dashboard/htdocs/js/jquery.easywidgets.js'], css=['dashboard/htdocs/css/dashboard.css'], title=_('Dashboard'))

<div id="dashboard">
   <script type="text/javascript">
      /* We are saving the global context for the widgets */
      widget_context = 'dashboard';
   </script>
   <table class="table table-invisible table-condensed">
      <tbody>
         <tr>
            <td>
               %hs = datamgr.get_hosts_synthesis()
               <center><a href="{{ webui.get_url('Hosts') }}" class="btn btn-sm">
                  <i class="fa fa-4x fa-server font-greyed"></i>
                  <span class="badger-title"><i class="fa fa-plus" style="color: #ccc"></i>&nbsp;{{_('Hosts')}}</span>
                  <span class="badger-big badger-left badger-info" title="{{_('Number of hosts up')}}">{{hs["nb_up"]}}</span>
                  <span class="badger-big badger-right badger-info" title="{{_('Number of hosts down')}}">{{hs["nb_down"]}}</span>
               </a></center>
            </td>

            <td>
               %hs = datamgr.get_hosts_synthesis()
               <center><a href="{{ webui.get_url('Hosts') }}" class="btn btn-sm">
                  <i class="fa fa-4x fa-server font-greyed"></i>
                  <span class="badger-title"><i class="fa fa-plus" style="color: #ccc"></i>&nbsp;{{_('Services')}}</span>
                  <span class="badger-big badger-left badger-info" title="{{_('Number of hosts up')}}">{{hs["nb_up"]}}</span>
                  <span class="badger-big badger-right badger-info" title="{{_('Number of hosts down')}}">{{hs["nb_down"]}}</span>
               </a></center>
            </td>

            <td>
               %hs = datamgr.get_hosts_synthesis()
               <center><a href="{{ webui.get_url('Hosts') }}" class="btn btn-sm">
                  <i class="fa fa-4x fa-server font-greyed"></i>
                  <span class="badger-title"><i class="fa fa-plus" style="color: #ccc"></i>&nbsp;{{_('Problems')}}</span>
                  <span class="badger-big badger-left badger-info" title="{{_('Number of hosts up')}}">{{hs["nb_up"]}}</span>
                  <span class="badger-big badger-right badger-info" title="{{_('Number of hosts down')}}">{{hs["nb_down"]}}</span>
               </a></center>
            </td>

            <td>
               %hs = datamgr.get_hosts_synthesis()
               <center><a href="{{ webui.get_url('Hosts') }}" class="btn btn-sm">
                  <i class="fa fa-4x fa-server font-greyed"></i>
                  <span class="badger-title"><i class="fa fa-plus" style="color: #ccc"></i>&nbsp;{{_('Impacts')}}</span>
                  <span class="badger-big badger-left badger-info" title="{{_('Number of hosts up')}}">{{hs["nb_up"]}}</span>
                  <span class="badger-big badger-right badger-info" title="{{_('Number of hosts down')}}">{{hs["nb_down"]}}</span>
               </a></center>
            </td>
         </tr>
      </tbody>
   </table>

   %if current_user.can_change_dashboard() and not len(dashboard_widgets):
   %if webui and webui.prefs_module:
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
   %else:
   <div class="panel panel-default">
      <div class="panel-heading" style="padding-bottom: -10">
         <center>
            <h3>{{_('There is no users preferences storage module installed.')}}</h3>
            <h4 class="alert alert-danger">{{_('The Web UI dashboard and user preferences will not be saved.')}}</h4>
         </center>
      </div>
   </div>
   %end
   %end

   <div class="container-fluid">
      <!-- Widgets loading indicator -->
      <div id="widgets_loading" style="position: absolute; top: 0px; left: 0px;"></div>

      <div class="row">
         <!-- /place-1 -->
         <div class="widget-place col-xs-12 col-sm-12 col-lg-4" id="widget-place-1"> </div>

         <!-- /place-2 -->
         <div class="widget-place col-xs-12 col-sm-12 col-lg-4" id="widget-place-2"> </div>

         <!-- /place-3 -->
         <div class="widget-place col-xs-12 col-sm-12 col-lg-4" id="widget-place-3"> </div>
      </div>
   </div>
</div>
<script type="text/javascript">
   var dashboard_logs = false;

   $(document).ready(function(){
      set_current_page("{{ webui.get_url(request.route.name) }}");

      %if not len(dashboard_widgets):
         // display the widgets proposal area.
         $('#propose-widgets').show();
      %end

      // load all widgets.
      %for w in dashboard_widgets:
         %if 'base_url' in w and 'position' in w:
            AddWidget("{{!w['base_url']}}", {{!w['options_json']}}, "{{w['position']}}");
         %end
      %end
   });
</script>
