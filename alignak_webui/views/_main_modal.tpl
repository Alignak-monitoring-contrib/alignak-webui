%setdefault('modal_style', '')

<!-- A modal div that will be filled and shown when we want forms ... -->
<div id="mainModal" class="modal fade" role="dialog" aria-labelledby="{{_('Generic modal box')}}" aria-hidden="true">
   <div class="modal-dialog {{modal_style}}">
      <div class="modal-content">
         <div class="modal-header">
            <h4 class="modal-title">{{_('Generic modal box')}}</h4>
         </div>
         <div class="modal-body">
            <!-- Filled by application ... -->
         </div>
         <div class="modal-footer">
            <a href="#" class="btn btn-default" data-dismiss="modal">{{_('Close')}}</a>
         </div>
      </div>
   </div>
</div>

