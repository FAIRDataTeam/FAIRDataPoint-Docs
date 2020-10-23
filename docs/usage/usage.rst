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

Creating a new resource definition.

**Name** defines the human readable name for a resource definition. This name is used in the admin dashboard to identify the definitions, and does not affect a definition on the functional level.

**URL Prefix** defines the URL path for a resource. This context path should be a unique identifier, unique in the scope of the other resource defined within the FAIR Data Point instance.

**Target Class URIs** links the :ref:`shape definitions <shapes>` to a resource definition. In the current implementation, each shape that should be applied to the resource must be listed here. The expected URI value must match the ``sh:targetClass`` value of the shape definition. A common example is to list the ``dcat:Resource`` shape target class along with the specific subclass for the resource, like ``dcat:Dataset``.

**Children** defines child resources, if any. This applies when the resource acts as a parent resource for other types of resources. Children are defined by the following properties to provide directives for both the server and the client side.

* *Child Resource* links to the child's *resource definition*. The child resource must be defined beforehand.
* *Child Relation URI* defines the predicate IRI that links the parent to the child on the metadata instance level.
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
