0.18.0 (unreleased)
-------------------

-

0.17.0 (2023-07-27)
-------------------

- Fix invalid uri fragment in rad_schema. [#286]

- Update the steps listed in ``cal_step`` to reflect the currently implemented steps.
  The new additions are ``outlier_detection``, ``refpix``, ``sky_match``, and ``tweak_reg``. [#282]

- Update the steps listed in ``cal_step`` with the ``resample`` step. [#295]

- Fix the URIs for ``inverselinearity`` and add consistency checks for names/uris. [#296]

0.16.0 (2023-06-26)
-------------------

- Fix minor discrepancies found when looking over the schemas. [#267]

- Bugfix for ``inverse_linearity-1.0.0``'s ``reftype`` so that it is CRDS
  compatible. [#272]

- Add schema ``refpix-1.0.0`` as a schema for the reference pixel correction's
  reference file. [#270]

- Add keyword to indicate if and which datamodel the schema describes. [#278]

- Add schema ``msos_stack-1.0.0`` as a level 3 schema for SSC. [#276]

0.15.0 (2023-05-12)
-------------------

- Update program to be a string to match association code [#255]

- Add gw_science_file_source to GW file, update size of the filename [#258]

- Update program to be a string to match association code [#255]

- Update guide star id, add catalog version, and add science file name [#258]

- Add gw_science_file_source to GW file, update size of the filename [#258]

- Remove use of deprecated ``pytest-openfiles`` ``pytest`` plugin. This has been replaced by
  catching ``ResourceWarning`` s. [#231]

- Add read pattern to the exposure group. [#233]

- Add ``distortion`` keyword option to the list of reference files, so that the ``distortion``
  reference file can be properly allowed in by the ``ref_file-1.0.0`` schema. [#237]

- Changelog CI workflow has been added. [#240]

- Clarifying database tables for guidewindows and guidestar." [#250]

- Remove the ``unit-1.0.0`` schema, because it is no-longer needed. [#248]

- Remove the unused ``pixelarea-1.0.0`` schema, which was replaced by the
  ``reference_files/pixelarea-1.0.0`` schema. [#245]

- Added support for level 3 mosaic model. [#241]

- Add further restrictions to the ``patternProperties`` keywords in the
  ``wfi_img_photom`` schema. [#254]


0.14.2 (2023-03-31)
-------------------

- Format the code with ``isort`` and ``black``. [#200]

- Switch linting from ``flake8`` to ``ruff``. [#201]

- Start using ``codespell`` to check and correct spelling mistakes. [#202]

- Created inverse non-linearity schema. [#213]

- Added PR Template. [#221]

- Begin process of decommissioning the Roman specific, non-VOunits. [#220]

- Fix schemas with $ref at root level. [#222]

- Add schema for source detection. [#215]

- Temporarily make source detection optional in cal_logs. [#224]

- Add database team to Code Owners file [#227]

- Update CodeOwners file [#230]


0.14.1 (2023-01-31)
-------------------

- Update guidwindow titles and descriptions. [#193]

- Changed science arrays to quantities. [#192]

- Add units to the schemas for science data quantities to specify allowed values. [#195]

- Update Reference file schemas to utilize quantities for all relevant arrays. [#198]

- Fix ``enum`` bug in schemas. [#194]

- move metadata to ``pyproject.toml`` in accordance with PEP621 [#196]

- Add ``pre-commit`` support. [#199]

- Add IPC reference schema. [#203]

- Updated  the variable type of x/y start/stop/size in guidewindow and guidestar schemas. [#205]

- Changed SDF "origin" in ephemeris-1.0.0.yaml to use definitve/predicted ephemeris. [#207]

- Adjust activity identifier in observation schema to better reflect potential values. [#204]

- Deleted source_type_apt from target-1.0.0.yaml [#206]

- Add reftype to IPC Schema. [#214]


0.14.0 (2022-11-04)
-------------------

- Use PSS views in SDF origin attribute. [#167]

- Add support for specific non-VOUnit units used by Roman. [#168]

0.13.2 (2022-08-23)
-------------------

- Add ``IPAC/SSC`` to ``origin`` enum. [#160]

- Add archive information to ``ref_file`` and fix indentation there. [#161]

0.13.1 (2022-07-29)
-------------------

- Removed CRDS version information from basic schema. [#146]

- Changed the dimensionality of the err variable in ramp. [149#]

- Create docs for RTD. [#151]

- Moved gw_function_start_time, gw_function_end_time, and
  gw_acq_exec_stat from GuideStar to GuideWindow. Removed duplicate
  gw time entries. [#154]

- Changed optical filter name W146 to F146. [#156]

- Moved archive related information in the ``basic`` schema directly
  into a tagged object for easier retrieval by ASDF. [#153, #158, #159]

- Fix ref_file schema. [#157]

0.13.0 (2022-04-25)
-------------------

- Remove start_time and end_time from the observation schema [#142]


0.12.0 (2022-04-15)
-------------------

- exposure schema update in include descriptions [#139]

- Moved ma_table_name and ma_table_number from observation to exposure schemas. [#138]

0.11.0 (2022-04-06)
-------------------

- Initial Guide Window Schema [#120]

- Enumerate aperture_name in the aperture schema [#129]

- Remove exptype and p_keywords from Distortion Model [#127]

- Added photom keyword attribute to cal_step schema. [#132]

- Added ma_table_number to observation and dark schemas. [#134]

- Create distortion schema [#122]

0.10.0 (2022-02-22)
-------------------

- Moved detector list to new file for importing to both data and reference schemas. [#119]

- Added support for Distortion reference files. Tweaked schema for WFI detector list. [#122]

- Changed input_unit and output_unit keyword types, titles, and tests. [#126]

- Removed exptype and p_keywords from Distortion schema. [#128]


0.9.0 (2022-02-15)
------------------

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
  separate arrays that contain the original border reference pixels copied during
  the dq_init step (and four additional arrays for their DQ). The level 2 file data
  array only contains the science pixels (the border pixels are trimmed during ramp fit),
  and contains separate arrays for the original border pixels and their dq arrays, and
  the amp33 reference pixels. [#112]

- Added ``uncertainty`` attributes to ``photometry`` and ``pixelareasr``
  to the photometry reference file schema. [#114]

- Removed ``Photometry`` from required properties in ``common``. [#115]

- Updated dark schema to include group keywords from exposure. [#117]

0.8.0 (2021-11-22)
------------------

- Add ``cal_logs`` to wfi_image-1.0.0 to retain log messages from romancal. [#96]

0.7.1 (2021-10-26)
------------------

- Reverted exposure time types from string back to astropy Time. [#94]

0.7.0 (2021-10-11)
------------------

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
------------------

- Changed ENGINEERING to F213 in optical_element. [#70]

- Workaround for setuptools_scm issues with recent versions of pip. [#71]

0.6.0 (2021-08-23)
------------------

- Added enumeration for ``meta.pedigree``. [#65, #67]

- Added more steps to the cal_step schema. [#66]

0.5.0 (2021-08-06)
------------------

- Adjust dimensionality of wfi_science_raw data array. [#64]

- Added dq_init step to cal_step. [#63]

0.4.0 (2021-07-23)
------------------

- Removed basic from ref_common and moved some of its attributes directly to ref_common [#59]

- Updated dq arrays to be of type uint32. Removed zeroframe, refout, and dq_def arrays. [#61]

0.3.0 (2021-06-28)
------------------

- Updated rampfitoutput model and WFIimgphotom models. Renamed rampfitoutput ramp_fit_output. [#58]

0.2.0 (2021-06-04)
------------------

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
------------------

- Initial Schemas for Roman Calibration Pipeline and SDP file generation
