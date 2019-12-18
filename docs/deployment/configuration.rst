*************
Configuration
*************

Application Configuration
=========================

You can override default settings in ``application-production.yml``
file. You can take inspiration in the `default
configuration <https://github.com/FAIRDataTeam/FAIRDataPoint/blob/develop/src/main/resources/application.yml>`__
and `default production
configuration <https://github.com/FAIRDataTeam/FAIRDataPoint/blob/develop/src/main/resources/application-production.yml>`__.
Create the ``application-production.yml`` in the ``/fdp`` folder and
attach it into a docker container using ``volumes`` directive.

::

    fdp:
        image: fairtools/fairdatapoint
        restart: always
        volumes:
          - ./application-production.yml:/fdp/application-production.yml
        ports:
          - 80:8080


Possible configuration
----------------------

Here you can list possible configuration. The configuration marked as
required should be addressed if you are intending to use the FDP
professionally.

+--------------------------------+---------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+ 
| Customization                  | Level         | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
+================================+===============+==========================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================+ 
| **Application (instance) URL** | **Required**  | Override property `instance.url` (e.g., `http://fdp-staging.fair-dtls.surf-hosted.nl`)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
+--------------------------------+---------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| Server Port                    | Optional      | Override property `server.port` (e.g., `80`)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
+--------------------------------+---------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **JWT Token secret**           | **Required**  | Override property `security.jwt.token.secret-key`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
+--------------------------------+---------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| Metadata Properties            | Optional      | Override property `metadataProperties` with nested properties: `rootSpecs`, `catalogSpecs`, `datasetSpecs`, `distributionSpecs`, `publisherURI`, `publisherName`, `language`, `license`, `accessRightsDescription`                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
+--------------------------------+---------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| Metadata Metrics               | Optional      | Override property `metadataMetrics`. Nested properties are captured as Map with metric uri as a key (e.g., `https://purl.org/fair-metrics/FM_F1A`) and with its value (e.g., `https://www.ietf.org/rfc/rfc3986.txt`)                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
+--------------------------------+---------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| PID                            | Optional      | Override property `pid`. You can choose between 2 types of persistent identifiers (`default PIDSystem (1)`, `purl.org PID System (2)`). Select one of those and write the number of the type into `type` property. To configure the concrete PID System, create a property named by the type of the PID System and include the required information for that repository. For `default`, you don't need to configure anything. For `purl`, you need to configure `baseUrl`.                                                                                                                                                                                               |
+--------------------------------+---------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **Mongo DB**                   | **Required**  | Override property `spring.data.mongodb.uri` with connection string (e.g. `mongodb://mongo:27017/fdp`)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
+--------------------------------+---------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| Triple Store                   | **Required**  | Override property `repository`. You can choose between 5 types of triple stores (`inMemoryStore (1)`, `NativeStore (2)`, `AllegroGraph (3)`, `graphDB (4)`, `blazegraph (5)`). Select one of those and write the number of the type into `type` property. To configure the concrete repository, create a property named by the type of repository and include the required information for that repository. For `agraph`, you need to configure `url`, `username` and `password`. For `graphDb`, you need to configure `url` and `repository`. For `blazegraph`, you need to configure `url` and `repository`. And for `native`, you need to configure `/tmp/fdp-store`. |
+--------------------------------+---------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

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
