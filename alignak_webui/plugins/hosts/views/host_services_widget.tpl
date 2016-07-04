<!-- Hosts services widget -->
%# embedded is True if the widget is got from an external application
%setdefault('embedded', False)
%from bottle import request
%setdefault('links', request.params.get('links', ''))
%setdefault('identifier', 'widget')
%setdefault('credentials', None)

%from alignak_webui.utils.helper import Helper

%include("services.tpl", services=services, layout=False, pagination=Helper.get_pagination_control('service', len(services), 0, len(services)))
