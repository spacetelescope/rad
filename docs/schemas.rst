.. _schemas:

Science Products Schemas
========================

The following ASDF schemas define the structures used in Nancy Grace Roman Space Telescope files.
See :ref:doc:`roman_datamodels:roman_datamodels/datamodels/general_structure` for more details about how these schemas are used.
See :ref:`asdf-standard:asdf-schemas` for more information about ASDF schemas.

Level 1 (uncalibrated) schema
-----------------------------

.. asdf-autoschemas::

  wfi_science_raw

Level 2 (calibrated exposure) schema
------------------------------------

.. asdf-autoschemas::

   wfi_image
   wfi_wcs

Level 3 (resampled mosaic) schema
---------------------------------

.. asdf-autoschemas::

  wfi_mosaic

Level 4 (ancillary) schemas
---------------------------

.. asdf-autoschemas::

  image_source_catalog
  segmentation_map
  mosaic_source_catalog
  mosaic_segmentation_map


Tags
----

.. asdf-autoschemas::

    associations
    basic
    cal_logs
    common
    coordinates
    ephemeris
    exposure_type
    exposure
    guidestar
    guidewindow_modes
    guidewindow
    image_source_catalog
    individual_image_meta
    l2_cal_step
    l3_cal_step
    mosaic_associations
    mosaic_basic
    mosaic_segmentation_map
    mosaic_source_catalog
    mosaic_wcsinfo
    msos_stack
    observation
    outlier_detection
    photometry
    pointing
    program
    rad_schema
    ramp_fit_output
    ramp
    rcs
    ref_file
    resample
    segmentation_map
    sky_background
    source_catalog
    statistics
    velocity_aberration
    visit
    wcsinfo
    wfi_detector
    wfi_mode
    wfi_optical_element
    tagged_scalars/file_date
    tagged_scalars/calibration_software_name
    tagged_scalars/calibration_software_version
    tagged_scalars/filename
    tagged_scalars/model_type
    tagged_scalars/origin
    tagged_scalars/prd_version
    tagged_scalars/product_type
    tagged_scalars/sdf_software_version
    tagged_scalars/telescope

Previous versions
-----------------

These are older versions of the schemas.

Level 1 (uncalibrated) schema
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. asdf-autoschemas::
  :standard_prefix: schemas

  wfi_science_raw-1.0.0

Level 2 (calibrated exposure) schema
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. asdf-autoschemas::
  :standard_prefix: schemas

   wfi_image-1.0.0

Level 3 (resampled mosaic) schema
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. asdf-autoschemas::
  :standard_prefix: schemas

  wfi_mosaic-1.0.0


Tags
^^^^

.. asdf-autoschemas::
  :standard_prefix: schemas

    common-1.0.0
    guidewindow-1.0.0
    image_source_catalog-1.0.0
    msos_stack-1.0.0
    ramp_fit_output-1.0.0
    ramp-1.0.0
    ref_file-1.0.0
