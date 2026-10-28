.. _usage:

*****
Usage
*****

The structure of the metadata in a FAIR Data Point is defined by two concepts that an admin manages in the client:

- :ref:`Metadata schemas <metadata-schemas>` define *what* a metadata record must contain, using `SHACL <https://www.w3.org/TR/shacl>`_.
- :ref:`Resource definitions <resource-definitions>` define *where* records live in the API and how they are related, for example that a catalog contains datasets.

Out of the box, the FDP comes with metadata schemas and resource definitions for the FAIR Data Point itself, catalogs, datasets, and distributions, based on `DCAT <https://www.w3.org/TR/vocab-dcat-3/>`_ and the `FAIR Data Point specification <https://specs.fairdatapoint.org>`_.

.. _metadata-schemas:

Metadata schemas
================

The **FAIR Data Point** reference implementation uses `SHACL <https://www.w3.org/TR/shacl>`_ to add validation constraints to the metadata model.
These SHACL shapes are managed as **metadata schemas** (before v1.14 they were called *shapes*).
Metadata schemas are versioned, can extend each other, and can be shared between FAIR Data Points.

Metadata schemas can be managed by an admin in the client, under :guilabel:`Metadata schemas`, or via the ``/metadata-schemas`` API endpoints.

Schema properties
-----------------

A metadata schema has the following properties:

**Name** and **Description** describe the schema for humans.

**Abstract** marks a schema that is only meant to be extended by other schemas, and that cannot be used directly in a resource definition.
For example, the default ``Resource`` schema is abstract, and is extended by the ``Catalog``, ``Dataset``, and ``Distribution`` schemas.

**Extends** lists the schemas whose constraints are inherited by this schema.

**Suggested Resource Name** and **Suggested URL Prefix** are offered as defaults when a resource definition is created for this schema.

**Form Definition** contains the SHACL shapes themselves, in Turtle syntax.
The target classes of the schema are derived from the ``sh:targetClass`` statements in this definition.

Drafts, versions, and publishing
--------------------------------

Changes to a schema are made in a **draft**.
The draft does not affect the metadata until it is **released** as a new version.
Versions follow `Semantic Versioning <https://semver.org>`_, e.g. ``1.0.0``, and the latest released version is the one that is used.

When releasing a version, you can mark it as :guilabel:`Public version`.
Public (published) schema versions are made available to other FAIR Data Points via the ``/metadata-schemas/public`` endpoint.
A version can only be made public if all schemas it extends are public as well.

Importing schemas from another FDP
----------------------------------

An admin can import published schemas from another FAIR Data Point, by entering its URL under :guilabel:`Metadata schemas` → :guilabel:`Import`.
Schemas that were imported in this way can later be checked for newer versions, under :guilabel:`Metadata schemas` → :guilabel:`Update`.
This makes it possible to reuse community schemas without copying them by hand.

.. _shapes:

Writing a schema definition
---------------------------

A typical resource shape contains the following key elements:

* ``sh:targetClass`` to indicate the type of resource the shape applies to
* ``sh:property`` for each resource property

  * ``sh:path`` defines the predicate IRI
  * ``sh:nodeKind``/``sh:datatype`` defines the object type
  * ``sh:minCount``/``sh:maxCount`` defines the property cardinality
  * ``sh:order`` defines the order of the property in forms and views

.. code-block:: turtle

    @prefix sh: <http://www.w3.org/ns/shacl#> .
    @prefix dash: <http://datashapes.org/dash#> .
    @prefix ex: <http://example.com/> .

    ex:MyResourceShape a sh:NodeShape ;
        sh:targetClass ex:MyResourceType ;
        sh:property [
            sh:path ex:value ;
            sh:nodeKind sh:Literal ;
            sh:minCount 1 ;
            sh:maxCount 2 ;
            dash:editor dash:TextFieldEditor ;
            dash:viewer dash:LiteralViewer ;
        ] .

To see complete examples, open one of the default schemas, such as ``Dataset``, in the client.

User interface directives
-------------------------

The `DASH <https://datashapes.org/dash>`_ vocabulary introduces extensions to the core SHACL model.
One of the extensions is focused on providing user interface hints for shape properties.
Introducing or removing a ``dash:viewer`` or ``dash:editor`` property to a ``sh:PropertyShape`` instance influences how the user interface displays the property value.

.. code-block:: turtle

    sh:property [
        sh:path ex:value ;
        sh:nodeKind sh:Literal ;
        dash:viewer dash:LiteralViewer ;
        dash:editor dash:TextFieldEditor ;
    ]

By adding a ``dash:viewer`` statement, the user interface is instructed to show the property value when the resource metadata is displayed.
Removing a ``dash:viewer`` statement will instruct the user interface not to render the property value at all.
The value will still be present in the metadata model.
Viewers with special behavior in the ``fdp-client``:

* ``dash:LabelViewer`` shows a human readable label for an IRI value
* ``dash:URIViewer`` shows an IRI value as a link

Any other viewer, such as ``dash:LiteralViewer``, shows the value as text.

By adding a ``dash:editor`` statement, the editor form in the user interface will show an edit field for the property.
Removing a ``dash:editor`` statement will prevent the property from being edited.
This could be intended behaviour for properties that are generated server side.
The editors supported by the ``fdp-client``:

* ``dash:TextFieldEditor``
* ``dash:TextAreaEditor``
* ``dash:URIEditor``
* ``dash:DatePickerEditor``
* ``dash:DateTimePickerEditor``
* ``dash:BooleanSelectEditor``
* ``dash:EnumSelectEditor`` (with ``sh:in``)
* ``dash:AutoCompleteEditor`` (uses the forms autocomplete sources configured in :ref:`settings`)

Extending an existing schema
----------------------------

Rather than editing a default schema, it is recommended to create a new schema that **extends** it.
For example, to add a property to datasets, create a schema that extends ``Dataset`` and targets the same class:

.. code-block:: turtle

    @prefix sh: <http://www.w3.org/ns/shacl#> .
    @prefix dash: <http://datashapes.org/dash#> .
    @prefix dcat: <http://www.w3.org/ns/dcat#> .

    <http://example.com/shapes/MyDatasetExtension> a sh:NodeShape ;
        sh:targetClass dcat:Dataset ;
        sh:property [
            sh:path <http://example.com/vocab#myProperty> ;
            sh:nodeKind sh:Literal ;
            sh:minCount 1 ;
            dash:editor dash:TextFieldEditor ;
            dash:viewer dash:LiteralViewer ;
        ] .

Then add the new schema to the ``Dataset`` :ref:`resource definition <resource-definitions>`, so the client shows the new property in the dataset forms.

.. NOTE::
   The ``fdp`` validates submitted metadata against the latest versions of *all* metadata schemas in the FDP, matched by ``sh:targetClass``, not only against the schemas listed in the resource definition.
   Constraints of the default ``Dataset`` schema therefore still apply.

Limitations
-----------

* The current implementation does not provide proper support for overriding properties when an existing schema is extended.
* The set of supported ``dash:viewer`` and ``dash:editor`` types does not cover the full range as specified in the DASH specs.

.. _resource-definitions:

Resource definitions
====================

The **FAIR Data Point** reference implementation introduces the concept of **Resource Definitions**.
A resource definition captures housekeeping data about a metadata resource: its URL, the metadata schemas that apply to it, and its relations to other resources.

Resource definitions can be managed by an admin in the client, under :guilabel:`Resources definitions`, or via the ``/resource-definitions`` API endpoints.

Managing resource definitions
-----------------------------

Resource definitions can be :ref:`created <create-resource-definition>`, :ref:`modified <modify-resource-definition>`, or :ref:`deleted <delete-resource-definition>`.

.. _create-resource-definition:

Creating resource definitions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

When creating a new resource definition, the user interface presents you a form where a resource can be defined through a number of properties.

**Name** defines the human readable name for a resource definition.
This name is used in the admin dashboard to identify the definitions, and does not affect a definition on the functional level.
For example, for the default ``dcat:Dataset`` resource, the human readable name would be ``"Dataset"``.

**URL Prefix** defines the URL path for a resource.
This context path should be a unique identifier, unique in the scope of the other resource defined within the FAIR Data Point instance.
Only letters, digits, ``-``, and ``_`` are allowed.
For example, for the ``dcat:Dataset`` resource the prefix is ``dataset``.

**Metadata Schemas** links the :ref:`metadata schemas <metadata-schemas>` to a resource definition.
These schemas (including the schemas they extend) determine the forms in the client and the shapes served at ``/${prefix}/spec``.
Metadata submitted for this resource must have an ``rdf:type`` that matches one of the target classes of these schemas.

**Children** defines child resources, if any.
This applies when the resource acts as a parent resource for other types of resources.
Children are defined by the following properties to provide directives for both the server and the client side.

* *Child Resource* links to the child's *resource definition*.
  The child resource must be defined beforehand.
* *Child Relation URI* defines the predicate IRI that links the parent to the child on the metadata instance level.
  A common example is the link from a ``dcat:Dataset`` to a ``dcat:Distribution``; these resources are linked by the ``dcat:distribution`` predicate.
* *Child List View Title* defines a literal value to be displayed as a section header for the child resources in the user interface.
* *Child List View Tags URI* defines the predicate IRI for values that are displayed in the user interface whenever the child resources are listed.
  A common example is ``dcat:theme`` for ``dcat:Dataset`` resources.
* *Child List View Metadata* defines predicate IRIs for values that are listed in the child resource summary.

**External links** defines predicate IRIs and literal values to be displayed in the user interface for primary interaction with a resource.
A common example is for the ``dcat:Distribution`` resource, ``dcat:accessURL`` is mapped to an ``Access URL`` literal, and displayed prominently in the user interface.

.. _modify-resource-definition:

Modifying resource definitions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

When modifying a resource definition in the client, the **URL Prefix** cannot be changed, to ensure the internal consistency of the system.

The other properties, like metadata schemas, child resources and external links are writable, and can be expanded or modified after the initial creation of the resource definition.

.. _delete-resource-definition:

Deleting resource definitions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Deleting a resource definition should be used with caution.
Existing metadata instances are no longer accessible after the resource definition is deleted.
This includes child resources, if those are not linked to other resources.


Metadata lifecycle
==================

New metadata records are created in the ``DRAFT`` state.
Drafts are only visible to logged-in users.
Once a record is complete, it can be **published**, after which everyone can read it.
In the client, use the :guilabel:`Publish` action on the record; via the API, see :ref:`create-metadata`.


Search
======

The client has a search field that searches the metadata of the FDP.
On the search page, results can be narrowed down using filters, and logged-in users can save queries for reuse.
The search filters are configured by an admin under :guilabel:`Settings` (see :ref:`settings`).

The search functionality is also available via the ``/search`` API endpoints.
For SPARQL queries, see the experimental :ref:`SPARQL endpoint <sparql-endpoint>`.


Reset to defaults
=================

An admin can reset users, metadata, resource definitions (including metadata schemas), and settings to the factory defaults, under :guilabel:`Reset to defaults`, or via the ``/reset`` endpoint.

.. DANGER::
   A reset permanently deletes the selected data.
