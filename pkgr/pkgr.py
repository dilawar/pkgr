__author__ = "Dilawar Singh"
__email__ = "dilawar.s.rajput@gmail.com"

import sys
import toml

from pathlib import Path
import typing as T

from loguru import logger

logger.remove()
logger.add(
    sys.stdout,
    colorize=True,
    format="{level: <8} <cyan>{name}:{function}</cyan> - <level>{message}</level>",
    level="INFO",
)

import typer

import pkgr.rpm
import pkgr.deb
import pkgr.changelog

app = typer.Typer()
app.add_typer(pkgr.rpm.app, name="rpm")
app.add_typer(pkgr.deb.app, name="deb")
app.add_typer(pkgr.changelog.app, name="changelog")


def main():
    app()


if __name__ == "__main__":
    main()
