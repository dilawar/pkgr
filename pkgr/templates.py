__author__           = "Dilawar Singh"
__email__            = "dilawar.s.rajput@gmail.com"

RPM: str = """
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

DOCKER = """
FROM: {image}
MAINTAINER: {author}

WORKDIR /work

{run}

{build}
"""
