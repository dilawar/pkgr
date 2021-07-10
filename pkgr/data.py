__author__ = "Dilawar Singh"
__email__ = "dilawar.s.rajput@gmail.com"

from loguru import logger

import typing as T
import urllib.request
import json
import re

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


# regex -> install commands.
INSTALL_CMDS = json.loads(
    """{
        "debian.*|ubuntu.*" : "apt install -y",
        "opensuse.*" : "zypper install -y",
        "centos7.*" : "yum install -y",
        "centos.*|fedora.*" : "dnf install -y"
        }"""
)

DEFAULT_APPS = json.loads(
    """{
        "debian.*|ubuntu.*" : "dpkg-dev dpkg build-depends pbuilder",
        "opensuse.*|centos.*|fedora.*" : "rpmlint rpm"
        }"""
)


def _get_best_match(data: T.Dict[str, T.Any], key: str) -> T.Any:
    global INSTALL_CMDS
    _keys = list(data.keys())
    _k = [x for x in _keys if re.match(x, key)]
    assert _k, f"No match found for {key}"
    return data[_k[0]]


def get_install_cmd(dist, release) -> str:
    key = f"{dist}{release}"
    return _get_best_match(INSTALL_CMDS, key)


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


def test_install_cmds():
    assert get_install_cmd("centos", "8") == "dnf install -y"
    assert get_install_cmd("centos", "7") == "yum install -y"
    assert get_install_cmd("debian", "10") == "apt install -y"
    assert get_install_cmd("debian", "11") == "apt install -y"
    assert get_install_cmd("ubuntu", "20.04") == "apt install -y"
    assert get_install_cmd("opensuse", "15.3") == "zypper install -y"


if __name__ == "__main__":
    test_install_cmds()
