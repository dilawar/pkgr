__author__ = "Dilawar Singh"
__email__ = "dilawar.s.rajput@gmail.com"

import sys
import subprocess
import time
import typing as T

from pathlib import Path

from loguru import logger
import docker


import pkgr.data
import pkgr.config


DOCKER_BUILD_DIR = "/pkgr/rpm"


def init_docker_container(image: str):
    client = docker.DockerClient(base_url="unix://var/run/docker.sock", timeout=4)

    return client.containers.run(
        image,
        tty=True,
        detach=True,
        auto_remove=True,
        mounts=[
            docker.types.Mount(
                target=DOCKER_BUILD_DIR, source=str(pkgr.config.work_dir()), type="bind"
            )
        ],
        working_dir=DOCKER_BUILD_DIR,
    )


def get_run_commands() -> str:
    INSTALL_CMD: str = pkgr.data.get_install_cmd()
    TO_INSTALL: str = pkgr.data.get_default_installs()
    return f"{INSTALL_CMD} {TO_INSTALL}"


def add_build_depdencies():
    builddeps = pkgr.common.get_val_dist_specific("builddeps", "rpm")
    assert builddeps
    install_cmd = pkgr.data.get_install_cmd()
    assert install_cmd
    return f"{install_cmd} {' '.join(builddeps)}"


def add_build_commands(pkgtype: str, cmd_options) -> T.List[str]:
    if pkgtype == "rpm":
        return pkgr.rpm.build_command(cmd_options)
    else:
        raise NotImplementedError(f"{pkgtype} is not supported.")


def run_docker(image: str, pkgtype: str) -> str:
    """Run docker"""
    extra = []
    builddir = pkgr.docker.DOCKER_BUILD_DIR
    if pkgtype == "rpm":
        extra = [
            "--mount",
            f"type=bind,source={pkgr.config.work_dir()},target={builddir}",
        ]
    else:
        raise NotImplementedError(f"Not implemented: {pkgtype}")

    container_name = (
        f"pkgr-{pkgtype}-{pkgr.config.get_val('distribution')}"
        + f"-{pkgr.config.get_val('arch')}"
    )
    cmd = ["docker", "run", "--name", container_name, "-t", *extra, image]
    logger.info(f"Running: {' '.join(cmd)}")
    return container_name

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


def copy_artifact(container):
    pass


def run_in_container(container, cmds):
    for cmd in cmds:
        logger.info(f"Executing in container: `{cmd}`")
        res = container.exec_run(cmd, stream=True, demux=False)
        for line in res.output:
            # logger.info(f"{line.decode('utf8').strip()}")
            print(f"{line.decode('utf8')}", end="")
            sys.stdout.flush()


def build(pkgtype: str, cmd_options):
    """Build dockerfile"""

    image = pkgr.data.get_image()
    assert image
    logger.info(f"Creating a container from {image}")

    container = init_docker_container(image)
    time.sleep(2)

    prepare = pkgr.data.get_prepare()
    run = get_run_commands()
    install = add_build_depdencies()
    run_in_container(container, [prepare, run, install])

    buildcmd = add_build_commands("rpm", cmd_options)
    run_in_container(container, buildcmd)
