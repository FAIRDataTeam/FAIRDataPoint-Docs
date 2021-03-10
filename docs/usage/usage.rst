*****
Usage
*****

.. _resource-definitions:

Resource definitions
====================

The **FAIR Data Point** reference implementations introduces the concept of **Resource Definitions**. A resource definition captures housekeeping data about a metadata resource.

Resource definitions can be accessed from the reference implementation user interface, in the dashboard of an admin user. Here the resource definitions can be managed.

Managing resource definitions
-----------------------------

Resource definitions can be :ref:`created <create-resource-definition>`, :ref:`modified <modify-resource-definition>`, or :ref:`deleted <delete-resource-definition>`.

.. _create-resource-definition:

Creating resource definitions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

When creating a new resource definition, the user interface presents you a form where a resource can be defined through a number of properties.

**Name** defines the human readable name for a resource definition. This name is used in the admin dashboard to identify the definitions, and does not affect a definition on the functional level. For example, for the default ``dcat:Dataset`` resource, the human readable name would be ``"Dataset"``.

**URL Prefix** defines the URL path for a resource. This context path should be a unique identifier, unique in the scope of the other resource defined within the FAIR Data Point instance. For example, for the ``dcat:Dataset`` resource the prefix is ``dataset``.

**Target Class URIs** links the :ref:`shape definitions <shapes>` to a resource definition. In the current implementation, each shape that should be applied to the resource must be listed here. The expected URI value must match the ``sh:targetClass`` value of the shape definition. A common example is to list the ``dcat:Resource`` shape target class along with the specific subclass for the resource, like ``dcat:Dataset``.

**Children** defines child resources, if any. This applies when the resource acts as a parent resource for other types of resources. Children are defined by the following properties to provide directives for both the server and the client side.

* *Child Resource* links to the child's *resource definition*. The child resource must be defined beforehand.
* *Child Relation URI* defines the predicate IRI that links the parent to the child on the metadata instance level. A common example is the link from a ``dcat:Dataset`` to a ``dcat:Distribution``; these resources are linked by the ``dcat:distribution`` predicate.
* *Child List View Title* defines a literal value to be displayed as a section header for the child resources in the user interface.
* *Child List View Tags URI* defines the predicate IRI for values that are displayed in the user interface whenever the child resources are listed. A common example is ``dcat:theme`` for ``dcat:Dataset`` resources.
* *Child List View Metadata* defines predicate IRIs for values that are listed in the child resource summary.

**External links** defines predicate IRIs and literal values to be displayed in the user interface for primary interaction with a resource. A common example is for the ``dcat:Distribution`` resource, ``dcat:accessURL`` is mapped to an ``Access URL`` literal, and displayed prominently in the user interface.

.. _modify-resource-definition:

Modifying resource definitions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

When modifying a resource definition, not all properties are writable. Some properties are write-protected to ensure the internal consistency of the system.

The **URL Prefix** and the **Target Class URIs** are not writable.

The other properties, like child resources and external links are writable, and can be expanded or modified after the initial creation of the resource definition.

.. _delete-resource-definition:

Deleting resource definitions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Deleting a resource definition should be used with caution. Existing metadata instances are no longer accessible after the resource definition is deleted. This includes child resources, if those are not linked to other resources.

.. _shapes:

Shapes
======

The **FAIR Data Point** reference implementation uses `SHACL <https://www.w3.org/TR/shacl>`_ to add validation constraints to the metadata model.

Creating a new shape
--------------------

A typical resource shape contains the following key elements:

* ``sh:targetClass`` to indicate the type of resource the shape applies to
* ``sh:property`` for each resource property

  * ``sh:path`` defines the predicate IRI
  * ``sh:nodeKind``/``sh:datatype`` defines the object type
  * ``sh:minCount``/``sh:maxCount`` defines the property cardinality

.. code :: turtle

    @prefix sh: <http://www.w3.org/ns/shacl#> .
    @prefix dash: <http://datashapes.org/dash#> .
    @prefix dct: <http://purl.org/dc/terms/> .
    @prefix dcat: <http://www.w3.org/ns/dcat#> .
    @prefix ex: <http://example.com/> .

    :MyResourceShape a sh:NodeShape ;
        sh:targetClass ex:MyResourceType ;
        sh:property [
            sh:path ex:value ;
            sh:nodeKind sh:Literal ;
            sh:minCount 1 ;
            sh:maxCount 2 ;
        ] .

User interface directives
-------------------------

The `DASH <http://datashapes.org/dash>`_ vocabulary introduces extensions to the core SHACL model. One of the extensions is focused on providing user interface hints for shape properties. Introducing or removing a ``dash:viewer`` or ``dash:editor`` property to a ``sh:PropertyShape`` instance influences how the user interface displays the property value.

.. code :: turtle

    sh:property [
        sh:path ex:value ;
        sh:nodeKind sh:Literal ;
        dash:viewer dash:LiteralViewer ;
        dash:editor dash:TextFieldEditor ;
    ]

By adding a ``dash:viewer`` statement, the user interface is instructed to show the property value when the resource metadata is displayed. Removing a ``dash:viewer`` statement will instruct the user interface will not render the property value at all. The value will still be present in the metadata model. The supported set of viewers (version 1.6.0):

* ``sh:LabelViewer``
* ``sh:URIViewer``

By adding a ``dash:editor`` statement, the editor form in the user interface will show an edit field for the property. Removing a ``dash:editor`` statement will prevent the property from being edited. This could be intended behaviour for properties that are generated server side. The supported set of editors (version 1.6.0):

* ``sh:TextFieldEditor``
* ``sh:TextAreaEditor``
* ``sh:URIEditor``
* ``sh:DatePickerEditor``

Extending an existing shape
---------------------------

Extending an existing shape can be achieved by targeting the same ``sh:targetClass``. For example, to extend the existing ``dcat:Dataset`` shape, an extension shape could look like the following:

.. code :: turtle

    :MyExtension a sh:NodeShape ;
        sh:targetClass dcat:Dataset ;
        sh:property [
            sh:path <http://example.com/vocab#myProperty> ;
            sh:nodeKind sh:Literal ;
            sh:minCount 1 ;
        ] .

Limitations
-----------
* The current implementation does not provide proper support for overriding properties when an existing resource is extended
* The set of supported ``dash:viewer`` and ``dash:editor`` types does not cover the full range as specified in the DASH specs.
