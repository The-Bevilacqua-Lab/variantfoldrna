from setuptools import setup, find_namespace_packages
from setuptools.command.develop import develop
from setuptools.command.install import install
import subprocess

_MAJOR              = 0
_MINOR              = 1
_MICRO              = 0
_VERSION            = '{}.{}.{}'.format(_MAJOR, _MINOR, _MICRO)
_PACKAGE_NAME       = 'sparcs'
_DESCRIPTION        = 'SPARCS: A Snakemake Pipeline for RiboSNitch Prediction'

metainfo = dict(
    authors = {"main": ("Kobie Kirven", "kjk6173@psu.edu")},
    version = _VERSION,
    license = "GNU General Public License v3.0",
    url = "https://github.com/The-Bevilacqua-Lab/SPARCS",
    description = _DESCRIPTION,
    platforms = ["Linux", "Mac OS-X", "Unix"],
    classifiers = [
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "programming Language :: Python :: 3.6",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
    ],
    )

NAME = 'sparcs'

setup(
    name=NAME,
    version=_VERSION,
    description=_DESCRIPTION,
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url=metainfo['url'],
    author=metainfo['authors']['main'][0],
    author_email=metainfo['authors']['main'][1],
    license=metainfo['license'],
    package_dir = {'':'workflow'},

    include_package_data = True,

    install_requires = open("requirements.txt").read(),

    # This is recursive include of data files
    exclude_package_data = {"": ["__pycache__"]},
    package_data = {
        'workflow': ['*.yaml', "*.rules", "*.json", "requirements.txt", "*png", "*yml", "*smk", "*.py"],
        "workflow.rules": ["*/*.rules"],
        "workflow.scripts":["*/*.py", "*/*.pl"],
        "workflow.envs": ["*/*.yaml"],
        },

    zip_safe=False,

    entry_points = {'console_scripts':[
        'sparcs=workflow.main:main']
    }

)

