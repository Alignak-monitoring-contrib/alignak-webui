<!-- Livestate services SLA widget -->
%# embedded is True if the widget is got from an external application
%setdefault('embedded', False)
%from bottle import request
%setdefault('links', request.params.get('links', ''))
%setdefault('identifier', 'widget')
%setdefault('credentials', None)

%from alignak_webui.objects.item_livestate import LiveState

%if not elements:
   <center>
      <h3>{{_('No elements matching the filter...')}}</h3>
   </center>
%else:
   %ss = datamgr.get_livesynthesis()['services_synthesis']
   %if ss:
   %state='critical' if ss['pct_problems'] >= ss['critical_threshold'] else 'warning' if ss['pct_problems'] >= ss['warning_threshold'] else 'ok'
   %font='critical' if ss['pct_problems'] >= ss['critical_threshold'] else 'warning' if ss['pct_problems'] >= ss['warning_threshold'] else 'ok'
   <div class="well">
      <div class="row">
         <!-- Services SLA icons -->
         <div class="col-xs-4 col-sm-4 text-center">
            {{! LiveState({'status':state}).get_html_state(text=None, size="fa-5x")}}
         </div>

         %for state in ['ok', 'warning', 'critical', 'unknown']:
         <div class="col-xs-4 col-sm-4 text-center">
            <span class='item_livestate_{{state.lower()}}'>
                 <span class="services-count" data-count="{{ ss['nb_' + state] }}" data-state="{{ state }}" style="font-size: 1.8em;">{{ ss['pct_' + state] }}%</span>
                 <br/>
                 <span style="font-size: 1em;">{{ state }}</span>
            </span>
         </div>
         %end
         %for state in ['problems']:
         <div class="col-xs-4 col-sm-4 text-center">
            <span class='item_livestate_{{state.lower()}}'>
               <span class="services-count" data-count="{{ ss['nb_' + state] }}" data-state="{{ state }}" style="font-size: 1.8em;">{{ ss['pct_' + state] }}%</span>
               <br/>
               <span style="font-size: 1em;">{{_('Known problems')}}</span>
            </a>
         </div>
      </div>
   </div>
   %end
%end
