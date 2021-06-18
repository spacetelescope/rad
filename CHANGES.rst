0.3.0 (unreleased)
==================

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

- Added Dark schema and updated Flat schema. [#35]

- Added dq schema. [#32]

- Added readnoise, mask, and gain schemas. [#37]

- Added support for ramp fitting schemas. [#36]
  
- Updated aperture, basic, ephemeris, exposure, guidestar, observation, pixelarea, and visit schemas. [#46]  

- Added support for variance object schemas. [#38] 


0.1.0 (unreleased)
==================

- Initial Schemas for Roman Calibration Pipeline and SDP file generation
