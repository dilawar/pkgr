__author__ = "Dilawar Singh"
__email__ = "dilawar.s.rajput@gmail.com"

import typing as T

import pkgr.config


def get_list_pkgs(key: str, pkgtype: str) -> T.List[str]:
    distribution = pkgr.config.get_val("distribution").split("-")
    dist, release = distribution
    vals = (
        pkgr.config.get_val(f"{key}.{dist}-{release}")
        or pkgr.config.get_val(f"{key}.{dist}{release}")
        or pkgr.config.get_val(f"{key}.{dist}")
        or pkgr.config.get_val(f"{key}.{pkgtype}")
    )
    assert vals is not None, f"Nothing found for {key}.{pkgtype} in config"
    vals = vals.strip() or []
    if isinstance(vals, str):
        vals = [x for x in vals.split() if x.strip()]

    assert isinstance(vals, T.List), f"Expected a list, got {vals}"
    return vals

def check_valid_str(val):
    assert val is not None
    if isinstance(val, str):
        assert len(val) > 0, f"{val} is empty string"
        assert val not in ['None', 'NONE'], "Cant be None"
    else:
        raise ValueError("Only strings are allowed")
    return val
