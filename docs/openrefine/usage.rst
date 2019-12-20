*****
Usage
*****

Here you can read how to use the **metadata** extension for OpenRefine to store FAIR data and create metadata in FAIR Data Point.

About metadata extension
========================

The **metadata** extension for OpenRefine promotes FAIRness of the data by its integration with FAIR Data Point. With the extension you can easily FAIRify your data that you work on in directly in OpenRefine in two steps:

1. :ref:`openrefine-store-data` in configured storage.
2. :ref:`openrefine-create-metadata` in selected FAIR Data Point.


It replaces the legacy project called `FAIRifier <https://github.com/FAIRDataTeam/FAIRifier>`_.

Features
========

The extension provides the features only through :guilabel:`FAIR Metadata` extension menu located in top right corner above data table (typically next to :guilabel:`Wikidata` and others).

.. _openrefine-store-data:

Store FAIR data
---------------

1. Open the dialog for storing the data by clicking :guilabel:`FAIR Metadata > Store data to FAIR storage`
2. Select the desired storage (see :ref:`openrefine-configuration-storages`)
3. Select the desired format (the selection changes based on storage)
4. Press :guilabel:`Preview (download)` to download the file to verify the contents
5. Press :guilabel:`Store` to store the data in the storage
6. You will see the URL to the file which you can easy copy to clipboard by clicking a button

.. _openrefine-create-metadata:

Create metadata in FAIR Data Point
----------------------------------

1. Open the dialog for creating the metadata by clicking :guilabel:`FAIRMetadata > Create metadata in FAIR Data Point`
2. Select pre-configured FAIR Data Point connection or select :guilabel:`Custom FDP connection` and fill information (if allowed, see :ref:`openrefine-configuration-settings`)
3. Press :guilabel:`Connect` to connect to the selected FAIR Data Point
4. Select a catalog from available or create a new one

   * For a new one, fill in the metadata form (see also the optional fields) and press :guilabel:`Create catalog`

5. Select a dataset from available or create a new one

   * For a new one, fill in the metadata form (see also the optional fields) and press :guilabel:`Create dataset`

5. Create a new distribution
6. Fill in the metadata form (se also the optional fiels)

   * For the download URL you can easily access :ref:`openrefine-store-data` feature and field will be filled after storing the data

7. Check your new distribution (and/or other layers) listed

