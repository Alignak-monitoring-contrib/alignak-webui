<!-- Livestate services counters widget -->
%# embedded is True if the widget is got from an external application
%setdefault('embedded', False)
%from bottle import request
%setdefault('links', request.params.get('links', ''))
%setdefault('identifier', 'widget')
%setdefault('credentials', None)

%if not elements:
   <center>
      <h3>{{_('No elements matching the filter...')}}</h3>
   </center>
%else:
   %ss = datamgr.get_livesynthesis()['services_synthesis']
   %if ss:
   <div class="well">
      <div class="row">
      %for state in 'ok', 'warning', 'critical', 'unknown', 'acknowledged', 'in_downtime':
         <div class="col-xs-6 col-md-4 text-center">
             %label = "%d<br/><em>(%s)</em>" % (ss['nb_' + state], state)
             <span class='item_livestate_{{state.lower()}}'>
                 <span class="hosts-count" data-count="{{ ss['nb_' + state] }}" data-state="{{ state }}" style="font-size: 3em;">{{ ss['nb_' + state] }}</span>
                 <br/>
                 <span style="font-size: 1.1em;">{{ state }}</span>
             </span>
         </div>
      %end
      </div>
   </div>
   %end
%end
