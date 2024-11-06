import os
import glob
import json
import requests
import time

for filename in sorted(glob.glob("strict-dependents-of-numba/level-*.txt"), key=lambda x: int(x[26:-4])):
    with open(filename) as file:
        for line in file:
            name = line.rstrip()

            output_filename = f"strict-dependents-of-numba/descriptions/{name}.json"
            if not os.path.exists(output_filename):
                print(name)

                try:
                    response = requests.get(f"https://pypi.org/pypi/{name}/json")
                except requests.exceptions.ReadTimeout:
                    time.sleep(2)
                    continue

                if response.status_code == 200:
                    with open(output_filename, "w") as output_file:
                        json.dump(response.json(), output_file)
                    print("    GOOD")
                elif response.status_code == 404 and response.text == '{"message": "Not Found"}':
                    with open(output_filename, "w") as output_file:
                        json.dump(response.json(), output_file)
                    print("    NOT FOUND")
                else:
                    with open(output_filename, "w") as output_file:
                        pass
                    print(f"    BAD {response.status_code = } {response.text = }")

                time.sleep(0.2)
