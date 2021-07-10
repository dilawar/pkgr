__author__ = "Dilawar Singh"
__email__ = "dilawar.s.rajput@gmail.com"

import toml
from pathlib import Path
import typing as T

config_: T.Dict[str, T.Any] = {}
config_dir_: T.Optional[Path] = None


def _dict2str(val, basepath: T.Optional[Path] = None):
    if "file" in val:
        assert basepath is not None
        return (basepath / val["file"]).open().read()
    if not val:
        return ""
    raise NotImplementedError(type(val))


def _to_str(val: T.Any, basepath: T.Optional[Path] = None) -> str:
    if isinstance(val, list):
        return "\n".join(val)
    if isinstance(val, dict):
        return _dict2str(val, basepath)
    return str(val)


def get(config: T.Dict[str, T.Any], key: str, default=None):
    keys = key.split(".")
    val = config.copy()
    while keys:
        k = keys.pop(0)
        val = val.get(k, default)
        if default is not None and val == default:
            break
    assert val is not None
    return _to_str(val, config_dir_)


def get_val(key: str, default=None):
    global config_
    val = config_.copy()
    keys = key.split(".")
    while keys:
        k = keys.pop(0)
        val = val.get(k, default)
        if default is not None and val == default:
            break
    assert val is not None, f"{key} has missing value"
    return _to_str(val, config_dir_)


def load(tomlfile: Path):
    global config_
    global config_dir_
    config_ = toml.load(tomlfile)
    config_dir_ = tomlfile.resolve().parent
    return config_


def config() -> T.Dict[str, T.Any]:
    assert config_, "Did you call pkgr.config.load?"
    return config_


def config_dir() -> Path:
    assert config_dir_.exists(), "Did you call pkgr.config.load?"
    return config_dir_
