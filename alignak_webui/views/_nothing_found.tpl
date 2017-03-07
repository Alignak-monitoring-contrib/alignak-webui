<div class="text-center alert alert-warning">
   %if search_string:
      <h4>{{_('What a bummer! We could not find anything.')}}</h4>
      <p>{{_('Use the pre-defined search filters to find what you are looking for, or try a new search query.')}}</p>
   %else:
      <h4>{{_('No elements found.')}}</h4>
   %end
</div>
