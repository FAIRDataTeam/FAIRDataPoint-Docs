.. _production-deployment:

*********************
Production Deployment
*********************

If you want to run the FAIR Data Point in production it is recommended to use HTTPS protocol with valid certificates.
You can easily configure FDP to run behind a reverse proxy which takes care of the certificates.

.. NOTE::
   The compose files in the `FAIRDataTeam/compose`_ repository are intended for development and testing.
   They do not take into account important production aspects such as security and data management.
   Nevertheless, the ``persistent/v1`` stack can be a useful starting point for your own production configuration.

In this example, we will configure FDP to run on ``https://fdp.example.com``.
We will see how to configure the reverse proxy in the same Docker Compose file.
However, it is not necessary, and the proxy can be configured elsewhere.

Certificates
============

First of all, we need to generate the certificates on the server where we want to run the FDP.
You can use `Let's Encrypt <https://letsencrypt.org>`__ and create the certificates with `certbot <https://certbot.eff.org>`__.
The certificates are generated in a standard location, e.g., ``/etc/letsencrypt/live/fdp.example.com`` for ``fdp.example.com`` domain.
We will mount the whole ``letsencrypt`` folder to the reverse proxy container later so that it can use the certificates.

Reverse proxy
=============

As a reverse proxy, we will use `nginx <https://nginx.org/index.html>`__.
We need to prepare some configuration, so create a new folder called ``nginx`` with the following structure and files:

::

  nginx/
  ├ nginx.conf
  ├ sites-available
  │  └ fdp.conf
  └ sites-enabled
     └ fdp.conf -> ../sites-available/fdp.conf

The file ``nginx.conf`` is the configuration of the whole nginx, and it includes all the files from ``sites-enabled`` which contains configuration for individual servers (we can use one nginx, for example, to handle multiple servers on different domains).
All available configurations for different servers are in the ``sites-available``, but only those linked to ``sites-enabled`` are used.

Let's see what should be the content of the configuration files.

.. code-block:: nginx

    # nginx/nginx.conf

    # Main nginx config
    user www-data www-data;
    worker_processes 5;

    events {
        worker_connections 4096;
    }

    http {
        # Docker DNS resolver
        # We can then use docker compose service names as hostnames in other configurations
        resolver 127.0.0.11 valid=10s;

        # Include all the configurations files from sites-enabled
        include /etc/nginx/sites-enabled/*.conf;
    }

Then, we need to configure the FDP server.

.. code-block:: nginx

    # nginx/sites-available/fdp.conf

    server {
        listen 443 ssl;

        # Generated certificates using certbot, we will mount these in compose.yml
        ssl_certificate /etc/letsencrypt/live/fdp.example.com/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/fdp.example.com/privkey.pem;

        server_name fdp.example.com;

        # We pass all the requests to the fdp-client container, we can use HTTP in the internal network
        # fdp-client is the name of the client service in our compose.yml, we can use it as host
        location / {
            proxy_set_header Host $host;
            proxy_set_header X-Forwarded-Proto $scheme;
            # Overwrite (do not append to) any X-Forwarded-For header sent by the remote client
            proxy_set_header X-Forwarded-For $remote_addr;
            proxy_pass_request_headers on;
            proxy_pass http://fdp-client;
        }
    }

    # We redirect all request from HTTP to HTTPS
    server {
        listen 80;
        server_name fdp.example.com;
        return 301 https://$host$request_uri;
    }

.. IMPORTANT::
   As of FDP v1.20.4, the FDP determines the remote IP address of a request from the ``X-Forwarded-For`` header, using Spring Boot's ``server.forward-headers-strategy: native`` (the default; do not change it).
   This IP address is used for rate limiting when the FDP runs as an :ref:`FDP Index <fdp-index>`.
   To prevent IP spoofing, the web-facing proxy must set ``X-Forwarded-For`` to a trusted value, as shown above, instead of appending to the header sent by the client (``$proxy_add_x_forwarded_for``).
   The old ``instance.behindProxy`` setting is no longer used and should be removed from your configuration.

Finally, we need to create a soft link from sites-enabled to sites-available for the FDP configuration.

::

    $ cd nginx/sites-enabled && ln -s ../sites-available/fdp.conf

Compose file
============

We have certificates generated and configuration for proxy ready.
Now we need to add the proxy to our ``compose.yml`` file so we can run the whole FDP behind the proxy.

.. code-block:: yaml
   :substitutions:

    # compose.yml

    services:
        proxy:
            image: nginx:stable
            restart: unless-stopped
            ports:
                - 80:80
                - 443:443
            volumes:
                # Mount the nginx folder with the configuration
                - ./nginx:/etc/nginx:ro
                # Mount the letsencrypt certificates
                - /etc/letsencrypt:/etc/letsencrypt:ro
            depends_on:
                - fdp-client

        fdp:
            image: fairdata/fairdatapoint:|fdp_ver|
            restart: unless-stopped
            environment:
                # Required: secret used to sign the JWT tokens (see below)
                FDP_JWT_SECRET_KEY: ${FDP_JWT_SECRET_KEY:?FDP_JWT_SECRET_KEY must be set}
            volumes:
                - ./application.yml:/fdp/application.yml:ro
            depends_on:
                - mongo
                - graphdb

        fdp-client:
            image: fairdata/fairdatapoint-client:|fdp_client_ver|
            restart: unless-stopped
            environment:
                FDP_HOST: fdp
            depends_on:
                - fdp

        mongo:
            image: mongo:|mongo_ver|
            restart: unless-stopped
            volumes:
                - mongo-data:/data/db

        graphdb:
            image: ontotext/graphdb:|graphdb_ver|
            restart: unless-stopped
            volumes:
                - graphdb-data:/opt/graphdb/home

    volumes:
        mongo-data:
        graphdb-data:

Note that only the proxy publishes ports on the host.
The ``fdp`` (port 80 in the default production profile), ``mongo``, and ``graphdb`` services are only reachable on the internal Docker network.

Don't forget to create the GraphDB repository (here called ``fdp``) before starting the ``fdp`` service.
You can do this in the GraphDB workbench, or automatically, as shown in the ``graphdb-init`` service in the :ref:`local deployment <quickstart>` section.

.. _jwt-secret:

JWT signing secret
==================

The FDP signs its API tokens with a secret.
As of FDP v1.22.1 there is no default value: the FDP refuses to start if the secret is missing or shorter than 32 bytes.
Generate a random value, for example:

.. code-block:: bash

    openssl rand -base64 48

Provide it via the ``FDP_JWT_SECRET_KEY`` environment variable, as shown above (for example from an ``.env`` file next to ``compose.yml`` that is not under version control), or via the ``security.jwt.token.secret-key`` property.
Keep the secret private and unique per deployment.
Changing it invalidates all tokens issued so far.

Application configuration
=========================

The last thing to do is to update our ``application.yml`` file.
We need to add ``clientUrl`` so that FDP knows the actual URL even if hidden behind the reverse proxy.
It's a good practice to set up a persistent URL for the metadata too, for example using a `w3id.org <https://w3id.org>`__ or `purl.org <https://purl.archive.org>`__ redirect.
Always set ``persistentUrl`` explicitly: its built-in default is ``http://localhost:8080``, which would end up in the IRIs of all your metadata records.
If you do not use a separate persistent URL, set it to the same value as ``clientUrl``.

.. code-block:: yaml

    # application.yml

    instance:
        clientUrl: https://fdp.example.com
        persistentUrl: https://w3id.org/example/fdp
        title: Example FAIR Data Point
        subtitle: Metadata of the Example project

    spring:
        mongodb:
            uri: mongodb://mongo:27017/fdp

    # repository settings (can be changed to different repository)
    repository:
        type: 4
        graphDb:
            url: http://graphdb:7200
            repository: fdp
            # if your graphdb has the security feature enabled, configure the credentials below
            username: ...
            password: ...

.. WARNING::
   As of FDP v1.20.3 (Spring Boot 4), the MongoDB connection property is ``spring.mongodb.uri``.
   The old ``spring.data.mongodb.uri`` property (environment variable ``SPRING_DATA_MONGODB_URI``) is no longer used, so update your configuration before upgrading.

At this point, we should be able to run all the containers using ``docker compose up -d`` and after everything starts, we can access the FAIR Data Point at https://fdp.example.com.
Of course, the domain you want to access the FDP on must be configured to the server where it runs.

.. DANGER::

    Don't forget to change the default user accounts as soon as your FAIR Data Point becomes publicly available.


.. DANGER::

    Do not expose the mongo port unless you secured the database with username and password.

.. WARNING::

    In order to improve findability of itself and its content, the FAIR Data Point has a built-in feature that registers its URL with the FDP Index at https://home.fairdatapoint.org and pings it once a week.
    This feature facilitates the indexing of the metadata of each registered and active FAIR Data Point.
    If you do not want your FAIR Data Point to be included in this registry, add these lines to your application configuration:

    .. code-block:: yaml

        # application.yml

        ping:
            enabled: false

    Alternatively, set the environment variable ``PING_ENABLED=false``, or disable the ping in the client under :guilabel:`Settings`.
    See :ref:`connecting-to-index` for more options.

.. _upgrading:

Upgrading
=========

Before upgrading an existing deployment, read the `release notes <https://github.com/FAIRDataTeam/FAIRDataPoint/releases>`_ for every version between your current version and the new one.
Depending on your current version, upgrading to v1.22 involves the following configuration changes:

- ``spring.data.mongodb.uri`` was renamed to ``spring.mongodb.uri`` (v1.20.3).
- ``instance.behindProxy`` was removed, the reverse proxy must set ``X-Forwarded-For`` (v1.20.4).
- A :ref:`JWT signing secret <jwt-secret>` is required (v1.22.1). This also applies when upgrading from v1.22.0, which still had a built-in default secret.

Database migrations are applied automatically when the new ``fdp`` version starts.
Back up the MongoDB database and the triple store before upgrading.

.. _FAIRDataTeam/compose: https://github.com/FAIRDataTeam/compose
