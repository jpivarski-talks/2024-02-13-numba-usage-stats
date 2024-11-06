# 2024-10-30 analysis

## Finding `import numba` in GitHub repos

Repeated the first two steps to produce

* [numba-packages.txt](https://pivarski-princeton.s3.us-east-1.amazonaws.com/GitHub-numba-2024-10-30/numba-packages.txt): dependents that GitHub lists as "packages"
* [numba-dependents.txt](https://pivarski-princeton.s3.us-east-1.amazonaws.com/GitHub-numba-2024-10-30/numba-dependents.txt): other dependents
* [numba-nonfork.txt](https://pivarski-princeton.s3.us-east-1.amazonaws.com/GitHub-numba-2024-10-30/numba-nonfork.txt): selected for `"fork": false`

From the GitHub API, the user and repo infos are

* [USER-INFO.tgz](https://pivarski-princeton.s3.us-east-1.amazonaws.com/GitHub-numba-2024-10-30/USER-INFO.tgz)
* [REPO-INFO.tgz](https://pivarski-princeton.s3.us-east-1.amazonaws.com/GitHub-numba-2024-10-30/REPO-INFO.tgz)

On a machine with 4 cores and a 1 TB disk, [collect-imports-and-strings.py](collect-imports-and-strings.py) (uses [bsparallel](https://github.com/jpivarski/bsparallel)) collected imports and strings from Python files and Jupyter files, as well as README/text files as strings.

* [numba-dependents-contents.tgz](https://pivarski-princeton.s3.us-east-1.amazonaws.com/GitHub-numba-2024-10-30/numba-dependents-contents.tgz) (32 GB) is the result of that process, a compressed tarball of arbitrarily-grouped 8799 JSONL files; each line of these files is a GitHub repo. Without compression, this would be 140 GB.

[find-import-numba.py](find-import-numba.py) streams through the tarball, collecting names and READMEs of repos that import `numba` or `numba.*`.

* [import-numba.jsonl](https://pivarski-princeton.s3.us-east-1.amazonaws.com/GitHub-numba-2024-10-30/import-numba.jsonl) (78 MB)

21.5% of the repos actually contained `import numba`/`from numba import` in some form (checking all syntactically valid expressions) in a Python or Jupyter Notebook file (so, Python 3 only) and _of those_, 84.5% had READMEs. I didn't need to go into the other text snippets.

```
18865 / 87710 = 0.21508379888268156; and has README: 15943 / 18865 = 0.8451099920487676
```

## Finding PyPI packages that strictly depend on Numba

The [pypi-json-data](https://github.com/pypi-data/pypi-json-data) repo has all of the PyPI dependencies as JSON (22 GB when cloned with `--depth 1`). I checked out commit [3a82645](https://github.com/pypi-data/pypi-json-data/commit/3a82645bf91531da2d8236575fe497e197d46bcb).

[json-to-gml.py](json-to-gml.py) turns the whole thing into a GML graph,

* [pypi-data-strict.gml](https://pivarski-princeton.s3.us-east-1.amazonaws.com/GitHub-numba-2024-10-30/pypi-data-strict.gml) (76 MB).
* there's also a non-strict version, which allows dependencies through `extras`, but this makes a subgraph that is too large (e.g. Pandas is a non-strict dependent of Numba): [pypi-data.gml](https://pivarski-princeton.s3.us-east-1.amazonaws.com/GitHub-numba-2024-10-30/pypi-data.gml) (90 MB).

[find-dependents-of-numba.py](find-dependents-of-numba.py) starts with the `numba` package and walks backward in the graph with networkx to find its dependents in levels (level 0 is Numba itself, level 1 is direct dependents, level 2 is dependents of dependents, etc.):

```
 2938 strict-dependents-of-numba/level-1.txt
 2655 strict-dependents-of-numba/level-2.txt
  489 strict-dependents-of-numba/level-3.txt
   55 strict-dependents-of-numba/level-4.txt
    8 strict-dependents-of-numba/level-5.txt
    1 strict-dependents-of-numba/level-6.txt
   47 strict-dependents-of-numba/level-7.txt
    1 strict-dependents-of-numba/level-8.txt
    0 strict-dependents-of-numba/level-9.txt
 6194 total
```

[describe-dependents-of-numba.py](describe-dependents-of-numba.py) fetches the full descriptions from PyPI's API because [pypi-json-data](https://github.com/pypi-data/pypi-json-data) does not include the long descriptions. These will be needed for ChatGPT to classify them by scientific field.

* [strict-dependents-of-numba.tgz](https://pivarski-princeton.s3.us-east-1.amazonaws.com/GitHub-numba-2024-10-30/strict-dependents-of-numba.tgz) (40 MB) is the result of both [find-dependents-of-numba.py](find-dependents-of-numba.py) and [describe-dependents-of-numba.py](describe-dependents-of-numba.py).

## Categorization by ChatGPT

The GitHub repos and the PyPI packages were independently categorized.

[chatgpt-categorize-github.py](chatgpt-categorize-github.py) used gpt-4o-mini and the prompt given in the script to categorize everything in [import-numba.jsonl](https://pivarski-princeton.s3.us-east-1.amazonaws.com/GitHub-numba-2024-10-30/import-numba.jsonl). 10 responses were requested, weighted by confidence, for a later majority vote.

* [categorized-github.tgz](https://pivarski-princeton.s3.us-east-1.amazonaws.com/GitHub-numba-2024-10-30/categorized-github.tgz) (4.8 MB; cost $5.72)

[chatgpt-categorize-pypi-strict.py](chatgpt-categorize-pypi-strict.py) did the same for the PyPI repos.

* [categorized-pypi-strict.tgz](https://pivarski-princeton.s3.us-east-1.amazonaws.com/GitHub-numba-2024-10-30/categorized-pypi-strict.tgz) (1.1 MB; $0.59)
