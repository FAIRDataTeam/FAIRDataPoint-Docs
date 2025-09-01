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

API tokens
----------

The FDP API uses token authentication.
To obtain a token, post your credentials to the ``/tokens`` endpoint, as described in your FDP's `API authentication docs`_.
You will then find the token in the response body.
This token can be included in the ``Authorization`` header for subsequent API requests that require authentication, as in ``'Authorization: Bearer <your-token>'``.
Refer to the :ref:`api-usage` section for an example.

For convenience, the interactive API docs have an ``Authorize`` button at the top where you can paste your token to authenticate for the session.


FAIR Data Point Roles
=====================

Two roles are available for authenticated users: ``user`` and ``admin``

Detailed user privileges are described in the table below:

========================== =============== ====== =======
\                          unauthenticated authenticated
-------------------------- --------------- --------------
privilege                                   user   admin
========================== =============== ====== =======
read metadata resources          yes         yes    yes
read resource definitions        yes         yes    yes
write metadata resources         no          yes    yes
write resource definitions       no          no     yes
manage users                     no          no     yes
manage settings                  no          no     yes
========================== =============== ====== =======


Catalog Roles
=============

Owner
-----

Owner can update catalog details, add other users and upload new datasets.

Data Provider
-------------

Data Provider can create new data sets in the catalog.


Dataset Roles
=============

Owner
-----

Owner of the data set can update catalog details and add other users.


.. _API authentication docs: http://localhost/swagger-ui/index.html#/Authentication%20and%20Authorization/generateToken
