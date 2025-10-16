.. _schemas:

Science Products Schemas
========================

The following ASDF schemas define the structures used in Nancy Grace Roman Space Telescope files.
See :ref:doc:`roman_datamodels:roman_datamodels/datamodels/general_structure` for more details about how these schemas are used.
See :ref:`asdf-standard:asdf-schemas` for more information about ASDF schemas.

Level 1 (uncalibrated) schema
-----------------------------

.. asdf-autoschemas::

  wfi_science_raw-1.4.0

Level 2 (calibrated exposure) schema
------------------------------------

.. asdf-autoschemas::

   wfi_image-1.4.0
   wfi_wcs-1.3.0

Level 3 (resampled mosaic) schema
---------------------------------

.. asdf-autoschemas::

  wfi_mosaic-1.4.0

Level 4 (ancillary) schemas
---------------------------

.. asdf-autoschemas::

  image_source_catalog-1.4.0
  forced_image_source_catalog-1.1.0
  segmentation_map-1.4.0
  mosaic_source_catalog-1.4.0
  forced_mosaic_source_catalog-1.1.0
  mosaic_segmentation_map-1.4.0
  multiband_source_catalog-1.1.0
  multiband_segmentation_map-1.0.0


Meta
----

.. asdf-autoschemas::

  meta/basic-1.0.0
  meta/cal_logs-1.0.0
  meta/calibration_software_name-1.0.0
  meta/calibration_software_version-1.0.0
  meta/catalog_image-1.0.0
  meta/common-1.0.0
  meta/coordinates-1.0.0
  meta/ephemeris-1.0.0
  meta/exposure-1.0.0
  meta/file_date-1.0.0
  meta/filename-1.0.0
  meta/guidestar-1.0.0
  meta/individual_image_meta-1.0.0
  meta/l2_cal_step-1.0.0
  meta/l2_catalog_common-1.0.0
  meta/l3_cal_step-1.0.0
  meta/l3_catalog_common-1.0.0
  meta/l3_common-1.0.0
  meta/l3_resample-1.0.0
  meta/l3_wcsinfo-1.0.0
  meta/model_type-1.0.0
  meta/observation-1.0.0
  meta/origin-1.0.0
  meta/outlier_detection-1.0.0
  meta/photometry-1.0.0
  meta/pointing-1.0.0
  meta/prd_version-1.0.0
  meta/product_type-1.0.0
  meta/program-1.0.0
  meta/rcs-1.0.0
  meta/ref_file-1.0.0
  meta/sdf_software_version-1.0.0
  meta/sky_background-1.0.0
  meta/source_catalog-1.0.0
  meta/telescope-1.0.0
  meta/velocity_aberration-1.0.0
  meta/visit-1.0.0
  meta/wcsinfo-1.0.0
  meta/wfi_mode-1.0.0

Enums
-----
.. asdf-autoschemas::

  enums/cal_step_flag-1.0.0
  enums/exposure_type-1.0.0
  enums/guidewindow_modes-1.0.0
  enums/wfi_detector-1.0.0
  enums/wfi_optical_element-1.0.0

Tables
------

.. asdf-autoschemas::

  tables/forced_catalog_table-1.0.0
  tables/multiband_catalog_table-1.0.0
  tables/prompt_catalog_table-1.0.0
  tables/source_catalog_columns-1.0.0
