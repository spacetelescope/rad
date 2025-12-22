0.29.0 (2025-12-18)
===================

New Features
------------

- Add initial schemas and docs for community contributed science product (CCSP)
  schemas. (`#747 <https://github.com/spacetelescope/rad/issues/747>`_)
- Added jitter keywords to l1, l2, and epsf schemas. (`#755
  <https://github.com/spacetelescope/rad/issues/755>`_)
- Add new Integral Non-Linearity reference file schema. (`#777
  <https://github.com/spacetelescope/rad/issues/777>`_)
- Added a schema for the Detector Status reference file. (`#778
  <https://github.com/spacetelescope/rad/issues/778>`_)
- Added a schema for Dark Decay Signal reference files. (`#779
  <https://github.com/spacetelescope/rad/issues/779>`_)
- Add wfi18_transient step to l2_cal_step schema. (`#780
  <https://github.com/spacetelescope/rad/issues/780>`_)
- Update ``ramp`` datamodel to require ``meta.cal_step`` entries. (`#782
  <https://github.com/spacetelescope/rad/issues/782>`_)


Misc
----

- Add correct types for archive_meta. (`#750
  <https://github.com/spacetelescope/rad/issues/750>`_)
- Updates archive destinations for B20 (`#754
  <https://github.com/spacetelescope/rad/issues/754>`_)
- Removes WFICommon from archive destinations under latest for B20 (`#757
  <https://github.com/spacetelescope/rad/issues/757>`_)
- Updates archive_destination details after interim RAD B20 testing (`#760
  <https://github.com/spacetelescope/rad/issues/760>`_)
- Refactor the guide window related schemas to combine common fields and create
  a common guide_window_id schema that all schemas can reference. (`#765
  <https://github.com/spacetelescope/rad/issues/765>`_)
- Removed the MA Table keywords from the dark current reference schema. (`#776
  <https://github.com/spacetelescope/rad/issues/776>`_)
- Make ``INCOMPLETE`` the first enum value for ``cal_step_flag``, this sets it
  as the
  default value when RDM creates nodes using this flag. (`#784
  <https://github.com/spacetelescope/rad/issues/784>`_)


0.28.0 (2025-10-16)
===================

Bug Fixes
---------

- Update fps schema to include reference to the statistics tag in its ``meta``
  section. (`#685 <https://github.com/spacetelescope/rad/issues/685>`_)
- Allow longer ref_file filenames (required for some user-supplied reference
  files). (`#729 <https://github.com/spacetelescope/rad/issues/729>`_)
- Remove redundant maxLength keywords for enum checking subschemas. (`#731
  <https://github.com/spacetelescope/rad/issues/731>`_)
- Remove unused default from coordinates schemas. (`#740
  <https://github.com/spacetelescope/rad/issues/740>`_)


Documentation
-------------

- Update the contributing docs to reflect the current contribution and review
  process. (`#682 <https://github.com/spacetelescope/rad/issues/682>`_)
- Update the RAD docs to reflect all the changes within RAD recently. (`#745
  <https://github.com/spacetelescope/rad/issues/745>`_)


New Features
------------

- Add effective area to the photom reference file schema. (`#630
  <https://github.com/spacetelescope/rad/issues/630>`_)
- Added complete set of CGI L1, L2a, and L2b archive search keywords (`#664
  <https://github.com/spacetelescope/rad/issues/664>`_)
- Introduce first draft of the SSC/GDPS schemas into the RAD repository. (`#665
  <https://github.com/spacetelescope/rad/issues/665>`_)
- Added first draft of the SSC/MSOS schemas into the RAD repository. (`#671
  <https://github.com/spacetelescope/rad/issues/671>`_)
- Make the previously deprecated guidewindow schema a static schema. (`#687
  <https://github.com/spacetelescope/rad/issues/687>`_)
- Remove active use of the tagged scalars in the latest schemas. (`#688
  <https://github.com/spacetelescope/rad/issues/688>`_)
- Remove the use of internal tags within RAD schemas and replace with standard
  schema $refs. (`#691 <https://github.com/spacetelescope/rad/issues/691>`_)
- Add psf field to msos_stack schema. (`#692
  <https://github.com/spacetelescope/rad/issues/692>`_)
- More complete archive search keyword definitions for MSOS catalogs and
  reference frame level 3
  Removed 'meta' nesting from MSOS archive search schemas.
  Switched asdf/time tagging to references to asdf/time iso_time (`#700
  <https://github.com/spacetelescope/rad/issues/700>`_)
- Move ``individual_image_meta`` schema information into its own distinct
  schema file. (`#716 <https://github.com/spacetelescope/rad/issues/716>`_)
- The remaining parts of reorganizing RAD schemas. This moves all the
  non-datamodels
  schemas out of the ``latest`` directory except the metaschema ``rad_schema``.
  (`#719 <https://github.com/spacetelescope/rad/issues/719>`_)
- Add super schema and archive schema parsers for the rad schemas. (`#721
  <https://github.com/spacetelescope/rad/issues/721>`_)
- Update L4 (catalog) metadata to better match input/image file metadata.
  (`#724 <https://github.com/spacetelescope/rad/issues/724>`_)
- Added "null" as a possible value for `acq_centroid_quality` in the L1
  Detector Guide Window schema. (`#737
  <https://github.com/spacetelescope/rad/issues/737>`_)


Misc
----

- Removed the "." prefix for MSOS keyword names to match their archive catalog
  column counterparts. (`#674
  <https://github.com/spacetelescope/rad/issues/674>`_)
- Remove direct ASDF packaging of the SSC schemas, and modify the versioning
  tests
  so that they no longer apply to the SSC schemas. (`#686
  <https://github.com/spacetelescope/rad/issues/686>`_)
- SSC ROMAN-3776 feedback from SSC GDPS G1DP on the
  wfi_spec_catalog_level_4.yaml and wfi_spec_data_quality_level_4.yaml data
  models (`#701 <https://github.com/spacetelescope/rad/issues/701>`_)
- Updates the archive_meta tag as necessary (`#711
  <https://github.com/spacetelescope/rad/issues/711>`_)
- Fixes typo WFICommon.telescopes to telescope (`#718
  <https://github.com/spacetelescope/rad/issues/718>`_)
- SSC ROMAN-3912 Update G2DP keywords in ``/latest/SSC`` directory (`#722
  <https://github.com/spacetelescope/rad/issues/722>`_)
- Made the `product_type` keyword required. (`#733
  <https://github.com/spacetelescope/rad/issues/733>`_)
- Removed the enum list for `pedigree` in `ref_common`. (`#734
  <https://github.com/spacetelescope/rad/issues/734>`_)
- Renamed the reset read variables to reference read in `wfi_science_raw` and
  removed them from `wfi_image`. (`#735
  <https://github.com/spacetelescope/rad/issues/735>`_)


Deprecations and Removals
-------------------------

- Make unused associations schema static. (`#702
  <https://github.com/spacetelescope/rad/issues/702>`_)


0.27.0 (2025-08-15)
===================

New Features
------------

- Introduce first draft of the CGI schemas into the RAD repository. (`#651
  <https://github.com/spacetelescope/rad/issues/651>`_)
- Fill in the placeholder values in the archive desinatations for the CGI
  schemas. (`#655 <https://github.com/spacetelescope/rad/issues/655>`_)


Misc
----

- Made dark data cube optional. (`#653
  <https://github.com/spacetelescope/rad/issues/653>`_)


0.26.0 (2025-07-17)
===================

Bug Fixes
---------

- Bugfixes for ``maxLength`` and ``nvarchar`` issues throughout the schemas.
  Note
  that this includes the introduction of unit tests to check that the
  ``maxLength``
  is included and matches the ``nvarchar`` when applicable. (`#611
  <https://github.com/spacetelescope/rad/issues/611>`_)
- Add missing tag validators to l1_detector_guidewindow schema. (`#613
  <https://github.com/spacetelescope/rad/issues/613>`_)
- Fixing erroneous wsm_edge_used title in l1_detector_guidewindow and
  l1_face_guidewindow schemas. (`#621
  <https://github.com/spacetelescope/rad/issues/621>`_)
- Fixed archive catalog string length for fgs_modes_used. (`#641
  <https://github.com/spacetelescope/rad/issues/641>`_)
- Added github url to versioning test. (`#644
  <https://github.com/spacetelescope/rad/issues/644>`_)


New Features
------------

- Add var_sky to WFI mosaic schema. (`#573
  <https://github.com/spacetelescope/rad/issues/573>`_)
- Add a helper script, ``scripts/rad.py`` to assist with the management of the
  RAD resources.
  Features include:
  - Listing the latest versions of all the RAD resources.
    - includes indications of which resources are "frozen" (not changeable
  without
      a new version) at the time of script execution.
  - Creating (and integrating) a new RAD resource.
    - Includes bumping the manifest version if necessary
  - Bumping existing RAD resource versions.
    - Includes solving the cascade of version bumps that maybe required.
  - Editing existing RAD resources.
    - Includes bumping the resource (and the cascade of other resources) if the
      edits necessitate a version bump. (`#593
  <https://github.com/spacetelescope/rad/issues/593>`_)
- Refactor the ``cal_step`` schemas to use a common schema for the step flags.
  (`#598 <https://github.com/spacetelescope/rad/issues/598>`_)
- Move ``wfi_mosaic.cal_logs`` to ``wfi_mosaic.meta.cal_logs`` for consistency
  with ``wfi_image.meta.cal_logs``. (`#601
  <https://github.com/spacetelescope/rad/issues/601>`_)
- Enable automatic yaml style formatting. (`#607
  <https://github.com/spacetelescope/rad/issues/607>`_)
- Bump manifest to 1.3.0 now that RAD 0.25.0 has been released with manifest
  version
  1.2.0. (`#612 <https://github.com/spacetelescope/rad/issues/612>`_)
- Remove ``fps`` and ``tvac`` schemas from the ``latest`` schemas and create a
  "static" manifest to track such removals. (`#617
  <https://github.com/spacetelescope/rad/issues/617>`_)
- Add schemas for tables in ImageSourceCatalog, MosaicSourceCatalog.
  Add new schemas for ForcedImageSourceCatalog, ForcedMosaicSourceCatalog and
  MultibandSourceCatalog. (`#624
  <https://github.com/spacetelescope/rad/issues/624>`_)
- Update level 3 MosaicModel schema based on new metadata structure. (`#632
  <https://github.com/spacetelescope/rad/issues/632>`_)


0.25.0 (2025-05-12)
===================

New Features
------------

- Reorganize the schemas so that schema changes are easier to review and
  understand
  if schema versions need to be bumped along with finding the cascade of
  changes to
  other schemas. (`#586 <https://github.com/spacetelescope/rad/issues/586>`_)
- Add ``NOT_CONFIGURED`` option to the ``wfi_optical_element`` schema. (`#599
  <https://github.com/spacetelescope/rad/issues/599>`_)
- Bump ASDF to ``>=4.1.0`` to ensure that the ``schema_info`` issue is fixed.
  (`#603 <https://github.com/spacetelescope/rad/issues/603>`_)
- Add new ``exposure_types`` to the ``exposure_type`` schema. (`#605
  <https://github.com/spacetelescope/rad/issues/605>`_)


Misc
----

- Adds basic keyword group to both L1 Guidewindow schemas
  Updated database keyword names
  Commented out archive_meta in deprecated guidewindow schema (`#594
  <https://github.com/spacetelescope/rad/issues/594>`_)


0.24.0 (2025-04-18)
===================

Documentation
-------------

- Update versioning docs to describe non-ASDF schema changes will not result in
  new schema versions. (`#572
  <https://github.com/spacetelescope/rad/issues/572>`_)


New Features
------------

- Added schema for MA Table reference files. (`#553
  <https://github.com/spacetelescope/rad/issues/553>`_)
- Added epsf and apcorr to ref_files and ref_files to image_source_catalog.
  Updated ref_files version in common, and common version elsewhere. (`#560
  <https://github.com/spacetelescope/rad/issues/560>`_)
- Define new schema WfiWcs. (`#564
  <https://github.com/spacetelescope/rad/issues/564>`_)
- Added the L1 Guide Window Detector schema. (`#579
  <https://github.com/spacetelescope/rad/issues/579>`_)
- Added L1 Average FACE Guide Window File Schema. (`#580
  <https://github.com/spacetelescope/rad/issues/580>`_)


Misc
----

- test with latest supported version of Python (`#546
  <https://github.com/spacetelescope/rad/issues/546>`_)
- Removed the WFICommon db from the guidestar schema. (`#570
  <https://github.com/spacetelescope/rad/issues/570>`_)
- Updated SDP origin names for various attributes. (`#571
  <https://github.com/spacetelescope/rad/issues/571>`_)
- Adjusted several RTB directed L1 & L2 metadata schema changes. (`#574
  <https://github.com/spacetelescope/rad/issues/574>`_)


0.23.1 (2025-02-14)
===================

Bug Fixes
---------

- Fix some inconsistencies in the ``msos_step`` and ``sky_background`` schemas.
  (`#532 <https://github.com/spacetelescope/rad/issues/532>`_)
- Reorder anyOf items in apcorr schema to work around asdf bug. (`#542
  <https://github.com/spacetelescope/rad/issues/542>`_)


Documentation
-------------

- Add section describing versioning and old file support. (`#528
  <https://github.com/spacetelescope/rad/issues/528>`_)


New Features
------------

- Require that ``archive_catalog`` and ``sdf`` marked keywords are in the
  ``required``
  list for the object containing those keywords. (`#505
  <https://github.com/spacetelescope/rad/issues/505>`_)
- Added schema for skycell reference file. (`#536
  <https://github.com/spacetelescope/rad/issues/536>`_)


Misc
----

- Adjust the RSDP origins for several keywords. (`#544
  <https://github.com/spacetelescope/rad/issues/544>`_)


0.23.0 (2025-01-16)
===================

Bug Fixes
---------

- Move schema references under allOf combiners if the schema contains other
  items. (`#525 <https://github.com/spacetelescope/rad/issues/525>`_)


Documentation
-------------

- Updates the RAD documentation to match the current schemas and fixes broken
  links. (`#514 <https://github.com/spacetelescope/rad/issues/514>`_)


New Features
------------

- Remove units from the reference file schemas. (`#490
  <https://github.com/spacetelescope/rad/issues/490>`_)
- Rename source_detection to source_catalog to match step name in romancal.
  (`#513 <https://github.com/spacetelescope/rad/issues/513>`_)
- Update all ``$ref`` so that they use absolute URIs rather than relative URIs.
  (`#527 <https://github.com/spacetelescope/rad/issues/527>`_)


Misc
----

- Changed the db type of `vparity`. (`#508
  <https://github.com/spacetelescope/rad/issues/508>`_)
- Remove upper pin for asdf. (`#510
  <https://github.com/spacetelescope/rad/issues/510>`_)
- Added null values to allowed APCORR and ABVEGAOFFSET keyword values. (`#516
  <https://github.com/spacetelescope/rad/issues/516>`_)
- Bump min Python to 3.11 per SPEC 0. (`#520
  <https://github.com/spacetelescope/rad/issues/520>`_)


0.22.0 (2024-11-15)
===================

Documentation
-------------

- use ``towncrier`` to handle change log entries (`#442
  <https://github.com/spacetelescope/rad/issues/442>`_)
- Update schema docs to clarify headings and add links to roman_datamodels and
  asdf. (`#446 <https://github.com/spacetelescope/rad/issues/446>`_)
- Added ``refpix`` entry in ``ref_file``. (`#458
  <https://github.com/spacetelescope/rad/issues/458>`_)


New Features
------------

- Add maxLength keywords to schemas matching nvarchar archive_catalog
  datatypes. (`#448 <https://github.com/spacetelescope/rad/issues/448>`_)
- Added ePSF, ABVegaOffset, and ApCorr schemas (`#452
  <https://github.com/spacetelescope/rad/issues/452>`_)
- remove var_flat from list of required mosaic attributes (`#462
  <https://github.com/spacetelescope/rad/issues/462>`_)
- Add python 3.13 support. (`#468
  <https://github.com/spacetelescope/rad/issues/468>`_)
- Remove units from Guidewindow schema. (`#499
  <https://github.com/spacetelescope/rad/issues/499>`_)


Misc
----

- Updated ``cal_step`` and ``cal_log`` schema information. (`#466
  <https://github.com/spacetelescope/rad/issues/466>`_)
- Update ``coordinate`` schema descriptions (`#467
  <https://github.com/spacetelescope/rad/issues/467>`_)
- Update ``ephemeris`` schema descriptions (`#469
  <https://github.com/spacetelescope/rad/issues/469>`_)
- Updates ``guide_star``, ``instrument``, and ``photometry`` schemas (`#471
  <https://github.com/spacetelescope/rad/issues/471>`_)
- Add ``rcs`` and removes ``aperture``, ``target`` schemas (`#473
  <https://github.com/spacetelescope/rad/issues/473>`_)
- Update and add keywords and descriptions in the basic-1.0.0 and statistics
  schemas (`#474 <https://github.com/spacetelescope/rad/issues/474>`_)
- Update the pointing schema (`#475
  <https://github.com/spacetelescope/rad/issues/475>`_)
- Update velocity_aberration descriptions and keywords (`#476
  <https://github.com/spacetelescope/rad/issues/476>`_)
- Updates wcs keywords and attribute information (`#477
  <https://github.com/spacetelescope/rad/issues/477>`_)
- Update exposure and program attributes information (`#478
  <https://github.com/spacetelescope/rad/issues/478>`_)
- Update ref_file descriptions (`#479
  <https://github.com/spacetelescope/rad/issues/479>`_)
- Update observation descriptions (`#480
  <https://github.com/spacetelescope/rad/issues/480>`_)
- Update visit, l1, and l2 attribute information (`#481
  <https://github.com/spacetelescope/rad/issues/481>`_)
- Update and add descriptions in the individual image metadata schema.
  Address merge issues created by the L1 and L2 metadata updates. (`#487
  <https://github.com/spacetelescope/rad/issues/487>`_)
- Added alternate WFI aperture names to match both the SIAF and legacy names.
  (`#498 <https://github.com/spacetelescope/rad/issues/498>`_)
- Added CRDS and reference steps required lists. (`#506
  <https://github.com/spacetelescope/rad/issues/506>`_)
- Updated the ePSF schema. (`#507
  <https://github.com/spacetelescope/rad/issues/507>`_)
- pin `asdf<4.0` (`#509 <https://github.com/spacetelescope/rad/issues/509>`_)


Deprecations and Removals
-------------------------

- Remove units from rad schema. (`#485
  <https://github.com/spacetelescope/rad/issues/485>`_)


0.21.0 (2024-08-06)
-------------------

- Added sky background schema. [#432]

0.20.0 (2024-05-15)
-------------------

- This PR removes reference file and guidewindow db tables from cal_step schemas. [#420]

- Separated TVAC and FPS schemas into their own suite of files. [#414]

- Fixed the TVAC & FPS archive catalog destinations. [#424]

- Added statistics schemas to both FPS and TVAC. [#423]

- Removed filepath_level_pnt5 from TVAC/FPS database. [#422]

- Removed the db entries for filename_l1a and filename_pnt5 in TVAC and FPS schemas. [#421]


0.19.4 (2024-05-08)
-------------------

- Updated RTD with documentation for new data products. [#419]


0.19.3 (2024-04-25)
-------------------

- Duplicated the keywords from groundtest to tvac_groundtest. [#409]


0.19.2 (2024-04-17)
-------------------

- Duplicated the keywords from base_exposure to exposure and similarly for base_guidestar and guidestar. [#406]

0.19.1 (2024-04-04)
-------------------

- Add new schemas to documentation. [#386]

- Convert tag keywords to wildcards for external tags. [#370]

- Added ``exact_datatype`` arguments to prevent ASDF from casting array
  datatypes during save. [#369]

- Add documentation on how to create a new schema. [#375]

- Add ``FPS`` and ``TVAC`` schemas. [#364]

- Update titles and descriptions to those provided by INS. [#361]

- Updated product table names. [#382]

- Changed image units from e/s to DN/s (and added support for MJy/sr). [#389]

- Add attributes under the ``basic`` schema to ``WfiMosaic.meta``. [#390]

- Split cal_step into L2 and L3 versions. [#397]

- Add Members Keyword to Resample Schema. [#396]

- Create the flux step schema. [#395]

- Create ``outlier_detection`` schema and add bit mask field to both it and ``resample``. [#401]

- Add source_catalog and segmentation_map schemas for Level 2 and Level 3 files. [#393]


0.19.0 (2024-02-09)
-------------------

- Added streamlined Level 3 Mosaic metadata schemas. [#334]

- Remove the unused ``variance-1.0.0`` schema. [#344]

- Add wcs tag to wfi_image and wfi_mosaic schemas. [#351]

0.18.0 (2023-11-06)
-------------------

- Added Slope and Error to Dark reference schema. [#323]

- Removed ``err`` array from dark schema. [#324]

- Expanded origin db string length. [#326]

- Updated minimum python version to 3.9. [#325]

- Added truncated keyword. [#330]

- Added GuideWindow db table to Basic tagged scalars. [#327]

- Added optional dq array. [#328]

- Update required elements for release. [#337]


0.17.1 (2023-08-03)
-------------------

- Added "archive_catalog" field to ref_file. [#303]

- Added a prefix ``s_`` to the archive destination in "cal_step". [#303]

- Require all the new ``cal_step`` steps to be present in the ``cal_step`` schema. [#301]

- Add missing unit enforcements to various schemas. [#300]

0.17.0 (2023-07-27)
-------------------

- Fix invalid uri fragment in rad_schema. [#286]

- Update the steps listed in ``cal_step`` to reflect the currently implemented steps.
  The new additions are ``outlier_detection``, ``refpix``, ``sky_match``, and ``tweak_reg``. [#282]

- Update the steps listed in ``cal_step`` with the ``resample`` step. [#295]

- Fix the URIs for ``inverselinearity`` and add consistency checks for names/uris. [#296]

- Add ``archive_meta`` keyword for the MAST archive to encode information specific
  to the archive's needs. [#279]

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

- Changed SDF "origin" in ephemeris-1.0.0.yaml to use definitive/predicted ephemeris. [#207]

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
