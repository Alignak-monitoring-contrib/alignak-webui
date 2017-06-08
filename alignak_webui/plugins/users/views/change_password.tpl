%setdefault('read_only', False)
%setdefault('auto_post', False)

%setdefault('form_class', 'form-horizontal')

%# Acknowledge attributes
%setdefault('element', 'user')
%setdefault('action', 'password')
%setdefault('elements_type', 'host')
%setdefault('element_id', '-1')
%setdefault('element_name', 'unknown')

<div class="modal-header">
   <a class="close" data-dismiss="modal">×</a>
   <h3>{{title}}</h3>
   <small>{{_('User login:')}}<em>
      {{', '.join(element_name)}}
   </em></small>
</div>

<div class="modal-body">
   <form id="password_change" class="{{form_class}}" data-action="{{action}}" method="post" action="/change_password" role="form">
      <div class="form-group" style="display: none">
         %for id in element_id:
         <input type="text" readonly id="element_id" name="element_id" value="{{id}}"/>
         %end
         %for name in element_name:
         <input type="text" readonly id="element_name" name="element_name" value="{{name}}"/>
         %end
         <input type="text" readonly id="elements_type" name="elements_type" value="{{elements_type}}"/>
         <input type="text" readonly id="valid_form" name="valid_form" value="false"/>
      </div>

      <fieldset>
         <div class="form-group">
            <label class="col-xs-4 control-label" for="password1">{{_('New password:')}}</label>
            <div class="checkbox col-xs-8">
               <label>
                  <input type="password" class="input-lg form-control" name="password1" id="password1"
                         placeholder="{{_('New password')}}" autocomplete="off">
               </label>
               <div class="row"><small>
                  <span id="8char" class="text-danger fa fa-close"></span>{{_('Eight characters long')}}
                  <span id="ucase" class="text-danger fa fa-close"></span>{{_('One uppercase letter')}}
                  <span id="lcase" class="text-danger fa fa-close"></span>{{_('One lowercase letter')}}
                  <span id="num" class="text-danger fa fa-close"></span>{{_('One number')}}
               </small></div>
               <p class="help-block">{{_('The password must be 8 characters long minimum, and it must contain one upppercase letter, one lowercase letter and one number.')}}</p>
            </div>
         </div>

         <div class="form-group">
            <label class="col-xs-4 control-label" for="password2">{{_('Confirm password:')}}</label>
            <div class="checkbox col-xs-8">
               <label>
                  <input type="password" class="input-lg form-control" name="password2" id="password2"
                         placeholder="{{_('Confirm password')}}" autocomplete="off">
               </label>
               <div class="row"><small>
                  <span id="passwords_match" class="text-danger fa fa-close"></span> {{_('Passwords match')}}
               </small>
               <p class="help-block">{{_('Repeat the passwork you entered in the first form field.')}}</p>
            </div>
         </div>
      </fieldset>

      <button type="submit" class="btn btn-success btn-lg btn-raised"> <i class="fa fa-check"></i>&nbsp;{{_('Set new password')}}</button>
   </form>
</div>

<script type="text/javascript">
$(document).ready(function() {
   action_logs = false;
   $('#password_change').on("submit", function (evt) {
      if (action_logs) console.debug('Submit form data: ', $(this));
      if (action_logs) console.debug('Form action: ', $(this).data("action"));
      if (action_logs) console.debug('Form fields: ', $(this).serialize({ checkboxesAsBools: true }));

      // Do not automatically submit ...
      evt.preventDefault();

      $.ajax({
         url: $(this).attr('action'),
         type: $(this).attr('method'),
         data: $(this).serialize({ checkboxesAsBools: true })
      })
      .done(function( data, textStatus, jqXHR ) {
         if (action_logs) console.debug('Submit form result: ', data, textStatus);
         if (jqXHR.status != 200) {
            raise_message_ko(data.message);
         } else {
            raise_message_ok(data.message)
         }
      })
      .fail(function( jqXHR, textStatus, errorThrown ) {
         raise_message_ko(jqXHR.responseJSON['message']);
      })
     .always(function() {
         window.setTimeout(function() {
            // Hide modal popup
            $('#mainModal').modal('hide');

            // Page refresh required
            refresh_required = true;
         }, refresh_delay_after_action);
      });
   });

   function check_password_form() {
      var valid = true;
      var ucase = new RegExp("[A-Z]+");
      var lcase = new RegExp("[a-z]+");
      var num = new RegExp("[0-9]+");

      if ($("#password1").val().length >= 8) {
         $("#8char").removeClass("fa-close");
         $("#8char").addClass("fa-check");
         $("#8char").removeClass("text-danger");
         $("#8char").addClass("text-success");
      } else {
         valid = false;
         $("#8char").removeClass("fa-check");
         $("#8char").addClass("fa-close");
         $("#8char").removeClass("text-success");
         $("#8char").addClass("text-danger");
      }

      if (ucase.test($("#password1").val())) {
         $("#ucase").removeClass("fa-close");
         $("#ucase").addClass("fa-check");
         $("#ucase").removeClass("text-danger");
         $("#ucase").addClass("text-success");
      } else {
         valid = false;
         $("#ucase").removeClass("fa-check");
         $("#ucase").addClass("fa-close");
         $("#ucase").removeClass("text-success");
         $("#ucase").addClass("text-danger");
      }

      if (lcase.test($("#password1").val())) {
         $("#lcase").removeClass("fa-close");
         $("#lcase").addClass("fa-check");
         $("#lcase").removeClass("text-danger");
         $("#lcase").addClass("text-success");
      } else {
         valid = false;
         $("#lcase").removeClass("fa-check");
         $("#lcase").addClass("fa-close");
         $("#lcase").removeClass("text-success");
         $("#lcase").addClass("text-danger");
      }

      if (num.test($("#password1").val())) {
         $("#num").removeClass("fa-close");
         $("#num").addClass("fa-check");
         $("#num").removeClass("text-danger");
         $("#num").addClass("text-success");
      } else {
         $("#num").removeClass("fa-check");
         $("#num").addClass("fa-close");
         $("#num").removeClass("text-success");
         $("#num").addClass("text-danger");
      }

      if ($("#password1").val() == $("#password2").val()) {
         $("#passwords_match").removeClass("fa-close");
         $("#passwords_match").addClass("fa-check");
         $("#passwords_match").css("color","#00A41E");
      } else {
         valid = false;
         $("#passwords_match").removeClass("fa-check");
         $("#passwords_match").addClass("fa-close");
         $("#passwords_match").css("color","#FF0004");
      }

      $("#valid_form").val(valid);
      return valid;
   }

   $("#password1").keyup(function() {
      check_password_form()
   });
   $("#password2").keyup(function() {
      check_password_form()
   });
});
</script>
