%setdefault('read_only', False)
%setdefault('auto_post', False)

%setdefault('form_class', 'form-horizontal')

%# Available commands
%setdefault('placeholder', _("Select a command from this list"))
%setdefault('commands_list', {'Yes': 'true', 'No': 'false', 'Both': ''})

%# command attributes
%setdefault('element', 'command')
%setdefault('action', 'add')
%setdefault('elements_type', '')
%setdefault('element_id', [])
%setdefault('element_name', 'unknown')

<div class="modal-header">
   <a class="close" data-dismiss="modal">×</a>
   <h3>{{title}}</h3>
   <small><em>
      {{', '.join(element_name) if elements_type else _("Alignak global command")}}
   </em></small>
</div>

<div class="modal-body">
   <form class="{{form_class}}" data-item="{{element}}" data-action="{{action}}" method="post" action="/{{element}}/{{action}}" role="form">
      <div class="form-group" style="display: none">
         %for id in element_id:
         <input type="text" readonly id="element_id" name="element_id" value="{{id}}">
         %end
         %for name in element_name:
         <input type="text" readonly id="element_name" name="element_name" value="{{name}}">
         %end
         <input type="text" readonly id="elements_type" name="elements_type" value="{{elements_type}}">
         <input type="text" readonly id="command" name="command" value="None">
      </div>

      <fieldset>
         <div class="form-group">
            <label class="col-md-2 control-label" for="commands_list">{{_('Available commands:')}}</label>
            <div class="col-md-offset-2 col-md-10">
               <select id="commands_list" class="form-control"></select>
               <p class="help-block">{{_('The selected command will pull the appropriate information fields to fill.')}}</p>
            </div>
         </div>

         <div id="command_parameters">

         </div>

         <div class="form-group">
            <div class="col-xs-12">
               <textarea hidden {{'readonly' if read_only else ''}} class="form-control" name="comment" id="comment" rows="1" placeholder="{{comment}}">{{comment}}</textarea>
               <p class="help-block">{{_('This comment will be associated to the command')}}</p>
            </div>
         </div>
      </fieldset>

      <button type="submit" class="btn btn-success btn-lg btn-raised"> <i class="fa fa-check"></i>&nbsp;{{_('Send command')}}</button>
   </form>
</div>

<script type="text/javascript">
var logs = false;

function add_field(where, id, obj) {
   if (logs) console.log("Add field", id, obj);

   if (! obj.default) obj.default = '';
   if (! obj.comment) obj.comment = '';

   if (obj.allowed) {
      add_field_list(where, id, obj);
   } else if (obj.type == 'integer') {
      add_field_integer(where, id, obj);
   } else if (obj.type == 'string') {
      add_field_text(where, id, obj);
   }
}
function add_field_integer(where, id, obj) {
   if (logs) console.log("Add an integer form field");

   var html = '<div class="form-group"> \
         <label class="col-md-2 control-label" for="'+ id +'">'+ obj.title +'</label> \
         <div class="col-md-offset-2 col-md-10"> \
            <input id="'+ id +'" name="'+ id +'" class="form-control" type="number" placeholder="'+ obj.default +'" value="'+ obj.default +'" /> \
            <p class="help-block">'+ obj.comment +'</p> \
         </div> \
      </div>';

   where.append(html);
}

function add_field_text(where, id, obj) {
   if (logs) console.log("Add a text form field");

   var html = '<div class="form-group"> \
         <label class="col-md-2 control-label" for="'+ id +'">'+ obj.title +'</label> \
         <div class="col-md-offset-2 col-md-10"> \
            <input id="'+ id +'" name="'+ id +'" class="form-control" type="text" placeholder="'+ obj.default +'" value="'+ obj.default +'" /> \
            <p class="help-block">'+ obj.comment +'</p> \
         </div> \
      </div>';

   where.append(html);
}

function add_field_list(where, id, obj) {
   if (logs) console.log("Add an integer form field");

   var html = '<div class="form-group"> \
         <label class="col-md-2 control-label" for="'+ id +'">'+ obj.title +'</label> \
         <div class="col-md-offset-2 col-md-10">';

   html = html + '<select id="'+ id +'" name="'+ id +'" class="form-control"></select>';

   if (logs) console.log("Allowed list:", obj.allowed);
   options = [];
   $.each(obj.allowed, function(key, value) {
      if (logs) console.log("Allowed key : "+key+" ; value : "+value);
      options.push({ 'id': key, 'name': value });
   });

   window.setTimeout(function() {
      var $select = $('#' + id).selectize({
         plugins: [],
         delimiter: ',',
         persist: true,

         valueField: 'id', labelField: 'name', searchField: 'name',
         create: false,

         render: {
            option: function(item, escape) {
               return '<div>' +
                  (item.name ? '<span class="name">' + escape(item.name) + '</span>' : '') +
                  (item.alias ? '<small><em><span class="alias"> (' + escape(item.alias) + ')</span></em></small>' : '') +
               '</div>';
            },
            item: function(item, escape) {
               return '<div>' +
                  (item.name ? '<span class="name">' + escape(item.name) + '</span>' : '') +
               '</div>';
            }
         },

         options: options,

         maxItems: 1,
         closeAfterSelect: true,

         //placeholder: obj.default,
         hideSelected: true,
         allowEmptyOption: false,

         onInitialize: function() {
            if (logs) console.log("Selectize initialized for", id);
         },
         onChange: function(value) {
            if (logs) console.log("Changed value:", id, value);
         }
      });

      // Add selected options / items to the control...
      var selectize = $select[0].selectize;
      $.each(obj.allowed, function(key, value) {
         if (logs) console.log("Add option: "+key+" ; value : "+value);
         selectize.addOption({id: key, name: value});
         selectize.addItem("key");
      });
      if (logs) console.log("Set default value", obj.default);
      selectize.setValue(obj.default, false)
   }, 500);

   html = html + '\
            <p class="help-block">'+ obj.comment +'</p> \
         </div> \
      </div>';

   where.append(html);
}

$(document).ready(function(){
   % allowed = commands_list
   $('#commands_list').selectize({
      plugins: [],
      delimiter: ',',
      persist: true,

      valueField: 'id',
      labelField: 'name',
      searchField: 'name',

      create: false,

      %if allowed:
      %  if isinstance(allowed, dict):
         options: [
      %     for k in allowed:
               { 'id': '{{k}}', 'name': '{{allowed[k].get('title', k)}}' },
      %     end
         ],
      %  end
      %end

      maxItems: 1,
      closeAfterSelect: true,
      placeholder: '{{placeholder}}',
      hideSelected: true,
      allowEmptyOption: false,
      onInitialize: function() {
         if (logs) console.log("Initialized!");
      },
      onChange: function(value) {
         if (logs) console.log("Changed:", value);

         $.ajax({
            url: '/command/parameters',
            method: "GET",
            data: { 'elements_type': '{{elements_type}}', 'command' : value }
         })
         .done(function( parameters, textStatus, jqXHR ) {
            if (logs) console.log('Got parameters: ', value, parameters);

            $('#command').val(value);
            $('#command_parameters').empty();
            $.each(parameters, function(key, value) {
               if (logs) console.log("key : "+key+" ; value : "+value);
               add_field($('#command_parameters'), key, value);
            });
         })
         .fail(function( jqXHR, textStatus, errorThrown ) {
            console.error('A problem occured, error: ', jqXHR, textStatus, errorThrown);
            raise_message_ko('A problem occured... report an issue for this please!');
         })
         .always(function() {
            // Do nothing...
         });
      }
   });

   %if auto_post:
      // Submit form
      $('form[data-item="command"]').submit();
   %end
});
</script>
