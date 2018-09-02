<!-- Hosts history widget -->
%# embedded is True if the widget is got from an external application
%setdefault('embedded', False)
%from bottle import request
%setdefault('links', request.params.get('links', ''))
%setdefault('identifier', 'widget')
%setdefault('credentials', None)

%#No filtering (full history)
%history_filter = []
%if history:
   %include("histories.tpl", histories=history, filter=history_filter, layout=False, pagination=webui.helper.get_pagination_control('history', len(history), 0, len(history)))
%else:
   <div class="alert alert-info">
      <p>{{_('No history logs available.')}}</p>
   </div>
%end
