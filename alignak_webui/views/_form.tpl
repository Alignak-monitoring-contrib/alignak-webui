%import json
%from alignak_webui.objects.element import BackendElement
%from alignak_webui.objects.element_state import ElementState

%# Default values
%setdefault('debug', False)
%setdefault('edition', edition_mode)
%setdefault('is_templated', '_is_template' in plugin.table)
%setdefault('is_template', False)
%setdefault('has_template', False)
%setdefault('refresh', False)

%if element:
%# An element still exists...
%setdefault('title', _('%s %s') % (plugin.backend_endpoint.capitalize(), element.name))

%if '_is_template' in element.__dict__ and element['_is_template']:
%is_template = True
%end

%if '_is_template' in element.__dict__ and not element['_is_template']:
%if '_template_fields' in element.__dict__ and element['_template_fields']:
%has_template = True
%end
%end

%else:
%# No element exist...
%setdefault('title', _('New %s') % (plugin.backend_endpoint))
%end

%rebase("layout", title=title, page="/{{plugin.backend_endpoint}}/{{element.name}}/form")

%if debug and element:
<div class="panel-group">
   <div class="panel panel-default">
      <div class="panel-heading">
         <h4 class="panel-title">
            <a data-toggle="collapse" href="#collapse_{{element.id}}"><i class="fa fa-bug"></i> Element as dictionary</a>
         </h4>
      </div>
      <div id="collapse_{{element.id}}" class="panel-collapse collapse">
         <dl class="dl-horizontal" style="height: 200px; overflow-y: scroll;">
            %for k,v in sorted(element.__dict__.items()):
               <dt>{{k}}</dt>
               <dd>{{v}}</dd>
            %end
         </dl>
      </div>
   </div>
</div>
%end

<div id="form_{{plugin.backend_endpoint}}">
   %post=""
   %if edition:
   %if element:
   %post='''method="post" action="/%s/%s/form"''' % (plugin.backend_endpoint, element.id)
   %else:
   %post='''method="post" action="/%s/%s/form"''' % (plugin.backend_endpoint, None)
   %end
   %end
   <form role="form" data-element="{{element.id if element else 'None'}}" class="element_form {{'template_form' if is_template else ''}}" {{! post}}>
      <fieldset>
      %# Editing a template
      %if is_template:
         <div class="alert alert-dismissible alert-warning">
            <button type="button" class="close" data-dismiss="alert">×</button>
            <h4>{{_('You are viewing or editing a %s template.') % plugin.backend_endpoint}}</h4>
            <hr/>
            <p>{{_('All the %ss based upon this template may be affected by your modifications.') % plugin.backend_endpoint}}</p>
         </div>

         <legend>{{! _('%s template <code>%s</code>') % (plugin.backend_endpoint.capitalize(), element.name)}}</legend>
      %# Editing an element
      %elif element:
         %if has_template:
         <div class="alert alert-dismissible alert-info">
            <button type="button" class="close" data-dismiss="alert">×</button>
            <h4>{{_('You are modifying a %s based upon one or more template(s).') % plugin.backend_endpoint}}</h4>
         </div>
         %end

          %if not edition:
             <div class="alert alert-dismissible alert-info">
                <button type="button" class="close" data-dismiss="alert">×</button>
                <h4>{{_('Read-only mode.')}}</h4>
             </div>
          %else:
             <div class="alert alert-dismissible alert-warning">
                <button type="button" class="close" data-dismiss="alert">×</button>
                <h4>{{_('Edition mode.')}}</h4>
             </div>
          %end
         <legend>{{! _('%s <code>%s</code>') % (plugin.backend_endpoint.capitalize(), element.name)}}</legend>
      %# Creating a new element/template
      %else:
         <div class="alert alert-dismissible alert-warning">
            <button type="button" class="close" data-dismiss="alert">×</button>
            <h4>{{_('You are creating a new %s.') % plugin.backend_endpoint}}</h4>

            <hr/>
            <p>{{! _('You must set a name for your new %s and then submit this form.') % plugin.backend_endpoint}}</p>
            %if is_templated:
            <p>{{_('The %s elements are based upon templates.') % plugin.backend_endpoint}}</p>
            <p>{{_('You can specify if the new element is a template and / or if it is based upon one (or several) template(s).')}}</p>
            %end
         </div>

         <legend>{{! _('New %s') % (plugin.backend_endpoint)}}</legend>
      %end

      %if not element:
         %field = 'name'
         %model = plugin.table[field]

         %label = model.get('title', '')
         %field_type = model.get('type', 'string')
         %content_type = model.get('content_type', field_type)
         %placeholder = model.get('placeholder', label)
         %comment = model.get('comment', label)
         %format = model.get('format')
         %unique = model.get('unique')
         %required = model.get('required')
         %editable = model.get('editable', True)

         <div class="well page">
            <h4>{{_('%s name:') % plugin.backend_endpoint.capitalize()}}</h4>
            <div class="form-group">
               <label class="control-label" for="{{field}}">{{_('Host name:')}}</label>
               <input class="form-control" type="text" id="{{field}}" name="{{field}}" placeholder="{{placeholder}}" value="" {{'readonly="readonly"' if not edition or not editable else ''}}>
               %if comment:
                  <p class="help-block">
                     {{comment}}
                     %if unique:
                     <br>{{_('This field must be unique.')}}
                     %end
                     %if required:
                     <br>{{_('This field is required.')}}
                     %end
                  </p>
               %end
            </div>
         </div>
      %end

      %if not element and ('_realm' in plugin.table or '_parent' in plugin.table):
         %field = '_realm'
         %if '_parent' in plugin.table:
         %field = '_parent'
         %end
         %model = plugin.table[field]

         %label = model.get('title', '')
         %field_type = model.get('type', 'string')
         %content_type = model.get('content_type', field_type)
         %placeholder = model.get('placeholder', label)
         %comment = model.get('comment', label)
         %allowed = model.get('allowed', '')
         %if not isinstance(allowed, list):
         %allowed = allowed.split(',')
         %end
         %if allowed[0] == '':
         %  allowed = []
         %end
         %format = model.get('format')
         %unique = model.get('unique')
         %required = model.get('required')
         %editable = model.get('editable', True)

         %list_values = []
         %is_list = True
         %selectize=True

         %linked_object_type = model.get('resource', '')
         %icon=''
         %if linked_object_type:
         %  icon = ElementState().get_icon_state('realm', 'unknown')
         %  icon=icon['icon'] if icon else ''
         %end
         <div class="well page">
            <h4>{{_('Realm:')}}</h4>
            <div class="form-group"  style="margin-bottom: 20px">
               <label for="{{field}}" class="col-md-2 control-label">{{label}}</label>
               <div class="col-md-10">
                  <div class="input-group">
                     <span class="input-group-addon text-info">
                        <i class="fa fa-clone" title="{{_('The value of this field is inherited from a template')}}"></i>
                     </span>
                     <select id="{{field}}" name="{{field}}"
                            class="form-control"
                            {{'readonly="readonly"' if not edition or not editable else ''}}>
                     </select>
                     <span class="input-group-addon text-info"><i class="fa fa-list"></i></span>
                  </div>
                  %if comment:
                  <p class="help-block">
                     {{comment}}
                     %if unique:
                     <br>{{_('This field must be unique.')}}
                     %end
                     %if required:
                     <br>{{_('This field is required.')}}
                     %end
                  </p>
                  %end
               </div>
            </div>
            <br/>
            %if selectize and edition:
            <script>
               $('#{{field}}').selectize({
                  %if not required:
                  'plugins': ["remove_button"],
                  %end

                  valueField: 'id',
                  labelField: 'name',
                  searchField: 'name',
                  create: false,

                  render: {
                     option: function(item, escape) {
                        return '<div>' +
                           %if icon:
                           '<i class="fa fa-{{icon}}"></i>&nbsp;' +
                           %end
                           (item.name ? '<span class="name">' + escape(item.name) + '</span>' : '') +
                           (item.alias ? '<small><em><span class="alias"> (' + escape(item.alias) + ')</span></em></small>' : '') +
                        '</div>';
                     },
                     item: function(item, escape) {
                        return '<div>' +
                           %if icon:
                           '<i class="fa fa-{{icon}}"></i>&nbsp;' +
                           %end
                           (item.name ? '<span class="name">' + escape(item.name) + '</span>' : '') +
                        '</div>';
                     }
                  },

                  %if allowed:
                  %  # List of allowed values
                  %  if allowed[0].startswith('inner://'):
                     preload: true,
                     openOnFocus: true,
                     load: function(query, callback) {
                        //if (!query.length) return callback();
                        $.ajax({
                           url: "{{allowed[0].replace('inner://', '/')}}",
                           type: 'GET',
                           error: function() {
                              callback();
                           },
                           success: function(res) {
                              // 10 first items only...
                              // callback(res.slice(0, 10));
                              callback(res);
                           }
                        });
                     },
                  %  else:
                     options: [
                     %     for option in allowed:
                        {
                           'id': '{{option}}', 'name': '{{model.get("allowed_%s" % option, option)}}'
                        },
                     %     end
                     ],
                  %  end
                  %end

                  maxItems: {{'null' if is_list or format == 'multiple' else '1'}},
                  closeAfterSelect: {{'true' if format == 'select' else 'false'}},

                  placeholder: '{{placeholder}}',
                  hideSelected: true,
                  %if not required:
                  allowEmptyOption: true
                  %end
               });
               // Add selected options / items to the control...
               var $select = $('#{{field}}').selectize();
               var selectize = $select[0].selectize;
               %for field_id, field_value in list_values:
                  selectize.addOption({id: "{{field_id}}", name: "{{field_value}}"});
               %end
               %for field_id, field_value in list_values:
                  selectize.addItem("{{field_id}}");
               %end
            </script>
            %end
         </div>
      %end

      %if not element and is_templated:
         %field = '_is_template'
         %model = plugin.table[field]

         %label = model.get('title', '')
         %comment = model.get('comment', label)
         %editable = model.get('editable', True)

         <div class="well page">
         <h4>{{_('The new %s element is a template:') % plugin.backend_endpoint.capitalize()}}</h4>
         <div class="form-group"  style="margin-bottom: 20px">
            <label class="col-md-2 control-label" for="{{field}}">{{label}}</label>
            <div class="col-md-offset-2 col-md-10">
               <div class="input-group">
                  <div class="togglebutton">
                     <label>
                        <input id="{{field}}" name="{{field}}" type="checkbox"
                           {{'disabled="disabled"' if not edition or not editable else ''}}
                           >
                     </label>
                  </div>
               </div>
               %if comment:
               <p class="help-block">
                  {{comment}}
               </p>
               %end
            </div>
         </div>
         </div>
      %end

      %if has_template or is_templated:
         %field = '_templates'
         %model = plugin.table['_templates']

         %label = model.get('title', '')
         %field_type = model.get('type', 'string')
         %content_type = model.get('content_type', field_type)
         %placeholder = model.get('placeholder', label)
         %comment = model.get('comment', label)
         %allowed = model.get('allowed', '')
         %if not isinstance(allowed, list):
         %allowed = allowed.split(',')
         %end
         %if allowed[0] == '':
         %  allowed = []
         %end
         %format = model.get('format')
         %unique = model.get('unique')
         %required = model.get('required')
         %editable = model.get('editable', True)

         %list_values = []
         %if element and element['_templates']:
         %for v in element['_templates']:
         %  list_values.append((v.id, v.name))
         %end
         %end
         %is_list = True
         %selectize=True

         %linked_object_type = model.get('resource', '')
         %icon=''
         %if linked_object_type:
         %  icon = ElementState().get_icon_state(linked_object_type, 'unknown')
         %  icon=icon['icon'] if icon else ''
         %end
         <div class="well page">
            <h4>{{_('Inherited templates:')}}</h4>
            <div class="form-group"  style="margin-bottom: 20px">
               <label for="{{field}}" class="col-md-2 control-label">{{label}}</label>
               <div class="col-md-10">
                  <div class="input-group">
                     <span class="input-group-addon text-info">
                        <i class="fa fa-clone" title="{{_('The value of this field is inherited from a template')}}"></i>
                     </span>
                     <select id="{{field}}" name="{{field}}"
                            class="form-control"
                            {{'readonly="readonly"' if not edition or not editable else ''}}>
                     </select>
                     <span class="input-group-addon text-info"><i class="fa fa-list"></i></span>
                  </div>
                  %if comment:
                  <p class="help-block">
                     {{comment}}
                     %if unique:
                     <br>{{_('This field must be unique.')}}
                     %end
                     %if required:
                     <br>{{_('This field is required.')}}
                     %end
                  </p>
                  %end
               </div>
            </div>
            <br/>
            %if selectize and edition:
            <script>
               $('#{{field}}').selectize({
                  %if not required:
                  'plugins': ["remove_button"],
                  %end

                  valueField: 'id',
                  labelField: 'name',
                  searchField: 'name',
                  create: false,

                  render: {
                     option: function(item, escape) {
                        return '<div>' +
                           %if icon:
                           '<i class="fa fa-{{icon}}"></i>&nbsp;' +
                           %end
                           (item.name ? '<span class="name">' + escape(item.name) + '</span>' : '') +
                           (item.alias ? '<small><em><span class="alias"> (' + escape(item.alias) + ')</span></em></small>' : '') +
                        '</div>';
                     },
                     item: function(item, escape) {
                        return '<div>' +
                           %if icon:
                           '<i class="fa fa-{{icon}}"></i>&nbsp;' +
                           %end
                           (item.name ? '<span class="name">' + escape(item.name) + '</span>' : '') +
                        '</div>';
                     }
                  },

                  %if allowed:
                  %  # List of allowed values
                  %  if allowed[0].startswith('inner://'):
                     preload: true,
                     openOnFocus: true,
                     load: function(query, callback) {
                        //if (!query.length) return callback();
                        $.ajax({
                           url: "{{allowed[0].replace('inner://', '/')}}",
                           type: 'GET',
                           error: function() {
                              callback();
                           },
                           success: function(res) {
                              // 10 first items only...
                              // callback(res.slice(0, 10));
                              callback(res);
                           }
                        });
                     },
                  %  else:
                     options: [
                     %     for option in allowed:
                        {
                           'id': '{{option}}', 'name': '{{model.get("allowed_%s" % option, option)}}'
                        },
                     %     end
                     ],
                  %  end
                  %end

                  maxItems: {{'null' if is_list or format == 'multiple' else '1'}},
                  closeAfterSelect: {{'true' if format == 'select' else 'false'}},

                  placeholder: '{{placeholder}}',
                  hideSelected: true,
                  %if not required:
                  allowEmptyOption: true
                  %end
               });
               // Add selected options / items to the control...
               var $select = $('#{{field}}').selectize();
               var selectize = $select[0].selectize;
               %for field_id, field_value in list_values:
                  selectize.addOption({id: "{{field_id}}", name: "{{field_value}}"});
               %end
               %for field_id, field_value in list_values:
                  selectize.addItem("{{field_id}}");
               %end
            </script>
            %end
         </div>
      %end

      %if edition:
      <div class="well form-group">
         <button type="reset" class="btn btn-default pull-left">{{_('Cancel')}}</button>
         <button type="submit" class="btn btn-primary pull-right">{{_('Submit')}}</button>
         <div class="clearfix"></div>
      </div>
      %end

      %#if element:
         %if debug and has_template:
         <div>
         <i class="fa fa-clone"></i>Templates fields: {{element['_template_fields']}}
         </div>
         %end

         %for field, model in plugin.table.iteritems():
            %selectize = False
            %if not model.get('editable', True) or (field[0] in ['#', '_'] and field not in ['_parent', '_realm']) or field.startswith('ls_'):
               %# Some fields are never displayed in a form...
               %if debug:
               %if element:
               <i class="fa fa-bug"></i><strong>Ignored</strong> '{{field}}' -> {{model}} field, value: {{element[field]}}<br>
               %else:
               <i class="fa fa-bug"></i><strong>Ignored</strong> '{{field}}' -> {{model}} field<br>
               %end
               %end
               %continue
            %end
            %if not element and not model.get('create_template', False):
               %# Only create_template=true fields are used when creating an element
               %if debug:
               <i class="fa fa-bug"></i><i class="fa fa-bug"></i><strong>Ignored</strong> '{{field}}' -> {{model}} field<br>
               %end
               %continue
            %end

            %if debug:
            <i class="fa fa-bug"></i>{{field}} -> {{model}}<br>
            %end

            %# Is a list of values?
            %is_list = False
            %list_values = []

            %label = model.get('title', '')
            %field_type = model.get('type', 'string')
            %content_type = model.get('content_type', field_type)
            %placeholder = model.get('placeholder', label)
            %comment = model.get('comment', label)
            %if is_template:
            %allowed = model.get('allowed_template', model.get('allowed', ''))
            %else:
            %allowed = model.get('allowed', '')
            %end
            %if not isinstance(allowed, list):
            %allowed = allowed.split(',')
            %end
            %if allowed[0] == '':
            %  allowed = []
            %end
            %format = model.get('format')
            %unique = model.get('unique')
            %required = model.get('required')
            %editable = model.get('editable', True)

            %if element:
            %field_value=element[field]
            %else:
            %if field_type=='integer':
            %field_value=int(model.get('default', '0'))
            %elif field_type=='float':
            %field_value=float(model.get('default', '0'))
            %elif field_type=='boolean':
            %field_value=model.get('default', False)
            %elif field_type=='dict':
            %field_value=eval(model.get('default', '{}'))
            %elif field_type=='list':
            %field_value=eval(model.get('default', '[]'))
            %elif field_type=='point':
            %field_value={"type": "Point", "coordinates": [46.60611, 1.87528]}
            %else:
            %field_value=model.get('default', '')
            %end
            %end

            %if field_type=='point':
            %field_value={'latitude': field_value['coordinates'][0], 'longitude': field_value['coordinates'][1]}
            %end

            %# The field value is a list
            %if isinstance(field_value, list):
            %  for v in field_value:
            %     if isinstance(v, BackendElement):
            %        list_values.append((v.id, v.name))
            %     elif isinstance(v, dict):
            %        for key,value in v.items():
            %           list_values.append(('%s|%s' % (key, value), '%s=%s' % (key, value)))
            %        end
            %     else:
            %        list_values.append((v, model.get("allowed_%s" % v, v)))
            %     end
            %  end
            %  is_list = True
            %  selectize=True

            %# The field value is a dictionary
            %elif isinstance(field_value, dict):
            %  for k,v in field_value.items():
            %     list_values.append(('%s|%s' % (k, v), '%s=%s' % (k, v)))
            %  end
            %  is_list = True
            %  selectize=True

            %# Field value is simple
            %else:
            %  if isinstance(field_value, BackendElement):
            %     list_values.append((field_value.id, field_value.name))
            %     field_value=field_value.name
            %     selectize=True
            %  else:
            %     list_values.append((field_value, model.get("allowed_%s" % field_value, field_value)))
            %     if allowed:
            %        selectize=True
            %     end
            %  end
            %end

            %if debug:
               <i class="fa fa-bug"></i>
               %if is_list:
               {{' is_list %s -> %s (%s) = %s' % (field, field_type, content_type, list_values)}}
               %else:
               {{'not list %s -> %s = %s (%s)' % (field, content_type, field_value, list_values)}}
               %end
               <br>
            %end

            %# Manage the different types of values
            %# ----------------------------------------------------------------------------------------
            %if field_type == 'hidden':
               <input type="hidden" name='{{name}}' value='{{value}}'/>
               %continue
            %end

            %if field_type in ['boolean']:
               <div class="form-group">
                  <label class="col-md-2 control-label" for="{{field}}">{{label}}</label>
                  <div class="col-md-offset-2 col-md-10">
                     <div class="input-group">
                        <span class="input-group-addon text-info">
                           %if has_template and field in element['_template_fields']:
                           <i class="fa fa-clone" title="{{_('The value of this field is inherited from a template')}}"></i>
                           %end
                        </span>
                        <div class="checkbox">
                           <label>
                              <input id="{{field}}" name="{{field}}" type="checkbox"
                                 {{'disabled="disabled"' if not edition or not editable else ''}}
                                 {{'checked="checked"' if field_value else ''}}
                                 >
                           </label>
                        </div>
                     </div>
                     %if comment:
                     <p class="help-block">
                     {{comment}}
                     %if unique:
                     <br>{{_('This field must be unique.')}}
                     %end
                     %if required:
                     <br>{{_('This field is required.')}}
                     %end
                     </p>
                     %end
                  </div>
               </div>
               %continue
            %end

            %linked_object_type = model.get('resource', '')
            %icon=''
            %if linked_object_type:
            %  icon = ElementState().get_icon_state(linked_object_type, 'unknown')
            %  icon=icon['icon'] if icon else ''
            %end
            <div class="form-group">
               <label for="{{field}}" class="col-md-2 control-label">{{label}}</label>
               <div class="col-md-10">
                  <div class="input-group">
                     <span class="input-group-addon text-info">
                        %if has_template and field in element['_template_fields']:
                        <i class="fa fa-clone" title="{{_('The value of this field is inherited from a template')}}"></i>
                        %end
                        %if is_list:
                        <i class="fa fa-list"></i>
                        %end
                     </span>
                     %if is_list:
                     <select id="{{field}}" name="{{field}}"
                            class="form-control"
                            {{'readonly="readonly"' if not edition or not editable else ''}}>
                     </select>
                     %elif format == 'textarea':
                     <textarea id="{{field}}" name="{{field}}"
                        class="form-control"
                        rows="3"
                        placeholder="{{placeholder}}"
                        {{'readonly="readonly"' if not edition or not editable else ''}}
                        >{{field_value}}</textarea>
                     %else:
                     <input id="{{field}}" name="{{field}}"
                        class="form-control"
                        type="{{'number' if field_type=='integer' else 'text'}}"
                        placeholder="{{placeholder}}"
                        value="{{field_value}}"
                        {{'readonly="readonly"' if not edition or not editable else ''}}
                        >
                     %end
                     <span class="input-group-addon text-info">
                        %if is_list:
                        <i class="fa fa-fw fa-list" title="{{_('The value of this field is a list of items')}}"></i>
                        %end
                     </span>
                  </div>
                  %if comment:
                  <p class="help-block">
                     {{comment}}
                     %if unique:
                     <br>{{_('This field must be unique.')}}
                     %end
                     %if required:
                     <br>{{_('This field is required.')}}
                     %end
                  </p>
                  %end
               </div>
            </div>
            %if selectize:
            <script>
               $('#{{field}}').selectize({
                  %if not required:
                  'plugins': ["remove_button"],
                  %end

                  valueField: 'id',
                  labelField: 'name',
                  searchField: 'name',

                  render: {
                     option: function(item, escape) {
                        return '<div>' +
                           %if icon:
                           '<i class="fa fa-{{icon}}"></i>&nbsp;' +
                           %end
                           (item.name ? '<span class="name">' + escape(item.name) + '</span>' : '') +
                           (item.alias ? '<small><em><span class="alias"> (' + escape(item.alias) + ')</span></em></small>' : '') +
                        '</div>';
                     },
                     item: function(item, escape) {
                        console.log("item {{field}}: ", item);
                        return '<div>' +
                           %if icon:
                           '<i class="fa fa-{{icon}}"></i>&nbsp;' +
                           %end
                           (item.name ? '<span class="name">' + escape(item.name) + '</span>' : '') +
                        '</div>';
                     }
                  },

                  %if allowed:
                  %  # List of allowed values
                  %  if allowed[0].startswith('inner://'):
                     create: false,
                     preload: true,
                     openOnFocus: true,
                     load: function(query, callback) {
                        //if (!query.length) return callback();
                        $.ajax({
                           url: "{{allowed[0].replace('inner://', '/')}}",
                           type: 'GET',
                           error: function() {
                              callback();
                           },
                           success: function(res) {
                              // 10 first items only...
                              // callback(res.slice(0, 10));
                              callback(res);

                           }
                        });
                     },
                  %  else:
                     options: [
                     %     for option in allowed:
                        {
                           'id': '{{option}}', 'name': '{{model.get("allowed_%s" % option, option)}}'
                        },
                     %     end
                     ],
                  %  end
                  %else:
                     create: true,
                  %end

                  maxItems: {{'null' if is_list or format == 'multiple' else '1'}},
                  closeAfterSelect: {{'true' if format == 'select' else 'false'}},

                  placeholder: '{{placeholder}}',
                  hideSelected: true,
                  %if not required:
                  allowEmptyOption: true,
                  allowed: '{{allowed}}'
                  %end
               });
               // Add selected options / items to the control...
               window.setTimeout(function() {
               var $select = $('#{{field}}').selectize();
               var selectize = $select[0].selectize;
               %for field_id, field_value in list_values:
                  selectize.addOption({id: "{{field_id}}", name: "{{field_value}}"});
               %end
               %for field_id, field_value in list_values:
                  selectize.addItem("{{field_id}}");
               %end
               }, 100);
            </script>
            %end
            %continue
         %end
      %#end
      </fieldset>

      <script>
         window.setTimeout(function() { $("div.alert-dismissible").alert('close'); }, 10000);
      </script>
      %if edition and element:
      <div class="well form-group">
         <button type="reset" class="btn btn-default pull-left">{{_('Cancel')}}</button>
         <button type="submit" class="btn btn-primary pull-right">{{_('Submit')}}</button>
         <div class="clearfix"></div>
      </div>
      %end
   </form>
</div>

%if edition:
<script>
   $('form[data-element="{{element.id if element else 'None'}}"]').on("submit", function (evt) {
      // Do not automatically submit ...
      evt.preventDefault();
      //console.log("Submit form...", $(this).attr('method'), $(this).attr('action'))

      // Submitting message
      wait_message('{{_('Submitting form...')}}', true)

      $.ajax({
         url: $(this).attr('action'),
         type: $(this).attr('method'),
         data: $(this).serialize()
      })
      .done(function(data, textStatus, jqXHR) {
         // data is JSON formed with a _message field
         if (jqXHR.status != 200) {
            console.error(jqXHR.status, data);
            raise_message_ko(data._message);
         } else {
            if (data._errors) {
               raise_message_ko(data._message);
               $.each(data._errors, function(field, value) {
                  console.error(field, value);
                  $('#'+field).parents("div.form-group").addClass("has-error");
                  raise_message_ko(field + ":" + value);
               })
            } else {
               raise_message_info(data._message);
            }
            $.each(data, function(field, value){
               if (field=='_message') return true;
               if (field=='_errors') return true;
               $('#'+field).parents("div.form-group").addClass("has-success");
               raise_message_ok("Updated " + field);
            });
            // Navigate to the new element edition form
            var url = document.location.href;
            url = url.replace("None", data['_id']);
            window.setTimeout(function() {
               window.location.href = url;
            }, 3000);
         }
      })
      .fail(function( jqXHR, textStatus, errorThrown ) {
         // data is JSON formed with a _message field
         if (jqXHR.status != 409) {
            console.error(errorThrown, textStatus);
         } else {
            raise_message_info(data._message);
            $.each(data, function(field, value){
               if (field=='_message') return true;
               $('#'+field).parents("div.form-group").addClass("has-success");
               raise_message_ok("Updated " + field);
            })
         }
      })
      .always(function() {
         wait_message('', false)
      });
   });
</script>
%end