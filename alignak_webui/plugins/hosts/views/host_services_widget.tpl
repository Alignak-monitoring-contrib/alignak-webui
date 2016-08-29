<!-- Hosts services widget -->
%# embedded is True if the widget is got from an external application
%setdefault('embedded', False)
%from bottle import request
%setdefault('links', request.params.get('links', ''))
%setdefault('identifier', 'widget')
%setdefault('credentials', None)

%from alignak_webui.utils.helper import Helper

%include("livestates.tpl", elts=livestate_services, elt_type='service', layout=False, pagination=webui.helper.get_pagination_control('livestate', len(livestate_services), 0, len(livestate_services)))
