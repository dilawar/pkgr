__author__ = "Dilawar Singh"
__email__ = "dilawar.s.rajput@gmail.com"

from loguru import logger

import typing as T
import urllib.request
import json
import re


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

# prepare section for docker image.
PREPARE = json.loads(
    """{
        "debian.*|ubuntu.*" : "RUN apt update",
        "opensuse.*" : "RUN zypper ref",
        "centos.*" : "RUN yum install -y epel-release"
        }"""
)


# regex -> install commands.
INSTALL_CMDS = json.loads(
    """{
        "debian.*|ubuntu.*" : "apt install -y",
        "opensuse.*" : "zypper install -y",
        "centos-7.*" : "yum install -y",
        "centos.*|fedora.*" : "dnf install -y"
        }"""
)

# default apps.
DEFAULT_APPS = json.loads(
    """{
        "debian.*|ubuntu.*" : "dpkg-dev dpkg build-depends pbuilder",
        "opensuse.*|centos.*|fedora.*" : "rpmlint rpm rpm-build rpmdevtools"
        }"""
)


def _get_best_match(data: T.Dict[str, T.Any], key: str) -> T.Any:
    global INSTALL_CMDS
    _keys = list(data.keys())
    _k = [x for x in _keys if re.match(x, key)]
    if not _k:
        return ""  # empty value.
    val = data[_k[0]]
    assert val
    return val


def get_install_cmd(dist: str, release: str) -> str:
    key = f"{dist}-{release}"
    return str(_get_best_match(INSTALL_CMDS, key))


def get_prepare(dist: str, release: str) -> str:
    key = f"{dist}-{release}"
    return str(_get_best_match(PREPARE, key))


def get_image(distribution: str, release: str = "latest") -> str:
    global IMAGES
    dist = distribution.lower()
    if dist not in IMAGES:
        logger.warning(f"{dist} is not supported. Supported OS: {IMAGES.keys()}")
        quit(0)
    images = IMAGES[dist]
    return images[release]


# def find_tags(dist: str):
#     DOCKER_IO_URL = "https://registry.hub.docker.com/v2/repositories/library/{dist}/tags"
#     url = DOCKER_IO_URL.format(dist=dist)
#     tags = json.loads(urllib.request.urlopen(url).read())
#     return [x["name"] for x in tags["results"]]


def get_default_installs(dist: str, release: str) -> str:
    key = f"{dist}{release}"
    return str(_get_best_match(DEFAULT_APPS, key))


def test_install_cmds():
    assert get_install_cmd("centos", "8") == "dnf install -y"
    assert get_install_cmd("centos", "7") == "yum install -y"
    assert get_install_cmd("debian", "10") == "apt install -y"
    assert get_install_cmd("debian", "11") == "apt install -y"
    assert get_install_cmd("ubuntu", "20.04") == "apt install -y"
    assert get_install_cmd("opensuse", "15.3") == "zypper install -y"


if __name__ == "__main__":
    test_install_cmds()
