%setdefault('read_only', False)
%setdefault('auto_post', False)

%# User attributes
%setdefault('password', 'default_password')
%setdefault('friendly_name', 'Friendly name')
%setdefault('is_admin', False)
%setdefault('is_read_only', True)
%setdefault('widgets_allowed', True)

<div class="modal-header">
   <a class="close" data-refresh="start" data-dismiss="modal">×</a>
    <h3>{{title}}</h3>
</div>

<div class="modal-body">
   <form data-item="user" data-action="add" class="form-horizontal" method="post" action="/user/add" role="form" enctype="multipart/form-data">
      <div class="form-group" >
         <label class="col-sm-3 control-label" for="user_name">{{_('User name: ')}}</label>
         <div class="col-sm-9">
            <input class="form-control" type="text" {{'readonly' if read_only else ''}} id="user_name" name="user_name" placeholder="{{user_name}}" value="{{user_name}}">
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
            <input class="form-control" type="text" {{'readonly' if read_only else ''}} id="friendly_name" name="friendly_name" placeholder="Friendly name" value="{{friendly_name}}">
         </div>
      </div>

      <div class="form-group">
         <label class="col-sm-3 control-label" for="doc_name">{{_('Mail address: ')}}</label>
         <div class="col-sm-9">
            <input class="form-control" type="email" {{'readonly' if read_only else ''}} id="mail" name="mail" placeholder="mail" value="">
         </div>
      </div>

      <div class="form-group">
         <label class="col-sm-3 control-label" for="doc_name">{{_('Skype address: ')}}</label>
         <div class="col-sm-9">
            <input class="form-control" type="email" {{'readonly' if read_only else ''}} id="lync" name="lync" placeholder="{{user_name}}@easyshare.ipmfrance.com" value="">
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
                  <input type="checkbox" {{'checked' if not is_read_only else ''}} value="{{not is_read_only}}"> {{_('User is allowed to run commands')}}
               </label>
            </div>
         </div>
         <div class="col-sm-offset-3 col-sm-9">
            <div class="checkbox">
               <label>
                  <input type="checkbox" {{'checked' if widgets_allowed else ''}} value="{{widgets_allowed}}"> {{_('User can change dashboard widgets')}}
               </label>
            </div>
         </div>
      </div>

      <div class="form-group">
         <div class="col-sm-12">
            <textarea hidden {{'readonly' if read_only else ''}} class="form-control" name="comment" id="comment" rows="3" placeholder="{{comment}}"></textarea>
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
