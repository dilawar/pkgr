__author__ = "Dilawar Singh"
__email__ = "dilawar.s.rajput@gmail.com"

import typing as T

import pkgr.config
import pkgr.templates
import pkgr.config
import pkgr.data
import pkgr.docker

from pathlib import Path
from loguru import logger

import typer


app = typer.Typer()


def _gen_build_requires(builddeps: T.List[str]) -> str:
    return "\n".join([f"BuildRequires: {x}" for x in builddeps])


def _gen_requires(reqs: T.List[str]) -> str:
    return "\n".join([f"Requires: {x}" for x in reqs])


def _generate_spec_str(config: T.Dict[str, T.Any]) -> str:
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


def default_dockerfile(distribution, release) -> Path:
    return pkgr.config.config_dir() / distribution / "Dockerfile"


@app.command()
def generate(
    distribution: str,
    specfile: T.Optional[Path] = None,
    dockerfile: T.Optional[Path] = None,
    release: str = "latest",
    toml: Path = Path("pkgr.toml"),
):
    """Generate build files and Dockerfile"""

    pkgr.config.load(toml)
    config = pkgr.config.config()
    assert config

    assert distribution
    specstr = _generate_spec_str(config)

    if specfile is None:
        specfile = pkgr.config.config_dir() / f'{config["name"]}.spec'
        logger.info(f"Using default specfile: {specfile}")

    with specfile.open("w") as f:
        f.write(specstr)
    logger.info(f"Wrote {specfile}")

    dockerfile = (
        default_dockerfile(distribution, release) if dockerfile is None else dockerfile
    )
    pkgr.docker.write_docker(dockerfile, config, distribution, release)


@app.command()
def build(
    distribution: str,
    dockerfile: T.Optional[Path] = None,
    release: str = "latest",
    toml: Path = Path("pkgr.toml"),
):
    pkgr.config.load(toml)
    dockerfile = (
        default_dockerfile(distribution, release) if dockerfile is None else dockerfile
    )
    assert dockerfile.exists(), f"{dockerfile} not found. Did you run the generate step"
    pkgr.docker.build(dockerfile)


if __name__ == "__main__":
    app()
