0.9.0 (2022-02-15)
==================

- Add FGS (Fine Guidance System) modes to guidestar schema. [#103]

- Set all calsteps to required. [#102]

- Added p_exptype to exposure group for reference files (dark & readnoise)
  to enable automatic rmap generation. Added test to ensure that the p_exptype
  expression matched the exposure/type enum list. [#105]

- Added boolean level0_compressed attribute keyword to exposure group to
  indicate if the level 0 data was compressed. [#104]

- Update schemas for ramp, level 1, and 2 files to contain accurate representation of
  reference pixels. The level 1 file has an array that contains both the science and
  the border reference pixels, and another array containing the amp33 reference pixels.
  Ramp models also have an array that contains the science data and the border reference
  pixels and another array for the amp33 reference pixels, and they also contain four
  seperate arrays that contain the original border reference pixels copied during
  the dq_init step (and four additional arrays for their DQ). The level 2 file data
  array only contains the science pixels (the border pixels are trimmed during ramp fit),
  and contains seperate arrays for the original border pixels and their dq arrays, and
  the amp33 reference pixels. [#112]

- Added ``uncertainty`` attributes to ``photometry`` and ``pixelareasr``
  to the photometry reference file schema. [#114]

- Removed ``Photometry`` from required properties in ``common``. [#115]

- Updated dark schema to include group keywords from exposure. [#117]

0.8.0 (2021-11-22)
==================

- Add ``cal_logs`` to wfi_image-1.0.0 to retain log messages from romancal. [#96]

0.7.1 (2021-10-26)
==================

- Reverted exposure time types from string back to astropy Time. [#94]

0.7.0 (2021-10-11)
==================

- Added nonlinearity support. [#79]

- Added saturation reference file support. [#78]

- Added support for super-bias reference files. [#81]

- Added pixel area reference file support. [#80]

- Removed ``pixelarea`` and ``var_flat`` from the list of required attributes in ``wfi_image``. [#83]

- Changed certain exposure time types to string. Added units to guidestar variables, where appropriate. Removed references to RGS in guidestar. Added examples of observation numbers. [#91]

- Added mode keyword to dark and readnoise. [#90]

- ``RampFitOutput.pedestal`` needs to be 2-dimensional. [#86]

- Added optical_element to appropriate reference file schemas. Added ma_table_name to dark schema. Adjusted pixelarea schema imports. [#92]


0.6.1 (2021-08-26)
==================

- Changed ENGINEERING to F213 in optical_element. [#70]

- Workaround for setuptools_scm issues with recent versions of pip. [#71]

0.6.0 (2021-08-23)
==================

- Added enumeration for ``meta.pedigree``. [#65, #67]

- Added more steps to the cal_step schema. [#66]

0.5.0 (2021-08-06)
==================

- Adjust dimensionality of wfi_science_raw data array. [#64]

- Added dq_init step to cal_step. [#63]

0.4.0 (2021-07-23)
==================

- Removed basic from ref_common and moved some of its attributes directly to ref_common [#59]

- Updated dq arrays to be of type uint32. Removed zeroframe, refout, and dq_def arrays. [#61]

0.3.0 (2021-06-28)
==================

- Updated rampfitoutput model and WFIimgphotom models. Renamed rampfitoutput ramp_fit_output. [#58]

0.2.0 (2021-06-04)
==================

- Updated yaml files to match latest in RomanCAL. [JIRA RCAL-143]

- Changed string date/time to astropy time objects. [JIRA RCAL-153]

- Updated id URIs. [JIRA RCAL-153]

- Updated all integers to proper integer types. [JIRA RCAL-153]

- Updated exposure.type. [JIRA RCAL-153]

- Change gs to gw in guidestar to reflect that they are all windows.
  [JIRA RCAL-153]

- Corrected Manifest URI. [#5]

- Removed keyword_pixelarea from Manifest. [#11]

- Removed .DS_Store files. [#7]

- Change URI prefix to asdf://, add tests and CI infrastructure. [#14]

- Moved common.yaml keywords to basic.yaml, and adjusted tests for
  basic.yaml. [JIRA RAD-7]

- Added misc. required db keyword attributes. [JIRA RAD-7]

- Added wfi photom schema and tests. [#34]

- Added Dark schema and updated Flat schema. [#35]

- Added dq schema. [#32]

- Added readnoise, mask, and gain schemas. [#37]

- Added support for ramp fitting schemas. [#43]

- Updated aperture, basic, ephemeris, exposure, guidestar, observation, pixelarea, and visit schemas. [#46]

- Added support for variance object schemas. [#38]

0.1.0 (unreleased)
==================

- Initial Schemas for Roman Calibration Pipeline and SDP file generation
