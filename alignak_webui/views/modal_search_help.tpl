<!-- DOCUMENTATION MODAL -->
<div class="modal-header">
  <button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>
  <h3 class="modal-title">{{_('Searching elements')}}</h3>
</div>

<div class="modal-body">
  <p>{{! _('The application search engine is using search qualifiers to build a search query. A qualifier is made of <code>field:pattern</code> where <em>field</em> is the concerned field identifier and <em>pattern</em> is the search pattern applied to this field.')}}</p>

  <p>{{! _('Several search qualifiers can be present in the search query and they must be separated with the space character: <code>field:pattern field:pattern</code>')}}</p>

  <p>{{! _('The <em>pattern</em> used for a field is considered as a regular expression. Searching with <code>field:pattern</code> will return all the elements which <em>name</em> field contains the string <em>pi</em>. To search for an exact match for a value in a <em>field</em>, use <code>field:^value$</code>.')}}</p>

  <p>{{! _('<strong>Note:</strong> the <em>field</em> or <em>pattern</em> may be surrounded by simple or double quotes if needed.')}}</p>

  <p>{{! _('<strong>Note:</strong> omitting the <em>field</em> in the search qualifier is considered as using an implicit <em>name</em> field.')}}</p>


  <h4>{{! _('Search by name')}}</h4>
  <p>{{! _('Searching elements by their name, examples:')}}</p>
  <ul>
    <li>{{! _('<code>name:pi</code> or <code>pi</code> matches elements with <em>pi</em> in their name.')}}</li>
    <li>{{! _('<code>^pi1$</code> matches elements which name is <em>pi1</em>.')}}</li>
    <li>{{! _('<code>pi1 pi2</code> matches elements with <em>pi1</em> or <em>pi2</em> in their name.')}}</li>
  </ul>


  <h4>{{! _('Search by another field')}}</h4>
  <p>{{! _('Searching by any field of elements, examples:')}}</p>
  <ul>
    <li>{{! _('<code>alias:pi</code> matches elements with <em>pi</em> in their alias field.')}}</li>
    <li>{{! _('<code>name:pi alias:pi</code> matches elements with <em>pi</em> in their name and alias fields.')}}</li>
  </ul>

  <p>{{! _('<strong>Note:</strong> the available field identifiers depends of the searched element type. Finding the field identifier to use in the search qualifiers is quite easy. In the elements table view, you can hover the corresponding column title to display the field identifier.')}}</p>

  <p>{{! _('<strong>Note:</strong> some existing fields are not included in the elements table view, only the most common are. The full list of field identifiers is defined in the <em>settings.cfg</em> file of each plugin but not currently published in the doc. Hopefully coming soon...')}}</p>


  <h4>{{! _('Negate the search')}}</h4>
  <p>{{! _('Using the <code>!</code> as the first character of the search pattern negates the search request. Some examples:')}}</p>
  <ul>
    <li>{{! _('<code>alias:!pi</code> matches elements which do not have <em>pi</em> in their alias field.')}}</li>
    <li>{{! _('<code>name:pi alias:!pi</code> matches elements with <em>pi</em> in their name field but not in their alias field.')}}</li>
  </ul>



  <h4>{{! _('Search by the state of an element')}}</h4>
  <p>{{! _('The <code>is</code> and <code>isnot</code> field qualifiers search elements by a certain state. For example:')}}</p>
  <ul>
    <li><code>is:OK</code> matches elements which live state is Ok.</li>
    <li><code>is:OK is:warning</code> matches elements which live state is Ok or Warning</li>
    <li><code>load isnot:ok</code> matches elements which name contains <em>load</em> and which state is not <em>ok</em>.</li>
    <li><code>is:ack</code> matches elements that are acknownledged.</li>
    <li><code>is:downtime</code> matches elements that are in a scheduled downtime.</li>
  </ul>

  <p>{{! _('<strong>Note:</strong> the state search is only available for searching hosts or services, because they are the only elements that have a live state to search for.')}}</p>
  <p>{{! _('The available searchable states are:')}}</p>
  <ul>
    <li>{{! _('<code>ok</code>: matches hosts/services that are Ok/Up.')}}</li>
    <li>{{! _('<code>acknowledged</code>: matches hosts/services that are a problem but acknowledged.')}}</li>
    <li>{{! _('<code>in_downtime</code>: matches hosts that are currently in a downtime period.')}}</li>
    <li>{{! _('<code>warning</code>: matches services that are Warning or Unknown or hosts that have some warning services.')}}</li>
    <li>{{! _('<code>critical</code>: matches services that are Critical or Unreachable or hosts that have some critical services.')}}</li>
  </ul>

  <h4>{{! _('Search by the business impact of an element')}}</h4>
  <p>{{! _('The <code>bi</code> qualifier searches elements by their business impact. For example:')}}</p>
  <ul>
    <li>{{! _('<code>bi:5</code> matches hosts and services that are top for business.')}}</li>
    <li>{{! _('<code>bi:>1</code> matches hosts and services with a business impact greater than 1.')}}</li>
  </ul>
</div>
