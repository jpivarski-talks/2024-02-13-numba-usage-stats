import json
import os
import re

match_name = re.compile("^([A-Za-z0-9_.-]+).*")
match_extra = re.compile(r"\bextra\s*(in|not|=|!|<|>)")

nodes_to_id = {}
edges = {}

node_id = 0
for subdir, dirs, filenames in sorted(os.walk("pypi-json-data/release_data")):
    for filename in sorted(filenames):
        fullname = f"{subdir}/{filename}"
        if fullname != "pypi-json-data/release_data/serials.json":
            print(fullname)
            with open(fullname) as file:
                data = json.load(file)
                package_name = None
                for version in data.values():
                    package_name = version["info"]["name"].replace("_", "-").lower()
                    assert filename[:-5].replace("_", "-").lower() == package_name

                    dependencies = set()
                    reqs = version["info"].get("requires_dist")
                    if reqs is not None:
                        for req in reqs:
                            req_name = match_name.match(req).group(1).replace("_", "-").lower()
                            if not match_extra.search(req[len(req_name):]):
                                dependencies.add(req_name)

                assert package_name is not None
                nodes_to_id[package_name] = node_id
                node_id += 1
                edges[package_name] = sorted(dependencies)

with open("pypi-data-strict.gml", "w") as output:
    output.write("""graph [
  directed 1
""")
    for package_name, node_id in nodes_to_id.items():
        output.write(f"  node [ id {node_id} label {json.dumps(package_name)} ]\n")
    for from_node, to_nodes in edges.items():
        for to_node in to_nodes:
            from_id = nodes_to_id.get(from_node)
            to_id = nodes_to_id.get(to_node)
            if from_id is None:
                print(f"missing: {from_node}")
            if to_id is None:
                print(f"missing: {to_node}")
            if from_id is not None and to_id is not None:
                output.write(f"  edge [ source {from_id} target {to_id} ]\n")
    output.write("""]
""")
