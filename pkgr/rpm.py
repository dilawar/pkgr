__author__ = "Dilawar Singh"
__email__ = "dilawar.s.rajput@gmail.com"

import typing as T

import pkgr.config

RPM_TEMPLATE: str = """
Name:     {name}
Version:  {version}
Release:  1%{{?dist}}
Summary:  {summary}

License: {license}
URL: {url}
Source0:  {source}

{build_requires}

{requires}

%description
{description}

%prep
{prep}

%build
{build}

%install
{install}

%files
{files}

%changelog
{changelog}
"""


def _gen_build_requires(builddeps: T.List[str]) -> str:
    return "\n".join([f"BuildRequires: {x}" for x in builddeps])


def _gen_requires(reqs: T.List[str]) -> str:
    return "\n".join([f"Requires: {x}" for x in reqs])


def generate_spec_str(config: T.Dict[str, T.Any]) -> str:
    global RPM_TEMPLATE
    config["build_requires"] = _gen_build_requires(config["builddeps"].get("rpm", []))
    config["requires"] = _gen_requires(
        config.get("deps", dict(rpm=[])).get("rpm", [])
    )
    config["prep"] = pkgr.config.get(config, "prep", "%autosetup")
    config["build"] = pkgr.config.get(config, "build", "%configure\n%make_build")
    config["install"] = pkgr.config.get(
        config, "install.bash", "rm -rf $RPM_TEMPLATE\n%make_install"
    )
    config["files"] = pkgr.config.get(config, "files", [])
    config["changelog"] = pkgr.config.get(config, "changelog", [])
    return RPM_TEMPLATE.format(**config)


def build(config: T.Dict[str, T.Any]):
    specstr = generate_spec_str(config)
    print(specstr)
