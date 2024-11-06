import json
import os
import time

import requests

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

dataset = []
with open("import-numba.jsonl") as file:
    for line in file:
        datum = json.loads(line)
        readme = datum["readme"]
        if readme is None or readme.strip() == "":
            readme = "(none)"
        readme = readme.encode("utf-8", errors="replace").decode(
            "utf-8", errors="replace"
        )
        text = f"GitHub repo title: {datum['repo']}\n\nReadme:\n\n{readme}"
        dataset.append({"name": datum["repo"], "text": text})

dataset.sort(key=lambda datum: -len(datum["text"]))


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
                    "content": "Given a software package description, categorize its academic, engineering, commercial/industrial, "
                    + "or non-profit subject and your confidence in that assessment as a percentage.",
                },
                {
                    "role": "user",
                    "content": text[:5000],
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
                                    "Architecture and Urban Planning",
                                    "Art, Design, Music, and Textiles",
                                    "Artificial Intelligence",
                                    "Astronomy and Astrophysics",
                                    "Biology",
                                    "Biomedical, Pharmacology, and Health Science",
                                    "Business and Management",
                                    "Chemistry",
                                    "Communications, Media Studies, and Social Media",
                                    "Computer Hardware, GPUs, and FPGAs",
                                    "Computer Science",
                                    "Computer Vision",
                                    "Criminology and Criminal Justice",
                                    "Cybersecurity",
                                    "Data science",
                                    "Data Science",
                                    "Distributed Systems",
                                    "Earth and Environmental Science",
                                    "Economics",
                                    "Education",
                                    "Engineering",
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
                                    "Programming languages",
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
                            "engineering": {"type": "boolean"},
                            "type": {
                                "enum": [
                                    "Academic Research",
                                    "Student Project or Homework",
                                    "Personal Project",
                                    "Commercial/Industrial",
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
    filename = f"categorized/github/{datum['name']}.json"
    print(f"{i:05d}/{len(dataset):05d} {filename}")

    if not os.path.exists(filename):
        try:
            result = get_category(datum["text"])
        except requests.exceptions.ReadTimeout:
            time.sleep(2)
            continue

        result["name"] = datum["name"]

        with open(filename, "w") as output:
            json.dump(result, output, indent=4)

        time.sleep(0.3)