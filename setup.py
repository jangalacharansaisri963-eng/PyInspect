from setuptools import setup, Extension, find_packages

c_extension = Extension(
    'pyinspect.pyinspect_core',
    sources=['pyinspect/pyinspect_core.c'],
)

setup(
    name="Dan-PyInspect",
    version="5.0.0",
    packages=find_packages(),
    ext_modules=[c_extension],
    zip_safe=False,
)
