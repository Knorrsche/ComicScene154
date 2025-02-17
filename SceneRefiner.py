import json


def refine_data(name: str, model_gemini):
    output_name = name

    with open('Prompts/SceneRefinerPrompt.txt', 'r', encoding="utf-8") as file:
        refine_prompt = file.read()

    dir_json = f"Data/{output_name}/{output_name}_annotated_scenes.json"

    with open(dir_json, "r", encoding="utf-8") as f:
        json_data = json.load(f)

    narrative_data = json_data["page_summaries"]

    prompt = str(narrative_data) + refine_prompt

    response = model_gemini.generate_content(
        prompt
    )

    output = response.text.strip()
    output = output.replace("```json", "").replace("```", "")
    print(output)

    try:
        output_json = json.loads(output)
        output_file = rf"Data\{output_name}\{output_name}_refined_data.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(output_json, f, indent=4)
    except json.JSONDecodeError:
        print("Error: Could not parse response as JSON. Saving raw output as text.")
        error_output_file = rf"Data\{output_name}\{output_name}_refined_output_error.txt"
        with open(error_output_file, "w", encoding="utf-8") as f:
            f.write(output)

import json
import math
import re
def find_panel_euclidane_distance(arc_coordinates, page_data):
    arc_x1, arc_y1, arc_x2, arc_y2 = arc_coordinates  # Unpack safely

    closest_panel = None
    min_distance = float("inf")

    for panel_data in page_data["panels"]:
        panel_x1, panel_y1, panel_x2, panel_y2 = panel_data["bbox"]

        distance = math.sqrt((arc_x1 - panel_x1) ** 2 + (arc_y1 - panel_y1) ** 2)

        if distance < min_distance:
            min_distance = distance
            closest_panel = panel_data

    return closest_panel


def segment_scenes(name: str):
    output_name = name

    scenes = []

    with open(rf"Data\{output_name}\{output_name}_refined_data.json", 'r',encoding="utf-8") as f:
        data = json.load(f)

    for arc in data["Major_Arcs"]:
        for sub_scene in arc["sub_scenes"]:
            scenes.append(sub_scene)

    scene_starting_panel = {}

    for sub_scene in scenes:
        starting_page = sub_scene.get("starting_page")
        coordinates = sub_scene.get("coordinates_of_starting_panel")

        if starting_page is not None and coordinates is not None:
            if starting_page not in scene_starting_panel:
                scene_starting_panel[starting_page] = []
            scene_starting_panel[starting_page].append(coordinates)

    with open(rf"Data\{output_name}\{output_name}_data.json", 'r', encoding="utf-8") as f:
        data = json.load(f)

    for page in data["comic_data"]["pages"]:
        print(page)
        page_number = page["page_number"]

        coordinates = scene_starting_panel.get(str(page_number), [])
        print(coordinates)

        for annotation in page["panels"]:
            annotation["starting_tag"] = False

        for coord in coordinates:
            coord = tuple(map(float, re.findall(r"[-+]?\d*\.\d+|\d+", coord)))

            if len(coord) == 4:
                scene_start = find_panel_euclidane_distance(coord, page)
                if scene_start:
                    scene_start["starting_tag"] = True
            else:
                print(f"Skipping invalid coordinate: {coord}")

    with open(rf"Data\{output_name}\{output_name}_annotated_refined.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
