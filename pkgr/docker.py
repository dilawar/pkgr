__author__ = "Dilawar Singh"
__email__ = "dilawar.s.rajput@gmail.com"

import sys
import subprocess

import pkgr.templates
import pkgr.data
import pkgr.config

from pathlib import Path
from loguru import logger

# Dockefile template.
DOCKER = """
FROM {image}
MAINTAINER {author}

# workdir: /root/rpmbuild for rpm.
# TODO: debian?
# Make sure that `.` has the required layout.
ADD . {RPM_BUILD_DIR}
WORKDIR {RPM_BUILD_DIR}

# Prepare docker image. Call `apt update`, setup additional repo etc.
{prepare}

# Install required packages to build successfully.
{install}

# Extra RUN ....
{run}

# CMD .. which build the package. e.g. rpmbuild -a ... etc.
{cmd}
"""


def _get_run_commands(distribution: str, release: str) -> str:
    INSTALL_CMD: str = pkgr.data.get_install_cmd(distribution, release)
    TO_INSTALL: str = pkgr.data.get_default_installs(distribution, release)
    runs = [f"{INSTALL_CMD} {TO_INSTALL}"]
    return "\n".join([f"RUN {x}" for x in runs])


def add_build_depdencies(distribution: str, release: str):
    builddeps = pkgr.config.get_val(f"builddeps.{distribution}")
    install_cmd = pkgr.data.get_install_cmd(distribution, release)
    assert install_cmd
    return f"RUN {install_cmd} {builddeps}"


def add_build_command(specname: str) -> str:
    return f'CMD ["rpmbuild", "-ba", "SPECS/{specname}"]'


def run_docker(label: str):
    cmd = ["docker", "run", "-t", label]
    logger.info(f"Running: {' '.join(cmd)}")
    popen = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        universal_newlines=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    _stdout = popen.stdout if popen.stdout is not None else []
    for line in _stdout:
        sys.stdout.write(f" {line}")
        sys.stdout.flush()
    popen.wait(500)


def write_docker(dockerfile, distribution: str, release: str):
    global DOCKER
    author = pkgr.config.get_val("author")
    maintainer = pkgr.config.get_val("maintainer", author)
    image = pkgr.data.get_image(distribution, release)

    prepare = pkgr.data.get_prepare(distribution, release)
    run = _get_run_commands(distribution, release)
    install = add_build_depdencies(distribution, release)
    cmd = add_build_command(f"{pkgr.config.get_val('name')}.spec")

    with dockerfile.open("w") as f:
        DOCKER = DOCKER.format(
            image=image,
            author=author,
            maintainer=maintainer,
            prepare=prepare,
            install=install,
            run=run,
            cmd=cmd,
            RPM_BUILD_DIR="/root/rpmbuild"
        )
        f.write(DOCKER)
    logger.info(f"Wrote docker file to {dockerfile}")


def build(dockerfile: Path):
    """Build dockerfile"""
    logger.info(f"Building using {dockerfile}")
    label = "pkgr/build"
    subprocess.run(
        ["docker", "build", "-t", label, "."], check=True, cwd=dockerfile.parent
    )
    run_docker(label)
