__author__ = "Dilawar Singh"
__email__ = "dilawar.s.rajput@gmail.com"

import pkgr.templates
import pkgr.data
import pkgr.config

from loguru import logger


def _get_run_commands(config, distribution, release) -> str:
    INSTALL_CMD: str = pkgr.data.get_install_cmd(distribution, release)
    TO_INSTALL: str = pkgr.data.default_install_pkgs(distribution, release)
    runs = [f"{INSTALL_CMD} {TO_INSTALL}"]
    return "\n".join([f"RUN {x}" for x in runs])


def write_docker(dockerfile, config, distribution: str, release: str):
    author = pkgr.config.get_val("author")
    maintainer = pkgr.config.get_val("maintainer", author)

    image = pkgr.data.get_image(distribution, release)

    with dockerfile.open("w") as f:
        DOCKER = pkgr.templates.DOCKER
        DOCKER = DOCKER.format(image=image, author=author, maintainer=maintainer)
        f.write(DOCKER)

    logger.info(f"{DOCKER}")
    logger.info(f"Wrote docker file to {dockerfile}")
