__author__ = "Dilawar Singh"
__email__ = "dilawar.s.rajput@gmail.com"

import typing as T

import pkgr.config
import pkgr.templates
import pkgr.config
import pkgr.data

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


@app.command()
def generate(
    toml: Path,
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
    datadir = pkgr.config.config_dir() / Path(distribution)
    datadir.mkdir(exist_ok=True)
    logger.info(f"Creating {datadir} for creating distribution.")

    specstr = _generate_spec_str(config)

    if specfile is None:
        specfile = datadir / Path(f'{config["name"]}.spec')
        logger.info(f"Using default specfile: {specfile}")

    with specfile.open("w") as f:
        f.write(specstr)
    logger.info(f"Wrote {specfile}")

    if dockerfile is None:
        dockerfile = datadir / "Dockerfile"

    with dockerfile.open("w") as f:
        DOCKER = pkgr.templates.DOCKER
        DOCKER.format(
            image=pkgr.data.get_image(distribution, release),
            maintainer=pkgr.config.get_val("maintainer"),
        )
        f.write(DOCKER)
    logger.info(f"Wrote docker file to {dockerfile}")


if __name__ == "__main__":
    app()
