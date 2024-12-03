.. _schemas:

Science Products Schemas
========================

The following ASDF schemas define the structures used in Nancy Grace Roman Space Telescope files.
See :ref:doc:`roman_datamodels:roman_datamodels/datamodels/general_structure` for more details about how these schemas are used.
See :ref:`asdf-standard:asdf-schemas` for more information about ASDF schemas.

Level 1 (uncalibrated) schema
-----------------------------

.. asdf-autoschemas::

  wfi_science_raw-1.0.0

Level 2 (calibrated exposure) schema
------------------------------------

.. asdf-autoschemas::

   wfi_image-1.0.0

Level 3 (resampled mosaic) schema
---------------------------------

.. asdf-autoschemas::

  wfi_mosaic-1.0.0

Level 4 (ancillary) schemas
---------------------------

.. asdf-autoschemas::

  image_source_catalog-1.0.0
  segmentation_map-1.0.0
  mosaic_source_catalog-1.0.0
  mosaic_segmentation_map-1.0.0


Tags
----

.. asdf-autoschemas::

    associations-1.0.0
    basic-1.0.0
    cal_logs-1.0.0
    common-1.0.0
    coordinates-1.0.0
    ephemeris-1.0.0
    exposure_type-1.0.0
    exposure-1.0.0
    guidestar-1.0.0
    guidewindow_modes-1.0.0
    guidewindow-1.0.0
    individual_image_meta-1.0.0
    l2_cal_step-1.0.0
    l3_cal_step-1.0.0
    mosaic_associations-1.0.0
    mosaic_basic-1.0.0
    mosaic_wcsinfo-1.0.0
    msos_stack-1.0.0
    observation-1.0.0
    outlier_detection-1.0.0
    photometry-1.0.0
    pointing-1.0.0
    program-1.0.0
    rad_schema-1.0.0
    ramp_fit_output-1.0.0
    ramp-1.0.0
    rcs-1.0.0
    ref_file-1.0.0
    resample-1.0.0
    sky_background-1.0.0
    statistics-1.0.0
    source_catalog-1.0.0
    velocity_aberration-1.0.0
    visit-1.0.0
    wcsinfo-1.0.0
    wfi_detector-1.0.0
    wfi_mode-1.0.0
    wfi_optical_element-1.0.0
    tagged_scalars/file_date-1.0.0
    tagged_scalars/calibration_software_name-1.0.0
    tagged_scalars/calibration_software_version-1.0.0
    tagged_scalars/filename-1.0.0
    tagged_scalars/model_type-1.0.0
    tagged_scalars/origin-1.0.0
    tagged_scalars/prd_version-1.0.0
    tagged_scalars/product_type-1.0.0
    tagged_scalars/sdf_software_version-1.0.0
    tagged_scalars/telescope-1.0.0
