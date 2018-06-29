%setdefault('l_events', None)
%setdefault('hosts_url', None)
%setdefault('search_string', None)
%from alignak_webui.objects.element_state import ElementState
%items_states = ElementState()

<style>
    #problems-list {
        margin-top: 60px;
        margin-bottom: 10px;
        margin-left: 10px;
        margin-right: 10px;
    }

    .icon-title {
        display: block;

        color: #666;
        state-size: 1em;
    }

    .icon-badge {
        background-color: #cccccc;
        border-radius: 3px;
        state-size: 1em;
        text-transform: uppercase;

        width: 100px;

        opacity: 0.9;
    }

    .icon-badge-top {
        background-color: #ffffff;
        state-size: 1.3em;
    }

    #problems-list a span.fa {
        opacity: 0.8;
    }
    .icon-info {
        color: #2980b9;
    }

    .icon-danger {
        color: #e74c3c;
    }

    .icon-warning {
        color: #e67e22;
    }

    .icon-success {
        color: #27ae60;
    }
</style>

<div id="problems-list" class="row">
   %if l_events is None:
      %if datamgr:
      %l_events = datamgr.get_events_log()
      %else:
      <div class="col-xs-12">
      No data manager!
      </div>
      %end
   %end


   %from alignak_webui.utils.helper import Helper
   %from alignak_webui.objects.item_command import Command
   %from alignak_webui.objects.item_host import Host

   <!-- histories filtering and display -->
   <div id="histories">
      <div class="panel panel-default">
         <div class="panel-body">
         %if not l_events:
            %include("_nothing_found.tpl", search_string=search_string)
         %else:
            <i class="pull-right small">{{_('%d elements') % (len(l_events))}}</i>

            <table class="table table-condensed" style="width: 100%">
               <thead><tr>
                  <th class="col-md-1"></th>
                  <th class="col-md-1">{{! _('<span class="fa fa-clock-o"></span>')}}</th>
                  <th>{{_('Message')}}</th>
                  <th></th>
               </tr></thead>

               <tbody>
                  %for lcr in l_events:
                  %css = 'success' if lcr['level'] == 'info' else 'warning' if lcr['level'] == 'warning' else 'danger' if lcr['level'] == 'error' else ''

                  <tr class="{{css}}">
                     <td>
                     <span class="{{lcr['class']}} fa fa-w fa-{{lcr['icon']}}"></span>
                     </td>

                     <td>
                        <small>
                        {{! lcr['timestamp']}}
                        </small>
                     </td>

                     <td>
                        {{! lcr['message']}}
                     </td>
                  </tr>
                %end
               </tbody>
            </table>
         %end
         </div>
      </div>
    </div>


</div>
