.. _versioning:

Schema Versioning
=================

As RAD contains ASDF compatible schemas the versioning strategy will
mostly follow that of other ASDF extensions where:

- schema modifications trigger creation of a new schema version
- the old schema is kept unmodified
- a new tag version is created for the new schema version
- the new tag version triggers a new manifest version

This allows files created with the old tag to be validated (against
the old schema) and opened.

Non-versioned changes
=====================

The RAD schemas contain archive database destination and other
non-ASDF information including schema keywords:

- archive_catalog
- origin
- sdf

Changes to content stored under these keys will not be trigger a new
schema version. Please consult the newest schema version for the most
accurate values for these keywords.


Manifest Versioning
===================

New manifests will often be created by:

- copying the newest manifest version
- incrementing the manifest version number, id and extension uri version
- updating the tag definition for that tag/schema change that triggered
  the manifest version

One exception is if the newest manifest version has not yet been
released. In this case the tag definition in the existing (unreleased)
manifest can be modified and no manifest version increase is needed.


Old version support
===================

RAD is not yet stable. Efforts will be made to retain support for
opening old files. As noted above supporting old versions of files
will require keeping several manifest versions and all old schemas.
As development continues it may be advantageous to drop support
for some old (pre-flight) versions.


Dropping support for pre-flight versions
========================================

If it is decided that support for an old (pre-flight) version
of a schema will be dropped the following steps will be taken:

- removal of the unsupported schema versions
- removal of the unsupported tag versions
- removal of all manifest versions that contain the dropped schema or tag versions

By following these steps, the unsupported old files can still
be opened with ``asdf.open``. When an unsupported file is opened
asdf will encounter one or more of the unsupported (and now unknown)
tags and issue ``AsdfConversionWarning`` describing that the tagged objects
are being returned as "raw data structures" (typically a
dictionary-like ``TaggedDict``). This will allow users to continue
to access the contents of the file and possibly migrate the old file
contents to a new supported tag/structure.
