.. _advanced-configuration:

**********************
Advanced Configuration
**********************

.. _triple-stores:

Triple Stores
=============

FDP uses InMemory triple store by default. In the Deployment example, there is a native store used. However, you can choose from 3 additional options.

**List of possible triple stores:**

1. In-Memory Store
2. Native Store
3. Allegro Graph Repository
4. GraphDB Repository
5. Blazegraph Repository

1. In-Memory Store
------------------

There is no need to configure additional properties to run FDP with In-Memory Store because it's the default option. If you want to explicitly type in configuration provided in ``application.yml``, add following lines there:

.. code:: yaml
    
    # application.yml

    repository:
        type: 1

2. Native Store
---------------

If you want to use the Native Store, make sure that you have these lines in your ``application.yml`` file:

.. code:: yaml
    
    # application.yml

    repository:
        type: 2
        native:
            dir: /tmp/fdp-store

where ``/tmp/fdp-store`` is a path to a location where you want to keep your data stored.

3. Allegro Graph
----------------

For running `Allegro Graph <https://franz.com/agraph/allegrograph/>`_, you need to first set up your Allegro Graph instance. Make sure that the FDP Docker container can ping the Allegro Graph Docker container. For configuring the connection from FDP, add these lines to your ``application.yml`` file:

.. code:: yaml
    
    # application.yml

    repository:
        type: 3
        agraph: 
            url: http://agraph:10035/repositories/fdp
            username: user
            password: password


``URL``, ``username`` and ``password`` should be adjusted by your actual Allegro Graph setup.

4. GraphDB
----------

For running `GraphDB <http://graphdb.ontotext.com>`_, you need to first set up your GraphDB instance. Make sure that the FDP Docker container can ping the GraphDB Docker container. For configuring the connection from FDP, add these lines to your ``application.yml`` file:

.. code:: yaml
    
    # application.yml

    repository:
        type: 4
        graphDb: 
            url: http://graphdb:7200
            repository: test


``URL`` and ``repository`` should be adjusted by your actual GraphDB setup.


5. Blazegraph
-------------

For running `Blazegraph <https://blazegraph.com/>`_, you need to first set up your Blazegraph instance. Make sure that the FDP Docker container can ping the Blazegraph Docker container. For configuring the connection from FDP, add these lines to your ``application.yml`` file:

.. code:: yaml
    
    # application.yml

    repository:
        type: 5
        blazegraph: 
            url: http://blazegraph:8079/blazegraph
            repository: test


``URL`` and ``repository`` should be adjusted by your actual Blazegraph setup.


Mongo DB
========
We store users, permissions, etc. in the `MongoDB database <https://www.mongodb.com/>`_. The default connection string is ``mongodb://mongo:27017/fdp``. If you want to modify it, add these lines to your ``application.yml`` file:

.. code:: yaml
    
    # application.yml

    spring:
        data:
            mongodb:
                uri: mongodb://mongo:27017/fdp

The ``uri`` should be adjusted by your actual MongoDB setup.

Default attached metadata
=========================
There are several default values that are attached to each created metadata. If you want to modify it, add the lines below to your ``application.yml`` file. The default values are listed below, too:

.. code:: yaml
    
    # application.yml

    metadataProperties:
        rootSpecs: https://www.purl.org/fairtools/fdp/schema/0.1/fdpMetadata
        catalogSpecs: https://www.purl.org/fairtools/fdp/schema/0.1/catalogMetadata
        datasetSpecs: https://www.purl.org/fairtools/fdp/schema/0.1/datasetMetadata
        publisherURI: http://localhost
        publisherName: localhost
        language: http://id.loc.gov/vocabulary/iso639-1/en
        license: http://rdflicense.appspot.com/rdflicense/cc-by-nc-nd3.0
        accessRightsDescription: This resource has no access restriction

    metadataMetrics:
        https://purl.org/fair-metrics/FM_F1A: https://www.ietf.org/rfc/rfc3986.txt
        https://purl.org/fair-metrics/FM_A1.1: https://www.wikidata.org/wiki/Q8777

PID System
==========
There are 2 basic PID systems - default PID system and ``purl.org`` PID system.

1. Default PID System
---------------------
You don't have to configure anything special to use the Default PID System. However, if you want to have an explicit usage in configuration, add following lines to your ``application.yml`` file:

.. code:: yaml
    
    # application.yml

    pidSystem:
        type: 1

2. `Purl.org` PID System
------------------------
If you want to use `Purl.org` PID System, you have to configure it in ``application.yml`` file - add the following lines below and adjust the ``baseUrl``.

.. code:: yaml
    
    # application.yml

    pidSystem:
        type: 2
        purl:
            baseUrl: http://purl.org/YOUR-PURL-DOMAIN/fdp

Customizations
==============

You can customize the look and feel of FDP Client using
`SCSS <https://sass-lang.com>`__. There are three files you can mount to
``/src/scss/custom``. If there are any changes in these files, the
styles will be regenerated when FDP Client starts.

Customization files
-------------------

_variables.scss
~~~~~~~~~~~~~~~

A lot of values related to styles are defined as variables. The easiest
way to customize the FDP Client is to define new values for these
variables. To do so, you create a file called ``_variables.scss`` where
you define the values that you want to change.

Here is an example of changing the primary color.

.. code:: scss

    // _variables.scss

    $color-primary: #087d63;

Have a look in `src/scss/\_variables.scss <https://github.com/FAIRDataTeam/FAIRDataPoint-client/blob/develop/src/scss/_variables.scss>`__
to see all the variables you can change.

_extra.scss
~~~~~~~~~~~

This file is loaded before all other styles. You can use it, for
example, to define new styles or import fonts.

_overrides.scss
~~~~~~~~~~~~~~~

This file is loaded after all other styles. You can use it to override
existing styles.

Example of setting a custom logo
--------------------------------

To change the logo, you need to do three steps:

1. Create ``_variables.scss`` with correct logo file name and dimensions
2. Mount the new logo to the assets folder
3. Mount ``_variables.scss`` to SCSS custom folder

.. code:: scss

    // _variables.scss

    $header-logo-url: '/assets/my-logo.png';  // new logo file
    $header-logo-width: 80px;  // width of the new logo 
    $header-logo-height: 40px;  // height of the new logo

.. code:: yaml

    # docker-compose.yml

    version: '3'
    services:
        server:
            # ... FDP configuration

        client:
            # ... FDP Client configuration
            volumes:
              # Mount new logo file to assets in the container
              - ./my-logo.png:/usr/share/nginx/html/assets/my-logo.png:ro
              
              # Mount _variables.scss so that styles are regenerated
              - ./_variables.scss:/src/scss/custom/_variables.scss:ro


Running FDP on a nested route
==============================

Sometimes, you might want to run FDP alongside other applications on the
same domain. Here is an example of running FDP on
``example.com/fairdatapoint``. If you run FDP in this configuration, you
**have to set PUBLIC\_PATH ENV variable**, in this example to
``/fairdatapoint``.

.. code:: yaml

    # docker-compose.yml

    version: '3'
    services:
        server:
            image: fairdata/fairdatapoint
            # ... FDP configuration

        client:
            image: fairdata/fairdatapoint-client
            ports:
                - 80:80
            environment:
            	- FDP_HOST=server
                - PUBLIC_PATH=/fairdatapoint

.. code:: nginx

    # Snippet for nginx configuration

    server {
        # Configruation for the server, certificates, etc.

        # Define the location FDP runs on
        location ~ /fairdatapoint(/.*)?$ {
            rewrite /fairdatapoint(/.*) $1 break;
            rewrite /fairdatapoint / break;
            proxy_pass http://<client_host>;
            proxy_set_header Host $host;
            proxy_pass_request_headers on;
        }
    }

.. Attention::

When running on nested route, don't forget to change paths to all
custom assets referenced in SCSS files.
