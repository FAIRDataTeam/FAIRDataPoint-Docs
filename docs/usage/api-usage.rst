.. _api-usage:

*********
API Usage
*********

The **FAIR Data Point** exposes API endpoints that allow consumers to interact with the metadata.
Some of the endpoints are available for all users, while others require an API token for authorization.


Obtaining an API token
======================

In order to obtain an API token, you invoke the ``/tokens`` endpoint with your user credentials.

.. code-block:: bash

    curl -X POST -H "Accept: application/json" \
        -H "Content-Type: application/json" \
        -d '{ "email": "user@example.com", "password": "secret" }' \
        https://fdp.example.com/tokens

A successful call will return a ``JSON`` object with a token.

.. code-block:: json

    { "token": "efIobn394nvJJFJ30..." }

Tokens are valid for 14 days by default.
For scripts and other long-running clients, you can use an :ref:`API key <users-and-roles>` instead, which is created in the client under :guilabel:`API Keys` or via ``POST /api-keys``, and is used in exactly the same way.

Issuing a request with the authorization token
----------------------------------------------

Subsequent requests should use this token in the `Authorization` header.
The authorization type is a `Bearer <https://datatracker.ietf.org/doc/html/rfc6750>`_ token.

.. code-block:: bash

    curl -H "Authorization: Bearer efIobn394nvJJFJ30..." \
        -H "Accept: application/json" https://fdp.example.com/users/current


Interacting with metadata
=========================

The metadata layers as defined by the :ref:`resource-definitions` are exposed through their respective endpoints.
The general approach is that each layer, defined by its ``prefix``, supports a number of read and write HTTP methods.
The root of the FDP (the FAIR Data Point record itself) is served at ``/``.

========== =========================================== ==========================
Method     URL pattern                                 Functionality
========== =========================================== ==========================
``GET``    ``/${prefix}/${uuid}``                      :ref:`retrieve-metadata`
``POST``   ``/${prefix}``                              :ref:`create-metadata`
``PUT``    ``/${prefix}/${uuid}``                      :ref:`update-metadata`
``PUT``    ``/${prefix}/${uuid}/meta/state``           :ref:`Publish metadata <create-metadata>`
``DELETE`` ``/${prefix}/${uuid}``                      :ref:`delete-metadata`
``GET``    ``/${prefix}/${uuid}/page/${childPrefix}``  List child records (paged)
``GET``    ``/${prefix}/spec``                         SHACL shapes that apply to the layer
========== =========================================== ==========================

.. _retrieve-metadata:

Retrieving metadata
-------------------

Retrieving published metadata is open for GET requests without authorization.
In the following example, we retrieve a ``Dataset`` resource by issuing a ``GET`` request to the ``/dataset`` prefix followed by its identifier (a UUID).

.. code-block:: bash

    curl -H "Accept: text/turtle" https://fdp.example.com/dataset/58d7fbde-6c16-483e-b152-0f3ced131ca9

The following RDF serializations are supported, either via the ``Accept`` header or via the ``format`` query parameter:

============== ======================== ======================
Format         ``Accept`` header        ``format`` parameter
============== ======================== ======================
Turtle         ``text/turtle``          ``?format=ttl``
JSON-LD        ``application/ld+json``  ``?format=jsonld``
RDF/XML        ``application/rdf+xml``  ``?format=rdf``
N3             ``text/n3``              ``?format=n3``
============== ======================== ======================

For example, https://fdp.example.com/dataset/58d7fbde-6c16-483e-b152-0f3ced131ca9?format=jsonld returns JSON-LD, also when opened in a web browser.

.. _create-metadata:

Creating metadata
-----------------

New metadata can be created by ``POST``-ing the content to the appropriate endpoint.
First we will create a file called ``metadata.ttl`` to store our new metadata.
The content must conform to the :ref:`metadata schemas <metadata-schemas>` of the resource, and must link to its parent using ``dct:isPartOf``.

.. code-block:: turtle

    @prefix dcat: <http://www.w3.org/ns/dcat#> .
    @prefix dct: <http://purl.org/dc/terms/> .
    @prefix foaf: <http://xmlns.com/foaf/0.1/> .

    <> a dcat:Dataset ;
        dct:title "test" ;
        dcat:version "1.0" ;
        dct:publisher [ a foaf:Agent ; foaf:name "Example User" ] ;
        dcat:theme <http://www.wikidata.org/entity/Q14944328> ;
        dct:isPartOf <https://fdp.example.com/catalog/5f4a32c5-1f26-4657-9240-fc7ede7f1ce5> .

.. NOTE::
   As of FDP v1.17.1, the default schemas use ``dcat:version`` instead of ``dct:hasVersion``.

This metadata can be created by the following ``POST`` request.

.. code-block:: bash

    curl -H "Authorization: Bearer efIobn394nvJJFJ30..." \
        -H "Content-Type: text/turtle" \
        -d @metadata.ttl https://fdp.example.com/dataset

The response has status ``201 Created``, and its ``Location`` header contains the IRI of the new record.

When created, the metadata is initially in a ``DRAFT`` state.
To publish the metadata using the API you can issue the following ``PUT`` request to transition the metadata from the ``DRAFT`` state to the ``PUBLISHED`` state.

.. code-block:: bash

    curl -X PUT -H "Authorization: Bearer efIobn394nvJJFJ30..." \
        -H "Accept: application/json" \
        -H "Content-Type: application/json" \
        -d '{ "current": "PUBLISHED" }' \
        https://fdp.example.com/dataset/79508287-a2a7-4ae2-95b3-3f595e3088cc/meta/state

.. _update-metadata:

Update metadata
---------------

Existing metadata can be updated by issuing a ``PUT`` request with the request body being the updated metadata.

.. code-block:: bash

    curl -X PUT -H "Authorization: Bearer efIobn394nvJJFJ30..." \
        -H "Content-Type: text/turtle" \
        -d @metadata.ttl https://fdp.example.com/dataset/79508287-a2a7-4ae2-95b3-3f595e3088cc

.. _delete-metadata:

Delete metadata
---------------

An admin can delete a metadata record, including its children, with a ``DELETE`` request.
The root FAIR Data Point record cannot be deleted.

.. code-block:: bash

    curl -X DELETE -H "Authorization: Bearer efIobn394nvJJFJ30..." \
        https://fdp.example.com/dataset/79508287-a2a7-4ae2-95b3-3f595e3088cc


Other endpoints
===============

Besides the metadata endpoints, the API offers endpoints for, among others:

- ``/users`` and ``/api-keys``: user accounts and API keys
- ``/{prefix}/{uuid}/members``: memberships of a metadata record
- ``/resource-definitions`` and ``/metadata-schemas``: the metadata model (see :ref:`usage`)
- ``/settings`` and ``/index/settings``: :ref:`settings <settings>` and :ref:`FDP Index settings <fdp-index>`
- ``/search``: metadata search, and the experimental :ref:`SPARQL endpoint <sparql-endpoint>` at ``/search/sparql``
- ``/actuator/health``: health check


API endpoint listing
====================

The available APIs are documented using `OpenAPI <https://www.openapis.org/>`_.
In the ``/swagger-ui.html`` endpoint the APIs are visualized through `Swagger UI <https://swagger.io/tools/swagger-ui/>`_.
The machine-readable OpenAPI description is available at ``/v3/api-docs``.
