.. raw:: LaTeX

    \newpage

.. _02_installation:

Installation
============

Requirements
------------


To use this application, you first need to install some Python modules that are listed in the ``requirements.txt`` file:

    .. literalinclude:: ../../../requirements.txt

**Note**: if you proceed to an end-user installation with pip, the required modules are automatically installed.

uWSGI
~~~~~

We recommend to use uWSGI as an application server for the Alignak WebUI and we provide a python pip installer that has `uwsgi` as a requirement.

If you prefer using your Unix/Linux ditribution packaging to install uWSGI and the alignak backend (not yet packaged... help needed for this), please refer to your distribution packages for installing. You will also need to install the uWSGI Python plugin.

As an example on Debian::

    sudo apt-get install uwsgi uwsgi-plugin-python


.. warning:: If you get some errors with the plugins, you will need to set some options in the alignak backend */usr/local/etc/alignak-backend/uwsgi.ini* configuration file. See this configuration file commented accordingly.


Installation with PIP
---------------------

**Note** that the recommended way for installing on a production server is mostly often to use the packages existing for your distribution. Nevertheless, the pip installation provides a startup script using an uwsgi server and, for FreeBSD users, rc.d scripts.

End user installation
~~~~~~~~~~~~~~~~~~~~~

You can install with pip::

    sudo pip install alignak-webui

The required Python modules are automatically installed if not they are not yet present on your system.


From source
~~~~~~~~~~~

You can install it from source::

    git clone https://github.com/Alignak-monitoring/alignak-webui
    cd alignak-webui
    pip install .


For contributors
~~~~~~~~~~~~~~~~

If you want to hack into the codebase (e.g for future contribution), just install like this::

    pip install -e .


Install from source without pip
-------------------------------

If you are on Debian:
::

    sudo apt-get -y install python python-dev python-pip git


Get the project sources:
::

    git clone https://github.com/Alignak-monitoring/alignak-webui


And then install::

    cd alignak-webui
    python setup.py install
