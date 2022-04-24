__version__ = '1.1.5'
import os

from setuptools import setup, find_packages

# README read-in
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()
# END README read-in


def get_resources(file_exts):
    directory = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'skytemple_dtef')
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            if any(filename.endswith(file_ext) for file_ext in file_exts):
                paths.append(os.path.relpath(os.path.join('..', path, filename), directory))
    return paths


setup(
    name='skytemple-dtef',
    version=__version__,
    packages=find_packages(),
    package_data={'skytemple_dtef': get_resources(['.png'])},
    description="Dungeon Tile Exchange Format: A format for standardized rule-based tilesets with 256 adjacency combinations.",
    long_description=long_description,
    long_description_content_type='text/x-rst',
    url='https://github.com/SkyTemple/skytemple-dtef/',
    install_requires=[
        'skytemple-files >= 1.2.0',
        'Pillow >= 6.1.0'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9'
    ],
)
