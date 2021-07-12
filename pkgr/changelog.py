__author__ = "Dilawar Singh"
__email__ = "dilawar.s.rajput@gmail.com"

import typer
import datetime

from pathlib import Path
import typing as T

from loguru import logger
import click

import pkgr.config

app = typer.Typer()


def collect_changelog() -> str:
    MARKER = '# Everything below is ignored\n'
    log = click.edit('\n\n' + MARKER)
    if log is not None:
        return log.split(MARKER, 1)[0].rstrip('\n')


@app.command()
def rpm(
    changefile: T.Optional[Path] = None,
    toml: Path = Path("pkgr.toml"),
    author: T.Optional[str] = None,
    logs: T.Optional[str] = None,
):
    pkgr.config.load(toml)

    if author is None:
        author = pkgr.config.get_val("author") or pkgr.config.get_val("maintainer")
    assert author, f"Could not determine the author of changelog"

    version = pkgr.config.get_val("version")
    assert version

    changelog = (
        f'* {datetime.datetime.now().strftime("%a %b %d %Y")} {author} - {version}'
    )
    changelog += collect_changelog() if logs is None else logs

    if changelog is None:
        print(changelog)
        return

    logger.info("Appending changelog to {changefile}")
    with Path(changefile).open("a") as f:
        f.write(changelog)


if __name__ == "__main__":
    app()
