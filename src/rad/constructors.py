from astropy.time import Time


def calibration_software_name(defaults=None):
    return "RomanCAL"


def file_date(defaults=None):
    if defaults:
        return Time(defaults)
    return Time.now()


def origin(defaults=None):
    return "STSCI/SOC"


def telescope(defaults=None):
    return "ROMAN"


def prd_version(defaults=None):
    return "8.8.8"


def sdf_software_version(defaults=None):
    return "7.7.7"
