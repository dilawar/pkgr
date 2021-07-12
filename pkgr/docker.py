__author__ = "Dilawar Singh"
__email__ = "dilawar.s.rajput@gmail.com"

import sys
import subprocess

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
    assert distribution
    assert release
    logger.info(f"Generating required install list for {distribution}-{release}")
    INSTALL_CMD: str = pkgr.data.get_install_cmd(distribution, release)
    TO_INSTALL: str = pkgr.data.get_default_installs(distribution, release)
    runs = [f"{INSTALL_CMD} {TO_INSTALL}"]
    return "\n".join([f"RUN {x}" for x in runs])


def add_build_depdencies(distribution: str, release: str):
    builddeps = pkgr.common.get_val_dist_specific("builddeps", "rpm")
    assert builddeps
    install_cmd = pkgr.data.get_install_cmd(distribution, release)
    assert install_cmd
    return f"RUN {install_cmd} {' '.join(builddeps)}"


def add_build_command(pkgtype: str, cmd_options) -> str:
    if pkgtype == "rpm":
        pkg_build_cmd = pkgr.rpm.build_command(cmd_options)
    else:
        raise NotImplementedError(f"{pkgtype} is not supported.")
    return f"CMD {pkg_build_cmd}"


def run_docker(image: str, pkgtype: str):
    """Run docker"""
    extra = []
    if pkgtype == "rpm":
        extra = [
            "--mount",
            f"type=bind,source={pkgr.config.work_dir()},target=/root/rpmbuild",
        ]

    container_name = (
        f"pkgr-{pkgtype}-{pkgr.config.get_val('distribution')}"
        + f"-{pkgr.config.get_val('arch')}"
    )
    cmd = ["docker", "run", "-l", container_name, "-t", *extra, image]
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


def write_docker(pkgtype: str, *, cmd_options: str = ""):
    global DOCKER

    author = pkgr.config.get_val("author")
    maintainer = pkgr.config.get_val("maintainer", author)

    distribution, release = pkgr.config.get_val("distribution").split("-")
    assert distribution
    assert release

    image = pkgr.data.get_image(distribution, release)

    prepare = pkgr.data.get_prepare(distribution, release)
    run = _get_run_commands(distribution, release)
    install = add_build_depdencies(distribution, release)

    cmd = add_build_command("rpm", cmd_options)

    __c = pkgr.common.check_valid_str

    dockerfile = pkgr.common.default_dockerfile()
    with dockerfile.open("w") as f:
        DOCKER = DOCKER.format(
            image=__c(image),
            author=__c(author),
            maintainer=__c(maintainer),
            prepare=__c(prepare),
            install=__c(install),
            run=__c(run),
            cmd=__c(cmd),
            RPM_BUILD_DIR="/root/rpmbuild",
        )
        f.write(DOCKER)
    logger.info(f"Wrote docker file to {dockerfile}")


def build(dockerfile: Path, pkgtype: str):
    """Build dockerfile"""
    logger.info(f"Building using {dockerfile} for package type {pkgtype}")
    label = "pkgr/build"
    cmd = ["docker", "build", "-t", label, "."]
    subprocess.run(cmd, check=True, cwd=dockerfile.parent)
    run_docker(label, pkgtype)
