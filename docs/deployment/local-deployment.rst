****************
Local Deployment
****************

Here you'll learn how to quickly set up a local deployment of the FAIR Data Point on your development system.
This will allow you to play around with the FDP and try out different configurations, without needing to worry about too many details.

.. warning::

   This local deployment is intended for *offline* testing only.
   If you are going to expose your FDP to the public internet, please have a look at the :ref:`production-deployment` section.


Prerequisites
=============

To set up an FDP stack, using containers described in the :ref:`components` section, we use `Docker Compose`_ or an equivalent tool.
If you don't have Docker Compose yet, follow the `Docker installation instructions`_ first.
Alternatively, you could install another tool that supports the `compose specification`_.


.. _quickstart:

Quickstart
==========

Set up
------

Here's how to get started quickly with a minimal FDP stack that has no data persistence (ephemeral):

1. Clone the `FAIRDataTeam/compose`_ repository from GitHub:

   .. code-block:: bash

      git clone https://github.com/FAIRDataTeam/compose.git

   The `FAIRDataTeam/compose`_ repository contains the latest compose files for a variety of FDP configurations and versions, such as ``persistent`` and ``ephemeral`` (i.e. non-persistent) configurations.
   These compose files are used by our development team for testing FDP deployments locally.
   As such, they represent a good starting point for reproducing any issues that you may encounter.
   See the `FAIRDataTeam/compose readme`_ for more information.

2. Change into the directory for the ``ephemeral/v1`` stack:

   .. code-block:: bash

      cd compose/fdp/ephemeral/v1

   This directory contains a compose configuration that defines a minimal stack consisting of the ``mongo``, ``fdp``, ``fdp-client``, and ``fdp-ui`` containers.
   Here ``ephemeral`` implies *"non-persistent data"* and ``v1`` refers to the current major version of the ``fdp`` and ``fdp-client`` components.
   (The ``v2`` directories in the compose repository belong to a discontinued development line and are deprecated.)

   The ``fdp`` is configured to use an in-memory triple store, and ``mongo`` data is stored only in the container.
   There are no persistent `volumes`_ or `bind mounts`_, so all data is lost when the stack is torn down.

   If you *do* need persistent data storage, you can try the ``persistent/v1`` configuration instead.
   That configuration includes a ``graphdb`` triple store and uses `volumes`_ for persistence of all data.
   It also enables the experimental :ref:`SPARQL endpoint <sparql-endpoint>`.

   If you want to try out an :ref:`FDP Index <fdp-index>`, use the ``ephemeral/v1/index`` configuration, which runs an FDP Index next to a regular FDP that pings it.

3. Set up the stack:

   .. code-block:: bash

      docker compose up -d

   This downloads the required Docker images, if necessary, and starts the containers in the proper order.

   The image versions are defined in the compose files, and can be overridden using environment variables, such as ``FDP_VERSION`` and ``FDP_CLIENT_VERSION``.
   See the `FAIRDataTeam/compose readme`_ for details.

.. note::

   As of FDP v1.22.1, the ``fdp`` refuses to start without a :ref:`JWT signing secret <jwt-secret>`.
   The compose files set a dummy secret for local testing, via the ``SECURITY_JWT_TOKEN_SECRETKEY`` environment variable.
   Never use that dummy value for an FDP that is reachable by others.

Play around
-----------

Once all containers are up, and healthy, you can start playing around with the FDP.

For example:

- Use ``curl http://localhost`` to see the machine readable FDP metadata
- Visit http://localhost in your favorite web browser to try the FDP client interface (also see the :ref:`authentication` and :ref:`usage` sections)
- Visit http://localhost/swagger-ui.html in the browser to inspect the interactive API documentation
- Use ``curl http://localhost:8080/actuator/health`` to check the health of the ``fdp`` back-end, which is also exposed directly on port ``8080``
- Visit http://localhost:81 to preview the new FAIRDataPoint-UI (read-only, under development)

Tear down
---------

Once you're done playing with your FDP, here's how to remove every trace:

1. Make sure you are (still) in the directory corresponding to the running stack, in our case ``ephemeral/v1``.

2. Tear down the stack:

   .. code-block:: bash

      docker compose down

   If you're running a ``persistent`` configuration, this command does *not* remove the persistent volumes.
   If you *do* want to remove the persistent volumes, it is most convenient to use ``docker compose down --volumes``.
   Alternatively you could use ``docker volume rm <volume-name>``.

3. If you really want to remove *every* trace of the FDP, you'll need to `remove the containers`_ and corresponding `images`_ as well.
   If not, you can leave them in place for the next time.

Deep dive
=========

A more detailed description of the compose configurations from the `FAIRDataTeam/compose`_ repo can be found below.
First we describe the basic `stack components`_, then we show you how to use them in `composing a stack`_.

Stack components
----------------

The compose repo ``fdp/components`` dir contains basic configurations for the components described in the :ref:`components` section.
These components are listed below:

.. literalinclude:: compose/fdp/components/v1/fdp/compose.yml
   :name: fdp compose
   :caption: minimal fdp v1 config
   :language: yaml

.. literalinclude:: compose/fdp/components/v1/fdp-client/compose.yml
   :name: fdp-client compose
   :caption: minimal fdp-client v1 config
   :language: yaml

.. literalinclude:: compose/fdp/components/db/mongo/compose.yml
   :name: mongo compose
   :caption: minimal mongo config
   :language: yaml

.. literalinclude:: compose/fdp/components/db/graphdb/compose.yml
   :name: graphdb compose
   :caption: minimal graphdb config
   :language: yaml

The ``graphdb-init`` service, defined above, requires a template file in order to create an initial GraphDB repository.
Here's a minimal example based on the `GraphDB API docs`_:

.. literalinclude:: compose/fdp/components/db/graphdb/repo-template.json
   :name: minimal graphdb repo template
   :caption: graphdb repo template
   :language: json

Alternatively, it is possible to remove the template file and the ``graphdb-init`` service, and create the required repository manually, using the GraphDB web interface.
See `GraphDB instructions`_ for more info.
Note that you would need to do this before starting the ``fdp`` container.

Composing a stack
-----------------

The components described above are the basic building blocks for our compose stack.
We use the `compose-file include`_ element to build our actual compose file.

Ephemeral
~~~~~~~~~

For example, the following compose file defines the minimal ephemeral FDP stack used in the `quickstart`_:

.. literalinclude:: compose/fdp/ephemeral/v1/compose.yml
   :name: ephemeral/v1
   :caption: ephemeral/v1/compose.yml
   :language: yaml

By itself, this file is not very informative.
In order to inspect the complete configuration resulting from the above, you can use the `config command`_:

.. code-block:: bash

   docker compose config

..

    It merges the Compose files set by -f flags, resolves variables in the Compose file, and expands short-notation into the canonical format.

Persistent
~~~~~~~~~~

A stack with persistent data requires a bit more configuration.
In this case we add ``graphdb`` as an external triple store:

.. literalinclude:: compose/fdp/persistent/v1/compose.yml
   :name: persistent/v1
   :caption: persistent/v1/compose.yml
   :language: yaml

In addition, we need to extend and/or override the configuration of the basic components.
This is achieved using a `compose.override.yml` file, as explained in the `compose-file merge docs`_:

.. literalinclude:: compose/fdp/persistent/v1/compose.override.yml
   :name: persistent/v1 override
   :caption: persistent/v1/compose.override.yml
   :language: yaml

Index
~~~~~

The ``ephemeral/v1/index`` stack runs an :ref:`FDP Index <fdp-index>` (``fdp-index``, with its own ``fdp-client`` on http://localhost:82) next to a regular FDP (``fdp``, with its client on http://localhost) that is configured to ping the index:

.. literalinclude:: compose/fdp/ephemeral/v1/index/compose.yml
   :name: ephemeral/v1/index
   :caption: ephemeral/v1/index/compose.yml
   :language: yaml

.. literalinclude:: compose/fdp/ephemeral/v1/index/compose.override.yml
   :name: ephemeral/v1/index override
   :caption: ephemeral/v1/index/compose.override.yml
   :language: yaml

Note that, by default, an FDP Index rejects pings from ``localhost`` URLs (see :ref:`fdp-index`).
For local testing, log in to the index client as admin, remove that entry from the deny list under :guilabel:`Index Settings`, and restart the ``fdp`` service so it pings again.
Also note that the ``fdp`` in this stack announces itself with the client URL ``http://localhost:8080``.
Inside the ``fdp-index`` container that URL points to the index itself, not to the ``fdp``, so the index does not harvest the metadata of the ``fdp`` in this stack without further changes.


FDP configuration options
-------------------------

The FAIRDataPoint backend is a Java application based on the `Spring framework`_.
Spring applications can be configured in several ways, as described in the Spring Boot `externalized configuration`_ docs.
The FAIRDataPoint app itself uses `application.yml` files for the default configuration.
In the `FAIRDataTeam/compose`_ repo, we use environment variables to override and/or extend this default configuration for the ``fdp`` service.
For example, the default ``server.port`` Spring configuration value is overridden using the ``SERVER_PORT`` environment variable, and ``instance.clientUrl`` is overridden using ``INSTANCE_CLIENTURL``.
This is convenient because we don't need to include multiple files.
In addition, the default `application.yml`_ defines a number of shorter ``FDP_*`` environment variables, such as ``FDP_TITLE`` and ``FDP_JWT_SECRET_KEY``.
The available options are described in the :ref:`advanced-configuration` section.

Nevertheless, it is also possible to override ``fdp`` configuration using an `application.yml` file.
To do this we need to mount our custom `application.yml` file as follows:

.. code-block:: yaml
   :substitutions:

      fdp:
          ...
          volumes:
            - ./application.yml:/fdp/application.yml:ro
            ...


.. _bind mounts: https://docs.docker.com/engine/storage/bind-mounts/
.. _compose-file include: https://docs.docker.com/reference/compose-file/include/
.. _compose-file merge docs: https://docs.docker.com/compose/how-tos/multiple-compose-files/merge/
.. _compose specification: https://compose-spec.io/
.. _config command: https://docs.docker.com/reference/cli/docker/compose/config/
.. _Docker Compose: https://docs.docker.com/compose/
.. _Docker installation instructions: https://docs.docker.com/engine/install/
.. _externalized configuration: https://docs.spring.io/spring-boot/reference/features/external-config.html#features.external-config.typesafe-configuration-properties.relaxed-binding
.. _FAIRDataTeam/compose: https://github.com/FAIRDataTeam/compose
.. _FAIRDataTeam/compose readme: https://github.com/FAIRDataTeam/compose/blob/master/readme.md
.. _GraphDB API create: https://graphdb.ontotext.com/documentation/10.8/manage-repos-with-restapi.html#create-a-repository
.. _GraphDB API docs: https://graphdb.ontotext.com/documentation/10.8/manage-repos-with-restapi.html#create-a-repository
.. _GraphDB instructions: https://graphdb.ontotext.com/documentation/10.8/creating-a-repository.html
.. _images: https://docs.docker.com/reference/cli/docker/image/rm/
.. _remove the containers: https://docs.docker.com/reference/cli/docker/container/rm/
.. _Spring framework: https://docs.spring.io/spring-framework/reference/index.html
.. _volumes: https://docs.docker.com/engine/storage/volumes/
.. _application.yml: https://github.com/FAIRDataTeam/FAIRDataPoint/blob/v1.22.2/src/main/resources/application.yml
