from types import MappingProxyType

# A mapping of the datamodel tags from before the internal tag removal to the
#   new equivalents without the internal tags.
_INTERNAL_TAG_REMOVAL_MAP = MappingProxyType(
    {
        # Changed datamodels
        "asdf://stsci.edu/datamodels/roman/tags/forced_image_source_catalog-1.0.0": "asdf://stsci.edu/datamodels/roman/tags/forced_image_source_catalog-1.1.0",
        "asdf://stsci.edu/datamodels/roman/tags/forced_mosaic_source_catalog-1.0.0": "asdf://stsci.edu/datamodels/roman/tags/forced_mosaic_source_catalog-1.1.0",
        "asdf://stsci.edu/datamodels/roman/tags/image_source_catalog-1.3.0": "asdf://stsci.edu/datamodels/roman/tags/image_source_catalog-1.4.0",
        "asdf://stsci.edu/datamodels/roman/tags/l1_detector_guidewindow-1.2.0": "asdf://stsci.edu/datamodels/roman/tags/l1_detector_guidewindow-1.3.0",
        "asdf://stsci.edu/datamodels/roman/tags/l1_face_guidewindow-1.2.0": "asdf://stsci.edu/datamodels/roman/tags/l1_face_guidewindow-1.3.0",
        "asdf://stsci.edu/datamodels/roman/tags/mosaic_segmentation_map-1.3.0": "asdf://stsci.edu/datamodels/roman/tags/mosaic_segmentation_map-1.4.0",
        "asdf://stsci.edu/datamodels/roman/tags/mosaic_source_catalog-1.3.0": "asdf://stsci.edu/datamodels/roman/tags/mosaic_source_catalog-1.4.0",
        "asdf://stsci.edu/datamodels/roman/tags/msos_stack-1.3.0": "asdf://stsci.edu/datamodels/roman/tags/msos_stack-1.4.0",
        "asdf://stsci.edu/datamodels/roman/tags/multiband_source_catalog-1.0.0": "asdf://stsci.edu/datamodels/roman/tags/multiband_source_catalog-1.1.0",
        "asdf://stsci.edu/datamodels/roman/tags/ramp_fit_output-1.3.0": "asdf://stsci.edu/datamodels/roman/tags/ramp_fit_output-1.4.0",
        "asdf://stsci.edu/datamodels/roman/tags/ramp-1.3.0": "asdf://stsci.edu/datamodels/roman/tags/ramp-1.4.0",
        "asdf://stsci.edu/datamodels/roman/tags/segmentation_map-1.3.0": "asdf://stsci.edu/datamodels/roman/tags/segmentation_map-1.4.0",
        "asdf://stsci.edu/datamodels/roman/tags/wfi_image-1.3.0": "asdf://stsci.edu/datamodels/roman/tags/wfi_image-1.4.0",
        "asdf://stsci.edu/datamodels/roman/tags/wfi_mosaic-1.3.0": "asdf://stsci.edu/datamodels/roman/tags/wfi_mosaic-1.4.0",
        "asdf://stsci.edu/datamodels/roman/tags/wfi_science_raw-1.3.0": "asdf://stsci.edu/datamodels/roman/tags/wfi_science_raw-1.4.0",
        "asdf://stsci.edu/datamodels/roman/tags/wfi_wcs-1.2.0": "asdf://stsci.edu/datamodels/roman/tags/wfi_wcs-1.3.0",
        # Changed reference files
        "asdf://stsci.edu/datamodels/roman/tags/reference_files/abvegaoffset-1.1.0": "asdf://stsci.edu/datamodels/roman/tags/reference_files/abvegaoffset-1.2.0",
        "asdf://stsci.edu/datamodels/roman/tags/reference_files/apcorr-1.1.0": "asdf://stsci.edu/datamodels/roman/tags/reference_files/apcorr-1.2.0",
        "asdf://stsci.edu/datamodels/roman/tags/reference_files/dark-1.3.0": "asdf://stsci.edu/datamodels/roman/tags/reference_files/dark-1.4.0",
        "asdf://stsci.edu/datamodels/roman/tags/reference_files/distortion-1.2.0": "asdf://stsci.edu/datamodels/roman/tags/reference_files/distortion-1.3.0",
        "asdf://stsci.edu/datamodels/roman/tags/reference_files/epsf-1.2.0": "asdf://stsci.edu/datamodels/roman/tags/reference_files/epsf-1.3.0",
        "asdf://stsci.edu/datamodels/roman/tags/reference_files/flat-1.2.0": "asdf://stsci.edu/datamodels/roman/tags/reference_files/flat-1.3.0",
        "asdf://stsci.edu/datamodels/roman/tags/reference_files/gain-1.1.0": "asdf://stsci.edu/datamodels/roman/tags/reference_files/gain-1.2.0",
        "asdf://stsci.edu/datamodels/roman/tags/reference_files/inverselinearity-1.1.0": "asdf://stsci.edu/datamodels/roman/tags/reference_files/inverselinearity-1.2.0",
        "asdf://stsci.edu/datamodels/roman/tags/reference_files/ipc-1.2.0": "asdf://stsci.edu/datamodels/roman/tags/reference_files/ipc-1.3.0",
        "asdf://stsci.edu/datamodels/roman/tags/reference_files/linearity-1.1.0": "asdf://stsci.edu/datamodels/roman/tags/reference_files/linearity-1.2.0",
        "asdf://stsci.edu/datamodels/roman/tags/reference_files/mask-1.1.0": "asdf://stsci.edu/datamodels/roman/tags/reference_files/mask-1.2.0",
        "asdf://stsci.edu/datamodels/roman/tags/reference_files/matable-1.1.0": "asdf://stsci.edu/datamodels/roman/tags/reference_files/matable-1.2.0",
        "asdf://stsci.edu/datamodels/roman/tags/reference_files/pixelarea-1.2.0": "asdf://stsci.edu/datamodels/roman/tags/reference_files/pixelarea-1.3.0",
        "asdf://stsci.edu/datamodels/roman/tags/reference_files/readnoise-1.2.0": "asdf://stsci.edu/datamodels/roman/tags/reference_files/readnoise-1.3.0",
        "asdf://stsci.edu/datamodels/roman/tags/reference_files/refpix-1.1.0": "asdf://stsci.edu/datamodels/roman/tags/reference_files/refpix-1.2.0",
        "asdf://stsci.edu/datamodels/roman/tags/reference_files/saturation-1.1.0": "asdf://stsci.edu/datamodels/roman/tags/reference_files/saturation-1.2.0",
        "asdf://stsci.edu/datamodels/roman/tags/reference_files/skycells-1.0.0": "asdf://stsci.edu/datamodels/roman/tags/reference_files/skycells-1.1.0",
        "asdf://stsci.edu/datamodels/roman/tags/reference_files/superbias-1.1.0": "asdf://stsci.edu/datamodels/roman/tags/reference_files/superbias-1.2.0",
        "asdf://stsci.edu/datamodels/roman/tags/reference_files/wfi_img_photom-1.2.0": "asdf://stsci.edu/datamodels/roman/tags/reference_files/wfi_img_photom-1.3.0",
    }
)
