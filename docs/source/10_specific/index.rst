.. raw:: LaTeX

    \newpage

.. _specific:

Specific parameters
===================

Hosts
-----------

Host location
~~~~~~~~~~~~~~~~~~~~~~~~

The Web UI allow to disply the monitored hosts on a map. To achieve this, each host should have GPS coordinates to get located properly.

Hosts fetched from the Alignak backend have a `location` GeoJson attribute that contains the host GPS coordinates. This position is used to locate the host on a map.

However, some specifc custom variables are handled by the Web UI:

    - `LOC_LAT` for the host latitude
    - `LOC_LNG` for the host longitude

Those variables, if they exist, are used first by the Web UI.


Custom variables
~~~~~~~~~~~~~~~~~~~~~~~~

All the host/service custom variables are displayed in the *Configuration* tab of the host/service view.

Some specifc custom variables are handled by the Web UI:

    - `DETAILLEDESC` contains the detailed description of the host/service
    - `IMPACT` contains the description of the impact of an host/service failure
    - `FIXACTIONS` contains the description of the actions that can be launched to fix a problem

Those variables, if they exist, are displayed in the host/service overview panel.


Notes and URLs
~~~~~~~~~~~~~~~~~~~~~~~~

In an host/service configuration, it is possible to define `notes`, `notes_url` and `action_url` This is how the Web UI uses these properties.

Each url may be formatted as:

    - url,,description
    - title::description,,url
    - title,,icon::description,,url

`description` is optional

If `title` is not specified, a default title is used as title
If `icon` is not specified, a default icon is used as icon

Some examples::

   notes                simple note
   notes                Label::note with a label
   notes                KB1023,,tag::<strong>Lorem ipsum dolor sit amet</strong>, consectetur adipiscing elit. Proin et leo gravida, lobortis nunc nec, imperdiet odio. Vivamus quam velit, scelerisque nec egestas et, semper ut massa. Vestibulum id tincidunt lacus. Ut in arcu at ex egestas vestibulum eu non sapien. Nulla facilisi. Aliquam non blandit tellus, non luctus tortor. Mauris tortor libero, egestas quis rhoncus in, sollicitudin et tortor.|note simple|Tag::tagged note ...

   notes_url            http://www.my-KB.fr?host=$HOSTADDRESS$|http://www.my-KB.fr?host=$HOSTNAME$

   action_url           http://www.google.fr|url1::http://www.google.fr|My KB,,tag::http://www.my-KB.fr?host=$HOSTNAME$|Last URL,,tag::<strong>Lorem ipsum dolor sit amet</strong>, consectetur adipiscing elit. Proin et leo gravida, lobortis nunc nec, imperdiet odio. Vivamus quam velit, scelerisque nec egestas et, semper ut massa.,,http://www.my-KB.fr?host=$HOSTADDRESS$

