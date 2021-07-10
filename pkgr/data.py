__author__ = "Dilawar Singh"
__email__ = "dilawar.s.rajput@gmail.com"

from loguru import logger
import urllib.request
import json

DOCKER_IO_URL = "https://registry.hub.docker.com/v2/repositories/library/{dist}/tags"


IMAGES = dict(
    opensuse={"latest": "opensuse/tumbleweed", "15.3": "opensuse/leap:15.3"},
    centos={"latest": "centos:latest", "8": "centos:8", "7": "centos:7"},
    fedora={"latest": "fedora:latest"},
    ubuntu={
        "latest": "ubuntu:latest",
        "20.04": "ubuntu:20.04",
        "18.04": "ubuntu:18.04",
    },
)


def get_image(distribution: str, release: str = "latest") -> str:
    global IMAGES
    dist = distribution.lower()
    if dist not in IMAGES:
        loguru.warning(f"{dist} is not supported. Supported OS: {IMAGES.keys()}")
        quit(0)
    images = IMAGES[dist]
    return images[release]


def find_tags(dist: str):
    url = DOCKER_IO_URL.format(dist=dist)
    tags = json.loads(urllib.request.urlopen(url).read())
    return [x["name"] for x in tags["results"]]


def main():
    tags = find_tags("centos")
    print(tags)


if __name__ == "__main__":
    main()
