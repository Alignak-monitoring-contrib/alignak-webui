Alignak Web UI
##############

*Web User Interface for Alignak monitoring framework ...*

.. image:: https://api.travis-ci.org/Alignak-monitoring-contrib/alignak-webui.svg?branch=develop
    :target: https://travis-ci.org/Alignak-monitoring-contrib/alignak-webui
    :alt: Develop branch build status

.. image:: https://landscape.io/github/Alignak-monitoring-contrib/alignak-webui/develop/landscape.svg?style=flat
    :target: https://landscape.io/github/Alignak-monitoring-contrib/alignak-webui/develop
    :alt: Development code static analysis

.. image:: https://codecov.io/gh/Alignak-monitoring-contrib/alignak-webui/branch/develop/graph/badge.svg
    :target: https://codecov.io/gh/Alignak-monitoring-contrib/alignak-webui
    :alt: Development code tests coverage

.. image:: https://readthedocs.org/projects/alignak-web-ui/badge/?version=develop
    :target: http://alignak-web-ui.readthedocs.io/?badge=develop
    :alt: Documentation Status

.. image:: https://badge.fury.io/py/alignak_webui.svg
    :target: https://badge.fury.io/py/alignak_webui
    :alt: Most recent PyPi version

.. image:: https://img.shields.io/badge/IRC-%23alignak-1e72ff.svg?style=flat
    :target: http://webchat.freenode.net/?channels=%23alignak
    :alt: Join the chat #alignak on freenode.net

.. image:: https://img.shields.io/badge/License-AGPL%20v3-blue.svg
    :target: http://www.gnu.org/licenses/agpl-3.0
    :alt: License AGPL v3


Warning
=======

As of now, the Alignak project is only maintained by one person. Though, I will not be able to maintain this Web UI anymore... sorry. For my own production environment, I am currently an alternative solution base on the former Shinken Web UI that I developed and still maintain. If you are using this Web UI for your Alignak instance, please feel free to contact me by mail

Screenshots
===========
.. image:: docs/source/images/Alignak-WebUI-captures.gif

Documentation
=============

You can find online documentation on `Read The Docs <http://alignak-web-ui.readthedocs.io/?badge=latest>`_ and in the */docs* directory.


Installation
============

The Alignak WebUI is easily installed and started thanks to the Python Package::

    # Installing...
    pip install alignak-webui
    # Running...
    alignak-webui-uwsgi
    # Using!
    http://127.0.0.1:5001


**Note**: *Please note that you need to have a running Alignak framework reporting the live state to the Alignak backend.*


Bugs, issues and contributing
=============================

Contributions to this project are welcome and encouraged, but please have a look to the `contributing guidelines <./CONTRIBUTING.md/>`_  before raising an issue, or writing code for the project.


License
=======

Alignak WebUI is available under the `GPL version 3 <http://opensource.org/licenses/GPL-3.0>`_.

