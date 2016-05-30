.. _install:

Installation
============

Requirements
------------


To use this application, you first need to install some Python modules that are listed in the ``requirements.txt`` file:

    .. literalinclude:: ../../requirements.txt

**Note**: if you proceed to an end-user installation with pip, the required modules are automatically installed.

Installation with PIP
------------------------

End user installation
~~~~~~~~~~~~~~~~~~~~~~~~

You can install with pip::

    pip install alignak_webui

The required Python modules are automatically installed if not present on your system.


From source
~~~~~~~~~~~~~~~~~~~~~~~~

You can install it from source::

    git clone https://github.com/Alignak-monitoring/alignak-webui
    cd alignak-webui
    pip install .


For contributors
~~~~~~~~~~~~~~~~~~~~~~~~

If you want to hack into the codebase (e.g for future contribution), just install like this::

    pip install -e .


Install from source without pip
-------------------------------

If you are on Debian::

    apt-get -y install python python-dev python-pip git


Get the project sources::

    git clone https://github.com/Alignak-monitoring/alignak-webui


Install python prerequisites::

    pip install -r alignak-webui/requirements.txt


And then install::

    cd alignak-webui
    python setup.py install
