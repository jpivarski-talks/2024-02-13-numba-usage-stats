import time
import os
import re
import glob
import mmap

matcher = re.compile(
    r"\b(import\s+([A-Za-z_][A-Za-z_0-9]*\s*,\s*)*numba|from\s+numba\s+import)\b"
)

filenames = glob.glob("GitHub-numba-user-nonfork-raw-data-1Mcut/*/*.grep")

for i, filename in enumerate(filenames):
    print(
        f"{time.strftime('%H:%M:%S')} {i:5d}/{len(filenames):5d} {filename[:-5]}",
        end="",
        flush=True,
    )
    with open(filename) as file:
        for line in file:
            if matcher.search(line) is not None:
                frompath = filename[:-4]
                topath = "/".join(frompath.split("/")[:-1]).replace(
                    "GitHub-numba-user-nonfork-raw-data-1Mcut/",
                    "GitHub-numba-user-nonfork-raw-data-1Mcut-imports/",
                )
                os.system(f"mkdir -p {topath}")
                os.system(f"mv {frompath}tgz {frompath}grep {topath}")
                print(" YES")
                break
        else:
            print(" NO")

print("DONE")
