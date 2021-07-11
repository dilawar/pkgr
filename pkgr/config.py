__author__ = "Dilawar Singh"
__email__ = "dilawar.s.rajput@gmail.com"

import re
from pathlib import Path
import typing as T

import toml

from loguru import logger

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


def rewrite(val: str, k: str, config: T.Dict[str, T.Any]) -> T.Any:
    """rewrite a term by replacing ${foo} with config[foo].

    Parameters
    ----------
    val :
        val
    k :
        k
    config : T.Dict[str, T.Any]
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


def walk(config: T.Dict[str, T.Any], func: T.Callable):
    """Walk over values of config"""
    for k, v in config.items():
        if isinstance(v, T.Dict):
            config[k] = walk(v, func)
        elif isinstance(v, T.List):
            config[k] = [func(x, k, config) for x in v]
        elif isinstance(v, str):
            config[k] = func(v, k, config)
    return config


def load(tomlfile: Path):
    global config_
    global config_dir_
    config_dir_ = tomlfile.resolve().parent
    config_ = walk(toml.load(tomlfile), rewrite)
    return config_


def config() -> T.Dict[str, T.Any]:
    assert config_, "Did you call pkgr.config.load?"
    return config_


def config_dir() -> Path:
    assert config_dir_.exists(), "Did you call pkgr.config.load?"
    return config_dir_


def test_config_subs():
    sdir = Path(__file__).parent
    configfile = sdir / ".." / "pkgr.toml"
    config = load(configfile)
    print(config)


if __name__ == "__main__":
    test_config_subs()
