__author__ = "Dilawar Singh"
__email__ = "dilawar.s.rajput@gmail.com"

import pkgr.templates
import pkgr.config

from loguru import logger

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
