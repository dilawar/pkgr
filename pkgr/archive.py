__author__ = "Dilawar Singh"
__email__ = "dilawar.s.rajput@gmail.com"

import subprocess

import typing as T
from pathlib import Path
from loguru import logger

import pkgr.config


def _to_files(txt: str, rootdir: Path) -> T.List[Path]:
    files = txt.strip().split("\n")
    return [Path(f) for f in files if (rootdir / f).exists()]


def list_src_files(source_dir: Path) -> T.List[Path]:
    logger.info(f" Searching for files in {source_dir}")
    if (source_dir / ".git").exists():
        # git ls-files
        txt = subprocess.check_output(
            ["git", "ls-files"], cwd=source_dir, universal_newlines=True
        )
        return _to_files(txt, source_dir)
    if (source_dir / ".svn").exists():
        txt = subprocess.check_output(
            ["svn", "list"], cwd=source_dir, universal_newlines=True
        )
        return _to_files(txt, source_dir)
    return list(source_dir.glob("**"))


def write_archive(archive: T.Union[Path, str], source_dir: Path):
    """Write archives. Format supported by zipfile and tarfile modules are
    supported.

    Parameters
    ----------
    outfile : T.Union[Path, str]
        Archive path. This function make sure that parent directory exists.
    source_dir : Path
        source_dir

    TODO
    -----
    Support more formats if required.
    """

    outfile: Path = Path(archive)

    # make sure parent exists
    outfile.resolve().parent.mkdir(parents=True, exist_ok=True)

    logger.info(f"Generating archive {outfile} from {source_dir}")
    files = list_src_files(source_dir)

    basepath = pkgr.config.get_val("name") + "-" + pkgr.config.get_val("version")

    ext = "".join(outfile.suffixes[-2:])  # max 2 suffixes
    if ext in [".zip"]:
        write_zip(outfile, files, Path(basepath))
    else:
        write_tarfile(outfile, files, Path(basepath))


def write_zip(outfile: Path, files, basedir: Path):
    import zipfile

    with zipfile.ZipFile(outfile, "w") as zf:
        for f in files:
            logger.info(f'  adding to archive: {f}')
            zf.write(f, arcname=(basedir / f))


def write_tarfile(outfile: Path, files, basedir: Path):
    import tarfile

    with tarfile.open(outfile, "w") as tf:
        for f in files:
            logger.info(f'  adding to archive: {f}')
            tf.add(f, arcname=(basedir / f))


def test_tar_file():
    write_archive("a.tar.gz", (Path(__file__).parent / "..").resolve())


def test_zip_file():
    write_archive("a.zip", (Path(__file__).parent / "..").resolve())


if __name__ == "__main__":
    test_tar_file()
