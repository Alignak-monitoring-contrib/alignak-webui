<!-- A modal div that will be filled and shown to create a waiting box... -->
<div id="waitingModal"
   class="modal fade" tabindex="-1" role="dialog" aria-labelledby="waitingModal"
   data-keyboard="false" data-backdrop="static">
   <div class="modal-dialog modal-sm">
      <div class="modal-content">
         <div class="modal-header text-center">
            <h4 class="modal-title">{{_('Default waiting message')}}</h4>
         </div>
         <div class="modal-body">
            <div style="height:120px" class="text-center">
               <i class="fa fa-spinner fa-spin fa-5x fa-fw"></i>
               <span class="sr-only">{{_('Loading...')}}</span>
            </div>
         </div>
      </div>
   </div>
</div>
