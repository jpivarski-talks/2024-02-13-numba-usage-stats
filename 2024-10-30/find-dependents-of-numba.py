import networkx as nx

g = nx.read_gml("pypi-data-strict.gml")

previous = set()
everything = set(["numba"])

level = 0
while len(previous) != len(everything):
    level += 1
    previous = everything
    everything = everything.union([y for x in everything for y in g.predecessors(x)])
    with open(f"strict-dependents-of-numba/level-{level}.txt", "w") as file:
        file.write("".join(f"{x}\n" for x in sorted(everything - previous)))
