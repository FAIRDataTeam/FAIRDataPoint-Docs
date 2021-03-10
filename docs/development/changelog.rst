*********
Changelog
*********

Overview
========

Here we summarize the key features and changes for each FAIR Data Point release. For details including bugfixes and minor changes, see :ref:`detailed-changelog`.

1.8.0
-----

- Added Admin UI to FDP Index with possibility to trigger metadata retrieval, change settings, or delete entry
- Several bug fixes and dependencies updated (including Java 15)

1.7.0
-----

- Including FDP Index functionality into FAIR Data Point with harvesting metadata
- Metadata search including RDF types
- Possibility to change profile and password for current user

1.6.0
-----

- API keys for making integrations with FDP easier
- State "draft" for created metadata

1.5.0
-----

- Support for editable resource definitions
- Possibility to specify custom storage in OpenRefine using frontend 

1.4.0
-----

- Ping service for *call home* functionality
- Suggesting prefixes for namespaces

1.3.0
-----

- Introduced `DASH <http://datashapes.org/dash>`_ and dynamic SHACL shapes 
- Audit log in OpenRefine extension to keep track of actions performed

1.2.0
-----

- Option to customize metamodel (metadata layers)
- Possibility to delete and create metadata entities

1.1.0
-----

- New monitoring and configuration for client application
- Several further improvements in terms of technical debt
- Enhanced connecting to FDP from OpenRefine extension and update to OpenRefine 3.3

1.0.0
-----

- User management, enhanced security, and ACL
- Huge refactoring and upgrades of previously accumulated features and technical debt
- Separate project for `FAIR Data Point Client <https://github.com/FAIRDataTeam/FAIRDataPoint-client>`_ (frontend application  using FDP API)
- New `OpenRefine Metadata Extension <https://github.com/FAIRDataTeam/OpenRefine-metadata-extension>`_ as a replacement for the deprecated FAIRifier


.. _detailed-changelog:

Detailed changelog
==================

Each of components developed has its own Changelog based on `Keep a Changelog <https://keepachangelog.com/en/1.0.0/>`_,
and our projects adhere to `Semantic Versioning <https://semver.org/spec/v2.0.0.html>`_. It is recommended to use matching
versions of all components.

- `FAIR Data Point Changelog <https://github.com/FAIRDataTeam/FAIRDataPoint/blob/develop/CHANGELOG.md>`_
- `FAIR Data Point Client Changelog <https://github.com/FAIRDataTeam/FAIRDataPoint-client/blob/develop/CHANGELOG.md>`_
- `OpenRefine Metadata Extensions Changelog <https://github.com/FAIRDataTeam/OpenRefine-metadata-extension/blob/develop/CHANGELOG.md>`_
