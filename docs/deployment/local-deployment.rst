****************
Local Deployment
****************

This section describes how to set up a local deployment of the FAIR Data Point on your development system.
This local deployment is intended for testing, allowing you to play around with the FDP and try out different configurations.


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
   These compose files are used by our development team for testing FDP deployments.
   As such, they represent a good starting point for reproducing any issues that you may encounter.
   See the `FAIRDataTeam/compose readme`_ for more information.

2. Change into the directory for the ``ephemeral/v1`` stack:

   .. code-block:: bash

      cd compose/fdp/ephemeral/v1

   This directory contains a compose configuration that defines a minimal stack consisting of the ``mongo``, ``fdp``, and ``fdp-client`` containers.
   Here  ``ephemeral`` implies *"non-persistent data"* and ``v1`` refers to the latest major version of the ``fdp`` and ``fdp-client`` components.
   The ``fdp`` is configured to use an in-memory triple store, and ``mongo`` data is stored only in the container.
   There are no persistent `volumes`_ or `bind mounts`_, so all data is lost when the stack is torn down.

   If you need persistent data storage, you can try the ``persistent/v1`` configuration instead.
   This configuration includes a ``graphdb`` triple store and uses `volumes`_ for persistence of all data.

3. Set up the stack:

   .. code-block:: bash

      docker compose up -d

   This downloads the required Docker images, if necessary, and starts the containers in the proper order.

4. Once all containers are up, and healthy, you can start playing around with the FDP.

   For example:

   - Use ``curl http://localhost`` to see the machine readable FDP metadata
   - Visit http://localhost in your favorite web browser to try the FDP client interface
   - Visit http://localhost/swagger-ui/index.html in the browser to inspect the API documentation

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


Minimal stack
=============

The absolute minimal FDP stack consists of just the ``fairdatapoint`` and ``mongo`` containers.
However, we also include the ``fairdatapoint-client`` to get a convenient browser interface.
See the :ref:`components` section to read more about what each image is for.

The following compose file represents a minimal stack for local testing:

.. literalinclude:: compose.yml
   :name: minimal compose file
   :caption: compose.yml
   :language: yaml

.. warning:: This is an ephemeral stack, so there is no `Persistence`_.
   All data from the mongo container and in-memory triple store are lost when the stack is torn down.

You can set this up using ``docker compose up -d``, and tear it back down, when you're done, using ``docker compose down``.
If necessary, container logs can be viewed using ``docker compose logs -f``.

The stack might take a while to start because of the health checks that are used to enforce the proper startup order.
Once started, you can visit http://localhost in your web browser.

API docs
--------

If you're planning to add metadata in bulk, you can write a script to use the FDP API.
Check out the API docs at http://localhost/swagger-ui/index.html.

Logging in
----------

Although unauthenticated users can view FDP content, you'll need to log in to add content.

The default demo accounts are:

+-----------------------------+-------+----------+
| User name                   | Role  | Password |
+=============================+=======+==========+
| albert.einstein@example.com | admin | password |
+-----------------------------+-------+----------+
| nikola.tesla@example.com    | user  | password |
+-----------------------------+-------+----------+

See the :ref:`Users and Roles <users-and-roles>` section to read more about users and roles.

.. danger::
   Using the default accounts is alright for testing on your local machine, but you should definitely change them before exposing your FDP to the public internet.


Persistence
===========

We don't have any data persistence with the previous configuration.
Once we remove the containers, all the data will be lost.
To keep it, we need to configure MongoDB volume and persistent triple store.


MongoDB volume
--------------

We use MongoDB to store information about user accounts and access permissions.
We can configure a `volume <https://docs.docker.com/storage/volumes/>`__ so that the data keep on our disk even if we delete MongoDB container.

We can also expose port ``27017`` so we can access MongoDB from our local computer using a client application like `Robo 3T <https://robomongo.org>`__.

Here is the updated docker compose file:

.. code-block:: yaml
   :substitutions:

    # compose.yml

    services:

        fdp:
            image: fairdata/fairdatapoint:|compose_ver|

        fdp-client:
            image: fairdata/fairdatapoint-client:|compose_ver|
            ports:
                - 80:80
            environment:
                - FDP_HOST=fdp

        mongo:
            image: mongo:4.0.12
            ports:
                - 27017:27017
            volumes:
                - ./mongo/data:/data/db


.. _persistent-repository:

Persistent Repository
-----------------------

FAIR Data Point uses repositories to store the metadata.
By default, it uses the in-memory store, which means that the data is lost after the FDP is stopped.

In this example, we will configure GraphDB as a triple store.
See :ref:`Triple Stores <triple-stores>` for other repository options.

If we don't have it already, we need to create a new file ``application.yml``.
We will use this file to configure the repository and mount it as a read-only volume to the ``fdp`` container.
This file can be used for other configuration, see :ref:`Advanced Configuration <advanced-configuration>` for more details.


.. code-block:: yaml

    # application.yml

    # ... other configuration

    repository:
        type: 4
        graphDb:
            url: http://graphdb:7200
            repository: fdp

We now need to update our ``compose.yml`` file, we add a new volume for the ``fdp`` and add ``graphdb`` service.
We can also expose port ``7200`` for GraphDB so we can access its user interface.

.. code-block:: yaml
   :substitutions:

    # compose.yml

    services:

        fdp:
            image: fairdata/fairdatapoint:|compose_ver|
            volumes:
                - ./application.yml:/fdp/application.yml:ro

        fdp-client:
            image: fairdata/fairdatapoint-client:|compose_ver|
            ports:
                - 80:80
            environment:
                - FDP_HOST=fdp

        mongo:
            image: mongo:4.0.12
            ports:
                - 27017:27017
            volumes:
                - ./mongo/data:/data/db

        graphdb:
            image: ontotext/graphdb:10.7.6
            ports:
                - 7200:7200
            volumes:
                - ./graphdb:/opt/graphdb/home

GraphDB needs to have a repository set up before the FDP can interact with it.
This can be done manually through the user interface, following these steps:

- Start only the GraphDB container: ``docker compose up -d graphdb``
- Navigate to your `local GraphDB instance <http://localhost:7200>`__
- Open the ``Setup`` menu on the left, and navigate to `Repositories <http://localhost:7200/repository>`__
- Click the `Create new repository <http://localhost:7200/repository/create>`__ button
- Select ``GraphDB Repository``
- Enter ``fdp`` as the ``Repository ID`` value
- You can leave all other values to their defaults
- Click the ``Create`` button on the bottom of the form

Alternatively, these steps can be automated with the following addition to the ``graphdb`` service in our ``compose.yml`` file.

.. code-block:: yaml

        fdp:
            image: fairdata/fairdatapoint:|compose_ver|
            volumes:
                - ./application.yml:/fdp/application.yml:ro
            depends_on:
                graphdb:
                    condition: service_healthy

        # ...

        graphdb:
            image: ontotext/graphdb:10.7.6
            ports:
                - 7200:7200
            volumes:
                - ./graphdb:/opt/graphdb/home
                - ./repo.json:/tmp/repo.json:ro
            entrypoint:
                - bash
                - -c
                - |
                  # enable bash job control
                  set -m

                  # start graphdb and move it to the background
                  /opt/graphdb/dist/bin/graphdb &
            
                  # wait for 10 sec
                  sleep 10
            
                  # create the repository
                  curl -X POST http://localhost:7200/rest/repositories -H "Content-Type: application/json" -d "@repo.json"

                  # move graphdb job to foreground
                  fg
            healthcheck:
                # https://graphdb.ontotext.com/documentation/11.1/database-health-checks.html
                test: curl --fail-with-body http://localhost:7200/repositories/fdp/health || exit 1
                interval: 5s

The ``repo.json`` file contains the configuration for the newly created GraphDB repository.
The following is a bare minimum example.

.. code-block:: json

    {
        "id": "fdp",
        "type": "graphdb",
        "params": {
            "title": {
                "label": "Repository description",
                "name": "",
                "value": ""
            },
            "defaultNS": {
                "label": "Default namespaces for imports(';' delimited)",
                "name": "defaultNS",
                "value": ""
            },
            "imports": {
                "label": "Imported RDF files(';' delimited)",
                "name": "imports",
                "value": ""
            }
        }
    }

.. _compose specification: https://compose-spec.io/
.. _Docker Compose: https://docs.docker.com/compose/
.. _Docker installation instructions: https://docs.docker.com/engine/install/
.. _FAIRDataTeam/compose: https://github.com/FAIRDataTeam/compose
.. _FAIRDataTeam/compose readme: https://github.com/FAIRDataTeam/compose/blob/master/readme.md
.. _volumes: https://docs.docker.com/engine/storage/volumes/
.. _bind mounts: https://docs.docker.com/engine/storage/bind-mounts/
.. _remove the containers: https://docs.docker.com/reference/cli/docker/container/rm/
.. _images: https://docs.docker.com/reference/cli/docker/image/rm/
