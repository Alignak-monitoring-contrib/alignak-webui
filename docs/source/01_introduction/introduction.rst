.. _introduction/introduction:


=============
About Alignak
=============

Alignak is an open source monitoring framework written in Python under the terms of the `GNU Affero General Public License`_ .
It is a fork of the Shinken project.

More information about Alignak is available in the `Alignak documentation <http://alignak-doc.readthedocs.io/en/latest/>`_.


===================
About Alignak WebUI
===================

The Alignak Web User Interface is an open source Web application written in Python under the terms of the `GNU Affero General Public License`_ .

It is intended to be used in the Alignak project as a Web User Interface to allow users to visualize and interact with the monitoring framework.


Alignak WebUI
=============

The main idea when developing this application is the configurability and the best suitability for
the needs of the different categories of users involved around the monitored system.


Features
========

Alignak WebUI has a lot of features:

  * nice and modern UI design, thanks to using the Bootstrap and Material Design librairies

  * user role management, thanks to the best use of the Alignak backend features, the WebUI user is granted rights on the monitored objects

  * configurability, many configuration parameters allow to customize the look and feel of the interface. Each user can have its own view on the system.

  * external widgets, many of the WebUI views are available to be used by an external application (such as the Glpi application and its Plugin Monitoring)


Release cycle
=============

Alignak WebUI has no strict schedule for releasing.

Feature addition is discussed throught the `project issues <https://github.com/Alignak-monitoring-contrib/alignak-webui>`_. Each feature is discussed in a separate issue.

.. _GNU Affero General Public License: http://www.gnu.org/licenses/agpl.txt
