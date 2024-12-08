import os
import sys
import argparse
from typing import Optional, Sequence, Set

import pytest


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("filenames", nargs="*", help="Filenames to check.")
    parser.add_argument("--folders", nargs="+", help="Folders to test.")
    args = parser.parse_args(argv)
    filenames = args.filenames
    folder_names = args.folders
    retval = 0

    tests_that_need_checking: Set[str] = set()

    for folder in folder_names:
        for filename in filenames:
            if filename.startswith(folder + "/"):
                tests_that_need_checking.add(folder)
                break

    for folder in tests_that_need_checking:
        sys.path.insert(0, os.getcwd())
        retval = pytest.main(["tests"])
        if retval > 0:
            break

    return retval


if __name__ == "__main__":
    exit(main())