.. _creating:

Creating a New Schema
=====================

This is intended to be a quick guide to how to create a new schema in RAD. It is
not intended to be a comprehensive guide, but rather a quick guide that
highlights all the important considerations for RAD schema creation.

Before you begin
----------------

Before you start writing your schema, you should have a clear idea of what data
you wish to store in a Roman file and how you want to organize it. Remember that
RAD supports a hierarchical data model, so you can topically organize your data
under headings and subheadings (or even deeper) as you see fit. In particular,
you should have a clear idea of the following:

    #. The name of the schema you wish to use. Be sure to determine the version
       number of the schema. Typically, if the schema is new, it will be
       ``1.0.0``. So the schema name will be ``<name>-1.0.0.yaml``.

    #. Where in RAD you wish to locate your schema. For example if it is for a
       reference file then it should be located in the ``reference_files``
       directory.

    #. The keywords for your fields and their hierarchical organization.

    #. The data types of all the fields that you wish to store. In particular,
       you need to pay attention to the following:

        * Which fields will be primitive data types like ``int``, ``float``,
          ``str``, or ``bool``. In JSON-schema these will be ``integer``,
          ``number``, ``string``, and ``boolean`` respectively.

        * Which fields will require using an ASDF tag to reference another
          schema corresponding to a non-primitive type. In particular, you need
          to know if that tag is a RAD tag or an external ASDF tag.

    #. Which fields will be required and which will be optional.

    #. What order you want your fields to appear in the ASDF file.

.. note::

    An ASDF tag will be defined within the tag manifest for the schema package,
    which adds ASDF support for the type you wish to use. For example,
    :ref:`manifests/datamodels-1.0` is the tag manifest for the RAD package.
    The tag itself will be the value under ``tag_uri`` and the schema it
    references will be under ``schema_uri``.


.. note::

    All external tags should end with a ``-<major version>.*`` version
    specifier. Rather than a specific version number, this is a wildcard that
    will match any version of that tag. This is to ensure that the schema is not
    tied to a specific version of the external tag.


Create the Schema Boilerplate
-----------------------------

After you have created your new schema file in the location under the name you
have chosen, you should add the following to your blank file

.. code:: yaml

    YAML 1.1
    ---
    $schema: asdf://stsci.edu/datamodels/roman/schemas/rad_schema-1.0.0
    id: asdf://stsci.edu/datamodels/roman/schemas/<file name of schema>  # No .yaml

    title: <Title of the schema>
    description: |
        <A long description of the schema>

    ...


The ``YAML 1.1`` needs to be on the very first line of the file, while the
``...`` needs to be on the second to last line of the file with the final line
being completely empty.


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

* Multiple Possibilities.
    If a field can take on multiple different types, you can use the ``oneOf``
    combiner to specify the different possibilities. For example:

    .. code:: yaml

        oneOf:
          - type: <type1>
          - type: <type2>
          - type: <type3>

    where further metadata can be added to each of the types as needed.

    .. note::

        Sometimes you might want to have a field which is required, but which
        may not take on any values at all. In this case you can use the
        ``null`` type as one of the possibilities in the ``oneOf`` combiner.


Add Required and Ordering Information
--------------------------------------

After you have added all of your fields, you will want to add the required
and ordering information. This is done at the same indentation level as the
``properties`` keyword, at the end of the right before the ``...``. This looks
like the following:

.. code:: yaml

    required: [<required field 1>, <required field 2>, <required field 3>]
    order: [<field 1>, <field 2>, <field 3>]


Tag Your Schema
---------------

In most cases, you will want to tag your schema with the RAD tag manifest. This
performs several useful tasks:

    #. It makes the object your schema represents independently (from any other
       RAD objects) serializable and de-serializable to ASDF.

    #. It flags the object within the human-readable header of the ASDF file
       using the tag. This is useful for quickly identifying the type of object
       and differentiating otherwise identical objects.

    #. It allows ASDF to easily search back into the schema from a data file to
       read out metadata about the object contained within the schema.

    #. Allows for the use of "tag", ``tag:`` references as opposed to
       JSON-schema references. This type of reference adds additional data
       validation.

To tag your schema, you will need to add an entry to the RAD tag manifest,
:ref:`manifests/datamodels-1.0`. To do this you will need to add the following
after the ``tags:`` keyword in the manifest file (before the end ``...``):

.. code:: yaml

    - tag_uri: <tag_uri>
      schema_uri: <schema_uri>
      title: <Title of the schema>
      description: |-
        <A long description of the schema>

Where ``<tag_uri>`` is the tag you wish to use and ``<schema_uri>`` matches the
``id`` in your schema file. If a schema is tagged, it should have

.. code:: yaml

    flowStyle: block

Added on the line before the ``...`` in the schema file. This is to ensure that
ASDF will write the human-readable in the file in a human-readable format.

.. warning::

    While not explicitly necessary, RAD recommends that your formulate your
    file name, ``schema_uri``, and ``tag_uri`` following standard convention.
    This is to avoid confusion and to make it easier to find the schema and tag
    and determine the associations between them. The convention is to use:

    #. Ignoring the file handle (which should always be ``.yaml``), the file
       name should be the path to the schema file with root being the
       ``rad/resources`` directory. E.g. ``schemas/reference_files/dark-1.0.0``
       or ``schemas/aperture-1.0.0``.

    #. The "version" of the schema should be the suffix of the file name having
       the form ``-<major>.<minor>.<patch>``. E.g. ``-1.0.0``.

    #. The ``schema_uri`` should be the same as the file name file name described
       above with the RAD URI prefix ``asdf://stsci.edu/datamodels/roman/``.
       E.g.
       ``asdf://stsci.edu/datamodels/roman/schemas/reference_files/dark-1.0.0``
       or
       ``asdf://stsci.edu/datamodels/roman/schemas/aperture-1.0.0``.

    #. The ``tag_uri`` should match the ``schema_uri`` with the ``schemas``
       replaced with ``tags``. E.g.
       ``asdf://stsci.edu/datamodels/roman/tags/reference_files/dark-1.0.0``
       or
       ``asdf://stsci.edu/datamodels/roman/tags/aperture-1.0.0``.

.. note::

    There are some cases where you might not want to tag a schema. These are
    generally, when the schema is not intended to be used as a standalone
    object. This can be the case when the schema is intended to be extended by
    another schema, see :ref:`pseudo-inheritance` for more information.


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

Tagged List
***********

Currently, there is only one case where the RAD schemas tag a list, the
:ref:`schemas/cal_logs-1.0.0` schema. Just as in this case, the top level of the
schema will be:

.. code:: yaml

    type: array
    items:
      - <sub-schema(s) describing items>

The ``items`` simply contains a bulleted list of the sub-schemas that describe
possibilities for the items in the list.

Tagged Scalar
*************

The other case is when one needs to tag a scalar type. This is mostly to help
with the ASDF metadata searching. All such schemas need to be inside the
``schemas/tagged_scalars`` directory so that the correct Python data nodes can
be automatically constructed for the data models.

In this case, you add the following after the schema description if the type of
the scalar is a primitive type:

.. code:: yaml

    type: <primitive type>

However, if the scalar is planned to be represented by a non-primitive type such
as a time or some other special type, then you will need to use a ``$ref`` back
to the ``schema_uri`` not ``tag_uri`` for the schema that describes this type.
It is important to use the ``schema_uri`` because referencing a ``tag_uri`` will
cause ASDF validation to not only check that the data is valid for the schema,
but also that the type being used is exactly one of the types associated with
that tag (sub-classes will fail validation in this case). Since the ASDF
extension supporting that type is outside of RAD's control, it is not possible
for it to even know about RAD's sub-classes and so this will not work. Hence,
a ``$ref`` to the ``schema_uri`` is necessary. This needs to be added after the
description of the schema using:

.. code:: yaml

    allOf:
      - $ref: <schema_uri>

The ``allOf`` combiner is necessary because of quirks in how JSON-schema
actually functions; meaning that for ASDF 3.0+ to correctly handle the schema
without issues, the ``allOf`` combiner is necessary, see
`PR 222 <https://github.com/spacetelescope/rad/pull/222>`_ for more details.

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
    archive_meta: None

The ``datamodel_name`` field is simply so that we can test that a
`~roman_datamodels.datamodels.DataModel` exists for each "top-level" schema and
that each of these schemas maps to exactly one
`~roman_datamodels.datamodels.DataModel`. Moreover, it documents which
`~roman_datamodels.datamodels.DataModel` maps to which schema as this is not
always completely clear due to the fact that the schema names and
`~roman_datamodels.datamodels.DataModel` names do not follow a strict naming
pattern.

The ``archive_meta`` field is a placeholder for future use. It is intended to
allow the archive to add additional metadata about specific Roman ASDF files,
which do not fit neatly into the metadata structures it uses for describing
the fields of in the schemas, see :ref:`external-metadata` for more details.

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
