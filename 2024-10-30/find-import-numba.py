import tarfile
import json

with open("import-numba.jsonl", "w") as output:

    num_import_numba = 0
    num_and_has_readme = 0
    num_total = 0
    with tarfile.open("numba-dependents-contents.tgz") as tfile:
        for tinfo in tfile:
            print(f"=== {tinfo.name} ====================================================")
            with tfile.extractfile(tinfo) as file:
                for line in file:
                    data = json.loads(line)

                    imports_numba = False
                    if data["success"]:
                        for f in data["files"]:
                            if any(x == "numba" or x.startswith("numba.") for x in f.get("imports", [])):
                                imports_numba = True
                                break

                        readme = None
                        if imports_numba:
                            for f in data["files"]:
                                if f["name"] == "/README.md":
                                    num_and_has_readme += 1
                                    readme = f["text"][0]
                                    break

                        num_total += 1
                        if imports_numba:
                            num_import_numba += 1
                            print(f"{num_import_numba} / {num_total} = {num_import_numba / num_total}; and has README: {num_and_has_readme} / {num_import_numba} = {num_and_has_readme / num_import_numba}")

                            output.write(json.dumps({"repo": data["repo"], "readme": readme}))
                            output.write("\n")
