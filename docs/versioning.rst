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
- sdf
- title
- description
- propertyOrder

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


Creating a New Version
======================

The RAD resources (both schemas and manifests) are located in the ``src/rad/resources``
directory for the purposes of the ASDF extension. Meaning that all resources must be
located in this directory or have a symlink from this directory to the actual location
for the resources. This directory is organized into two subdirectories:

1. ``schemas`` - contains the ASDF schemas or symlinks to the schemas

2. ``manifests`` - contains the ASDF manifests or symlinks to the manifests

While ``src/rad/resources`` is where the resources are located for the ASDF extension,
not all of the resources are directly located in this directory. Instead, the *latest*
version of any schema is instead located within the ``latest`` directory in the top
level of the RAD repository, while the *latest* version of any manifest is located within
the ``latest/manifests`` directory. These files are linked to from the ``src/rad/resources``
directory. Note that the path relative to the ``latest`` directory for schemas (``latest/manifests``
for manifests) is the same as the path to the respective symlink relative to the ``src/rad/resources/schemas`` for schemas
(``src/rad/resources/manifests`` for manifests).

The naming conventions for resources follows two different patterns:

1. The files within the ``src/rad/resources`` directory are named with a version suffix
   (``-a.b.c.yaml``) with the latest (highest semantic) version number actually being
   a symlink targeting a file within ``latest``.

2. The files within the ``latest`` directory end only with the normal ``.yaml`` suffix
   with no version number included. These files are then the target of the version indicated
   by the symlink file name corresponding to the version number indicated by the URI (``id:`` keyword)
   within the file itself.

.. note::

   These file naming conventions and the underlying directory structure exist to facilitate
   a straightforward review process in git for reviewing changes to resources whenever
   a version number is updated.

   This allows for the git diff to directly show the changes to the resource within
   ``latest`` rather than having the new version of the file appear as a brand new file
   in the git diff. This is facilitated by the fact that the name of the ``latest`` file
   never changes, only its contents, while the files in the ``src/rad/resources`` end
   up with being brand new files or symlink name updates.

Workflow for Updating a Resource Version
----------------------------------------

.. note::

   We strongly recommend using the :ref:`RAD Helper Tool's <rad_helper>` Bump function
   to update the version of a given resource. In addition, the tool will also tell you
   if you need to bump the version of a resource when you attempt to edit it.

   The tool will take care of updating all the references to the new version number within
   the ``latest``.

To update the version of a given resource the following steps should be taken:

1. Determine the new version number to be used for the resource following the
   [Semantic Versioning](https://semver.org/) guidelines.

2. Update the version number in the symlink name in the ``src/rad/resources`` directory
   from the current version number to the new selected (in step 1) version number.

   .. note::

      The symlink's target should **never** be modified as the new target of the
      symlink will still be the resource's file with in the ``latest`` directory,
      which will later be modified starting in step 4 to reflect the new version
      number.

3. Copy the given file in the ``latest`` directory (as is) to the appropriate
   location in the ``src/rad/resources`` modifying the name of the file to include
   the current version number (e.g. ``-a.b.c.yaml``).

   .. note::

      This should be done **before** making any modifications to the contents of
      any resource file. This is important as the goal is to preserve the exact
      contents of the resource as it was under the current version number.

4. In ``latest`` update the version number for the URI (``id:`` keyword) to
   match the new version number selected in step 1 within the file itself.

   .. note::

      In addition to the ``id:`` keyword for manifests (``datamodels.yaml``), the
      ``extension_uri:`` keyword should also be updated to match the new version
      number.

5. Throughout the ``latest`` directory update the version number for all related
   URIs (``tag`` and ``$ref``) to match the version number selected in step 1.

   .. note::

      This may cause a cascading effect where the version number for other files
      in the ``latest`` directory need to be updated as well. This may necessitate
      following the version update process for these files as well.

6. Make the updates to the file in ``latest`` with the changes that necessitated
   the new version.

.. note::

   The RAD unit tests have been designed so that the ``tests/test_versioning.py``
   tests will fail if a file is modified without updating the version number whenever
   a version number update would be required.

   Therefore, it is suggested that one runs the unit tests after making modifications
   to a given resource **prior** to committing those changes. If a test failure occurs
   then simply stash the changes and then follow the version update process above.
   The resource changes can then be unstashed and committed as the ``latest`` version
   has now been updated properly.

.. note::

   The unit tests in ``tests/test_latest.py`` are designed to ensure that if a version
   number is updated all the necessitated changes to the resources are made. This includes:

   - Checking that all relevant URIs in ``latest`` have been updated to reflect the new
     version number.
   - Checking the integrity of the symlinks in ``src/rad/resources`` to ensure that they are
     pointing to the correct file in ``latest``.
   - Checking that the old version of the file has not gone missing (in combination with the
     ``test_versioning.py`` tests).

.. note::

   It is important to run the unitests regularly while making changes to the resources
   to ensure that the versioning process has been followed correctly, as they will
   guide you through the process of when and how to update resource version numbers.


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
