.. _api-usage:

*********
API Usage
*********

The **FAIR Data Point** exposes API endpoints that allow consumers to interact with the metadata. Some of the endpoints are available for all users, while others require an API token for authorization.

Obtaining an API token
======================

In order to obtain an API token, you invoke the ``/tokens`` endpoint with your user credentials.

.. code :: bash

    curl -X POST -H "Accept: application/json" \
        -H "Content-Type: application/json" \
        -d '{ "email": "user@example.com", "password": "secret" }' \
        https://fdp.example.com/tokens

A successful call will return a ``JSON`` object with a token.

.. code ::

    { "token": "efIobn394nvJJFJ30..." }

Issueing a request with the authorization token
------------------------------------------------

Subsequent requests should use this token in the `Authorization` header. The authorization type is a `Bearer <https://tools.ietf.org/html/rfc6750>`_ token.

.. code :: bash

    curl -H "Authorization: Bearer efIobn394nvJJFJ30..." \
        -H "Accept: application/json" https://fdp.example.com/users

Interacting with metadata
=========================

The metadata layers as defined by the :ref:`resource-definitions` are exposed through their respective endpoints. The general approach is that each layer, defined by its ``prefix``, supports a number of read and write HTTP methods.

======== ====================== ========================
Method   URL pattern            Functionality
======== ====================== ========================
``GET``  ``/${prefix}/${uuid}`` :ref:`retrieve-metadata`
``POST`` ``/${prefix}``         :ref:`create-metadata`
``PUT``  ``/${prefix}/${uuid}`` :ref:`update-metadata`
======== ====================== ========================

.. _retrieve-metadata:

Retrieving metadata
-------------------

Retrieving metadata is open for GET requests without authorization. In the following example, we retrieve a ``Dataset`` resource by issuing a ``GET`` request to the ``/dataset`` prefix followed by its identifier (a UUID).

.. code :: bash

    curl -H "Accept: text/turtle" https://fdp.example.com/dataset/58d7fbde-6c16-483e-b152-0f3ced131ca9

.. _create-metadata:

Creating metadata
-----------------

New metadata can be created by ``POST``-ing the content to the appropriate endpoint. First we will create a file called ``metadata.ttl`` to store our new metadata.

.. code :: turtle

    @prefix dcat: <http://www.w3.org/ns/dcat#> .
    @prefix dct: <http://purl.org/dc/terms/> .
    @prefix foaf: <http://xmlns.com/foaf/0.1/> .

    <> a dcat:Dataset ;
        dct:title "test" ;
        dct:hasVersion "1.0" ;
        dct:publisher [ a foaf:Agent ; foaf:name "Example User" ] ;
        dcat:theme <http://www.wikidata.org/entity/Q14944328> ;
        dct:isPartOf <https://fdp.example.com/catalog/5f4a32c5-1f26-4657-9240-fc7ede7f1ce5> .

This metadata can be created by the following ``POST`` request.

.. code :: bash

    curl -H "Authorization: Bearer efIobn394nvJJFJ30..." \
        -H "Content-Type: text/turtle" \
        -d @metadata.ttl https://fdp.example.com/dataset

When created, the metadata is initially in a ``DRAFT`` state. To publish the metadata using the API you can issue the following ``PUT`` request to transistion the metadata from the ``DRAFT`` state to the ``PUBLISHED`` state.

.. code :: bash

    curl -X PUT -H "Authorization: Bearer efIobn394nvJJFJ30..." \
        -H "Accept: application/json" \
        -H "Content-Type: application/json" \
        -d '{ "current": "PUBLISHED" }' \
        https://fdp.example.com/dataset/79508287-a2a7-4ae2-95b3-3f595e3088cc/meta/state

.. _update-metadata:

Update metadata
---------------

Existing metadata can be updated by issuing a ``PUT`` request with the request body being the updated metadata.

.. code :: bash

    curl -X PUT -H "Authorization: Bearer efIobn394nvJJFJ30..." \
        -H "Content-Type: text/turtle" \
        -d @metadata.ttl https://fdp.example.com/dataset/79508287-a2a7-4ae2-95b3-3f595e3088cc

API endpoint listing
====================

The available APIs are documented using `OpenAPI <https://www.openapis.org/>`_. In the ``/swagger-ui.html`` endpoint the APIs are visualized through `Swagger UI <https://swagger.io/tools/swagger-ui/>`_.
