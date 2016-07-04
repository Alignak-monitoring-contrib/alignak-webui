<!-- livestates chart widget -->
%# embedded is True if the widget is got from an external application
%setdefault('embedded', False)
%from bottle import request
%setdefault('links', request.params.get('links', ''))
%setdefault('identifier', 'widget')
%setdefault('credentials', None)

%from alignak_webui.objects.item import LiveState

%if not livestates:
   <center>
      <h3>{{_('No livestate hosts matching the filter...')}}</h3>
   </center>
%else:
   %hs = datamgr.get_livesynthesis()['hosts_synthesis']
   %if hs:
   %state='down' if hs['pct_problems'] >= hs['critical_threshold'] else 'unreachable' if hs['pct_problems'] >= hs['warning_threshold'] else 'up'
   %font='critical' if hs['pct_problems'] >= hs['critical_threshold'] else 'warning' if hs['pct_problems'] >= hs['warning_threshold'] else 'ok'
   <div class="well">
      <div class="row">
         <!-- Hosts SLA icons -->
         <div class="col-xs-4 col-sm-4 text-center">
            {{! LiveState({'status':state}).get_html_state(text=None, size="fa-5x")}}
         </div>

         %for state in ['up', 'unreachable', 'down']:
         <div class="col-xs-4 col-sm-4 text-center">
            <span class='item_livestate_{{state.lower()}}'>
                 <span class="hosts-count" data-count="{{ hs['nb_' + state] }}" data-state="{{ state }}" style="font-size: 1.8em;">{{ hs['pct_' + state] }}%</span>
                 <br/>
                 <span style="font-size: 1em;">{{ state }}</span>
            </span>
         </div>
         %end
         %for state in ['problems']:
         <div class="col-xs-4 col-sm-4 text-center">
            <span class='item_livestate_{{state.lower()}}'>
               <span class="hosts-count" data-count="{{ hs['nb_' + state] }}" data-state="{{ state }}" style="font-size: 1.8em;">{{ hs['pct_' + state] }}%</span>
               <br/>
               <span style="font-size: 1em;">{{_('Known problems')}}</span>
            </a>
         </div>
      </div>
   </div>
   %end
%end
