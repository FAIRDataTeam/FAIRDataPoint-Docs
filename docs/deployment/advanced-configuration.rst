.. _advanced-configuration:

**********************
Advanced Configuration
**********************

.. _configuration-methods:

Configuration methods
=====================

The ``fdp`` is a `Spring Boot`_ application.
Its default configuration is defined in the built-in `application.yml`_ file, and it can be changed in two ways:

1. Mount your own ``application.yml`` file into the container at ``/fdp/application.yml``.
   Values in this file override the built-in defaults.
   The examples in this section use this format.

2. Set environment variables on the ``fdp`` container.
   Spring Boot maps environment variables to configuration properties using `relaxed binding`_: upper case, with dots replaced by underscores and dashes removed.
   For example, ``instance.clientUrl`` becomes ``INSTANCE_CLIENTURL`` and ``repository.graphDb.url`` becomes ``REPOSITORY_GRAPHDB_URL``.
   For many options, the built-in ``application.yml`` also defines a shorter ``FDP_*`` variable, listed in the tables below.

Both methods can be combined.
Relaxed-binding variables, such as ``INSTANCE_TITLE``, take precedence over values in any ``application.yml`` file.
The ``FDP_*`` variables only fill in placeholders in the built-in ``application.yml``, so they have no effect for a property that is also set in your own mounted ``application.yml``.

.. _instance-configuration:

Instance
========

.. list-table::
   :header-rows: 1
   :widths: 25 25 20 30

   * - Property
     - Environment variable
     - Default
     - Description
   * - ``instance.clientUrl``
     - ``INSTANCE_CLIENTURL``
     - ``http://localhost``
     - Public URL of the FDP, as seen by users (e.g. the reverse proxy URL)
   * - ``instance.persistentUrl``
     - ``FDP_PERSISTENT_URL``
     - ``http://localhost:8080``
     - Base URL used in the IRIs of the metadata records
   * - ``instance.title``
     - ``FDP_TITLE``
     - ``FAIR Data Point``
     - Application title shown in the client
   * - ``instance.subtitle``
     - ``FDP_SUBTITLE``
     - ``Metadata for machines``
     - Application subtitle shown in the client
   * - ``instance.index``
     - ``FDP_INDEX``
     - ``false``
     - Run as :ref:`FDP Index <fdp-index>`
   * - ``instance.indexAutoPermit``
     - ``FDP_INDEX_AUTOPERMIT``
     - ``true``
     - Default for automatically accepting new index entries
   * - ``instance.sparqlProxyEnabled``
     - ``INSTANCE_SPARQLPROXYENABLED``
     - ``false``
     - Enable the experimental :ref:`SPARQL endpoint <sparql-endpoint>`

.. WARNING::
   Always set both ``clientUrl`` and ``persistentUrl`` explicitly.
   If you have no separate persistent URL, use the same value for both.
   The ``persistentUrl`` determines the IRIs of all metadata records, and its built-in default (``http://localhost:8080``) is not suitable for any real deployment.
   Set it before you create any metadata, because records created earlier keep their original IRIs.

.. NOTE::
   The built-in ``application.yml`` also defines an ``FDP_CLIENT_URL`` variable, but the default ``production`` profile overrides ``instance.clientUrl``, so that variable has no effect.
   Use ``INSTANCE_CLIENTURL`` or an ``application.yml`` file instead.

The title and subtitle can also be changed by an admin in the client, under :guilabel:`Settings`.

.. _jwt-configuration:

Security
========

.. list-table::
   :header-rows: 1
   :widths: 30 25 15 30

   * - Property
     - Environment variable
     - Default
     - Description
   * - ``security.jwt.token.secret-key``
     - ``FDP_JWT_SECRET_KEY``
     - (none)
     - **Required.** Secret (at least 32 bytes) used to sign API tokens
   * - ``security.jwt.token.expiration``
     - ``SECURITY_JWT_TOKEN_EXPIRATION``
     - ``14``
     - Token validity, in days

See :ref:`jwt-secret` for details.

.. _triple-stores:

Triple Stores
=============

The FDP stores its metadata in a triple store.
By default, it uses an in-memory triple store, which means that all metadata are lost when the ``fdp`` container stops.
For anything other than testing, configure one of the persistent options below.

**List of possible triple stores:**

1. In-Memory Store (default)
2. Native Store
3. AllegroGraph Repository
4. GraphDB Repository
5. Blazegraph Repository

The type is selected using ``repository.type`` (environment variable ``FDP_TRIPLE_STORE_TYPE``).
The connection details can also be set using the ``FDP_TRIPLE_STORE_URL``, ``FDP_TRIPLE_STORE_REPOSITORY``, ``FDP_TRIPLE_STORE_USERNAME``, ``FDP_TRIPLE_STORE_PASSWORD``, and ``FDP_TRIPLE_STORE_DIR`` environment variables, which apply to the selected type.

The configured triple store is shown, read-only, in the client under :guilabel:`Settings`.

1. In-Memory Store
------------------

There is no need to configure additional properties to run FDP with In-Memory Store because it's the default option.
If you want to explicitly type in configuration provided in ``application.yml``, add following lines there:

.. code-block:: yaml

    # application.yml

    repository:
        type: 1

2. Native Store
---------------

With this option, FDP will simply save the data to the file system.
If you want to use the Native Store, make sure that you have these lines in your ``application.yml`` file:

.. code-block:: yaml

    # application.yml

    repository:
        type: 2
        native:
            dir: /fdp/store

where ``/fdp/store`` is a path to a location where you want to keep your data stored.
When running in Docker, mount a volume at this location, otherwise the data is lost when the container is removed.

3. AllegroGraph
---------------

For running `AllegroGraph <https://allegrograph.com/products/allegrograph/>`_, you need to first set up your AllegroGraph instance.
For configuring the connection from FDP, add these lines to your ``application.yml`` file:

.. code-block:: yaml

    # application.yml

    repository:
        type: 3
        agraph:
            url: http://agraph:10035/repositories/fdp
            username: user
            password: password


``url``, ``username`` and ``password`` should be configured according to your actual AllegroGraph setup.

4. GraphDB
----------

For running `GraphDB <https://graphdb.ontotext.com>`_, you need to first set up your GraphDB instance and **create the repository**.
For configuring the connection from FDP, add these lines to your ``application.yml`` file:

.. code-block:: yaml

    # application.yml

    repository:
        type: 4
        graphDb:
            url: http://graphdb:7200
            repository: <repository-name>
            # only if GraphDB security is enabled
            username: <username>
            password: <password>


``url`` and ``repository`` should be configured according to your actual GraphDB setup.
The ``persistent/v1`` stack in the `FAIRDataTeam/compose`_ repository shows a working GraphDB configuration, including the automatic creation of the repository.

5. Blazegraph
-------------

For running `Blazegraph <https://blazegraph.com/>`_, you need to first set up your Blazegraph instance.
For configuring the connection from FDP, add these lines to your ``application.yml`` file:

.. code-block:: yaml

    # application.yml

    repository:
        type: 5
        blazegraph:
            url: http://blazegraph:8080/blazegraph
            repository:


``url`` and ``repository`` should be configured according to your actual Blazegraph setup.
``repository`` is the Blazegraph namespace.
If it is not configured, the built-in default ``test`` is used; set it to an empty value to use the Blazegraph default namespace ``kb``.

.. NOTE::
   Blazegraph is no longer actively maintained upstream.
   For new deployments, GraphDB is the triple store that is used and tested by the FAIR Data Team.


MongoDB
=======

We store users, permissions, settings, metadata schemas, etc. in the `MongoDB database <https://www.mongodb.com/>`_.
The default connection string is ``mongodb://mongo:27017/fdp``.
The host, port, and database name can be changed using the ``FDP_MONGO_HOST``, ``FDP_MONGO_PORT``, and ``FDP_MONGO_DB`` environment variables.
For other changes, such as adding credentials, set the full connection string in your ``application.yml`` file:

.. code-block:: yaml

    # application.yml

    spring:
        mongodb:
            uri: mongodb://<username>:<password>@mongo:27017/fdp?authSource=admin

The ``uri`` should be adjusted by your actual MongoDB setup.
The equivalent environment variable is ``SPRING_MONGODB_URI``.

.. WARNING::
   Up to FDP v1.20.2 this property was called ``spring.data.mongodb.uri`` (``SPRING_DATA_MONGODB_URI``).
   That name is ignored by newer versions, which then fall back to the default connection string.


Default attached metadata
=========================

There are several default values that are attached to each created metadata.
If you want to modify it, add the lines below to your ``application.yml`` file.
The default values are listed below, too:

.. code-block:: yaml

    # application.yml

    metadataProperties:
        language: http://id.loc.gov/vocabulary/iso639-1/en
        license: http://purl.org/NET/rdflicense/cc-zero1.0
        accessRightsDescription: This resource has no access restriction

The corresponding environment variables are ``FDP_METADATA_LANGUAGE``, ``FDP_METADATA_LICENSE``, and ``FDP_METADATA_ACCESS_RIGHTS``.



.. _settings:

Settings in the client
======================

Some configuration is stored in the database instead of in ``application.yml``.
An admin can change it in the client under :guilabel:`Settings`, or via the ``/settings`` API endpoint:

- App title and subtitle (overriding ``instance.title`` and ``instance.subtitle``)
- FDP Index connection: enable or disable the ping, and add FDP Index endpoints (in addition to those from ``application.yml``)
- Forms autocomplete: SPARQL endpoints and queries used to suggest IRIs in metadata forms
- Search filters shown on the search page

All settings can be reset to the factory defaults under :guilabel:`Reset to defaults`.


.. _sparql-endpoint:

SPARQL endpoint (experimental)
==============================

The FDP can expose a read-only `SPARQL 1.1 <https://www.w3.org/TR/sparql11-protocol/>`_ query endpoint at ``/search/sparql``, which forwards queries to the SPARQL endpoint of the external triple store.
To enable it, set ``instance.sparqlProxyEnabled: true`` (environment variable ``INSTANCE_SPARQLPROXYENABLED=true``).

- Only authenticated users can use the endpoint.
- Only queries are allowed; SPARQL updates are rejected.
- It requires an external triple store (GraphDB, AllegroGraph, or Blazegraph); with the in-memory or native store, the endpoint responds with "not found".

This endpoint is not part of the stable API and may change in future releases.


Monitoring
==========

The ``fdp`` includes `Spring Boot Actuator`_ endpoints.
The ``/actuator/health`` and ``/actuator/info`` endpoints are enabled by default, and can be used for health checks.

An experimental ``/actuator/metrics`` endpoint, with a request counter, can be enabled by setting ``MANAGEMENT_ENDPOINTS_WEB_EXPOSURE_INCLUDE=health,info,metrics``.
The metrics endpoint requires authentication.


.. _fdp-index:

FDP Index
=========

You can turn your FAIR Data Point instance into a FDP Index that can be contacted by other FDPs and harvests metadata from them.

Hosting FDP Index
-----------------

To enable FDP Index mode on your FDP server, just simply adjust your ``application.yml`` file:

.. code-block:: yaml

    # application.yml

    instance:
        index: true

or set the environment variable ``FDP_INDEX=true``.

As of ``fdp-client`` 1.18.0, the regular ``fairdata/fairdatapoint-client`` image detects the index mode automatically, so no separate client image is needed.
The client then shows the list of registered FDPs, their metadata, and the index administration pages.

The ``ephemeral/v1/index`` stack in the `FAIRDataTeam/compose`_ repository shows a complete example, which is described in the :ref:`quickstart` section.

Index entries and permits
-------------------------

When an FDP pings the index, the index creates an entry for it and retrieves (harvests) its metadata.
Each entry has a *permit*: ``ACCEPTED``, ``PENDING``, or ``REJECTED``.
Only accepted entries are listed publicly.

If :guilabel:`Auto Permit` is enabled, new entries are accepted automatically.
Otherwise new entries are ``PENDING`` until an admin accepts or rejects them in the client.
Metadata of an entry is only harvested once the entry is accepted.

The ``instance.indexAutoPermit`` property only provides the initial value.
Once the index settings have been saved in the client, the stored value is used.

Index settings
--------------

An admin can configure the index in the client under :guilabel:`Index Settings`, or via the ``/index/settings`` API endpoint:

============================== ============= ==========================================================================
Setting                        Default       Description
============================== ============= ==========================================================================
Auto Permit                    ``true``      Accept new entries automatically
Retrieval, Rate Limit Wait     10 minutes    Minimum time between two metadata retrievals for the same FDP
Retrieval, Timeout             1 minute      Timeout for a metadata retrieval
Ping, Valid Duration           7 days        An entry without a ping during this period is considered inactive
Ping, Rate Limit Duration      6 hours       Time window for the ping rate limit (per IP address)
Ping, Rate Limit Hits          10            Maximum number of pings per time window
Ping, Deny List                ``localhost`` Regular expressions for client URLs whose pings are rejected
============================== ============= ==========================================================================

The default deny list contains ``^(http|https)://localhost(:[0-9]+){0,1}.*$``, so pings from FDPs with a ``localhost`` client URL are rejected.
Remove this entry if you want to test an index locally.
Note that an FDP pings about 10 seconds after it starts and then once per ping interval, so restart the pinging FDP after changing the deny list.

An admin can also trigger a new metadata retrieval for one or all entries, in the client or via the ``/index/admin/trigger`` and ``/index/admin/trigger-all`` endpoints.

.. _connecting-to-index:

Connecting to FDP Index
-----------------------

By default, FDPs use https://home.fairdatapoint.org as their primary FDP Index that they ping every 7 days.
You can adjust that in your ``application.yml`` file if needed:

.. code-block:: yaml

    # application.yml

    ping:
        endpoints:
            - https://my-index.example.com
        interval: P1D # ISO-8601 duration, here one day

Setting ``ping.endpoints`` replaces the default endpoint, so include https://home.fairdatapoint.org in the list if you still want to be indexed there:

.. code-block:: yaml

    # application.yml

    ping:
        endpoints:
            - https://my-index1.example.com
            - https://my-index2.example.com
            - https://home.fairdatapoint.org

The equivalent environment variables are ``PING_ENABLED``, ``PING_ENDPOINTS`` (comma-separated), and ``PING_INTERVAL``.

An admin can add more FDP Index endpoints in the client, under :guilabel:`Settings` → :guilabel:`FDP Index connection`.
The FDP pings the endpoints from ``application.yml`` and those from the settings.
The ping is only sent if it is enabled in both places.

.. NOTE::
   Older versions of this documentation used a single ``ping.endpoint`` property.
   The current property is ``ping.endpoints``, which takes a list.

FDP Index behind proxy
----------------------

FDP Index uses IP-based rate limits to avoid excessive communication caused by bots or misconfigured FDPs.
The FDP obtains the remote IP address from the ``X-Forwarded-For`` header, so the reverse proxy must set this header to a trusted value.
See the reverse proxy configuration in the :ref:`production-deployment` section.

You can check in the logs which IP address is used when a ping is received.


Customizations
==============

You can customize the look and feel of FDP Client using `SCSS <https://sass-lang.com>`__.
There are three files you can mount to ``/src/scss/custom``.
If there are any changes in these files, the styles will be regenerated when FDP Client starts.

Customization files
-------------------

_variables.scss
~~~~~~~~~~~~~~~

A lot of values related to styles are defined as variables.
The easiest way to customize the FDP Client is to define new values for these variables.
To do so, you create a file called ``_variables.scss`` where you define the values that you want to change.

Here is an example of changing the primary color.

.. code-block:: scss

    // _variables.scss

    $color-primary: #087d63;

Have a look in `src/scss/\_variables.scss <https://github.com/FAIRDataTeam/FAIRDataPoint-client/blob/master/src/scss/_variables.scss>`__
to see all the variables you can change.

_extra.scss
~~~~~~~~~~~

This file is loaded before all other styles.
You can use it, for example, to define new styles or import fonts.

_overrides.scss
~~~~~~~~~~~~~~~

This file is loaded after all other styles.
You can use it to override existing styles.

Example of setting a custom logo
--------------------------------

To change the logo, you need to do three steps:

1. Create ``_variables.scss`` with correct logo file name and dimensions
2. Mount the new logo to the assets folder
3. Mount ``_variables.scss`` to SCSS custom folder

.. code-block:: scss

    // _variables.scss

    $header-logo-url: '/assets/my-logo.png';  // new logo file
    $header-logo-width: 80px;  // width of the new logo
    $header-logo-height: 40px;  // height of the new logo

.. code-block:: yaml

    # compose.yml

    services:
        fdp:
            # ... FDP configuration

        fdp-client:
            # ... FDP Client configuration
            volumes:
              # Mount new logo file to assets in the container
              - ./my-logo.png:/usr/share/nginx/html/assets/my-logo.png:ro

              # Mount _variables.scss so that styles are regenerated
              - ./_variables.scss:/src/scss/custom/_variables.scss:ro


Running FDP on a nested route
==============================

Sometimes, you might want to run FDP alongside other applications on the same domain.
Here is an example of running FDP on ``https://example.com/fairdatapoint``.
If you run FDP in this configuration, you have to set ``PUBLIC_PATH`` ENV variable, in this example to ``/fairdatapoint``.
Also, don't forget to set correct client URL in the application config.

.. code-block:: yaml
   :substitutions:

    # compose.yml

    services:
        fdp:
            image: fairdata/fairdatapoint:|fdp_ver|
            volumes:
                - ./application.yml:/fdp/application.yml:ro
                # ... other volumes

        fdp-client:
            image: fairdata/fairdatapoint-client:|fdp_client_ver|
            ports:
                - 80:80
            environment:
                - FDP_HOST=fdp
                - PUBLIC_PATH=/fairdatapoint

.. code-block:: yaml

    # application.yml

    instance:
        clientUrl: https://example.com/fairdatapoint

.. code-block:: nginx

    # Snippet for nginx configuration

    server {
        # Configuration for the server, certificates, etc.

        # Define the location FDP runs on
        location ~ /fairdatapoint(/.*)?$ {
            rewrite /fairdatapoint(/.*) $1 break;
            rewrite /fairdatapoint / break;
            proxy_pass http://<client_host>;
        }
    }


.. HINT::

   When running on nested route, don't forget to change paths to all
   custom assets referenced in SCSS files.


.. _application.yml: https://github.com/FAIRDataTeam/FAIRDataPoint/blob/v1.22.2/src/main/resources/application.yml
.. _FAIRDataTeam/compose: https://github.com/FAIRDataTeam/compose
.. _relaxed binding: https://docs.spring.io/spring-boot/reference/features/external-config.html#features.external-config.typesafe-configuration-properties.relaxed-binding.environment-variables
.. _Spring Boot: https://spring.io/projects/spring-boot
.. _Spring Boot Actuator: https://docs.spring.io/spring-boot/reference/actuator/index.html
