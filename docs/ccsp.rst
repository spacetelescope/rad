.. _ccsp_schemas:

CCSP Schemas
============

"Community Contributed Science Product" (CCSP) schemas are located in the
`resources/schemas/CCSP` directory of this package.

.. _ccsp-creating:

Creating a New CCSP Schema
--------------------------

Please start a conversation with MAST and the RAD maintainers by creating
an `issue <https://github.com/spacetelescope/rad/issues/new>`_. Any
details that you can provide are helpful. We are happy to help guide
you through the process and fill in any gaps in the following documentation.
Opening the issue allows us to know that there is interest in a contribution
to RAD and help us to plan development and releases.

Please review the :ref:`creating` documentation to understand the process
for creating new SOC schemas. The process for CCSP schemas is very similar
with a few differences noted here.

.. _ccsp-external_metadata:

External Metadata
^^^^^^^^^^^^^^^^^

The archival process for CCSP files differs from the process used for SOC
products. As a result, CCSP schemas should not add the keywords
described at :ref:`external-metadata`

- ``sdf``
- ``archive_catalog``
- ``archive_meta``

Instead CCSP schemas must contain a reference to either:

.. asdf-autoschemas::

   CCSP/ccsp_minimal-1.0.0
   CCSP/ccsp_custom_product-1.0.0

Which schema to use will depend on the details of the product as described
below. In both cases these schemas will require the addition of a new
ASDF subtree ``meta.ccsp`` which will contain information necessary
for accurate archival of CCSP files.

Custom Products
"""""""""""""""

Products that don't closely match a SOC product should have schemas
that reference ``ccsp_custom_product`` as in the following example.

.. code:: yaml

    YAML 1.1
    ---
    $schema: asdf://stsci.edu/datamodels/roman/schemas/rad_schema-1.0.0
    id: asdf://stsci.edu/datamodels/roman/schemas/CCSP/EXAMPLE/example_custom_product-1.0.0

    title: Example CCSP custom product

    datamodel_name: ExampleCustomProductModel

    type: object
    properties:
      meta:
        allOf:
          - $ref: asdf://stsci.edu/datamodels/roman/schemas/CCSP/ccsp_custom_product-1.0.0
    required: [meta]
    flowStyle: block

This will check that the produced file contains:

- a ``meta`` key
- the contents of ``meta`` conform to ``ccsp_custom_product``

The schema should be expanded to include descriptions and constraints on the
data and metadata that will be added to the product. Let's assume that the
product contains:

- 2 arrays, ``data`` (required) and ``err`` (optional)
- a WCS (that applies to both arrays) stored at ``meta.wcs``
- metadata about a widget stored at ``meta.widget`` with nested values ``state`` and ``count``

The following shows one way to expand the above schema to include information
about those additional product contents.

.. code:: yaml

    type: object
    properties:
      meta:
        allOf:
          - $ref: asdf://stsci.edu/datamodels/roman/schemas/CCSP/ccsp_custom_product-1.0.0
          - type: object
            properties:
              wcs:
                title: World Coordinate System (WCS)
                tag: tag:stsci.edu:gwcs/wcs-*
              widget:
                title: Widget metadata
                properties:
                  state:
                    title: Widget state
                    type: string
                  count:
                    title: Widget count
                    type: integer
                required: [state, count]
            required: [wcs, widget]
      data:
        title: My data
        description: Described here
        tag: tag:stsci.edu:asdf/core/ndarray-1.*
        datatype: float32
        exact_datatype: true
        unit: "DN"
      err:
        title: Optional err
        description: Described here
        tag: tag:stsci.edu:asdf/core/ndarray-1.*
        datatype: float32
        exact_datatype: true
        unit: "DN"
    required: [data, meta]
    flowStyle: block

During interaction with SOC and RAD maintainers you may be asked to add requirements
for some optional contents in ``ccsp_custom_product``. For our example the WCS can
be used to generate a single reference RA and DEC for this file and the optional
``target_coordinates`` sections of ``ccsp_custom_product`` can be made required
by modifying the schema to include:

.. code:: yaml

    properties:
      meta:
        allOf:
          - $ref: asdf://stsci.edu/datamodels/roman/schemas/CCSP/ccsp_custom_product-1.0.0
          - required: [target_coordinates]


Extending SOC Products
""""""""""""""""""""""

If the contributed product largely (or entirely) matches a SOC product
it may make sense, through conversation with SOC,
to extend the corresponding SOC schema. This has some benefits and
some downsides. Extending a SOC schema enforces consistentcy for
the CCSP and SOC products but also requires that the CCSP product follow
any changes made to SOC schemas.

Let's consider an example for a community developed coadd (Level 3) product with
metadata that conforms to the SOC ``wfi_mosaic`` schema. The CCSP schema could contain:

.. code:: yaml

    YAML 1.1
    ---
    $schema: asdf://stsci.edu/datamodels/roman/schemas/rad_schema-1.0.0
    id: asdf://stsci.edu/datamodels/roman/schemas/CCSP/EXAMPLE/example_derived_mosaic-1.0.0

    title: Example CCSP mosaic derived product

    datamodel_name: ExampleDerivedMosaicModel

    allOf:
      - $ref: asdf://stsci.edu/datamodels/roman/schemas/wfi_mosaic-1.4.0
      - type: object
        properties:
          meta:
            allOf:
              - $ref: asdf://stsci.edu/datamodels/roman/schemas/CCSP/ccsp_minimal-1.0.0

    flowStyle: block

This schema will check that the file conforms to the ``wfi_mosaic`` schema
and contains the metadata required by ``ccsp_minimal``. Additional schema
contents should be added to document and constrain any file contents
added that aren't described in the linked schemas (see :ref:`creating` for more details).
