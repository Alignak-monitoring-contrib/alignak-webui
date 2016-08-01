%setdefault('read_only', False)
%setdefault('auto_post', False)

<div class="modal-header">
   <a class="close" data-refresh="start" data-dismiss="modal">×</a>
   <h3>{{title}}</h3>
</div>

<div class="modal-body">
   <form data-item="user" data-action="delete" method="post" action="/user/delete" role="form" enctype="multipart/form-data">
      <div class="form-group" style="display: none">
         <label for="user_id">{{_('User id: ')}}</label>
         <input type="text" readonly id="user_id" name="user_id" placeholder="{{user_id}}" value="{{user_id}}">
      </div>

      <div class="form-group" >
         <label for="user_name">{{_('User name: ')}}</label>
         <input type="text" readonly id="user_name" name="user_name" placeholder="{{user_name}}" value="{{user_name}}">
      </div>

      <div class="form-group">
         <textarea {{'readonly' if read_only else ''}} class="form-control" name="notes" id="notes" rows="3" placeholder="{{notes}}"></textarea>
      </div>

      <button type="submit" class="btn btn-danger btn-lg btn-block"> <i class="fa fa-close"></i>{{_('Confirm deletion')}}</button>
   </form>
</div>

<script type="text/javascript">
$(document).ready(function(){
   console.log("Loaded !")
   %if auto_post:
      console.log("Auto post !")
      // Submit form
      $('form[data-item="user"][data-action="delete"]').submit();
   %end
});
</script>
