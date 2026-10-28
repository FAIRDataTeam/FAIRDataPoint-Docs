*********************
About FAIR Data Point
*********************

The **FAIRDataPoint** (**FDP**) consists of a REST API and a Web Client for creating, storing, and serving **FAIR metadata**.
The metadata content is generated **semi-automatically** according to the `FAIR Data Point specification <https://specs.fairdatapoint.org>`__.

This documentation describes the reference implementation, version |release| of the ``fdp`` back-end, used together with version |fdp_client_ver| of the ``fdp-client``.

Features
--------

-  Store and serve metadata resources, like catalogs, datasets, and distributions, as RDF (Turtle, JSON-LD, RDF/XML, N3)
-  Define custom metadata resources, based on versioned :ref:`metadata schemas <metadata-schemas>` (SHACL)
-  Share metadata schemas between FAIR Data Points (publish and import)
-  Search the metadata, with configurable search filters and saved queries
-  Run as an :ref:`FDP Index <fdp-index>` that harvests metadata from other FAIR Data Points
-  Manage user accounts, access per metadata record, and API keys

Security
--------

Everyone can read all published metadata resources, such as catalogs, datasets, and so on.
Only authenticated users can make changes to any of the FDP content.
Two roles are available for authenticated users: ``user`` and ``admin``.
Details are discussed in :ref:`Users and Roles <users-and-roles>`.

Getting started
---------------

Want to try it out? Set up a local test FAIR Data Point following the instructions in the :ref:`quickstart` section.
