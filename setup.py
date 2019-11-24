from setuptools import setup, find_packages


setup(
    name='gcs',
    version='0.0.1',
    description='Geometric constraint solver',
    packages=find_packages(),
    install_requires=[
        'numpy',
        'scipy',
        'matplotlib',
        'python-igraph',
        'pycairo',
        'blist',
        'sortedcontainers',
    ]
)
