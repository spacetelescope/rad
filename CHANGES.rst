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
