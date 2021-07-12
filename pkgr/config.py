__author__ = "Dilawar Singh"
__email__ = "dilawar.s.rajput@gmail.com"

import re
from pathlib import Path
import typing as T
from urllib.parse import urlparse

import toml  # type:ignore

from loguru import logger

import pkgr
import pkgr.archive

config_dir_: Path = Path(".").resolve()

# declare type.
ConfigType = T.MutableMapping[str, T.Any]

config_: ConfigType = {}


def _dict2str(val, basepath: T.Optional[Path] = None) -> str:
    if "file" in val:
        assert basepath is not None
        return str((basepath / val["file"]).open().read())
    if not val:
        return ""

    raise NotImplementedError(type(val))
    return ""


def _to_str(val, basepath: T.Optional[Path] = None) -> str:
    if isinstance(val, list):
        return "\n".join(val)
    if isinstance(val, dict):
        return _dict2str(val, basepath)
    return str(val)


def set_val(key: str, val, subconfig=None):
    global config_
    assert key
    assert val
    if subconfig is None:
        subconfig = config_
    if "." not in key:
        subconfig[key] = val
        return
    fs = key.split(".", 1)
    return set_val(fs[1], val, subconfig[fs[0]])


def get(config: ConfigType, key: str, default={}) -> str:
    keys = key.split(".")
    val = config
    while keys:
        k = keys.pop(0)
        val = val.get(k, default)
        if val == default:
            break
    assert val
    return _to_str(val, config_dir_)


def get_val(key: str, default=None):
    global config_
    val = config_
    keys = key.split(".")
    while keys:
        k = keys.pop(0)
        val = val.get(k, default)
        if val is None:
            return None
    return _to_str(val, config_dir_)


def rewrite(val: str, k: str, config: ConfigType):
    """rewrite a term after:

    1. replacing ${foo} with config[foo].

    Parameters
    ----------
    val :
        val
    k :
        k
    config : ConfigType
        config

    Returns
    -------
    rewritten term if rewrite was possible, original term otherwise.
    """
    m = re.search(r"\$\{(.+?)\}", val)
    if not m:
        return val

    if config.get(m.group(1), None) is not None:
        assert isinstance(config[m.group(1)], str)
        val = val.replace(m.group(0), config[m.group(1)])

    return val


def get_file_content(filestr: str) -> str:
    assert filestr.startswith("file://")
    file = pkgr.config.config_dir() / filestr[7:]
    assert file.exists(), f"{filestr} did not resolve to a readable file: {file}"
    return file.open().read()


def replace_file_with_content(section) -> None:
    # change file:// with the content of the file.
    global config_
    assert section
    if section not in config_:
        return

    secval = config_[section]
    if isinstance(secval, str):
        if secval.startswith("file://"):
            config_[section] = get_file_content(secval)
        return

    # it must be dict otherwise. Go one level deep and no deeper.
    for k, val in config_[section].items():
        if not isinstance(val, str):
            continue
        if val.startswith("file://"):
            config_[section][k] = get_file_content(val)


def walk(config: ConfigType, func: T.Callable) -> ConfigType:
    """Walk over values of config"""
    for k, v in config.items():
        if isinstance(v, T.Dict):
            config[k] = walk(v, func)
        elif isinstance(v, T.List):
            config[k] = [func(x, k, config) for x in v]
        elif isinstance(v, str):
            config[k] = func(v, k, config)
    return config


def setup_config_dir(config: ConfigType = {}):
    """Make sure work directory is ready.

    1. Generate source archive.
    2. Verify the source archive (if possible).
    3. ?

    Parameters
    ----------
    config : ConfigType
        config
    cdir : Path
        cdir
    """
    global config_

    srcstr = config_["source"].split("#", 1)
    assert len(srcstr) == 2, (
        f"Invalid format source. Expected <file_or_url>#<archive_path>"
        ". For example `file://.#pkgr-0.1.0.tar.gz'"
    )
    src, tgt = srcstr
    tgtfile = work_dir() / "SOURCES" / tgt

    try:
        urlparse(src)
        raise NotImplementedError("URL support is not implemnted")
    except Exception:
        # its a  filesystem.
        if "file://" in src:
            src = src[7:]
        src = Path(src)
        assert src.is_dir(), f"Source directory {src} is not a directory"
        pkgr.archive.write_archive(tgtfile, src)

    assert tgtfile.exists(), f"{tgtfile} is not created."

    config_["source"] = tgt


def load(tomlfile: Path) -> ConfigType:
    global config_
    global config_dir_
    config_dir_ = tomlfile.resolve().parent
    config_ = walk(toml.load(tomlfile), rewrite)
    config_["pkgr_version"] = pkgr.__version__
    replace_file_with_content("description")
    replace_file_with_content("changelog")
    return config_


def config() -> ConfigType:
    assert config_, "Did you call pkgr.config.load?"
    return config_


def config_dir() -> Path:
    assert config_dir_.exists(), "Did you call pkgr.config.load?"
    return config_dir_


def work_dir() -> Path:
    global config_
    assert config_dir_.exists(), "Did you call pkgr.config.load?"
    assert "distribution" in config_, "'distribution' not found."
    wdir = config_dir_ / f"{pkgr.config.get_val('distribution')}"
    wdir.mkdir(parents=True, exist_ok=True)
    return wdir


def get_distribution() -> T.Tuple[str, str]:
    return get_val("distribution").split("-")


def test_config_subs():
    sdir = Path(__file__).parent
    configfile = sdir / ".." / "pkgr.toml"
    config = load(configfile)
    assert config
    assert config["version"] in config["source"]


def test_source_rewrite():
    sdir = Path(__file__).parent
    configfile = sdir / ".." / "pkgr.toml"
    config = load(configfile)
    assert config
    assert config["version"] in config["source"]


def test_set_val():
    global config_
    config_ = dict(a=dict(b=5, c=10, d=dict(xx=5)), z=9)
    set_val("a.b", 10)
    assert config_["a"]["b"] == 10
    set_val("a.d.xx", 9)
    assert config_["a"]["d"]["xx"] == 9


if __name__ == "__main__":
    test_set_val()
    test_config_subs()
