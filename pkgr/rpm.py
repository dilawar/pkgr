__author__ = "Dilawar Singh"
__email__ = "dilawar.s.rajput@gmail.com"

import typing as T

import pkgr.config
import pkgr.templates

from pathlib import Path

import typer

import pkgr.config

app = typer.Typer()


def _gen_build_requires(builddeps: T.List[str]) -> str:
    return "\n".join([f"BuildRequires: {x}" for x in builddeps])


def _gen_requires(reqs: T.List[str]) -> str:
    return "\n".join([f"Requires: {x}" for x in reqs])


def generate_spec_str(config: T.Dict[str, T.Any]) -> str:
    RPM_TEMPLATE = pkgr.templates.RPM
    config["build_requires"] = _gen_build_requires(config["builddeps"].get("rpm", []))
    config["requires"] = _gen_requires(config.get("deps", dict(rpm=[])).get("rpm", []))
    config["prep"] = pkgr.config.get(config, "prep", "%autosetup")
    config["build"] = pkgr.config.get(config, "build", "%configure\n%make_build")
    config["install"] = pkgr.config.get(
        config, "install.bash", "rm -rf $RPM_TEMPLATE\n%make_install"
    )
    config["files"] = pkgr.config.get(config, "files", [])
    config["changelog"] = pkgr.config.get(config, "changelog", [])
    return RPM_TEMPLATE.format(**config)


def build(config: T.Dict[str, T.Any]):
    specstr = generate_spec_str(config)
    print(specstr)


def _load_toml(tomlfile: Path):
    assert tomlfile.exists(), f"{tomlfile} does not exists"
    cfg = toml.load(tomlfile)
    cfg["basepath"] = tomlfile.resolve().parent
    return cfg


def gen_dockerfile(toml: Path, distribution: str):
    """Generate a Dockerfile for given distribution"""
    config = _load_toml(toml)
    basedir = toml.parent

    specstr = pkgr.rpm.generate_spec_str(config)
    logger.debug(f"{specstr}")
    if specfile is None:
        specfile = Path(f'{config["name"]}.spec')
        logger.info(f"Using default specfile: {specfile}")

    with specfile.open("w") as f:
        f.write(specstr)
    logger.info(f"Wrote {specfile}")


@app.command()
def generate(
    toml: Path,
    distribution: str,
    specfile: T.Optional[Path] = None,
    dockerfile: T.Optional[Path] = None,
):
    """Generate build files and Dockerfile"""

    pkgr.config.load(toml)
    config = pkgr.config.get()
    assert config

    assert distribution
    datadir = pkgr.config.config_dir() / Path(distribution)
    datadir.mkdir(exist_ok=True)
    logger.info(f"Creating {datadir} for creating distribution.")

    specstr = pkgr.rpm.generate_spec_str(config)
    if specfile is None:
        specfile = datadir / Path(f'{config["name"]}.spec')
        logger.info(f"Using default specfile: {specfile}")

    with specfile.open("w") as f:
        f.write(specstr)
    logger.info(f"Wrote {specfile}")

    if dockerfile is None:
        dockerfile = datadir / 'Dockerfile'

    with dockerfile.open('w') as f:
        DOCKER = pkgr.templates.DOCKER
        f.write(DOCKER)
    logger.info(f'Wrote docker file to {dockerfile}')



if __name__ == "__main__":
    app()
