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


  <h4>{{! _('Search by the state of an element')}}</h4>
  <p>{{! _('The <code>is</code> and <code>isnot</code> field qualifiers finds elements by a certain state. For example:')}}</p>
  <ul>
    <li><code>is:DOWN</code> matches elements that are DOWN.</li>
    <li><code>isnot:0</code> matches services and hosts that are not OK or UP (all the problems). Equivalent to <code>isnot:OK isnot:UP</code></li>
    <li><code>load isnot:ok</code> matches elements which name contains <em>load</em> and which state is not <em>ok</em>.</li>
    <li><code>is:ack</code> matches elements that are acknownledged.</li>
    <li><code>is:downtime</code> matches elements that are in a scheduled downtime.</li>
  </ul>

  <p><strong>Note:</strong> default search on state is made only against HARD states.</p>
  <p>Preceding the state with the letter <code>s</code> makes the search only consider SOFT states. For example:</p>
  <ul>
    <li><code>is:sDOWN</code> matches hosts that are SOFT state DOWN.</li>
    <li><code>isnot:s0</code> matches services and hosts that are SOFT state not OK neither UP (all the not yet confirmed problems)</li>
  </ul>

  <h4>Search by the business impact of an element</h4>
  <p>The <code>bp</code> qualifier finds elements by it's business priority. For example:</p>
  <ul>
    <li><code>bp:5</code> matches hosts and services that are top for business.</li>
    <li><code>bp:>1</code> matches hosts and services with a business impact greater than 1.</li>
  </ul>

  <h4>Search by duration</h4>
  <p>You can also search by the duration of the last state change. This is very useful to find elements that are warning or critical for a long time. For example:</p>
  <ul>
    <li><code>isnot:OK duration:>1w</code> matches hosts and services not OK for at least one week.</li>
    <li><code>isnot:OK duration:<1h</code> matches hosts and services not OK for less than one hour.</li>
  </ul>
  <p>You can use the following time units: s(econds), m(inutes), h(ours), d(ays), w(eeks).</p>

  <p>Of course, you can't use the "=" sign here. Finding something that is exactly matching would be a huge luck.</p>

  <h4>Search by host group, service group, host tag and service tag</h4>
  <p>Examples:</p>
  <ul>
    <li><code>hg:infra</code> matches hosts in the group "infra".</li>
    <li><code>sg:test</code> matches services in the group "test".</li>
    <li><code>htag:linux</code> matches hosts tagged "linux".</li>
    <li><code>stag:mysql</code> matches services tagged "mysql".</li>
  </ul>

  <p>Obviously, you can't combine htag and stag qualifiers in a search and expect to get results.</p>

  <h4>Search by contact group and contact tag</h4>
  <p>Examples:</p>
  <ul>
    <li><code>cg:admins</code> matches hosts and services related to contacts in contact group "admins".</li>
    <li><code>ctag:client</code> matches hosts and services related to contacts tagged "client".</li>
  </ul>

  <h4>Find hosts and services by realm</h4>
  <p>The <code>realm</code> qualifier finds elements by a certain realm. For example:</p>
  <ul>
    <li><code>realm:aws</code> matches all AWS hosts and services.</li>
  </ul>
</div>
