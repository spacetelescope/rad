"""
Test features of the schemas not covered by the metaschema.
"""

from collections.abc import Mapping
from re import match

import asdf
import asdf.schema
import asdf.treeutil
import pytest
from crds.config import is_crds_name

METADATA_FORCING_REQUIRED = ("archive_catalog", "sdf")

METADATA_FORCE_XFAILS = (
    # <resource uri>
)

VARCHAR_XFAILS = (
    # <resource uri>
    "asdf://stsci.edu/datamodels/roman/schemas/meta/ref_file-1.0.0",
)

REF_COMMON_XFAILS = ("asdf://stsci.edu/datamodels/roman/schemas/reference_files/skycells-1.1.0",)

ARRAY_TAG_XFAILS = (
    # <resource uri>
)

REQUIRED_SKIPS = (
    "asdf://stsci.edu/datamodels/roman/schemas/wfi_mosaic-1.5.0",
    "asdf://stsci.edu/datamodels/roman/schemas/meta/l3_catalog_common-1.0.0",
    "asdf://stsci.edu/datamodels/roman/schemas/multiband_source_catalog-1.1.0",
    "asdf://stsci.edu/datamodels/roman/schemas/CCSP/EXAMPLE/example_custom_product-1.0.0",
)

NESTED_REQUIRED_SKIPS = (
    "asdf://stsci.edu/datamodels/roman/schemas/meta/l3_common-1.0.0",
    "asdf://stsci.edu/datamodels/roman/schemas/CCSP/ccsp_custom_product-1.0.0",
)


class TestSchemaContent:
    """
    Basic tests for schema content and formatting
    """

    def test_required_properties(self, schema, metaschema_uri):
        """
        Check that all schemas have the required properties
        -> id, title, and $schema
        """
        assert schema["$schema"] == metaschema_uri
        assert "id" in schema
        assert "title" in schema

    def test_schema_style(self, current_content):
        """
        Make sure that the schema has the correct style
        -> YAML 1.1
        Note the rest of the checks should be covered by the autoformatter
        """
        assert current_content.startswith(b"%YAML 1.1\n---\n")
        assert b"\t" not in current_content
        assert not any(line != line.rstrip() for line in current_content.split(b"\n"))

    def test_required(self, schema):
        """
        Checks that all required properties are present in the schema
        """
        if schema["id"] in REQUIRED_SKIPS:
            pytest.skip(f"skipped required keyword test for {schema['id']}")

        def callback(node):
            """Callback for required properties being present"""
            if isinstance(node, Mapping) and "required" in node:
                assert node.get("type", "object") == "object"
                property_names = set(node.get("properties", {}).keys())
                required_names = set(node["required"])
                if not required_names.issubset(property_names):
                    message = f"required references names that do not exist: {','.join(required_names - property_names)}"
                    raise ValueError(message)

        asdf.treeutil.walk(schema, callback)

    def test_exact_datatype(self, schema):
        """Confirm that `datatype` and `exact_datatype` is defined for all arrays"""

        def callback_ndarray(node, entry):
            """
            Identify and check ndarray nodes (entry passed in for error messages)
            """
            if isinstance(node, Mapping) and "tag" in node and node["tag"].startswith("tag:stsci.edu:asdf/core/ndarray-"):
                assert "datatype" in node, f"datatype not found for ndarray entry {entry}"
                assert "exact_datatype" in node, f"exact_datatype not found for ndarray entry {entry}"
                assert node["exact_datatype"] is True, f"exact_datatype not True for ndarray entry {entry}"

        def callback(node):
            """
            Identify and check all nodes, note that we loop over the entries for better error messages
            """
            if isinstance(node, Mapping):
                for entry, sub_node in node.items():
                    callback_ndarray(sub_node, entry)

        asdf.treeutil.walk(schema, callback)

    def test_array_tag(self, schema_uri, schema, request):
        """
        Any schema using ndim, datatype, etc also has an array tag
        """
        if schema_uri in ARRAY_TAG_XFAILS:
            request.applymarker(
                pytest.mark.xfail(
                    reason=f"{schema_uri} is not being altered to ensure array tags, due to it being in either tvac or fps."
                    if "fps" in schema_uri or "tvac" in schema_uri
                    else f"{schema_uri} is a published schema."
                )
            )

        def callback(node):
            if not isinstance(node, dict):
                return
            if "destination" in node:
                # don't check archive_catalog entries
                return
            if "byteorder" in node:
                # don't check sub-dtypes
                return
            if isinstance(node.get("datatype"), dict):
                # table (and old quantity containing) schemas use datatype in a different way
                return
            if any(k in node for k in ("ndim", "datatype", "exact_datatype")):
                tag = node.get("tag", "")
                assert tag.startswith("tag:stsci.edu:asdf/core/ndarray-")

        asdf.treeutil.walk(schema, callback)

    @pytest.mark.parametrize("uri", ARRAY_TAG_XFAILS)
    def test_array_tag_xfail_relevant(self, uri, schema_uris):
        """
        Test that URIS that are marked as failing the array tagging are still relevant (in use).
        -> Smokes out when ARRAY_TAG_XFAILS is not relevant anymore.
        """
        assert uri in schema_uris, f"{uri} is not in the list of schemas to be tested."

    def test_ref_loneliness(self, schema):
        """
        An object with a $ref should contain no other items
        """

        def callback(node):
            if not isinstance(node, dict):
                return
            if "$ref" not in node:
                return
            assert len(node) == 1

        asdf.treeutil.walk(schema, callback)

    def test_no_default(self, schema):
        """
        Test that schemas do not contain the default keyword
        """

        for node in asdf.treeutil.iter_tree(schema):
            if isinstance(node, dict):
                assert "default" not in node

    def test_absolute_ref(self, schema):
        """
        Test that all $ref are absolute URIs matching those registered with ASDF
        """
        resources = asdf.config.get_config().resource_manager

        def callback(node):
            if not isinstance(node, dict):
                return
            if "$ref" not in node:
                return

            # Check that the $ref is a full URI registered with ASDF
            ref_uri = node["$ref"]

            # remove a fragment if it exists
            if "#" in ref_uri:
                ref_uri, _ = ref_uri.split("#", maxsplit=1)
            assert ref_uri in resources

        asdf.treeutil.walk(schema, callback)

    def test_metadata_force_required(self, schema_uri, schema, request):
        """
        Test that if certain properties have certain metadata entries, that they are in a required list.
        -> Also checks that once required is present in a subnode it is present in the parent node for mappings
        """
        # Apply the xfail marker if we expect the test to fail
        if schema_uri in METADATA_FORCE_XFAILS:
            request.applymarker(
                pytest.mark.xfail(
                    reason=f"{schema_uri} is not being altered to ensure required lists for archive metadata, due to it being in either tvac or fps."
                )
            )

        if schema_uri in NESTED_REQUIRED_SKIPS:
            pytest.skip(f"skipping nested required keyword test for {schema_uri}")

        def callback(node):
            if isinstance(node, Mapping) and "properties" in node:
                for prop_name, prop in node["properties"].items():
                    # Test that if a subnode has a required list, that the parent has a required list
                    if isinstance(prop, Mapping) and "required" in prop:
                        assert "required" in node
                        assert prop_name in node["required"]

                    # Test that if a subnode has certain metadata entries, that the parent has a required list
                    for metadata in METADATA_FORCING_REQUIRED:
                        if isinstance(prop, Mapping) and metadata in prop:
                            assert "required" in node, f"metadata {metadata} in {prop_name} requires required list"
                            assert prop_name in node["required"]

        asdf.treeutil.walk(schema, callback)

    @pytest.mark.parametrize("uri", METADATA_FORCE_XFAILS)
    def test_metadata_force_xfail_relevant(self, uri, latest_uris):
        """
        Test that URIS that are marked as failing the metadata are still relevant (in use).
        -> Smokes out when METADATA_FORCE_XFAILS is not relevant anymore.
        """
        assert uri in latest_uris, f"{uri} is not in the list of schemas to be tested."

    def test_string_max_length(self, schema):
        """
        Checks that if a `maxLength` is specified, that it is specified along with a `type` of `string`.
        """

        def callback(node):
            if isinstance(node, Mapping) and "maxLength" in node:
                assert node.get("type") == "string", "maxLength is only valid for strings"

        asdf.treeutil.walk(schema, callback)

    def test_varchar_length(self, schema_uri, schema, request):
        """
        Test that varchar(N) in archive_metadata for string objects
        has a matching maxLength: N validation keyword
        """
        # Apply the xfail marker if we expect the test to fail
        if schema_uri in VARCHAR_XFAILS:
            request.applymarker(pytest.mark.xfail(reason=f"{schema_uri} not checked for maxLength/varchar consistency."))

        def callback(node):
            if (
                isinstance(node, Mapping)
                and "archive_catalog" in node
                and node["archive_catalog"]["datatype"].startswith("nvarchar(")
            ):
                m = match(r"^nvarchar\(([0-9]+)\)$", node["archive_catalog"]["datatype"])
                if m:
                    length = int(m.group(1))

                    def check_max_length(node):
                        nonlocal found
                        nonlocal ref_uri
                        if isinstance(node, Mapping) and "enum" in node:
                            max_enum_length = max(len(v) for v in node["enum"])
                            assert max_enum_length <= length, (
                                f"archive_catalog.datatype nvarchar indicates maxLength={length}, but enum of length {max_enum_length} found."
                            )
                            found = True
                            return
                        if isinstance(node, Mapping) and "type" in node:
                            if node["type"] == "string":
                                msg = "archive_catalog.datatype nvarchar indicates maxLength is required"
                                msg += f" in schema {ref_uri}" if ref_uri else ""
                                msg += ", but it is not present"
                                assert "maxLength" in node, msg
                                assert node["maxLength"] == length, (
                                    f"archive_catalog.datatype nvarchar indicates maxLength={length}, but found {node['maxLength']}."
                                )
                                found = True

                            # Arrays may have a nvarchar described for archive, but they don't have a maxLength
                            # json-schema descriptor so we assume that we found maxLength
                            elif node["type"] == "array":
                                found = True

                    if "type" in node:
                        found = False
                        ref_uri = None
                        asdf.treeutil.walk(node, check_max_length)
                        assert found, "archive_catalog.datatype nvarchar indicates maxLength is required, none is found"
                        return

                    if "allOf" in node or "anyOf" in node:
                        for sub_schema in node.get("allOf", []) + node.get("anyOf", []):
                            if isinstance(sub_schema, Mapping):
                                found = False
                                ref_uri = sub_schema.get("$ref")
                                sub_node = asdf.schema.load_schema(sub_schema["$ref"]) if "$ref" in sub_schema else sub_schema
                                asdf.treeutil.walk(sub_node, check_max_length)
                                assert found, (
                                    f"archive_catalog.datatype nvarchar indicates there should be a maxLength in {sub_schema['$ref']}"
                                )
                                return

                    # Fallback failure
                    raise AssertionError("archive_catalog.datatype is nvarchar but no maxLength found.")

        asdf.treeutil.walk(schema, callback)

    @pytest.mark.parametrize("uri", VARCHAR_XFAILS)
    def test_varchar_xfail_relevant(self, uri, latest_uris):
        """
        Test that URIS that are marked as failing for varchar length are still relevant (in use).
        -> Smokes out when VARCHAR_XFAILS is not relevant anymore.
        """
        assert uri in latest_uris, f"{uri} is not in the list of schemas to be tested."

    def test_no_static_tags(self, schema, latest_static_tags):
        """
        Check that the schema does not contain any static tags
        """

        def callback(node):
            """Callback to check for static tags"""
            if isinstance(node, Mapping) and "tag" in node:
                assert node["tag"] not in latest_static_tags

        asdf.treeutil.walk(schema, callback)

    def test_latest_refs(self, schema, latest_uris, current_resources):
        """
        Check that all $ref in the schema point to the latest version of the referenced schema
        """

        def callback(node):
            """Callback to check for latest refs"""
            if isinstance(node, Mapping) and "$ref" in node:
                ref_uri = node["$ref"]
                if "#/" in ref_uri:
                    ref_uri, part_path = ref_uri.split("#/")

                    def_schema = current_resources[ref_uri]
                    for part in part_path.split("/"):
                        if part in def_schema:
                            def_schema = def_schema[part]
                        else:
                            raise ValueError(f"Could not find part {part} in schema {ref_uri}")
                assert ref_uri in latest_uris, f"$ref {node['$ref']} does not point to the latest version of the schema"

        asdf.treeutil.walk(schema, callback)


class TestTaggedSchemaContent:
    """
    Tests for content related to schemas and their tags
    """

    def test_tag(self, schema, valid_tag_uris):
        """
        Check that the tags in the schema are valid
        """

        def callback(node):
            """Callback to check for valid tags"""
            if isinstance(node, Mapping) and "tag" in node:
                assert node["tag"] in valid_tag_uris

        asdf.treeutil.walk(schema, callback)

    def test_property_order(self, schema_uri, schema, tagged_schema_uris):
        """
        Check that the propertyOrder is consistent with the properties and is only used in the tag schemas
        """
        if schema_uri in tagged_schema_uris:

            def callback(node):
                """Callback for tagged schemas"""
                if isinstance(node, Mapping) and "propertyOrder" in node:
                    assert node.get("type") == "object"
                    property_names = set(node.get("properties", {}).keys())
                    property_order_names = set(node["propertyOrder"])
                    if property_order_names != property_names:
                        missing_list = ", ".join(property_order_names - property_names)
                        extra_list = ", ".join(property_names - property_order_names)
                        message = (
                            "propertyOrder does not match list of properties:\n\n"
                            "missing properties: " + missing_list + "\n"
                            "extra properties: " + extra_list
                        )
                        raise ValueError(message)
        else:

            def callback(node):
                """Callback for non-tagged schemas"""
                if isinstance(node, Mapping):
                    assert "propertyOrder" not in node, "Only schemas associated with a tag may specify propertyOrder"

        asdf.treeutil.walk(schema, callback)

    def test_flowstyle(self, schema_uri, schema, tagged_schema_uris):
        """
        Test that tagged schemas have flowStyle: block
        -> untagged schemas should not have flowStyle
        """
        if schema_uri in tagged_schema_uris:
            found_flowstyle = False

            def callback(node):
                """Callback for tagged schemas"""
                nonlocal found_flowstyle
                if isinstance(node, Mapping) and node.get("flowStyle") == "block":
                    found_flowstyle = True

            asdf.treeutil.walk(schema, callback)

            assert found_flowstyle, "Schemas associated with a tag must specify flowStyle: block"
        else:

            def callback(node):
                """Callback for non-tagged schemas"""
                if isinstance(node, Mapping):
                    assert "flowStyle" not in node, "Only schemas associated with a tag may specify flowStyle"

            asdf.treeutil.walk(schema, callback)

    def test_datamodel_name(self, schema_uri, schema):
        def callback(node):
            if isinstance(node, Mapping) and "datamodel_name" in node:
                schema_name = schema_uri.split("/")[-1].split("-")[0]
                class_name = "".join([p.capitalize() for p in schema_name.split("_")])
                if schema_uri.startswith("asdf://stsci.edu/datamodels/roman/schemas/reference_files/"):
                    class_name += "Ref"

                if class_name not in ["WfiWcs"]:  # Names to be unmodified
                    if class_name.startswith("Wfi") and "Ref" not in class_name:
                        class_name = class_name.split("Wfi")[-1]
                    elif class_name.startswith("MatableRef"):
                        class_name = "MATableRef" + class_name.split("MatableRef")[-1]

                datamodel_name = f"{class_name}Model"
                assert node["datamodel_name"] == datamodel_name, (
                    f"datamodel_name {node['datamodel_name']} does not match expected {datamodel_name}"
                )

        asdf.treeutil.walk(schema, callback)


class TestReferenceFileSchemas:
    """Reference file schema specific tests"""

    def get_reftype(self, schema):
        """
        Extract the reftype from the schema
        """
        all_of = schema["properties"]["meta"]["allOf"]

        for sub_schema in all_of:
            if "properties" in sub_schema:
                assert "reftype" in sub_schema["properties"], "A defined reftype is required"
                assert "enum" in sub_schema["properties"]["reftype"], "The reftype must be enumerated"
                assert len(sub_schema["properties"]["reftype"]["enum"]) == 1, "The reftype must be a single value"
                return sub_schema["properties"]["reftype"]["enum"][0]

        raise ValueError("No reftype found in schema")

    def test_reftype(self, ref_file_schema):
        """
        Check that the reftype is valid for CRDS
        """

        def callback(node):
            if (
                isinstance(node, Mapping)
                and "properties" in node
                and "meta" in node["properties"]
                and "allOf" in node["properties"]["meta"]
            ):
                reftype = self.get_reftype(node)
                assert is_crds_name(f"roman_wfi_{reftype.lower()}_0000.asdf"), f"Invalid reftype {reftype} for CRDS"

        asdf.treeutil.walk(ref_file_schema, callback)

    def test_reftype_tag(self, ref_file_uri, schema_tag_map, ref_file_schema):
        """
        Check that the URIs match the reftype for a valid CRDS check
        """

        if ref_file_uri in schema_tag_map:
            reftype = self.get_reftype(ref_file_schema).lower()
            ref_file_tag_uri = schema_tag_map[ref_file_uri]
            assert asdf.util.uri_match(f"asdf://stsci.edu/datamodels/roman/tags/reference_files/*{reftype}-*", ref_file_tag_uri)
            assert asdf.util.uri_match(f"asdf://stsci.edu/datamodels/roman/schemas/reference_files/*{reftype}-*", ref_file_uri)

    def test_ref_file_meta_common(self, ref_file_uri, ref_file_schema, schema_tag_map, request):
        """
        Test that the meta for all reference files contains a reference to `ref_common`
        """
        # Apply the xfail marker if we expect the test to fail
        if ref_file_uri in REF_COMMON_XFAILS:
            request.applymarker(
                pytest.mark.xfail(
                    reason=f"{ref_file_uri}, does not have a ref_common entry in the meta because it is inconsistent with the skycell formulation."
                )
            )

        if ref_file_uri in schema_tag_map:
            for item in ref_file_schema["properties"]["meta"]["allOf"]:
                if isinstance(item, dict) and "$ref" in item:
                    assert item["$ref"].startswith("asdf://stsci.edu/datamodels/roman/schemas/reference_files/ref_common-")
                    return

            raise ValueError("ref_common not found in meta")

    @pytest.mark.parametrize("uri", REF_COMMON_XFAILS)
    def test_ref_common_xfail_relevant(self, uri, latest_uris):
        """
        Test that URIS that are marked as failing the ref_common are still relevant (in use).
        -> Smokes out when REF_COMMON_XFAILS is not relevant anymore.
        """
        assert uri in latest_uris, f"{uri} is not in the list of schemas to be tested."


class TestCCSPSchemas:
    def test_ref_to_ccsp(self, ccsp_model_schema, rad_uri_prefix):
        """
        Test that the schema contains a reference to ccsp_minimal or ccsp_custom_product
        """
        # all CCSP model schemas should ref one of these
        targets = (
            "asdf://stsci.edu/datamodels/roman/schemas/CCSP/ccsp_custom_product-",
            "asdf://stsci.edu/datamodels/roman/schemas/CCSP/ccsp_minimal-",
        )

        def iter_path_value_pairs(value, path=()):
            """
            Generator returning (path, value) pairs for a nested schema.
            """
            if isinstance(value, dict):
                for key, subvalue in value.items():
                    yield from iter_path_value_pairs(subvalue, path=(*path, key))
            elif isinstance(value, list):
                for index, subvalue in enumerate(value):
                    yield from iter_path_value_pairs(subvalue, path=(*path, index))
            else:
                yield path, value

        soc_ref = None
        ccsp_ref = None
        schema_uri = ccsp_model_schema["id"]

        for path, value in iter_path_value_pairs(ccsp_model_schema):
            if path[-1] != "$ref":
                continue
            if any(value.startswith(target) for target in targets):
                assert ccsp_ref is None, f"{schema_uri} contains multiple ccsp references: {((path, value), ccsp_ref)}"
                ccsp_ref = (path, value)
            elif "CCSP" not in value and value.startswith(rad_uri_prefix):
                soc_ref = (path, value)

        assert ccsp_ref, f"{schema_uri} does not contain a '$ref' to either ccsp_minimal or ccsp_custom_product"

        if soc_ref:
            assert "ccsp_minimal" in ccsp_ref[1], (
                f"{schema_uri} contains a '$ref' to a SOC schema ({soc_ref}) but does not use ccsp_minimal"
            )

        # Check that the ccsp schema is referenced within meta
        # This won't catch all schema structures but checks for the common one.
        target_path = ["properties", "meta", "$ref"]
        for sub_path in ccsp_ref[0]:
            if sub_path == target_path[0]:
                target_path.pop(0)
        assert not target_path, f"{schema_uri} ccsp '$ref' is not under 'meta': {ccsp_ref[0]}"


class TestPatternElementConsistency:
    def test_phot_table_keys_have_optical_element_entry(self, phot_table_key_patterns, optical_element):
        """
        Confirm that the optical_element filter in wfi_img_photom.yaml matches optical_element
        """
        for pattern in phot_table_key_patterns:
            if pattern.search(optical_element):
                return

        raise AssertionError(f"phot_table_key pattern is missing {optical_element}.")

    def test_optical_elements_have_phot_table_key(self, phot_table_key, optical_elements):
        """
        Confirm that the optical_element filter in wfi_img_photom.yaml matches optical_element
        """
        # NOTE: GRISM_0 is a special case that will only ever be used in the photom table,
        #   It is due to a special photom measurement only relevant for calibration purposes
        #   so it will never appear anywhere else, so it is excluded from the optical elements
        #   in general.
        assert phot_table_key in (*optical_elements, "GRISM_0"), f"phot_table_key {phot_table_key} not found in optical_elements."

    def test_p_exptype_entries_have_exposure_type(self, p_exptype_pattern, exposure_type):
        """Confirm that the p_keyword version of exposure type match the enum version."""
        assert p_exptype_pattern.search(f"{exposure_type}|"), f"p_exptype pattern is missing {exposure_type}."

    def test_exposure_types_have_p_exptype_entry(self, p_exptype, exposure_types):
        """Confirm that the p_exptype entry is in the exposure_types enum."""
        assert p_exptype in exposure_types, f"p_exptype {p_exptype} not found in exposure_types."


class TestSSCSchemas:
    @pytest.mark.usefixtures("asdf_ssc_config")
    def test_metaschema(self, ssc_schema_path, ssc_schema_uri):
        """
        Test that the SSC Schemas are valid against the metaschema. This has to be done
        outside the normal asdf-pytest-plugin because we are purposefully excluding them
        from ASDF by default so they need to be manually loaded into asdf and then validated
        against the metaschema.
        """
        schema = asdf.schema.load_schema(ssc_schema_path, resolve_references=True)
        assert schema["id"] == ssc_schema_uri

        asdf.schema.check_schema(schema)
