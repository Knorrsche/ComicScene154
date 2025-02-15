import json


str_name = "Treasure_Comics"
with open(f"Data/{str_name}/{str_name}.json", "r", encoding="utf-8") as f:
    data_source_2 = json.load(f)

processed_data = {"comic_data": {"pages": []}}

page_number = 1

for chapter in data_source_2["comic"]["chapters"]:
    for page in chapter["pages"]:
        page_entry = {"page_number": page_number, "panels": []}

        for panel in page:
            panel_entry = {"starting_tag": True if panel == 1 else False}
            page_entry["panels"].append(panel_entry)

        processed_data["comic_data"]["pages"].append(page_entry)

        page_number += 1

with open(f"Data/{str_name}/{str_name}_new.json", "w", encoding="utf-8") as f:
    json.dump(processed_data, f, ensure_ascii=False, indent=4)

print(f"Processed JSON saved as '{str_name}_new.json'.")


import json

with open(f"Data/{str_name}/{str_name}_new.json", "r") as f:
    starting_tags_data = json.load(f)

with open(f"{str_name}_data_1.json", "r", encoding="utf-8") as f:
    comic_data = json.load(f)

starting_tags_lookup = {
    page["page_number"]: [panel["starting_tag"] for panel in page["panels"]]
    for page in starting_tags_data["comic_data"]["pages"]
}

for page in comic_data["comic_data"]["pages"]:
    page_number = page["page_number"]
    for panel in page["annotations"]:
        panel["starting_tag"] = False
    if page_number in starting_tags_lookup:
        starting_tags = starting_tags_lookup[page_number]

        for idx, annotation in enumerate(page["annotations"]):
            if idx < len(starting_tags):
                annotation["starting_tag"] = starting_tags[idx]

with open(f"Data/{str_name}/updated_comic_metadata.json", "w", encoding="utf-8") as f:
    json.dump(comic_data, f, ensure_ascii=False, indent=4)

print("Updated JSON saved as 'updated_comic_metadata.json'.")
