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

SPEC_TEMPLATE: str = """
Name:       {name}
Version:    {version}
Release:    1%{{?dist}}
Summary:    {summary}

License:    {license}
URL:        {url}
Source0:    {source}

{build_requires}

{requires}

%description
{description}

%prep
{configure}

%build
{build}

%install
{install}

%files
{files}

%changelog
{changelog}
"""


def _gen_build_requires(builddeps: T.List[str]) -> str:
    return "\n".join([f"BuildRequires: {x}" for x in builddeps])


def _gen_requires(reqs: T.List[str]) -> str:
    return "\n".join([f"Requires: {x}" for x in reqs])


def generate_spec_str() -> str:
    options = {}
    options["build_requires"] = _gen_build_requires(options["builddeps"].get("rpm", []))
    options["requires"] = _gen_requires(
        options.get("deps", dict(rpm=[])).get("rpm", [])
    )
    options["optionsure"] = pkgr.config.get_val("optionsure.spec") or "%autosetup"
    options["build"] = pkgr.config.get_val("build.rpm") or "%optionsure\n%make_build"
    options["install"] = (
        pkgr.config.get_val("install.rpm") or "rm -rf $SPEC_TEMPLATE\n%make_install"
    )
    options["files"] = pkgr.config.get_val("files") or ""
    options["changelog"] = pkgr.config.get_val("changelog.rpm") or ""
    return SPEC_TEMPLATE.format(**options)


def default_dockerfile(distribution, release) -> Path:
    return pkgr.config.work_dir() / "Dockerfile"


def init_workdir_tree(wdir: Path):
    """Equivalent to rpmdev-setuptree equivalent"""
    assert wdir.exists() and wdir.is_dir()
    for x in "BUILD RPMS SOURCES SPECS SRPMS".split():
        (wdir / x).mkdir(exist_ok=True)
        assert (wdir / x).is_dir()


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

    init_workdir_tree(pkgr.config.work_dir())

    specfile = (
        pkgr.config.work_dir() / "SPECS" / f'{pkgr.config.get_val("name")}.spec'
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
