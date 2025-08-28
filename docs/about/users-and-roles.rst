.. _users-and-roles:

***************
Users and Roles
***************

There are different roles for different levels in the FAIR Data Point.

FAIR Data Point Roles
=====================

Two roles are available for authenticated users: ``user`` and ``admin``

Detailed user privileges are described in the table below:

========================== =============== ====== =======
.                          unauthenticated authenticated
-------------------------- --------------- --------------
privilege                  .                user   admin
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
