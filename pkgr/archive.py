__author__ = "Dilawar Singh"
__email__ = "dilawar.s.rajput@gmail.com"

import subprocess

import typing as T
from pathlib import Path

from loguru import logger


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


def write_archive(outfile: T.Union[Path, str], source_dir: Path):
    logger.info(f"Generating archive {outfile} from {source_dir}")
    ext = "".join(Path(outfile).suffixes[-2:])  # max 2 suffixes
    files = list_src_files(source_dir)
    logger.info(f"Adding files to archive:\n {files}")
    if ext in [".zip"]:
        write_zip(outfile, files)
    else:
        write_tarfile(outfile, files)


def write_zip(outfile: Path, files):
    import zipfile

    with zipfile.ZipFile(outfile, "w") as zf:
        [zf.write(f) for f in files]


def write_tarfile(outfile: Path, files):
    import tarfile

    with tarfile.open(outfile, "w") as tf:
        [tf.add(f) for f in files]


def test_tar_file():
    write_archive("a.tar.gz", (Path(__file__).parent / "..").resolve())

def test_zip_file():
    write_archive("a.zip", (Path(__file__).parent / "..").resolve())

if __name__ == "__main__":
    test_tar_file()
