import os
import subprocess
import concurrent.futures


def task(reponame):
    if os.path.exists(f"ARCHIVED-REPOS/{reponame}.tgz"):
        return

    try:
        subprocess.run(
            [
                "git",
                "clone",
                "--depth",
                "1",
                f"https://github.com/{reponame}.git",
                f"REPO/{reponame}",
                "--quiet",
            ],
            check=True,
            env={"GIT_TERMINAL_PROMPT": "0"},
        )
        subprocess.run(
            [
                "mkdir",
                "-p",
                f"ARCHIVED-REPOS/{reponame.split('/')[0]}",
            ],
            check=True,
        )
        grep = subprocess.run(
            [
                "grep",
                "-i",
                "-r",
                r"\bnumba\b",
                f"REPO/{reponame}/",
            ],
            capture_output=True,
        )
        with open(f"ARCHIVED-REPOS/{reponame}.grep", "wb") as file:
            file.write(grep.stdout)
        subprocess.run(
            [
                "rm",
                "-rf",
                f"REPO/{reponame}/.git",
            ],
            check=True,
        )
        subprocess.run(
            [
                "find",
                f"REPO/{reponame}/",
                "-type",
                "f",
                "-not",
                "(",
                "-name",
                '"*.py"',
                "-o",
                "-name",
                '"*.PY"',
                "-o",
                "-name",
                '"*.ipynb"',
                "-o",
                "-name",
                '"*.IPYNB"',
                "-o",
                "-name",
                '"*.c"',
                "-o",
                "-name",
                '"*.cc"',
                "-o",
                "-name",
                '"*.cpp"',
                "-o",
                "-name",
                '"*.cp"',
                "-o",
                "-name",
                '"*.cxx"',
                "-o",
                "-name",
                '"*.c++"',
                "-o",
                "-name",
                '"*.C"',
                "-o",
                "-name",
                '"*.CC"',
                "-o",
                "-name",
                '"*.CPP"',
                "-o",
                "-name",
                '"*.CP"',
                "-o",
                "-name",
                '"*.CXX"',
                "-o",
                "-name",
                '"*.C++"',
                "-o",
                "-name",
                '"*.h"',
                "-o",
                "-name",
                '"*.hpp"',
                "-o",
                "-name",
                '"*.hp"',
                "-o",
                "-name",
                '"*.hh"',
                "-o",
                "-name",
                '"*.H"',
                "-o",
                "-name",
                '"*.HPP"',
                "-o",
                "-name",
                '"*.HP"',
                "-o",
                "-name",
                '"*.HH"',
                "-o",
                "-name",
                '"*.cu"',
                "-o",
                "-name",
                '"*.cuh"',
                "-o",
                "-name",
                '"*.CU"',
                "-o",
                "-name",
                '"*.CUH"',
                ")",
                "-size",
                "+1M",
                "-delete",
            ],
            check=True,
        )
        subprocess.run(
            [
                "tar",
                "-czf",
                f"ARCHIVED-REPOS/{reponame}.tgz",
                f"REPO/{reponame}/",
            ],
            check=True,
        )
    except Exception as err:
        print("BAD ", reponame, repr(err), str(err), flush=True)
    else:
        print("GOOD", reponame, flush=True)
    finally:
        subprocess.run(
            [
                "rm",
                "-rf",
                f"REPO/{reponame}/",
            ]
        )


reponames = []
with open("non-fork.txt") as file:
    for reponame in file:
        reponames.append(reponame.rstrip())

with concurrent.futures.ProcessPoolExecutor(max_workers=24) as executor:
    executor.map(task, reponames)

print("DONE", flush=True)
