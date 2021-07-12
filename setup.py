__author__           = "Dilawar Singh"
__email__            = "dilawar.s.rajput@gmail.com"

from setuptools import setup
from pathlib import Path

packages = ["pkgr"]

package_data = {"": ["*"]}

install_requires = [
    "loguru>=0.5.3,<0.6.0",
    "toml>=0.10.2,<0.11.0",
    "typer>=0.3.2,<0.4.0",
]

entry_points = {"console_scripts": ["pkgr = pkgr.pkgr:main"]}

long_description = (Path(__file__).resolve().parent / 'README.md').open().read()

setup_kwargs = {
    "name": "pkgr",
    "version": "0.1.0",
    "description": "Create packages for various Linuses using docker",
    "long_description": long_description,
    "author": "Dilawar Singh",
    "author_email": "dilawar.s.rajput@gmail.com",
    "maintainer": "Dilawar Singh",
    "maintainer_email": "dilawar.s.rajput@gmail.com",
    "url": "https://github.com/dilawar/pkgr",
    "packages": packages,
    "package_data": package_data,
    "install_requires": install_requires,
    "entry_points": entry_points,
    "python_requires": ">=3.7,<4.0",
}

setup(**setup_kwargs)
