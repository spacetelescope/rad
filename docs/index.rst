.. image:: https://github.com/spacetelescope/branding/blob/81b7021231e885bda9c022e6c082b3cf26009b3b/stsci_pri_combo_mark_horizonal_white_bkgd.svg?raw=true
   :width: 83%
   :target: https://stsci.edu

.. image:: https://github.com/spacetelescope/romancal/blob/dc903a0164c3ce349caeb4f9f3a8bdc215cf05d3/docs/_static/A_Rst_1020_Logo_Box_Color_Seafoamondarkblue_Logo_Full_Color_RGB_850px%4072ppi.png?raw=true
   :width: 15%
   :target: https://science.nasa.gov/mission/roman-space-telescope/

.. _rad:

**************************
Roman Attribute Dictionary
**************************

The Roman Attribute Dictionary (RAD) is a package which defines schemas for the Nancy Grace
Roman Space Telescope files. Metadata attributes are used by both Science Data Processing and
the Archive Keyword Dictionary.

.. note::
  These are schemas for the :ref:`ASDF file <asdf-standard:asdf-standard>` file format,
  used by ASDF to serialize and deserialize data for the Nancy Grace Roman Space Telescope.

Included Resources
==================

The following are listings of all the schemas provided by this package for ASDF.

.. note::
  Typically, schemas are used in ASDF via their tag, which can be found in the manifest.

.. toctree::
  :maxdepth: 1

  schemas.rst
  reference_files.rst
  manifests.rst
  ground_tests.rst
  ccsp.rst
  ssc.rst

Developer Resources
===================

.. toctree::
  :maxdepth: 1

  helper.rst
  creating.rst
  versioning.rst
  contributing.rst
  changes.rst
  legacy.rst

Index
=====

* :ref:`genindex`
