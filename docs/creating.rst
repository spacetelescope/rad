.. _creating:

Creating a New Schema
=====================

This is intended to be a quick guide to how to create a new schema in RAD. It is
not intended to be a comprehensive guide, but rather a quick guide that
highlights all the important considerations for RAD schema creation.


.. note::
    We strongly recommend that you use the :ref:`RAD Helper Tool <rad_helper>`
    to help you set up your schemas. This will take care of things such as creating
    the necessary symbolic links and checking that your selected URIs follow outward
    conventions. It will also help you with bumping the version of your schema
    when you make changes to it.

Before you begin
----------------

Before you start writing your schema, you should have a clear idea of what data
you wish to store in a Roman file and how you want to organize it. Remember that
RAD supports a hierarchical data model, so you can topically organize your data
under headings and subheadings (or even deeper) as you see fit. In particular,
you should have a clear idea of the following:

    #. The base name of the schema you which to create. This should be a short
       descriptive name that should only include lower case letters and underscores.
       No spaces or hyphens should be used in the name or path. For example, ``dark``, ``aperture``,
       ``wcsinfo``, ``cal_logs``, etc. Typically, this name will form the base name
       that the object you are describing will be called in Python. For example,
       ``aperture`` may correspond to an ``Aperture`` object in Python. This is not
       always the case, but it is a good rule of thumb. From now on we will use
       ``<name>`` to refer to this base name.

    #. Now we need to determine the version number of the schema.  Typically, if
       the schema is new, it will be ``1.0.0``. This means that your schema will
       often be referenced with ``<name>-<version>``. The version number should
       follow standard semantic versioning, see `semver.org <https://semver.org/>`_
       for more details.

       .. note::
          The URI for your schema will include this version number, so it will
          look like ``asdf://stsci.edu/datamodels/roman/schemas/<path>/<name>-<version>``.
          The version number will not typically be included in the file name itself,
          but will appear in the symbolic link to the schema file that you will need
          to create.

    #. Next you will need to decided where in RAD to locate your schema. Look inside
       the ``latest`` directory in the top of your working copy of RAD to see the
       organization of the existing schemas.

       .. note::
        In the end you will have something like: ``latest/<path/to/your/schema>``,
        where ``<path/to/your/schema>`` is the path to the directory inside ``latest``
        that your schema will be located. This means you now have the URI
        fragment ``<path/to/your/schema>/<name>-<version>``, which can be formed
        into the full RAD schema URI by prefixing it with
        ``asdf://stsci.edu/datamodels/roman/schemas/``. E.G.

        .. code::yaml

            asdf://stsci.edu/datamodels/roman/schemas/<path/to/your/schema>/<name>-<version>

       * If your schema is not for the SOC then it should be located within a
         directory that corresponds to the origin of the data. For example, the
         IPAC/SSC schemas are located in ``latest/SSC``. Items located within
         those directories should follow the organisational structure of the
         schemas already in that directory. These directory names must be in ALL CAPS.

       * If your schema is for the SOC, then it will follow a different convention.

          #. The only schemas allowed in ``latest`` are those that correspond to
             the outputs of the Romancal pipeline. For example ``latest/wfi_image.yaml``,
             is the output of the exposure level Romancal Pipeline.

          #. If your schema is for a reference file, then it should be located
             in ``latest/reference_files/``. For example, ``latest/reference_files/dark.yaml``,
             ``latest/reference_files/flat.yaml``, etc. All represent reference
             files that are made available via CRDS.

          #. If your schema describes some data that is part of the ``meta`` attribute
             of a Romancal pipeline output, then it should be located in
             ``latest/meta/``. For example, ``latest/meta/exposure.yaml`` is the
             schema for the ``meta.exposure`` attribute of Romancal pipeline outputs.

          #. If your schema provides some enumerated object which is used in multiple
             places, then it should be located in ``latest/enums/``. For example,
             ``latest/enums/wfi_detector.yaml`` is the schema which lists all the
             possible WFI detectors that can be used in Romancal pipeline outputs.

          #. If your schema works to describe the columns of a table, then it should be
             located in ``latest/tables/``. For example, ``latest/tables/prompt_catalog_table.yaml``
             describes the columns for the prompt source catalog table that is created by
             the Romancal pipeline.

          #. If your schema does not fit into one of the above categories, then it should
             be discussed with the RAD maintainers to determine the best location.

    #. The keywords for your fields and their hierarchical organization.

       * *Keywords* are the key in the key-value pairs for information. For example,
         the keyword may refer to a specific value like ``ra_ref`` for the right ascension
         of the reference position for the WCS. Or it may refer to an entire group
         of related information like ``wcsinfo``, which contains keywords that point at
         information about the WCS.

       * *Hierarchical organization* refers to how you organize your keywords. In
         the WCS example for keywords, ``ra_ref`` is a keyword that is organized
         under the ``wcsinfo`` keyword. If you were using the Roman Datamodels objects
         you might reference the ``ra_ref`` data via ``model.meta.wcsinfo.ra_ref``.

       .. note::
            Unlike FITS headers, RAD and ASDF place no restrictions on the length
            or composition of the keywords. We do ask that you use keywords that will
            not conflict with the reserved words for the Python programming language.
            Simply to avoid confusion when developing code that interacts with the
            data.

            This means that we strongly recommend that you use descriptive keywords
            that are easy to understand. For example, ``start_time`` is a much
            better keyword than ``st_tm``. While ``st_tm`` may save a few characters
            it is not immediately clear what it means.

            We also recommend that you nest your keywords in a logical manner. For example,
            if you find your self doing ``thing_keyword1``, ``thing_keyword2``,
            ``thing_keyword3``, etc. then you should consider creating a ``thing``
            keyword and nesting ``keyword1``, ``keyword2``, ``keyword3`` under
            it. This will make it much easier to find and understand the data.

    #. The data types of all the fields that you wish to store. In particular,
       you need to pay attention to the following:

        * Which fields will be primitive data types like ``int``, ``float``,
          ``str``, or ``bool``. In JSON-schema these will be ``integer``,
          ``number``, ``string``, and ``boolean`` respectively.

        * Which fields will require using an ASDF tag to reference another
          schema corresponding to a non-primitive type.

          .. note::
            We currently do not allow internal tag references within RAD,
            meaning that all the structures you are creating will essentially act
            as nested dictionaries/mappings.  The RDM library can give life to
            these as something that looks like a Python object.

          .. note::
            We currently only allow the use of the following external tags:

                * ``tag:stsci.edu:asdf/core/ndarray-1.*`` for numpy arrays.
                * ``tag:stsci.edu:asdf/time/time-1.*`` for astropy time objects.
                * ``tag:astropy.org:astropy/table/table-1.*`` for astropy tables.
                * ``tag:stsci.edu:gwcs/wcs-*`` for gwcs WCS objects.

            We also allow the following tags, but their use should be limited as
            there are code performance implications:

                * ``tag:stsci.edu:asdf/unit/quantity-1.*"`` for astropy quantities.
                * ``tag:stsci.edu:asdf/unit/unit-1.*`` for VO standard units.
                * ``tag:astropy.org:astropy/units/unit-1.*`` for units that astropy
                  defines that are not VO standard units.

            If you wish to use other external tags, please discuss this with the RAD
            maintainers. This limited subset of tags is to make it easier for us to
            provide support for opening and using the RAD data in languages other than
            Python. The more external tags we allow, the more burden it places on the
            ASDF maintainers to support these tags in other languages.

    #. Which keywords will be required and which will be optional. When you create
       your schema you will need to specify at each level in the hierarchy which
       keywords will be required. Any keywords that are not listed as required
       will be considered optional and will require the user to check that they exist
       prior to using them.

.. note::

    We only allow the tagging of schemas that describe the top-level objects
    (datamodels) that RAD outlines. Each of these *tags* is an *ASDF tag* that
    you will need to define in the RAD manifest. This file is ``latest/manifests/datamodels.yaml``. See :ref:`tag-your-schema` for more
    information

.. note::

    All external tags should end with a ``-<major version>.*`` version
    specifier. Rather than a specific version number, this is a wildcard that
    will match any version of that tag. This is to ensure that the schema is not
    tied to a specific version of the external tag.


Create the Schema Boilerplate
-----------------------------

We suggest that you use the :ref:`RAD Helper Tool <rad_helper>` to help you create
a new schema. This can be done via clicking the ``New`` button once the helper has
been started. It will require you to enter the following information:

#. The title of the schema.
#. (Optional) A short description of the schema.
#. Selecting that this is a schema for RAD.
#. Entering the path, name and version that you have
   selected for your schema: ``<path/to/schema>/<name>-<version>``.

This will create a new schema file at ``latest/<path/to/schema>/<name>.yaml``
with the contents:

.. code:: yaml

    YAML 1.1
    ---
    $schema: asdf://stsci.edu/datamodels/roman/schemas/rad_schema-1.0.0
    id: asdf://stsci.edu/datamodels/roman/schemas/<path/to/schema>/<name>-<version>  # Note the lack of .yaml

    title: <Title of the schema>
    description: |
        <A long description of the schema>
    # description portion will be missing if not proveded by the tool.


If you do not wish to use the RAD Helper Tool, can create a file at ``latest/<path/to/schema>/<name>.yaml``
with the boiler plate above. You will need to create an additional symbolic link from
``src/rad/resources/schemas/<path/to/schema>/<name>-<version>.yaml`` to this file. Without this
link, RAD will not be able to find your schema.

.. note::
    The ``YAML 1.1`` needs to be the very first line of the file, as this defines
    the start of the YAML file and its version.

Add Your Fields
---------------

Now we will populate your schema with the fields you wish to use. In almost all
cases you will want to use an ``object`` type for your top level of the schema,
for other cases see :ref:`alternate-fields`.  In this case you add the following
after your ``description`` in the boilerplate:

.. code:: yaml

    type: object
    properties:
        <first keyword>:
            title: <Title of the field>
            description: |
                <A long description of the field, can be multiline>

You will repeat this step for each of the top-level fields you wish to add.


Populate a Field's Sub-Schema
*****************************

After the field's ``description`` at the same indentation level as the
``description`` keyword, you will start to add the sub-schema for the field.
There are several different possibilities at this point:

* Primitive type.
    Things like ``int``, ``float``, ``str``, or ``bool``. In this case you will
    add the following:

    .. code:: yaml

        type: <type>

.. note::

    The ``<type>`` for a Python ``float`` is ``number`` and the ``<type>`` for a
    Python ``bool`` is ``boolean``. While the ``<type>`` for a Python ``int`` is
    ``integer`` and the ``<type>`` for a Python ``str`` is ``string``.

* Tagged type.
    Things that are referenced via an ASDF tag. In this case you add the
    following:

    .. code:: yaml

        tag: <tag_uri>

    If you want to narrow the tag further than its general schema you add after
    the tag (at the same indentation level):

    .. code:: yaml

        properties:
          <narrowed key from tag>: <schema information to narrow the key>

    .. note::

        If you say want to narrow an ``ndarray`` to a specific datatype and
        number of dimensions you would add the following:

        .. code:: yaml

            properties:
              datatype: <dtype of the ndarray>
              exact_datatype: true
              ndim: <number of dimensions of the ndarray>

        RAD requires that both ``datatype`` and ``exact_datatype: true`` be
        defined for ``ndarray`` tags. The ``exact_datatype: true`` prevents
        ASDF from attempting to cast the datatype to the one in the schema,
        meaning that if the dtype is not a perfect match to the schema a
        validation error will be raised.

* Dictionary-like type.
    These are things that nest further fields within them. In this case you add:

    .. code:: yaml

        type: object
        properties:
          <first keyword>:
            title: <Title of the field>
              description: |
                <A long description of the field>

    And then repeat the process of adding the sub-schema for each of the fields.

* List-like type.
    These are lists of the same type of item. These are called an ``array`` in
    the schema, meaning that you add the following:

    .. code:: yaml

        type: array
        items:
          type: <type>

    If further narrowing is required you can narrow them just like you would a
    tag. If you create an object or another array you likewise add the metadata
    in the same way as if it were a top-level field only indented appropriately.


Special Field Considerations
****************************

There are a few special considerations that you might need to take into account
when creating your schema:

* Enum.
    If you have a field that can only take on a specific set of values, you can
    use the ``enum`` keyword to specify the possible values. For example:

    .. code:: yaml

        enum: [<value1>, <value2>, <value3>]

    .. note::
       ``enum`` only works for very primitive types like ``string``, ``integer``,
        and ``number``. You should specify the ``type`` of the field when using ``enum``
        as it gets ambiguous about if something like ``1`` is a ``string``, an ``integer``, or a ``number``.

* Multiple Possibilities.
    If a field can take on multiple different types, you can use the ``anyOf``
    combiner to specify the different possibilities. For example:

    .. code:: yaml

        anyOf:
          - type: <type1>
          - type: <type2>
          - type: <type3>

    where further metadata can be added to each of the types as needed.

    .. note::

        Sometimes you might want to have a field which is required, but which
        may not take on any values at all. In this case you can use the
        ``null`` type as one of the possibilities in the ``anyOf`` combiner.


Add Required and Ordering Information
--------------------------------------

After you have added all of your fields, you will want to add the required
and ordering information. This is done at the same indentation level as the
``properties`` keyword.

.. code:: yaml

    required: [<required field 1>, <required field 2>, <required field 3>]
    propertyOrder: [<field 1>, <field 2>, <field 3>]

.. warning::
    The ``propertyOrder`` can only be included in schemas that are tagged. using
    it outside of a tagged context will cause ASDF to fail to validate the schema, even if it might otherwise be valid.

.. _tag-your-schema:

Tag Your Schema
---------------

.. warning::
    You should tag only your top-level schema, the one that describes an entire product.

We suggest that when using the :ref:`RAD Helper Tool <rad_helper>` to create your schema, you
also use it to tag your schema. This can be done via selecting the ``tag`` option.

.. note::
    If you wish to tag your schema manually, you will need to add an entry to the RAD tag
    manifest, in ``latest/manifests/datamodels.yaml``.  To do this you will need to add
    the following after the ``tags:`` keyword in the manifest file:

    .. code:: yaml

        - tag_uri: <tag_uri>
          schema_uri: <schema_uri>
          title: <Title of the schema>
          description: |-
              <A long description of the schema>

    Where ``<tag_uri>`` is the tag you wish to use and ``<schema_uri>`` matches the
    ``id`` in your schema file. If a schema is tagged, it should have (the tool will
    automatically do this for you if you use it to create a tagged schema):

    .. code:: yaml

        flowStyle: block

.. warning::

    While not explicitly necessary, RAD recommends that your formulate your
    file name, ``schema_uri``, and ``tag_uri`` following standard convention.
    This is to avoid confusion and to make it easier to find the schema and tag
    and determine the associations between them. The convention is to use:

    #. Start with formulating the file name. It should always be located in the ``latest``
       directory. The version number should not be included as part of the file name
       and it should always end with a ``.yaml`` file extension. E.g. relative to ``latest/``
       ``reference_files/dark.yaml``, ``meta/exposure.yaml``, or ``wfi_image.yaml``.

    #. The "version" of the schema should be the suffix of the file name having
       the form ``-<major>.<minor>.<patch>``. E.g. ``-1.0.0``.

    #. Next formulate the ``schema_uri`` from the file name by dropping the ``.yaml``
       file extension and prefixing the result with the RAD schema URI prefix
       ``asdf://stsci.edu/datamodels/roman/``. Then appending ``-<version>``
       E.g.
       ``asdf://stsci.edu/datamodels/roman/schemas/reference_files/dark-1.0.0``,
       ``asdf://stsci.edu/datamodels/roman/schemas/meta/exposure-1.0.0``,
       or
       ``asdf://stsci.edu/datamodels/roman/schemas/wfi_image-1.0.0``,

    #. The ``tag_uri`` should match the ``schema_uri`` with the ``schemas``
       replaced with ``tags``. E.g.
       ``asdf://stsci.edu/datamodels/roman/tags/reference_files/dark-1.0.0``,
       ``asdf://stsci.edu/datamodels/roman/tags/meta/exposure-1.0.0``, (in reality this is untagged)
       or
       ``asdf://stsci.edu/datamodels/roman/tags/wfi_image-1.0.0``,

    All of these conventions are enforced by the helper tool as it will check that
    you have correctly formulated the ``schema_uri`` and then use these conventions
    to automatically create the ``tag_uri`` and filename/location for you.

.. note::

    In most cases you will not tag a schema. Tags are generally used only when the schema
    is intended to be used as a datamodel. This allows for easy reuse of schemas
    and extending another schema, see :ref:`pseudo-inheritance` for more information.


.. _alternate-fields:

Alternate Ways of Adding Fields
-------------------------------

There are two additional ways that one might formulate the top level of a schema
which do not involve using an ``object`` type (:ref:`pseudo-inheritance` is also
a method but it still involves objects). These are when one needs to tag a
specially defined list (array) data or when one needs tag a scalar type. In both
these cases, the schema is acting to mix metadata into the schema in a way that
can be reused in other schemas rather than to define a standalone object.

Aside from reuse this is done so that ASDF can correctly search and pull
metadata from the underpinning schemas. This is largely due to the difficulty
in having ASDF traverse through multiple layers of ``allOf`` combiners in its
search and find efforts in the schemas. These combiners are largely the results
of :ref:`pseudo-inheritance`. By having a ``tag`` ASDf is able to
bypass the recursive search and jump directly to the schema that is being
referenced.

Testing Schemas
---------------

Once you created a schema, run the tests in the ``rad`` package before proceeding
to write the model.

.. note::
     The schemas need to be committed to the working repository and the ``rad``
     package needs to be installed before running the tests.

Creating a Data Model
---------------------

The `~roman_datamodels.datamodels.DataModel` objects from
:ref:`RDM <roman_datamodels:data-models>` which act as the primary outward
facing Python interface to the data described by the RAD schemas are simply
wrappers around the actual data container objects. As such these
`~roman_datamodels.datamodels.DataModel` objects are not directly defined by
anything in RAD. However, they are closely related to the RAD schemas. As
such, certain additional things are added to some schemas to make this
relationship between `~roman_datamodels.datamodels.DataModel` objects and some
schemas more clear.

First, note that since all the schemas in RAD are hierarchical, there eventually
will exist a "top-level" schema which acts to describe all the data that is
expected to be in a given ASDF file for Roman. Since each ASDF file will
correspond to a specific `~roman_datamodels.datamodels.DataModel` object and
those objects are wrappers around the actual data container objects, that
"top-level" schema effectively describes the data structure of a given
`~roman_datamodels.datamodels.DataModel` object. Hence, this "top-level" schema
should be called out in a way that makes it clear that it is the schema which
fully describes the structure of a `~roman_datamodels.datamodels.DataModel` and
its associated Roman ASDF file.

To do this, right after the description of the schema in the schema file, the
following should be added:

.. code:: yaml

    datamodel_name: <name of the datamodel in Python>
    archive_meta: <archive meta table information>

The ``datamodel_name`` field is simply so that we can test that a
`~roman_datamodels.datamodels.DataModel` exists for each "top-level" schema and
that each of these schemas maps to exactly one
`~roman_datamodels.datamodels.DataModel`. Moreover, it documents which
`~roman_datamodels.datamodels.DataModel` maps to which schema as this is not
always completely clear due to the fact that the schema names and
`~roman_datamodels.datamodels.DataModel` names do not follow a strict naming
pattern.

The ``archive_meta`` field is used by the archive to define some meta table
information. This should only be included if the schema describes a datamodel
which will be archived. The value of this field should be determined by the archive
for you. Start with adding ``archive_meta: None`` and then update it when you
have the correct information from the archive team.

.. _pseudo-inheritance:

Pseudo Inheritance
------------------

When creating schemas, there are cases in which you might want multiple schemas
to share identical structures, but do not want to repeat this information in
multiple places. Since JSON-schema does not support inheritance in the
"classical" sense, we have to employ a workaround. This workaround employs the
JSON-schema ``allOf`` combiner together with the JSON-schema reference keyword,
``$ref``. This results in a schema code block that looks like the following:

.. code:: yaml

    allOf:
      - $ref: <schema_uri>
      - type: object
        properties:
           <additional properties to add to existing schema>

This acts somewhat like inheritance because it requires that the data described
by the schema must satisfy the requirements of the schema being referenced and
the additional new object included in the ``allOf`` combiner.

This method of combining schemas maybe used at the top level of a schema in
order to create a full inheritance-like relationship or it may be used in some
sub-schema to do a similar thing. In any case, this should be the only usage of
the ``$ref`` keyword in the schema file.

.. _external-metadata:

External Metadata
-----------------

In addition to describing the data structure of Roman ASDF files, RAD also acts
to house metadata about how the Roman ASDF files are to be interacted with.
This "external metadata" is not directly related to the structure of the data
structure itself, but rather describes how the data contained within that
structure will be integrated into the archives or how some of that data was
created external to the Romancal pipeline.

Currently, there are two types of external metadata that are supported by RAD:

    #. ``sdf``

    #. ``archive_catalog``

sdf
***

This is the metadata given to fields which are populated by the SDF software
before the data is processed by the Romancal pipeline. This metadata currently
consists of two fields:

    #. ``special_processing``: which is a string that describes the special
       processing that was done to create the data in SDF.

    #. ``source``: which is a string that describes the source of the data used
       by SDF.

Both of these values are typically provided to us by the SDF software teams and
thus should be done in consultation with them. If the SDF software teams have
not indicated the values yet then the fields should be filled with
``VALUE_REQUIRED`` and ``origin: TBA`` respectively.

archive_catalog
***************

This is the metadata given to fields that will be incorporated into the archive
to describe the Roman ASDF file. This metadata consists of two fields:

    #. ``datatype``: which describes the datatype of that will be used by the
       archive's database to store the data contained within the field. This
       maybe things such as if its a string and if so how long or what type of
       number it will be.

    #. ``destination``: This is a list of strings of the form
       ``<table name>.<column name>``, which describe where that data will be
       stored in the archive's database. Typically ``<column name>``, will match
       the keyword of the field in the schema. This is not always the case as
       sometimes multiple fields from different parts of the files may end up
       in the same table, but whose keywords are the same. When this occurs,
       the archive will inform us of what the correct ``<column name>`` should
       be. The ``<table name>`` is the name of the table in the archive's
       database and is typically provided to us by the archive to be recorded in
       the schema.

In both cases, the metadata should be added in consultation with the archive
team. This includes if the field should even be included into the archive.
