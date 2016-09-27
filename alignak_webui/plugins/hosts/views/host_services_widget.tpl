<!-- Hosts services widget -->
%# embedded is True if the widget is got from an external application
%setdefault('embedded', False)
%from bottle import request
%setdefault('links', request.params.get('links', ''))
%setdefault('identifier', 'widget')
%setdefault('credentials', None)

%from alignak_webui.utils.helper import Helper

%include("services.tpl", elts=services, elt_type='service', in_host_view=True, layout=False, pagination=webui.helper.get_pagination_control('service', len(services), 0, len(services)))
