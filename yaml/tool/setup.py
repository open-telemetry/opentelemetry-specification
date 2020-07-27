import os

import setuptools

BASE_DIR = os.path.dirname(__file__)
VERSION_FILENAME = os.path.join(BASE_DIR, "src", "dynatrace", "semconv", "version.py")
PACKAGE_INFO = {}
with open(VERSION_FILENAME) as f:
    exec(f.read(), PACKAGE_INFO)


VERSION_SUFFIX = os.environ.get("SEMCONGEN_VERSION_SUFFIX")
PUBLIC_VERSION = PACKAGE_INFO["__version__"]

setuptools.setup(
    version=PUBLIC_VERSION
    if not VERSION_SUFFIX
    else PUBLIC_VERSION + "+" + VERSION_SUFFIX
)
