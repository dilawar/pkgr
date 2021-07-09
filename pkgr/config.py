__author__           = "Dilawar Singh"
__email__            = "dilawar.s.rajput@gmail.com"

from pathlib import Path
import typing as T

def _dict2str(val, basepath: T.Optional[Path] = None):
    if 'file' in val:
        assert basepath is not None
        return (basepath / val['file']).open().read()
    if not val:
        return ''
    raise NotImplementedError(type(val))

def _to_str(val: T.Any, basepath: T.Optional[Path] = None) -> str:
    if isinstance(val, list):
        return '\n'.join(val)
    if isinstance(val, dict):
        return _dict2str(val, basepath)
    return str(val)

def get(config: T.Dict[str, T.Any], key: str, default=None):
    keys = key.split('.')
    val = config.copy()
    while keys:
        k = keys.pop(0)
        val = val.get(k, default)
        if default is not None and val == default:
            break
    assert val is not None
    return _to_str(val, config['basepath'])
