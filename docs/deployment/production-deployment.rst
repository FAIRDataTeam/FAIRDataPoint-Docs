.. _production-deployment:

*********************
Production Deployment
*********************

Disclaimer
==========

Running a FAIR Data Point in production is a bit more involved than running one offline on your development machine.
The configuration details of a production deployments depend on many factors, such as available resources and security requirements.

Whether you're setting up your own bare metal server or using a cloud provider with lots of managed services, many of the same topics will need attention.
Here's just a few that come to mind, in no particular order:

- network security
- secrets storage
- identity and access management (IAM)
- data management (security, privacy, replication, backups)
- service availability (container orchestration, monitoring)
- performance
- audit logging
- deployment automation (infrastructure as code, CI/CD)
- and so on and so forth...

Obviously this list is far from exhaustive.

Due to this complexity we cannot provide a generic solution for a production deployment.
However, we *can* provide some pointers and suggestions to help you get started.
Assuming basic infrastructure hardening is already in place (see e.g. `OWASP cheat sheets`_), we'll look at a few things:

- HTTPS (encrypted communication based on TLS)
- database security
- database backups

These topics are covered by extending the :ref:`local-deployment` examples with some additional configuration.

HTTPS setup
===========

One of the first requirements for a production deployment is to set up Transport Layer Security (TLS) to provide encrypted communication, better known as HTTPS (HTTP over TLS).
This is very important, because, among many other things, it prevents unauthorized parties from intercepting and reading your login credentials.

Https connections can be handled, for example, by configuring a load balancer or a reverse proxy.

As a minimal example, we'll describe how to use Docker compose to configure an ``nginx`` container as reverse proxy that terminates https, on the same host that runs the FDP containers.
In this case, communication between the ``nginx`` container and the upstream web server (either ``fdp`` or ``fdp-client``) still uses plain http, but in our case that occurs on the private Docker network.
It is also possible to configure the ``fdp``'s `embedded web server`_ and the ``fdp-client``'s embedded nginx instance to handle https connections, but that is outside the scope of this document.

TLS certificates
----------------

In order to set up HTTPS, a valid TLS certificate is required (a.k.a. SSL certificate).
For this example, we assume a TLS certificate is already available, *on the Docker host*, for our domain ``fdp.example.com``.

Certificate files can be obtained from various sources.
Our example assumes that the `certbot`_ tool was used to obtain a certificate from `Let's Encrypt`_.
The certificate file and corresponding key file can then be found in `certbot's default location`_ ``/etc/letsencrypt/live/fdp.example.com`` on the host.

Nginx compose service
---------------------

A minimal compose service definition for nginx is described below.
Bind mounts are used to make the nginx configuration files and certificates from the Docker host available in the ``nginx`` container.
The ``FDP_HOST`` environment variable is used in the ``server.conf`` config file described in the next section.

..  literalinclude:: nginx/compose.yml
    :name: nginx compose config
    :caption: minimal nginx service
    :language: yaml
    :lines: 2-

This is just a minimal example, so you may want to  specify an image version, adjust the paths, where necessary, and/or add some addional config.
There is also an ``nginxinc/nginx-unprivileged`` image, but that will require a bit more configuration.

..  note::

    Here we assume that the ``nginx`` container shares a Docker network with the ``fdp-client`` container.
    Only the ``nginx`` container ports (``80`` and ``443``) should be exposed to the public internet.
    Make sure to remove any lines exposing ports from other components, such as the following for ``fdp-client``:

    ..  literalinclude:: compose/fdp/components/v1/fdp-client.yml
        :name: remove exposed ports
        :language: yaml
        :lines: 2,5-6

Nginx server configuration
--------------------------

Here's a minimal example of an nginx server configuration that does the following:

- redirect ``http`` to ``https``
- pass ``https`` requests for ``fdp.example.com`` on to the upstream ``fdp-client`` container (over ``http``)
- catch any other requests

..  literalinclude:: nginx/server.conf.template
    :name: nginx server config
    :caption: server.conf template
    :language: none

..  note::

    The `official nginx image`_ has the ability to render configuration file templates with environment variables.
    Any ``*.template`` files from the ``/etc/nginx/templates`` directory are rendered into ``/etc/nginx/conf.d``.
    The image's default ``/etc/nginx/nginx.conf`` then automatically includes ``*.conf`` files from ``/etc/nginx/conf.d`` in the ``http`` block.

    ..  code-block::
        :caption: default nginx.conf http block includes files from conf.d

        ...
        http {
            ...
            include /etc/nginx/conf.d/*.conf;
        }


Database security
=================

The FDP uses two types of database:

- MongoDB, for application data
- A triple store, such as GraphDB, for the actual metadata

Both need to be secured.

- `database security cheat sheet`_
- `mongodb security cecklist`_
- `graphdb security`_

Secrets
=======

The best way to handle application secrets strongly depends on your use-case.
In our minimal example we take one of the simplest (and least secure) approaches, which is using environment variables.

List of secrets:

- jwt token secret key
- default fdp user accounts
- mongodb credentials
- triple store credentials

Backups
=======

(...)

.. _OWASP cheat sheets: https://cheatsheetseries.owasp.org
.. .. _: https://cheatsheetseries.owasp.org/cheatsheets/Web_Service_Security_Cheat_Sheet.html
.. _database security cheat sheet: https://cheatsheetseries.owasp.org/cheatsheets/Database_Security_Cheat_Sheet.html
.. .. _: https://cheatsheetseries.owasp.org/cheatsheets/Docker_Security_Cheat_Sheet.html
.. .. _: https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html
.. .. _: https://ubuntu.com/blog/what-is-system-hardening-definition-and-best-practices
.. _mongodb security cecklist: https://www.mongodb.com/docs/manual/administration/security-checklist/
.. _graphdb security: https://graphdb.ontotext.com/documentation/11.1/enabling-security.html
.. _embedded web server: https://docs.spring.io/spring-boot/how-to/webserver.html#howto.webserver.configure-ssl
.. _certbot: https://certbot.eff.org/instructions
.. _Let's Encrypt: https://letsencrypt.org
.. _certbot's default location: https://eff-certbot.readthedocs.io/en/stable/using.html#where-are-my-certificates
.. _official nginx image: https://hub.docker.com/_/nginx

TODO: update the text below



The last thing to do is to update our ``application.yml`` file.
We need to add ``clientUrl`` so that FDP knows the actual URL even if hidden behind the reverse proxy.
It's a good practice to set up a persistent URL for the metadata too.
We recommend using ``https://purl.org``.
If you don't specify ``persistentUrl``, the ``clientUrl`` will be used instead.
And we also need to set a random JWT token for security.

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



At this point, we should be able to run all the containers using ``docker compose up -d`` and after everything starts, we can access the FAIR Data Point at https://fdp.example.com.
Of course, the domain you want to access the FDP on must be configured to the server where it runs.

.. DANGER::

    Don't forget to change the default user accounts as soon as your FAIR Data Point becomes publicly available.



.. warning::

    In order to improve findability of itself and its content, the FAIR Data Point has a built-in feature that registers its URL into our server and pings it once a week.
    This feature facilitates the indexing of the metadata of each registered and active FAIR Data Point.
    If you do not want your FAIR Data Point to be included in this registry, add these lines to your application configuration:

    ..  code-block:: yaml

        # application.yml

        ping:
            enabled: false
