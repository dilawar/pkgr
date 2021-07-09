__author__ = "Dilawar Singh"
__email__ = "dilawar.s.rajput@gmail.com"

from pathlib import Path
import toml
import typing as T

from loguru import logger

import typer

import pkgr.rpm

app = typer.Typer()


def _load_toml(tomlfile: Path):
    assert tomlfile.exists(), f"{tomlfile} does not exists"
    cfg = toml.load(tomlfile)
    cfg["basepath"] = tomlfile.resolve().parent
    return cfg


@app.command()
def genspec(toml: Path, specfile: T.Optional[Path] = None):
    """Generate RPM"""
    config = _load_toml(toml)
    specstr = pkgr.rpm.generate_spec_str(config)
    logger.debug(f'{specstr}')
    if specfile is None:
        specfile = Path(f'{config["name"]}.spec')
        logger.info(f'Using default specfile: {specfile}')

    with specfile.open("w") as f:
        f.write(specstr)
    logger.info(f"Wrote {specfile}")


@app.command()
def deb(toml: Path):
    """Generate DEB"""
    config = _load_toml(toml)
    raise NotImplementedError("Not implemented")


def main():
    app()


if __name__ == "__main__":
    main()
