# 2024-10-30 analysis

Repeated the first two steps to produce

* [numba-packages.txt](https://pivarski-princeton.s3.us-east-1.amazonaws.com/GitHub-numba-2024-10-30/numba-packages.txt): dependents that GitHub lists as "packages"
* [numba-dependents.txt](https://pivarski-princeton.s3.us-east-1.amazonaws.com/GitHub-numba-2024-10-30/numba-dependents.txt): other dependents
* [numba-nonfork.txt](https://pivarski-princeton.s3.us-east-1.amazonaws.com/GitHub-numba-2024-10-30/numba-nonfork.txt): selected for `"fork": false`

From the GitHub API, the user and repo infos are

* [USER-INFO.tgz](https://pivarski-princeton.s3.us-east-1.amazonaws.com/GitHub-numba-2024-10-30/USER-INFO.tgz)
* [REPO-INFO.tgz](https://pivarski-princeton.s3.us-east-1.amazonaws.com/GitHub-numba-2024-10-30/REPO-INFO.tgz)

On a machine with 4 cores and a 1 TB disk, [collect-imports-and-strings.py](collect-imports-and-strings.py) (uses [bsparallel](https://github.com/jpivarski/bsparallel)) collected imports and strings from Python files and Jupyter files, as well as README/text files as strings.
