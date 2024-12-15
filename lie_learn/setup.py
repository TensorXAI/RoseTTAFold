# pylint: disable=missing-docstring
from Cython.Build import cythonize
import numpy as np
import glob
import os
from setuptools import setup, Extension, find_packages

"""
extensions = [
    Extension(
        "lie_learn",
        sources=["lie_learn/**/*.pyx"],
        include_dirs=[np.get_include()],
        extra_compile_args=["-DNPY_NO_DEPRECATED_API=NPY_1_7_API_VERSION"]
    )
]
"""

pyx_files = glob.glob("lie_learn/**/*.pyx", recursive=True)

# Create a list of Extension objects for each .pyx file
extensions = [
    Extension(
        name="lie_learn." + os.path
            .splitext(os.path.relpath(pyx_file, "lie_learn"))[0]
            .replace(os.path.sep, "."),  # Convert path to module name
        sources=[pyx_file],  # The source file
        include_dirs=[np.get_include()],  # Include NumPy headers
        libraries=["lapack", "blas"], 
        extra_compile_args=[
            "-O3", 
            "-DACCELERATE_NEW_LAPACK", 
            "-mmacosx-version-min=13.3", 
            "-DNPY_NO_DEPRECATED_API=NPY_1_7_API_VERSION"
        ], # Optimization flags
        extra_link_args=[
            "-framework",
            "Accelerate", 
            "-mmacosx-version-min=13.3",
            "-Wl,-rpath,/opt/miniconda3/envs/RoseTTAFold-OSX-ARM64/lib"
        ],  # Link against the Accelerate framework
    )
    for pyx_file in pyx_files
]

setup(
    name='lie_learn',  # Project name (Root directory)
    version='0.1.0',  # Version
    description="XPU-Ready Python Library For Learning Lie Groups",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Stealth Lab",
    author_email="your.email@example.com",
    url="https://github.com/stealthlab/lie_learn",
    license="MIT",
    packages=find_packages(),  # Specify the root directory
    package_dir={'': '.'},              # Indicate that packages are in the root
    include_package_data=True,  # Include files specified in MANIFEST.in
    ext_modules=cythonize(extensions, language_level=2, force=True),
    zip_safe=False,  # Do not zip the package
)

"""
setup(
    name="lie_learn",  # Library name
    version="0.1.0",  # Start with an initial version
    description="XPU-Ready Python Library For Learning Lie Groups",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Stealth Lab",
    author_email="your.email@example.com",
    url="https://github.com/stealthlab/lie_learn",
    license="MIT",
    packages=find_packages(),
    ext_modules=cythonize(extensions, language_level=2, force=True),
)
"""
