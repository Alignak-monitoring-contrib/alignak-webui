<!-- livestates chart widget -->
%# embedded is True if the widget is got from an external application
%setdefault('embedded', False)
%from bottle import request
%setdefault('links', request.params.get('links', ''))
%setdefault('identifier', 'widget')
%setdefault('credentials', None)

%if not livestates:
   <center>
      <h3>{{_('No livestates matching the filter...')}}</h3>
   </center>
%else:
   %hs = datamgr.get_livesynthesis()['hosts_synthesis']
   %if hs:
   <div class="well">
      <div class="row">
      %for state in 'up', 'unreachable', 'down', 'acknowledged', 'in_downtime':
         <div class="col-xs-6 col-md-4 text-center">
            %label = "%d<br/><em>(%s)</em>" % (hs['nb_' + state], state)
            <span class='item_livestate_{{state.lower()}}'>
               <span class="hosts-count" data-count="{{ hs['nb_' + state] }}" data-state="{{ state }}" style="font-size: 3em;">{{ hs['nb_' + state] }}</span>
               <br/>
               <span style="font-size: 1.1em;">{{ state }}</span>
            </span>
         </div>
      %end
      </div>
   </div>
   %end
%end
