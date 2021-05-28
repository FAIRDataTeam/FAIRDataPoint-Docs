.. _advanced-configuration:

**********************
Advanced Configuration
**********************

.. _triple-stores:

Triple Stores
=============

FDP uses InMemory triple store by default. In previous examples, there is Blazegraph used. However, you can choose from 3 additional options.

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

With this option, FDP will simply save the data to the file system. If you want to use the Native Store, make sure that you have these lines in your ``application.yml`` file:

.. code:: yaml
    
    # application.yml

    repository:
        type: 2
        native:
            dir: /tmp/fdp-store

where ``/tmp/fdp-store`` is a path to a location where you want to keep your data stored.

3. Allegro Graph
----------------

For running `Allegro Graph <https://franz.com/agraph/allegrograph/>`_, you need to first set up your Allegro Graph instance. For configuring the connection from FDP, add these lines to your ``application.yml`` file:

.. code:: yaml
    
    # application.yml

    repository:
        type: 3
        agraph: 
            url: http://agraph:10035/repositories/fdp
            username: user
            password: password


``URL``, ``username`` and ``password`` should be configured according to your actual Allegro Graph setup.

4. GraphDB
----------

For running `GraphDB <http://graphdb.ontotext.com>`_, you need to first set up your GraphDB instance and **create the repository**. For configuring the connection from FDP, add these lines to your ``application.yml`` file:

.. code:: yaml
    
    # application.yml

    repository:
        type: 4
        graphDb: 
            url: http://graphdb:7200
            repository: <repository-name>


``URL`` and ``repository`` should be configured according to your actual GraphDB setup.


5. Blazegraph
-------------

For running `Blazegraph <https://blazegraph.com/>`_, you need to first set up your Blazegraph instance. For configuring the connection from FDP, add these lines to your ``application.yml`` file:

.. code:: yaml
    
    # application.yml

    repository:
        type: 5
        blazegraph: 
            url: http://blazegraph:8080/blazegraph
            repository:


``URL`` and ``repository`` should be configured according to your actual Blazegraph setup. Repository should be set only if you don't use the default one.


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
        language: http://id.loc.gov/vocabulary/iso639-1/en
        license: http://rdflicense.appspot.com/rdflicense/cc-by-nc-nd3.0
        accessRightsDescription: This resource has no access restriction

    metadataMetrics:
        https://purl.org/fair-metrics/FM_F1A: https://www.ietf.org/rfc/rfc3986.txt
        https://purl.org/fair-metrics/FM_A1.1: https://www.wikidata.org/wiki/Q8777

FDP Index
=========

You can turn your FAIR Data Point instance into a FDP Index that can be contacted by other FDPs and harvests metadata from them.

Hosting FDP Index
-----------------

To enable FDP Index mode on your FDP server, just simply adjust your ``application.yml`` file:

.. code:: yaml
    
    # application.yml

    fdp-index:
        enabled:  true


Then for the FDP client, you need to use ``fairdata/fairdatapoint-index-client`` Docker image for browsing indexed FDPs and searching harvested metadata. In case you want to use your deployment both as FDP and FDP Index, you can deploy both FDP and FDP Index client applications. The configuration of both clients are identical.

.. code:: yaml

    # docker-compose.yml

    version: '3'
    services:

    # ...

    index_client:
      image: fairdata/fairdatapoint-index-client:1.10.0
      restart: always
      # ...


Connecting to FDP Index
-----------------------

By default, FDPs use https://home.fairdatapoint.org as their primary FDP Index that they ping every 7 days. You can adjust that in  your ``application.yml`` file if needed:

.. code:: yaml
    
    # application.yml

    ping:
        endpoint: https://my-index.example.com
        interval: 86400000 # milliseconds

You can also set multiple endpoints if needed:

.. code:: yaml
    
    # application.yml

    ping:
        endpoint: >
            https://my-index1.example.com
            https://my-index2.example.com
            https://home.fairdatapoint.org


FDP Index behind proxy
----------------------

FDP Index uses IP-based rate limits to avoid excessive communication caused by bots or misconfigured FDPs. If the FDP Index is deployed behind a proxy, it must correctly set header, e.g., ``X-Forwarded-For``. Furthermore, you need to add this to ``application.yml``:

.. code:: yaml
    
    # application.yml

    server:
        forward-headers-strategy: NATIVE


There may be differences based on you specific deployment. You should check in logs, which IP address is used when ping is received.


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

Sometimes, you might want to run FDP alongside other applications on the
same domain. Here is an example of running FDP on
``https://example.com/fairdatapoint``. If you run FDP in this configuration, you
have to set ``PUBLIC\_PATH`` ENV variable, in this example to
``/fairdatapoint``. Also, don't forget to set correct client URL in the application config.

.. code :: yaml

    # docker-compose.yml

    version: '3'
    services:
        fdp:
            image: fairdata/fairdatapoint:1.10.0
            volumes:
                - ./application.yml:/fdp/application.yml:ro
                # ... other volumes

        fdp-client:
            image: fairdata/fairdatapoint-client:1.10.0
            ports:
                - 80:80
            environment:
            	- FDP_HOST=fdp
                - PUBLIC_PATH=/fairdatapoint

.. code :: yaml

    # application.yml

    instance:
        clientUrl: https://example.com/fairdatapoint

.. code :: nginx

    # Snippet for nginx configuration

    server {
        # Configruation for the server, certificates, etc.

        # Define the location FDP runs on
        location ~ /fairdatapoint(/.*)?$ {
            rewrite /fairdatapoint(/.*) $1 break;
            rewrite /fairdatapoint / break;
            proxy_pass http://<client_host>;
        }
    }

.. Attention::

When running on nested route, don't forget to change paths to all
custom assets referenced in SCSS files.
