Demonstration server configuration
===

This demo configuration is built to set-up a demo server 


What's behind this demo?
---

This demonstration is made to involve the most possible Alignak components on a single node server.

To set-up this demo, you must:

    - install Alignak
    - install Alignak backend
    - install Alignak Web UI
    - install Alignak modules (backend and nsca)
    - install Alignak checks packs (NRPE, WMI, SNMP, ...)
    - import the configuration into the backend
    - start the backend, the Web UI and Alignak
    - open your web browser and rest for a while looking at what happens :)

Setting-up the demo
---
  TO DO ...
  
Directory 'scripts'
---

This directory contains some example scripts to start/stop Alignak demonstration components.
Directory 'scripts'
---

This directory contains some example scripts to start/stop Alignak demonstration components.

The sub-directory *bash* is for `bash` shell environments (eg. Ubuntu, Debian, ...). 

The sub-directory *csh* is for `C` shell environments (eg. FreeBSD, ...). 

Directory 'alignak'
---

This directory is an Alignak configuration for:

    - loading monitored objects from the Alignak backend
    