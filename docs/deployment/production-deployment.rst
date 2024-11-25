.. _production-deployment:

*********************
Production Deployment
*********************

If you want to run the FAIR Data Point in production it is recommended to use HTTPS protocol with valid certificates. You can easily configure FDP to run behind a reverse proxy which takes care of the certificates.

In this example, we will configure FDP to run on ``https://fdp.example.com``. We will see how to configure the reverse proxy in the same Docker Compose file. However, it is not necessary, and the proxy can be configured elsewhere.

First of all, we need to generate the certificates on the server where we want to run the FDP. You can use `Let's Encrypt <https://letsencrypt.org>`__ and create the certificates with `certbot <https://certbot.eff.org>`__. The certificates are generated in a standard location, e.g., ``/etc/letsencrypt/live/fdp.example.com`` for ``fdp.example.com`` domain. We will mount the whole ``letsencrypt`` folder to the reverse proxy container later so that it can use the certificates.

As a reverse proxy, we will use `nginx <http://nginx.org/en/>`__. We need to prepare some configuration, so create a new folder called ``nginx`` with the following structure and files:

::

  nginx/
  ├ nginx.conf
  ├ sites-available
  │  └ fdp.conf
  └ sites-enabled
     └ fdp.conf -> ../sites-available/fdp.conf

The file ``nginx.conf`` is the configuration of the whole nginx, and it includes all the files from ``sites-enabled`` which contains configuration for individual servers (we can use one nginx, for example, to handle multiple servers on different domains). All available configurations for different servers are in the ``sites-available``, but only those linked to ``sites-enabled`` are used.

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
        # We can then use docker container names as hostnames in other configurations
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

        # We pass all the request to the fdp-client container, we can use HTTP in the internal network
        # fdp-client_1 is the name of the client container in our configuration, we can use it as host
        location / {
            proxy_set_header Host $host;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_pass_request_headers on;
            proxy_pass http://fdp-client_1;
        }
    }

    # We redirect all request from HTTP to HTTPS
    server {
        listen 80;
        server_name fdp.example.com;
        return 301 https://$host$request_uri;
    }

Finally, we need to create a soft link from sites-enabled to sites-available for the FDP configuration.

::

    $ cd nginx/sites-enabled && ln -s ../sites-available/fdp.conf

We have certificates generated and configuration for proxy ready. Now we need to add the proxy to our ``compose.yml`` file so we can run the whole FDP behind the proxy.

.. code-block:: yaml
   :substitutions:
    
    # compose.yml

    services:
        proxy:
            image: nginx:1.17.3
            ports:
                - 80:80
                - 443:443
            volumes:
                # Mount the nginx folder with the configuration
                - ./nginx:/etc/nginx:ro
                # Mount the letsencrypt certificates
                - /etc/letsencrypt:/etc/letsencrypt:ro

        fdp:
            image: fairdata/fairdatapoint:|compose_ver|
            volumes:
                - ./application.yml:/fdp/application.yml:ro

        fdp-client:
            image: fairdata/fairdatapoint-client:|compose_ver|
            environment:
                - FDP_HOST=fdp

        mongo:
            image: mongo:4.0.12
            ports:
              - "127.0.0.1:27017:27017"
            volumes:
                - ./mongo/data:/data/db

        graphdb:
            image: ontotext/graphdb:10.7.6
            volumes:
                - ./graphdb:/opt/graphdb/home

Don't forget to create the GraphDB repository as described in the :ref:`Persistent Repository <persistent-repository>` section.

The last thing to do is to update our ``application.yml`` file. We need to add ``clientUrl`` so that FDP knows the actual URL even if hidden behind the reverse proxy. It's a good practice to set up a persistent URL for the metadata too. We recommend using ``https://purl.org``. If you don't specify ``persistentUrl``, the ``clientUrl`` will be used instead. And we also need to set a random JWT token for security.

.. code-block:: yaml

    # application.yml

    instance:
        clientUrl: https://fdp.example.com
        persistentUrl: https://purl.org/fairdatapoint/example

    security:
        jwt:
            token:
                secret-key: <random 128 characters string>

    # repository settings (can be changed to different repository)
    repository:
        type: 4
        graphDb:
            url: http://graphdb:7200
            repository: fdp
            # if your graphdb has the security feature enabled, configure the credentials below
            username: ...
            password: ...



At this point, we should be able to run all the containers using ``docker compose up -d`` and after everything starts, we can access the FAIR Data Point at https://fdp.example.com. Of course, the domain you want to access the FDP on must be configured to the server where it runs.

.. DANGER::

    Don't forget to change the default user accounts as soon as your FAIR Data Point becomes publicly available.


.. DANGER::

    Do not expose mongo port unless you secured the database with username and password.

.. WARNING::

    In order to improve findability of itself and its content, the FAIR Data Point has a built-in feature that registers its URL into our server and pings it once a week. This feature facilitates the indexing of the metadata of each registered and active FAIR Data Point. If you do not want your FAIR Data Point to be included in this registry, add these lines to your application configuration:

    .. code-block:: yaml

        # application.yml

        ping:
            enabled: false
