import ast
import json
import os
import shutil
import subprocess
import warnings

import jupytext

import bsparallel


warnings.filterwarnings("ignore", message="invalid escape sequence")


def get_docstrings(syntax_tree):
    docstrings = []
    for node in ast.walk(syntax_tree):
        if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.Module)):
            docstring = ast.get_docstring(node)
            if docstring:
                docstrings.append(docstring)
    return docstrings


def get_imports(syntax_tree):
    imports = set()
    for node in ast.walk(syntax_tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            imports.add("." * node.level + ("" if node.module is None else node.module))
    return sorted(imports)


def get_repo(repo_name):
    print(repo_name)

    try:
        os.mkdir(f"RESULTS/{repo_name.split('/')[0]}")
    except FileExistsError:
        pass

    output_filename = f"RESULTS/{repo_name}.json"

    with open(output_filename, "w") as output:
        json.dump({"repo": repo_name, "success": False}, output)
        output.write("\n")

    try:
        subprocess.run(
            [
                "git",
                "clone",
                "--depth",
                "1",
                f"https://github.com/{repo_name}.git",
                f"REPO/{repo_name}",
                "--quiet",
            ],
            check=True,
            env={"GIT_TERMINAL_PROMPT": "0"},
        )

    except:
        pass

    else:
        thesefiles = []
        for subdir, dirs, filenames in os.walk(f"REPO/{repo_name}", followlinks=False):
            for filename in filenames:
                fullname = f"{subdir}/{filename}"

                if os.path.islink(fullname):
                    continue

                thisfile = {"name": fullname[len(f"REPO/{repo_name}") :]}

                f = filename.lower()
                if f.endswith(".py") or f.endswith(".pyi"):
                    with open(
                        fullname, encoding="utf-8", errors="surrogateescape"
                    ) as file:
                        python_source = file.read()

                        try:
                            syntax_tree = ast.parse(python_source)
                        except:
                            thisfile["parse"] = False
                        else:
                            thisfile["parse"] = True
                            thisfile["text"] = get_docstrings(syntax_tree)
                            thisfile["imports"] = get_imports(syntax_tree)

                elif f.endswith(".ipynb"):
                    with open(
                        fullname, encoding="utf-8", errors="surrogateescape"
                    ) as file:
                        try:
                            notebook = jupytext.reads(file.read())
                            all_markdown = [
                                x["source"]
                                for x in notebook["cells"]
                                if x["cell_type"] == "markdown"
                            ]
                            python_source = jupytext.writes(notebook, fmt="py:percent")
                            syntax_tree = ast.parse(python_source)
                        except:
                            thisfile["parse"] = False
                        else:
                            thisfile["parse"] = True
                            thisfile["text"] = all_markdown + get_docstrings(
                                syntax_tree
                            )
                            thisfile["imports"] = get_imports(syntax_tree)

                elif (
                    f.endswith(".md")
                    or f.endswith(".mkd")
                    or f.endswith(".mdwn")
                    or f.endswith(".mdown")
                    or f.endswith(".mdtxt")
                    or f.endswith(".mdtext")
                    or f.endswith(".mdml")
                    or f.endswith(".markdown")
                    or f.endswith(".rst")
                    or f.endswith(".txt")
                    or f.endswith(".text")
                    or f.endswith(".htm")
                    or f.endswith(".html")
                    or "readme" in f
                ):
                    with open(
                        fullname, encoding="utf-8", errors="surrogateescape"
                    ) as file:
                        thisfile["text"] = [file.read(512000)]

                thesefiles.append(thisfile)

        with open(output_filename, "w") as output:
            json.dump({"repo": repo_name, "success": True, "files": thesefiles}, output)
            output.write("\n")

    finally:
        try:
            shutil.rmtree(f"REPO/{repo_name}")
        except FileNotFoundError:
            pass


with open("numba-nonfork.txt") as file:
    nonfork = sorted([x.rstrip("\n") for x in file])


bsparallel.run(24, get_repo, nonfork)
