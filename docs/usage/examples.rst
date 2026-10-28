.. _usage-examples:

**************
Usage examples
**************

This section shows how to carry out common tasks with a FAIR Data Point, both in the client and via the API.
The API examples use `curl <https://curl.se>`_ and `jq <https://jqlang.org>`_, and assume an FDP at ``https://fdp.example.com`` whose ``persistentUrl`` is the same URL.
Replace the URL, the credentials, and the UUIDs with your own values.

.. contents:: On this page
   :local:
   :depth: 1


.. _example-first-catalog:

Publishing a catalog, a dataset, and a distribution
===================================================

In the client
-------------

1. Log in.
2. On the home page of the FDP, click :guilabel:`Create` next to the list of catalogs, fill in the form, and save.
   Any logged-in user can create a catalog, and becomes its owner (see :ref:`users-and-roles`).
3. On the page of the new catalog, click :guilabel:`Create` next to the list of datasets, and fill in the dataset form.
4. On the page of the new dataset, create a distribution in the same way.
5. New records are drafts.
   Open each record and click :guilabel:`Publish` to make it visible to everyone.

Via the API
-----------

The following script does the same.
Each record is posted with ``dct:isPartOf`` pointing to its parent, and the FDP adds the link from the parent to the child itself.
The IRI of a new record is returned in the ``Location`` header of the response.

.. code-block:: bash

    FDP=https://fdp.example.com

    # log in and keep the token
    TOKEN=$(curl -s -X POST -H "Content-Type: application/json" \
        -d '{"email": "albert.einstein@example.com", "password": "password"}' \
        $FDP/tokens | jq -r .token)

    # helper: POST Turtle to a prefix, print the IRI of the new record
    create() {
        curl -s -i -X POST -H "Authorization: Bearer $TOKEN" \
            -H "Content-Type: text/turtle" --data-binary @- "$FDP/$1" \
            | awk 'tolower($1) == "location:" {print $2}' | tr -d '\r'
    }

    # helper: publish a record
    publish() {
        curl -s -X PUT -H "Authorization: Bearer $TOKEN" \
            -H "Content-Type: application/json" \
            -d '{"current": "PUBLISHED"}' "$1/meta/state" > /dev/null
    }

    CATALOG=$(create catalog <<EOF
    @prefix dcat: <http://www.w3.org/ns/dcat#> .
    @prefix dct: <http://purl.org/dc/terms/> .
    @prefix foaf: <http://xmlns.com/foaf/0.1/> .
    <> a dcat:Catalog ;
        dct:title "Example catalog" ;
        dcat:version "1.0" ;
        dct:publisher [ a foaf:Agent ; foaf:name "Example Organisation" ] ;
        dct:isPartOf <$FDP> .
    EOF
    )

    DATASET=$(create dataset <<EOF
    @prefix dcat: <http://www.w3.org/ns/dcat#> .
    @prefix dct: <http://purl.org/dc/terms/> .
    @prefix foaf: <http://xmlns.com/foaf/0.1/> .
    <> a dcat:Dataset ;
        dct:title "Example dataset" ;
        dcat:version "1.0" ;
        dct:publisher [ a foaf:Agent ; foaf:name "Example Organisation" ] ;
        dcat:theme <http://www.wikidata.org/entity/Q14944328> ;
        dcat:keyword "example" ;
        dct:isPartOf <$CATALOG> .
    EOF
    )

    DISTRIBUTION=$(create distribution <<EOF
    @prefix dcat: <http://www.w3.org/ns/dcat#> .
    @prefix dct: <http://purl.org/dc/terms/> .
    @prefix foaf: <http://xmlns.com/foaf/0.1/> .
    <> a dcat:Distribution ;
        dct:title "Example distribution (CSV)" ;
        dcat:version "1.0" ;
        dct:publisher [ a foaf:Agent ; foaf:name "Example Organisation" ] ;
        dcat:mediaType "text/csv" ;
        dcat:downloadURL <https://example.com/data.csv> ;
        dct:isPartOf <$DATASET> .
    EOF
    )

    for record in $CATALOG $DATASET $DISTRIBUTION; do publish $record; done

The required properties come from the default metadata schemas.
Every catalog, dataset, and distribution needs a ``dct:title``, a ``dcat:version``, and a ``dct:publisher`` with a ``foaf:name``.
A dataset also needs at least one ``dcat:theme``, and a distribution needs a ``dcat:mediaType``.
If a required property is missing, the FDP responds with ``400 Bad Request`` and a SHACL validation report.
The FDP completes the record with the ``rdf:type`` values of the resource definition, the identifier, timestamps, the default ``dct:language`` and ``dct:license``, an access rights statement, and ``dct:conformsTo`` pointing to the profile of the resource.


.. _example-custom-type:

Defining a custom resource type
===============================

The default model has catalogs, datasets, and distributions, but you can add your own resource types.
As an example, we add a **Software** type for research software, described with `schema.org <https://schema.org>`_ terms, that can be listed in a catalog next to datasets.
This takes three steps: a metadata schema, a resource definition, and a link from the parent resource definition.

Step 1. Create the metadata schema
----------------------------------

In the client, go to :guilabel:`Metadata schemas` and click :guilabel:`+ Create`.

- **Name** ``Software``
- **Abstract** not checked
- **Extends** ``Resource``, so the software gets the common properties (title, description, publisher, version, license, and so on)
- **Suggested Resource Name** ``Software``
- **Suggested URL Prefix** ``software``
- **Form Definition**

  .. code-block:: turtle

      @prefix : <http://fairdatapoint.org/> .
      @prefix sh: <http://www.w3.org/ns/shacl#> .
      @prefix dash: <http://datashapes.org/dash#> .
      @prefix schema: <https://schema.org/> .

      :SoftwareShape a sh:NodeShape ;
          sh:targetClass schema:SoftwareSourceCode ;
          sh:property [
              sh:path schema:codeRepository ;
              sh:nodeKind sh:IRI ;
              sh:minCount 1 ;
              sh:maxCount 1 ;
              dash:editor dash:URIEditor ;
              dash:viewer dash:URIViewer ;
              sh:order 30 ;
          ], [
              sh:path schema:programmingLanguage ;
              sh:nodeKind sh:Literal ;
              dash:editor dash:TextFieldEditor ;
              dash:viewer dash:LiteralViewer ;
              sh:order 31 ;
          ] .

Click :guilabel:`Save and release`, enter version ``1.0.0``, and release it.
Only released versions are used by the FDP.

Step 2. Create the resource definition
--------------------------------------

Go to :guilabel:`Resources definitions` and click :guilabel:`+ Create resource definition`.

- **Name** ``Software`` and **URL Prefix** ``software`` (the suggestions from the schema can be clicked)
- **Metadata Schemas** ``Software``
- **External links** (optional) title ``Code repository``, property URI ``https://schema.org/codeRepository``, so the link is shown prominently on the software page

Because the ``Software`` schema extends ``Resource``, records of this type get both ``schema:SoftwareSourceCode`` and ``dcat:Resource`` as ``rdf:type``.

Step 3. Add the new type as a child of catalogs
-----------------------------------------------

Open the ``Catalog`` resource definition and add a child.

- **Child Resource** ``Software``
- **Child Relation URI** ``http://www.w3.org/ns/dcat#resource``
- **Child List View Title** ``Software``

Save the resource definition.
Catalog pages now show a *Software* list with a :guilabel:`Create` button, and the software records are available at ``/software/<uuid>``.

.. NOTE::
   The FDP only accepts a new record if its parent's resource definition lists the record's resource definition as a child.
   Without step 3, posting a software record to a catalog fails with "Parent is not of correct type".

Creating a software record via the API
--------------------------------------

.. code-block:: bash

    curl -s -i -X POST -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: text/turtle" --data-binary @- $FDP/software <<EOF
    @prefix dcat: <http://www.w3.org/ns/dcat#> .
    @prefix dct: <http://purl.org/dc/terms/> .
    @prefix foaf: <http://xmlns.com/foaf/0.1/> .
    @prefix schema: <https://schema.org/> .
    <> a schema:SoftwareSourceCode ;
        dct:title "Example analysis pipeline" ;
        dcat:version "2.1.0" ;
        dct:publisher [ a foaf:Agent ; foaf:name "Example Organisation" ] ;
        schema:codeRepository <https://github.com/example/pipeline> ;
        schema:programmingLanguage "Python" ;
        dct:isPartOf <$CATALOG> .
    EOF

The FDP adds the target classes of all schemas of the resource definition to the record before validation, so ``dcat:Resource`` does not need to be included in the posted ``rdf:type``.
The constraints of the ``Resource`` schema, such as the required ``dct:title``, apply either way.

Setting up the type via the API
-------------------------------

The same set-up can be scripted, which is useful to configure several FDPs in the same way.
All calls below require an admin token.

.. code-block:: bash

    # 1. create a schema draft (definition read from software-shape.ttl)
    RESOURCE_SCHEMA=$(curl -s -H "Authorization: Bearer $TOKEN" $FDP/metadata-schemas \
        | jq -r '.[] | select(.name == "Resource") | .uuid')
    SCHEMA=$(jq -n --rawfile def software-shape.ttl --arg ext "$RESOURCE_SCHEMA" \
        '{name: "Software", description: "Research software", abstractSchema: false,
          definition: $def, extendsSchemaUuids: [$ext],
          suggestedResourceName: "Software", suggestedUrlPrefix: "software"}' \
        | curl -s -X POST -H "Authorization: Bearer $TOKEN" \
            -H "Content-Type: application/json" -d @- $FDP/metadata-schemas \
        | jq -r .uuid)

    # 2. release version 1.0.0
    curl -s -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
        -d '{"version": "1.0.0", "description": "First version", "published": false}' \
        $FDP/metadata-schemas/$SCHEMA/versions

    # 3. create the resource definition
    RD=$(jq -n --arg s "$SCHEMA" \
        '{name: "Software", urlPrefix: "software", metadataSchemaUuids: [$s], children: [],
          externalLinks: [{title: "Code repository", propertyUri: "https://schema.org/codeRepository"}]}' \
        | curl -s -X POST -H "Authorization: Bearer $TOKEN" \
            -H "Content-Type: application/json" -d @- $FDP/resource-definitions \
        | jq -r .uuid)

    # 4. add it as a child of the Catalog resource definition (PUT takes the full definition)
    CATALOG_RD=$(curl -s $FDP/resource-definitions | jq -r '.[] | select(.urlPrefix == "catalog") | .uuid')
    curl -s $FDP/resource-definitions/$CATALOG_RD \
        | jq --arg rd "$RD" '{name, urlPrefix, metadataSchemaUuids, externalLinks,
              children: (.children + [{resourceDefinitionUuid: $rd,
                  relationUri: "http://www.w3.org/ns/dcat#resource",
                  listView: {title: "Software", metadata: []}}])}' \
        | curl -s -X PUT -H "Authorization: Bearer $TOKEN" \
            -H "Content-Type: application/json" -d @- $FDP/resource-definitions/$CATALOG_RD


.. _example-extend-type:

Adding a property to an existing resource type
==============================================

To add a property to all datasets, create a schema that extends ``Dataset``, instead of editing the default ``Dataset`` schema.
This keeps the default schema intact, so it can still be updated by future FDP versions.
The example below adds an *access level*, chosen from a fixed list in the form.

.. code-block:: turtle

    @prefix : <http://fairdatapoint.org/> .
    @prefix sh: <http://www.w3.org/ns/shacl#> .
    @prefix dash: <http://datashapes.org/dash#> .
    @prefix dcat: <http://www.w3.org/ns/dcat#> .
    @prefix ex: <https://example.com/vocab#> .

    :DatasetAccessLevelShape a sh:NodeShape ;
        sh:targetClass dcat:Dataset ;
        sh:property [
            sh:path ex:accessLevel ;
            sh:name "access level" ;
            sh:nodeKind sh:Literal ;
            sh:maxCount 1 ;
            sh:in ( "open" "restricted" "closed" ) ;
            dash:editor dash:EnumSelectEditor ;
            dash:viewer dash:LiteralViewer ;
            sh:order 40 ;
        ] .

Create the schema with **Extends** ``Dataset``, release it, and add it to the ``Dataset`` resource definition under **Metadata Schemas**.

.. WARNING::
   The FDP validates every submitted record against the latest versions of all metadata schemas, matched by ``sh:targetClass``.
   A new ``sh:minCount 1`` constraint therefore applies to all existing datasets as soon as the schema is released, and they can no longer be updated until the property is added.
   Start with optional properties, as in the example, unless all records can be updated at once.


.. _example-users-access:

Managing users and access
=========================

Securing the default accounts
-----------------------------

Before an FDP becomes public, log in as ``albert.einstein@example.com`` and do the following under :guilabel:`Users`:

1. Create your own admin account.
2. Log in with the new account, and delete the default accounts, or at least change their passwords.

Via the API, an admin can create a user and change passwords as follows:

.. code-block:: bash

    curl -s -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
        -d '{"firstName": "Ada", "lastName": "Lovelace", "email": "ada@example.org",
             "password": "a-strong-password", "role": "USER"}' \
        $FDP/users

    curl -s -X PUT -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
        -d '{"password": "another-strong-password"}' \
        $FDP/users/<user-uuid>/password

Use ``"role": "ADMIN"`` for an admin account.
Users can change their own password via ``PUT /users/current/password``.

Giving a user access to a catalog
---------------------------------

In the client, open the catalog, go to its :guilabel:`Settings` page, and add the user as *Owner* or *Data Provider*.
Via the API, look up the membership UUIDs with ``GET /memberships`` and assign one:

.. code-block:: bash

    MEMBERSHIP=$(curl -s -H "Authorization: Bearer $TOKEN" $FDP/memberships \
        | jq -r '.[] | select(.name == "Data Provider") | .uuid')

    curl -s -X PUT -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
        -d "{\"membershipUuid\": \"$MEMBERSHIP\"}" \
        $CATALOG/members/<user-uuid>

A data provider can now add datasets to the catalog, and becomes the owner of each dataset they create.


.. _example-api-key:

Using an API key in scripts
===========================

Tokens expire after 14 days by default.
For scheduled jobs, such as a nightly script that updates metadata from another system, create an API key instead:

1. Log in to the client as the user the script should act as.
2. Open :guilabel:`API Keys` in the user menu, and create a key.
3. Store the key as a secret in the job's environment, and send it as ``Authorization: Bearer <api-key>``.

Use a dedicated user with only the memberships the job needs, and delete the key when it is no longer used.


.. _example-reuse-schemas:

Reusing metadata schemas from another FDP
=========================================

When a community has agreed on a metadata schema, one FDP can publish it and others can import it:

1. On the source FDP, release the schema version with :guilabel:`Public version` checked.
2. On your FDP, go to :guilabel:`Metadata schemas` → :guilabel:`Import`, enter the URL of the source FDP, and select the schemas to import.
3. Create or update resource definitions to use the imported schemas.
4. Later, use :guilabel:`Metadata schemas` → :guilabel:`Update` to check for and import newer versions.

Schemas that the imported schemas extend must also be public on the source FDP, or present on your FDP.


.. _example-reading:

Reading and harvesting metadata
===============================

Anyone can read published metadata, in several RDF formats:

.. code-block:: bash

    # the FDP itself, as Turtle
    curl -H "Accept: text/turtle" https://fdp.example.com

    # a dataset, as JSON-LD
    curl "https://fdp.example.com/dataset/<uuid>?format=jsonld"

    # the datasets of a catalog, ten per page
    curl -H "Accept: text/turtle" \
        "https://fdp.example.com/catalog/<uuid>/page/dataset?page=0&size=10"

    # the SHACL shapes that apply to datasets
    curl -H "Accept: text/turtle" https://fdp.example.com/dataset/spec

    # a simple text search
    curl -X POST -H "Content-Type: application/json" \
        -d '{"query": "covid"}' https://fdp.example.com/search

The representation of each record includes LDP containers that link to its children, so a harvester can start at the root and follow these links.
For more complex queries, enable the experimental :ref:`SPARQL endpoint <sparql-endpoint>`.


.. _example-indexing:

Making your FDP findable in an FDP Index
========================================

By default, every FDP pings https://home.fairdatapoint.org once a week, so it appears in that index.
To be listed in another index as well, for example a national or project index:

- add the index URL under :guilabel:`Settings` → :guilabel:`FDP Index connection` in the client, or
- add it to ``ping.endpoints`` in ``application.yml``, together with https://home.fairdatapoint.org if you want to keep that one.

The index harvests your published metadata after each ping, once it has accepted your FDP.
Make sure ``clientUrl`` is the public URL of your FDP, because that is the URL that is sent to the index.
See :ref:`fdp-index` for details, and for running your own index.
