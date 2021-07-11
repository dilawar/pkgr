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


def generate_spec_str() -> str:
    RPM_TEMPLATE = pkgr.templates.RPM
    config = pkgr.config.config()
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
    return pkgr.config.work_dir() / "Dockerfile"


@app.command()
def generate(
    distribution: str,
    arch: str = "x86_64",
    specfile: T.Optional[Path] = None,
    dockerfile: T.Optional[Path] = None,
    release: str = "latest",
    toml: Path = Path("pkgr.toml"),
):
    """Generate build files and Dockerfile"""
    assert distribution

    pkgr.config.load(toml)
    pkgr.config.set_val("distribution", (distribution, release))
    assert "distribution" in pkgr.config.config()

    pkgr.config.set_val("arch", arch)
    assert "arch" in pkgr.config.config()

    pkgr.config.setup_config_dir()
    specstr = generate_spec_str()

    specfile = (
        pkgr.config.work_dir() / f'{pkgr.config.get_val("name")}.spec'
        if specfile is None
        else specfile
    )

    specfile.write_text(specstr)
    logger.info(f"Wrote specfile {specfile}")

    dockerfile = (
        default_dockerfile(distribution, release) if dockerfile is None else dockerfile
    )
    pkgr.docker.write_docker(dockerfile, distribution, release)


@app.command()
def build(
    distribution: str,
    release: str = "latest",
    arch: str = "x86_64",
    dockerfile: T.Optional[Path] = None,
    toml: Path = Path("pkgr.toml"),
):
    generate(distribution, arch, None, dockerfile, release, toml)
    dockerfile = (
        default_dockerfile(distribution, release) if dockerfile is None else dockerfile
    )
    assert dockerfile.exists(), f"{dockerfile} not found. Did you run the generate step"
    pkgr.docker.build(dockerfile)


if __name__ == "__main__":
    app()
