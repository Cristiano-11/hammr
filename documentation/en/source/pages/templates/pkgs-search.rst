.. Copyright (c) 2007-2016 UShareSoft, All rights reserved

.. _pkgs-search:

Searching for Packages
======================

You can search for the available packages as follows:

.. code-block:: shell

	$ hammr os search

When running a search you will need to specify the OS ``id`` and a search string.

.. code-block:: shell

	$ hammr os search --id 121 --pkg ntpdate
	Search package 'ntpdate' ...
	for OS 'CentOS', version 6
	+---------+---------+------+--------------+---------------------+------+
	|  Name   | Version | Arch |   Release    |     Build date      | Size |
	+=========+=========+======+==============+=====================+======+
	| ntpdate | 4.2.4p8 | i686 | 3.el6.centos | 2013-02-22 11:22:14 | 56K  |
	+---------+---------+------+--------------+---------------------+------+
	| ntpdate | 4.2.4p8 | i686 | 2.el6.centos | 2011-11-29 12:06:40 | 56K  |
	+---------+---------+------+--------------+---------------------+------+
	| ntpdate | 4.2.4p8 | i686 | 2.el6        | 2010-08-25 01:51:27 | 56K  |
	+---------+---------+------+--------------+---------------------+------+
	| ntpdate | 4.2.6p5 | i686 | 1.el6.centos | 2013-11-23 06:20:19 | 74K  |
	+---------+---------+------+--------------+---------------------+------+

	Found 4 packages

To get the OS ``id``, list the OS information by running:

.. code-block:: shell

	$ hammr os list