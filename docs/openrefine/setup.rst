*****
Setup
*****

This part describes how to set up your own OpenRefine with the **metadata** extension and how to configure it according to your needs.


Installation
============

There are two ways of using our **metadata** extension for OpenRefine. You can have installed OpenRefine and add extension to it or use Docker with our prepared image.

Installed OpenRefine
--------------------

This option requires you to have installed compatible version of OpenRefine, please check :ref:`openrefine-compatibility`. In case you need to install OpenRefine first, visit their `documentation <https://github.com/OpenRefine/OpenRefine/wiki/Installation-Instructions>`_. 

* Get the desired version of the **metadata** extension from `our GitHub releases page <https://github.com/FAIRDataTeam/OpenRefine-metadata-extension/releases>`_ by downloading tgz or zip archive, e.g., ``metadata-1.1.0-OpenRefine-3.2.zip``.
* Extract the archive to ``extensions`` folder of your OpenRefine (see `OpenRefine documentation <https://github.com/OpenRefine/OpenRefine/wiki/Installing-Extensions>`_).

::

   unzip metadata-1.1.0-OpenRefine-3.2.zip path/to/openrefine-3.2/webapp/extensions


With Docker
-----------

If you want to use Docker, we provide a Docker image `fairdata/openrefine-metadata-extension <https://hub.docker.com/r/fairdata/openrefine-metadata-extension>`_ that combines the extension with OpenRefine of supported version. It is of course possible to use volume for the ``data`` directory (eventually ``data/extensions`` to include other extensions). All you need to have is Docker running and then:

::

   docker run -p 3333:3333 -v /home/me/openrefine-data:/data:z fairdata/openrefine-metadata-extension

This will run the OpenRefine with **metadata** extension on port 3333 that will be exposed and mounts your folder ``/home/me/openrefine-data`` as OpenRefine data folder. You should be able to open OpenRefine in browser on ``localhost:3333``. If there are some other extensions in ``/home/me/openrefine-data/extensions``, those should be loaded as well. For more information, see `OpenRefine documentation <https://github.com/OpenRefine/OpenRefine/wiki/Installing-Extensions>`_.

For configuration files you need to mount ``/webapp/extensions/metadata/module/config``, see :ref:`openrefine-configuration` for more details.


.. _openrefine-configuration:

Configuration
=============

Configuration files of the **metadata** extension use the :abbr:`YAML (YAML Ain't Markup Language)` format and are stored in ``extensions/metadata/module/config`` directory of the used OpenRefine installment. The configuration files are loaded when OpenRefine is started. Therefore, you are required to restart OpenRefine before changes in configuration files take effect. We provide `examples <https://github.com/FAIRDataTeam/OpenRefine-metadata-extension/tree/develop/src/main/resources/module/config>`_ of the configuration files that you can (re)use.

.. _openrefine-configuration-settings:

Settings
--------

Settings configuration file serves for generic configuration options that adjust behaviour of the extension. The structure of the file is following:

* ``allowCustomFDP`` (boolean) = should be user allowed to enter custom FAIR Data Point :abbr:`URI (Uniform Resource Identifier)`, username, and password (or use only the pre-configured)
* ``metadata`` (map) = key-value specification of instance-wide pre-defined metadata, e.g., set ``license`` to ``http://purl.org/NET/rdflicense/cc-by3.0`` and that :abbr:`URI (Uniform Resource Identifier)` will be pre-set in all metadata forms in field ``license`` (but can be overwritten by the user)
* ``fdpConnections`` (list) = list of pre-configured FAIR Data Point connections that users can use, each is object with attributes:

   * ``name`` (string) = custom name identifying the connection
   * ``baseURI`` (string) = base :abbr:`URI (Uniform Resource Identifier)` of FAIR Data Point
   * ``email`` (string) = email address identifying user of FAIR Data Point
   * ``password`` (string) = password for authenticating the user of FAIR Data Point
   * ``preselected`` (boolean, optional) = flag if should be pre-selected in the form (in case that more connections have this set to true, only first one is applied)
   * ``metadata`` (map, optional) = similar to instance-wide but only for specific connection

.. _openrefine-configuration-storages:

Storages
--------

Storages configuration file holds details about storages that are possible to use for :ref:`openrefine-store-data` feature. In the file, list of storage object is expected where each of them has:

* ``name`` (string) = custom name identifying the storage
* ``type`` (string) = one of the allowed types (others are ignored): ``ftp``, ``virtuso``, ``tripleStoreHTTP``
* ``enabled`` (string) = flag if should be offered to the user
* ``username`` (string, optional) = username for authentication
* ``password`` (string, optional) = password for authentication
* ``host`` (string) = :abbr:`URI (Uniform Resource Identifier)` of the storage server
* ``directory`` (string) = directory or other location for storing the data

For :abbr:`FTP (File Transfer Protocol)` and Virtuoso, ``directory`` should containt absolute path where files should be stored. In case of triple stores, repository name is used to specify the target location.

.. _openrefine-compatibility:

Compatibility
=============

+---------------------+------------------------+------------------+
|  metadata extension |             OpenRefine |  FAIR Data Point |
+=====================+========================+==================+
|         ``vX.Y.Z``  |  ``3.3-beta``, ``3.2`` |       ``vX.Y.Z`` |
+---------------------+------------------------+------------------+

