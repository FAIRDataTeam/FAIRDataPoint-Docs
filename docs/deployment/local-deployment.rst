****************
Local Deployment
****************

FAIR Data Point is distributed in Docker images. For a simple local deployment, you need to run ``fairdatapoint``, ``fairdatapoint-client`` and ``mongo`` images. See the :ref:`Components <components>` section to read more about what each image is for.

Here is an example of the simplest `Docker Compose <https://docs.docker.com/compose/>`__ configuration to run FDP.

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


Then you can run it using ``docker compose up -d``. It might take a while to start. You can run ``docker compose logs -f`` to follow the output log. Once you see a message, that the application started, the FAIR Data Point should be working, and you can open http://localhost.


There are two default user accounts. See the :ref:`Users and Roles <users-and-roles>` section to read more about users and roles. The default accounts are

+-----------------------------+-------+----------+
| User name                   | Role  | Password |
+=============================+=======+==========+
| albert.einstein@example.com | admin | password |
+-----------------------------+-------+----------+
| nikola.tesla@example.com    | user  | password |
+-----------------------------+-------+----------+

.. DANGER::

    Using the default accounts is alright if you run FDP on your machine, but you should change them if you want to run FDP publicly.


Running locally on a different port
===================================

If you want to run the FAIR Data Point locally on a different port than the default ``80``, additional configuration is necessary. First, we need to create a new file ``application.yml`` and set the client URL to the actual URL we want to use.

.. code-block:: yaml

    # application.yml

    instance:
        clientUrl: http://localhost:8080

Then, we need to mount the application config into the FDP container and update the port which the FDP client runs on.

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
                - 8080:80
            environment:
                - FDP_HOST=fdp

        mongo:
            image: mongo:4.0.12


Persistence
===========

We don't have any data persistence with the previous configuration. Once we remove the containers, all the data will be lost. To keep it, we need to configure MongoDB volume and persistent triple store.


MongoDB volume
--------------

We use MongoDB to store information about user accounts and access permissions. We can configure a `volume <https://docs.docker.com/storage/volumes/>`__ so that the data keep on our disk even if we delete MongoDB container.

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


Persistent Repository
-----------------------

FAIR Data Point uses repositories to store the metadata. By default, it uses the in-memory store, which means that the data is lost after the FDP is stopped.

In this example, we will configure GraphDB as a triple store. See :ref:`Triple Stores <triple-stores>` for other repository options.

If we don't have it already, we need to create a new file ``application.yml``. We will use this file to configure the repository and mount it as a read-only volume to the ``fdp`` container. This file can be used for other configuration, see :ref:`Advanced Configuration <advanced-configuration>` for more details.


.. code-block:: yaml

    # application.yml

    # ... other configuration

    repository:
        type: 4
        graphDb:
            url: http://graphdb:7200
            repository: fdp

We now need to update our ``compose.yml`` file, we add a new volume for the ``fdp`` and add ``graphdb`` service. We can also expose port ``7200`` for GraphDB so we can access its user interface.

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

GraphDB needs to have a repository set up before the FDP can interact with it. This can be done manually through the user interface, following these steps:

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
                # https://graphdb.ontotext.com/documentation/10.7/database-health-checks.html
                test: curl --fail-with-body http://localhost:7200/repositories/fdp/health || exit 1
                interval: 5s

The ``repo.json`` file contains the configuration for the newly created GraphDB repository. The following is a bare minimum example.

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
