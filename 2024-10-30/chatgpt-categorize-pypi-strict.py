import json
import os
import time
import glob

import requests

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

levels = {}
for filename in glob.glob("strict-dependents-of-numba/level-*.txt"):
    level = int(filename[33:-4])
    with open(filename) as file:
        for line in file:
            levels[line.rstrip("\n")] = level

filenames = glob.glob("strict-dependents-of-numba/descriptions/*.json")
dataset = []
for i, filename in enumerate(filenames):
    with open(filename) as file:
        datum = json.load(file)

        if datum.get("message", "") == "Not Found":
            continue

        name = filename[40:-5]
        summary = datum["info"].get("summary")
        if summary is None:
            summary = "(none)"
        description = datum["info"].get("description")
        if description is None:
            description = "(none)"
        text = f"PyPI package name: {name}\n\nSummary: {summary.strip()}\n\nLong description:\n\n{description.strip()}"
        dataset.append({"name": name, "text": text, "level": levels[name]})

dataset.sort(key=lambda datum: (datum["level"], -len(datum["text"])))


def get_category(text, model="gpt-4o-mini", temperature=0.7):
    result = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {OPENAI_API_KEY}",
        },
        json={
            "model": model,
            "temperature": temperature,
            "messages": [
                {
                    "role": "system",
                    "content": "Given a software package description, categorize its academic, engineering, commercial/industrial, or non-profit subject and your confidence in that assessment as a percentage.",
                },
                {
                    "role": "user",
                    "content": text[:3000],
                },
            ],
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": "response",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "subject": {
                                "enum": [
                                    "Agricultural and Veterinary Science",
                                    "AI Ethics and Safety",
                                    "Applied Mathematics",
                                    "Architecture and Urban Planning",
                                    "Art, Design, Music, and Textiles",
                                    "Artificial Intelligence",
                                    "Astronomy and Astrophysics",
                                    "Atomic and Solid State Physics",
                                    "Biology",
                                    "Biomedical, Pharmacology, and Health Science",
                                    "Business and Management",
                                    "Chemical Engineering",
                                    "Chemistry",
                                    "Communications, Media Studies, and Social Media",
                                    "Computer Hardware, GPUs, and FPGAs",
                                    "Computer Science",
                                    "Computer Vision",
                                    "Criminology and Criminal Justice",
                                    "Cybersecurity",
                                    "Data Science",
                                    "Distributed Systems",
                                    "Earth and Environmental Science",
                                    "Economics",
                                    "Education",
                                    "Finance",
                                    "Gender Studies",
                                    "Generative AI",
                                    "Genetics, Genomics, and Bioinformatics",
                                    "Geography",
                                    "History",
                                    "Hospitality, Tourism, and Culinary Arts",
                                    "Law/Legal",
                                    "Linguistics",
                                    "Literature",
                                    "Marketing",
                                    "Mathematics",
                                    "Natural Language Processing",
                                    "Nuclear and Particle Physics",
                                    "Nursing and Healthcare Management",
                                    "Philosophy, Theology, and Ethics",
                                    "Physics",
                                    "Political Science, Public Administration, and International Relations",
                                    "Probability and Statistics",
                                    "Programming languages and Compilers",
                                    "Psychology, Sociology, Anthropology",
                                    "Robotics",
                                    "Software Engineering and DevOps",
                                    "Speech Recognition",
                                    "Sports Science and Physical Education",
                                    "Supply Chain and Logistics",
                                    "Other (describe below)",
                                ]
                            },
                            "other (if not in list above)": {
                                "type": ["string", "null"]
                            },
                            "type": {
                                "enum": [
                                    "Student Project or Homework",
                                    "Personal Project",
                                    "Commercial/Industrial Research",
                                    "Academic Research",
                                    "Commercial/Industrial Engineering",
                                    "Non-Profit",
                                ]
                            },
                            "confidence": {
                                "type": "integer",
                                "minimum": 0,
                                "maximum": 100,
                            },
                        },
                    },
                },
            },
            "n": 10,
        },
    ).json()

    if "choices" in result:
        for choice in result["choices"]:
            if "message" in choice and "content" in choice["message"]:
                choice["message"]["content"] = json.loads(choice["message"]["content"])

    return result


for i, datum in enumerate(dataset):
    name = datum["name"]
    level = datum["level"]
    text = datum["text"]
    filename = f"categorized/pypi-strict/level-{level}/{name}.json"
    print(f"{i:4d}/{len(dataset):4d} {filename}")

    if not os.path.exists(filename):
        try:
            result = get_category(text)
        except requests.exceptions.ReadTimeout:
            time.sleep(2)
        else:
            with open(filename, "w") as output:
                json.dump(result, output, indent=4)
            time.sleep(0.3)
