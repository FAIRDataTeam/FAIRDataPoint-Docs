****************
Local Deployment
****************

FAIR Data Point is distributed in Docker images. For a simple local deployment, you need to run ``fairdatapoint``, ``fairdatapoint-client`` and ``mongo`` images. See the :ref:`Components <components>` section to read more about what each image is for.

Here is an example of the simplest `Docker Compose <https://docs.docker.com/compose/>`__ configuration to run FDP.

.. code :: yaml

    # docker-compose.yml

    version: '3'
    services:

        fdp:
            image: fairdata/fairdatapoint:1.5.0

        fdp-client:
            image: fairdata/fairdatapoint-client:1.5.0
            ports:
                - 80:80
            environment:
                - FDP_HOST=fdp

        mongo:
            image: mongo:4.0.12


Then you can run it using ``docker-compose up -d``. It might take a while to start. You can run ``docker-compose logs -f`` to follow the output log. Once you see a message, that the application started, the FAIR Data Point should be working, and you can open http://localhost.


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

.. code :: yaml

    # application.yml

    instance:
        clientUrl: http://localhost:8080

Then, we need to mount the application config into the FDP container and update the port which the FDP client runs on.

.. code :: yaml

    # docker-compose.yml

    version: '3'
    services:

        fdp:
            image: fairdata/fairdatapoint:1.5.0
            volumes:
                - ./application.yml:/fdp/application.yml:ro

        fdp-client:
            image: fairdata/fairdatapoint-client:1.5.0
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

Here is the updated docker-compose file:

.. code :: yaml

    # docker-compose.yml

    version: '3'
    services:

        fdp:
            image: fairdata/fairdatapoint:1.5.0

        fdp-client:
            image: fairdata/fairdatapoint-client:1.5.0
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

In this example, we will configure Blazegraph as a triple store. See :ref:`Triple Stores <triple-stores>` for other repository options.

If we don't have it already, we need to create a new file ``application.yml``. We will use this file to configure the repository and mount it as a read-only volume to the ``fdp`` container. This file can be used for other configuration, see :ref:`Advanced Configuration <advanced-configuration>` for more details.


.. code :: yaml

    # application.yml

    # ... other configuration

    repository:
        type: 5
        blazegraph:
            url: http://blazegraph:8080/blazegraph

We now need to update our ``docker-compose.yml`` file, we add a new volume for the ``fdp`` and add ``blazegraph`` service. We can also expose port ``8080`` for Blazegraph so we can access its user interface.

.. code :: yaml

    # docker-compose.yml

    version: '3'
    services:

        fdp:
            image: fairdata/fairdatapoint:1.5.0
            volumes:
                - ./application.yml:/fdp/application.yml:ro

        fdp-client:
            image: fairdata/fairdatapoint-client:1.5.0
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

        blazegraph:
            image: metaphacts/blazegraph-basic:2.2.0-20160908.003514-6
            ports:
                - 8080:8080
            volumes:
                - ./blazegraph:/blazegraph-data
