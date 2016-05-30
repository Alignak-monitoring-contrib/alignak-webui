
<div class="panel-heading">
   <center class="alert-warning">
   %if search_string:
      <h3>{{_('What a bummer! We could not find anything.')}}</h3>
      {{_('Use the filters or the bookmarks to find what you are looking for, or try a new search query.')}}
   %else:
      <h3>{{_('No elements found.')}}</h3>
   %end
   </center>
</div>