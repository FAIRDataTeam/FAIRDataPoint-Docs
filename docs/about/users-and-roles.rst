.. _users-and-roles:

***************
Users and Roles
***************

Although unauthenticated users can view all published FDP content, only authenticated users can modify FDP content.
There are different roles for different privilege levels in the FAIR Data Point.

.. _authentication:

Authentication
==============

To make any changes to FDP content, you need to authenticate.

Default credentials
-------------------

For convenience the FDP comes configured with two user accounts straight out-of-the-box:

===== =============================== ============
Role  Username                        Password
===== =============================== ============
admin ``albert.einstein@example.com`` ``password``
user  ``nikola.tesla@example.com``    ``password``
===== =============================== ============

.. warning::
   These default user accounts are only intended for *offline* testing on your local machine.
   Make sure to change or remove the default user credentials *before* exposing your FDP to the public internet.
   An admin can do this in the client under :guilabel:`Users`, or via the ``/users`` API endpoints.

API tokens
----------

The FDP API uses token authentication.
To obtain a token, post your credentials to the ``/tokens`` endpoint, as described in your FDP's `API authentication docs`_.
You will then find the token in the response body.
This token can be included in the ``Authorization`` header for subsequent API requests that require authentication, as in ``'Authorization: Bearer <your-token>'``.
Refer to the :ref:`api-usage` section for an example.

Tokens are `JSON Web Tokens <https://jwt.io>`_ signed with a secret that must be configured for every deployment, as described in :ref:`jwt-secret`.
By default, a token is valid for 14 days.

For convenience, the interactive API docs have an ``Authorize`` button at the top where you can paste your token to authenticate for the session.

API keys
--------

For scripts and other machine clients, a logged-in user can create long-lived API keys, either in the client under :guilabel:`API Keys`, or via the ``/api-keys`` endpoint.
An API key is used in exactly the same way as a token, i.e. ``'Authorization: Bearer <your-api-key>'``, and it has the same privileges as the user who created it.
API keys do not expire, so delete keys that are no longer needed.


FAIR Data Point Roles
=====================

Two roles are available for authenticated users: ``user`` and ``admin``

Detailed user privileges are described in the table below:

=========================== =============== ====== =======
\                           unauthenticated authenticated
--------------------------- --------------- --------------
privilege                                   user   admin
=========================== =============== ====== =======
read metadata resources          yes         yes    yes
read resource definitions        yes         yes    yes
write metadata resources         no          yes    yes
write resource definitions       no          no     yes
manage metadata schemas          no          no     yes
manage users                     no          no     yes
manage settings                  no          no     yes
reset to factory defaults        no          no     yes
=========================== =============== ====== =======

A ``user`` can only change metadata records for which they have a membership, as described below.
Deleting metadata records is restricted to admins.


Membership Roles
================

Access to individual metadata records is managed through memberships.
The user who creates a metadata record automatically becomes its owner.
To create a child record, such as a dataset in a catalog, a user needs a membership on the parent record that allows this (owner or data provider).
Admins can create, change, and delete any record.

Members can be managed by the owner, in the client via the record's :guilabel:`Settings` page, or via the ``/{prefix}/{uuid}/members`` API endpoints.

Owner
-----

An owner can update the record, create child records (such as datasets in a catalog), and manage the members of the record.
The owner role can be assigned on catalogs, datasets, and distributions.

Data Provider
-------------

A data provider can create new datasets in a catalog, but cannot change the catalog itself.
The data provider role can be assigned on catalogs only.


.. _API authentication docs: http://localhost/swagger-ui.html
