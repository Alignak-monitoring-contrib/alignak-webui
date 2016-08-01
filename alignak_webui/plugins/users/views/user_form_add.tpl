%setdefault('read_only', False)
%setdefault('auto_post', False)

%# User attributes
%setdefault('password', 'default_password')
%setdefault('alias', 'Friendly name')
%setdefault('is_admin', False)
%setdefault('can_submit_commands', True)
%setdefault('expert', True)

<div class="modal-header">
   <a class="close" data-refresh="start" data-dismiss="modal">×</a>
    <h3>{{title}}</h3>
</div>

<div class="modal-body">
   <form data-item="user" data-action="add" class="form-horizontal" method="post" action="/user/add" role="form" enctype="multipart/form-data">
      <div class="form-group" >
         <label class="col-sm-3 control-label" for="name">{{_('User name: ')}}</label>
         <div class="col-sm-9">
            <input class="form-control" type="text" {{'readonly' if read_only else ''}} id="name" name="name" placeholder="{{name}}" value="{{name}}">
         </div>
      </div>

      <div class="form-group">
         <label class="col-sm-3 control-label" for="doc_name">{{_('Password: ')}}</label>
         <div class="col-sm-9">
            <input class="form-control" type="password" {{'readonly' if read_only else ''}} id="password" name="password" placeholder="{{password}}" value="">
         </div>
      </div>

      <div class="form-group">
         <label class="col-sm-3 control-label" for="doc_name">{{_('Friendly name: ')}}</label>
         <div class="col-sm-9">
            <input class="form-control" type="text" {{'readonly' if read_only else ''}} id="alias" name="alias" placeholder="Friendly name" value="{{alias}}">
         </div>
      </div>

      <div class="form-group">
         <label class="col-sm-3 control-label" for="doc_name">{{_('Mail address: ')}}</label>
         <div class="col-sm-9">
            <input class="form-control" type="email" {{'readonly' if read_only else ''}} id="mail" name="mail" placeholder="{{name}}@mail.com" value="">
         </div>
      </div>

      <div class="form-group">
         <label class="col-sm-3 control-label">{{_('User profile: ')}}</label>
         <div class="col-sm-offset-3 col-sm-9">
            <div class="checkbox">
               <label>
                  <input type="checkbox" {{'checked' if is_admin else ''}} value="{{is_admin}}"> {{_('User is an administrator')}}
               </label>
            </div>
         </div>
         <div class="col-sm-offset-3 col-sm-9">
            <div class="checkbox">
               <label>
                  <input type="checkbox" {{'checked' if not can_submit_commands else ''}} value="{{not can_submit_commands}}"> {{_('User is allowed to run commands')}}
               </label>
            </div>
         </div>
         <div class="col-sm-offset-3 col-sm-9">
            <div class="checkbox">
               <label>
                  <input type="checkbox" {{'checked' if expert else ''}} value="{{expert}}"> {{_('User is an expert')}}
               </label>
            </div>
         </div>
      </div>

      <div class="form-group">
         <div class="col-sm-12">
            <textarea hidden {{'readonly' if read_only else ''}} class="form-control" name="notes" id="notes" rows="3" placeholder="{{notes}}"></textarea>
         </div>
      </div>

      <button type="submit" class="btn btn-success btn-lg btn-block"> <i class="fa fa-check"></i>{{_('Confirm creation')}}</button>
   </form>
</div>

<script type="text/javascript">
$(document).ready(function(){
   %if auto_post:
      // Submit form
      $('form[data-item="user"]').submit();
   %end
});
</script>
