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
to RAD, and helps us to plan development and releases.

Please review the :ref:`creating` documentation to understand the process
for creating new SOC schemas. The process for CCSP schemas is very similar
with a few differences noted here.

.. _ccsp-archival_metadata:

Archival Metadata
^^^^^^^^^^^^^^^^^

The archival process for CCSP files differs from the process used for SOC
products. As a result, CCSP teams should entirely ignore the  :ref:`external-metadata` section, and should not add the keywords described therein.

Instead CCSP schemas must contain a reference to either:

.. asdf-autoschemas::

   CCSP/ccsp_minimal-1.0.0
   CCSP/ccsp_custom_product-1.0.0

Which schema to use will depend on the details of the product, as described
below. In both cases, these schemas will require the addition of a new
ASDF subtree ``meta.ccsp``, which will contain information necessary
to archive CCSP files.

CCSP Products
"""""""""""""

CCSP products that aren't closely mimicking a SOC product should have schemas that reference ``ccsp_custom_product``, as in the following example.

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

This will check that:

- the produced file contains a ``meta`` key
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
                description: |
                  WCS for the data array, and for the err array if present
                tag: tag:stsci.edu:gwcs/wcs-*
              widget:
                title: Widget metadata
                description: |
                  Metadata describing the state of whatever the "widget" is
                properties:
                  state:
                    title: Widget state
                    description: |
                      Explanation of what widget state means
                    type: string
                  count:
                    title: Widget count
                    description: |
                      Explanation of what widget count means
                    type: integer
                required: [state, count]
            required: [wcs, widget]
      data:
        title: Science Data (MJy/sr)
        description: |
          Described here
        tag: tag:stsci.edu:asdf/core/ndarray-1.*
        datatype: float32
        exact_datatype: true
        ndim: 2
        unit: "MJy/sr"
      err:
        title: Error (MJy/sr)
        description: |
          Total error array corresponding to Science Data
        tag: tag:stsci.edu:asdf/core/ndarray-1.*
        datatype: float32
        exact_datatype: true
        ndim: 2
        unit: "MJy/sr"
    required: [data, meta]
    flowStyle: block

During interaction with MAST and the RAD maintainers, you may be asked to add requirements
for some optional contents in ``ccsp_custom_product``. For example, for targeted
observational data with a relatively small sky footprint, MAST will typically ask for a set of
predefined metadata sub-trees to be populated with information about the exposure,
instrument, telescope, target coordinates, sky footprint, pixel scale, and
wavelength information. These previously optional sections of ``ccsp_custom_product``
can be made required by modifying your schema to include:

.. code:: yaml

    properties:
      meta:
        allOf:
          - $ref: asdf://stsci.edu/datamodels/roman/schemas/CCSP/ccsp_custom_product-1.0.0
          - required:
              [
                exposure,
                instrument,
                telescope,
                target_coordinates,
                s_region,
                pixel_scale,
                wavelength,
              ]

If your product closely resembles a SOC product, another option is to largely copy the contents of a SOC schema, and reference the ``ccsp_minimal`` schema instead of ``ccsp_custom_product``. The ``ccsp_minimal`` schema contains only archival metadata which cannot be found in a typical SOC schema, allowing you to avoid duplicating metadata. Consult with MAST and the RAD maintainers for further advice on this approach.
