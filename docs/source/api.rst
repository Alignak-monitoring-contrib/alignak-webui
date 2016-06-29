.. _develop:

API
===========

External access
---------------
An external application can embed some Alignak WebUI widgets and pages.

Authentication
~~~~~~~~~~~~~~~~~~~~~~~~

Embedding a part of Alignak WebUI requires an authentication. Provide credentials in a Basic HTTP authentication form in the page request. The HTTP request must have an 'Authorization' header  containing the authentication. As of it, the WebUI will use this authentication parameters to check authentication on its Alignak backend.

API
~~~~~~~~~~~~~~~~~~~~~~~~

 URL syntax::

    GET <alignak_webui>/external/<type>/<identifier>

    where:
        <alignak_webui> is the base url of your Alignak WebUI (eg. http://127.0.0.1:8868)
        <type> = widget for a widget
        <type> = table for a table

        <identifier> is the identifier of the widget or table

Requests mode
~~~~~~~~~~~~~~~~~~~~~~~~

As default, the widget is provided as it is defined in the Alignak WebUI. Mainly, it is an HTML <div> with its content ...

.. image:: images/api-1.png


Use the URL parameter **page** to get a full page embeddable in an iframe. Without this parameter only the required widget is provided as a text/html response.

.. image:: images/api-2.png

Use the URL parameter **links** to have the navigable links in the embedded page. Else, the links are replaced with their text counterpart.

.. image:: images/api-3.png

Please note that in the default mode (no **page** parameter), it is the caller's responsibility to include the necessary Javascript and CSS files. Currently, those files are (at minimum)::

    <link rel="stylesheet" href="/static/css/bootstrap.min.css" >
    <link rel="stylesheet" href="/static/css/bootstrap-theme.min.css" >
    <link rel="stylesheet" href="/static/css/font-awesome.min.css" >
    <link rel="stylesheet" href="/static/css/alignak_webui-items.css" >

    <script type="text/javascript" src="/static/js/jquery-1.12.0.min.js"></script>
    <script type="text/javascript" src="/static/js/bootstrap.min.js"></script>

This list is to be confirmed but it should be the right one ;) All the Css and Javascript files (except for Alignak WebUI...) are easily found on CDNs...

For some external widgets, it is necessary to include also::

    <!-- Datatables jQuery plugin -->
    <link rel="stylesheet" href="/static/css/datatables.min.css" >
    <script type="text/javascript" src="/static/js/datatables.min.js"></script>
