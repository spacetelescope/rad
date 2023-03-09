.. _archive:

Archive Functions
=================

In order to use the archive functions, you must install ``rad`` with the optional
``archive`` dependency. This can be done by running ``pip install rad[archive]`` or
``pip install -e ".[archive]"`` (for editable installs).

Destinations
------------

The output of the method ``rad.archive.destinations`` is a listing of all the
``archive_catalog.destination`` end points listed in the ``rad`` schemas.

.. code-block:: python

    >>> from rad import archive
    >>> archive.destinations()  # doctest: +ELLIPSIS
    ['ScienceCommon.aperture_name', 'ScienceCommon.calibration_software_version', ...]
