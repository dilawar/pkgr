__author__ = "Dilawar Singh"
__email__ = "dilawar.s.rajput@gmail.com"

from pathlib import Path
import toml
import typing as T

from loguru import logger

import typer

import pkgr.rpm
import pkgr.deb

app = typer.Typer()
app.add_typer(pkgr.rpm.app, name="rpm")
app.add_typer(pkgr.deb.app, name="deb")


def main():
    app()


if __name__ == "__main__":
    main()
