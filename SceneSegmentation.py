import os
import json
import re
from SceneUtils import find_panel_euclidane_distance
from PIL import Image
import time

def predict_scene_data(name: str,model_gemini):

    with open('Prompts/ScenePrompt.txt', 'r', encoding="utf-8") as file:
        scene_segmentation_prompt = file.read()

    output_name = name
    dir_json = f"Data/{output_name}/{output_name}.json"
    dir_image = f"Data/{output_name}/images"

    with open(dir_json,'r',encoding="utf-8") as file:
        data = json.load(file)

    previous_output = ""
    comic_data = {"pages": []}
    page_summaries = []

    for page in data["pages"]:

        page_number = page["page_number"]
        image_path = os.path.join(dir_image, page["file_name"])
        image = Image.open(image_path)

        panels = page["panels"]

        context_string = f"Page {page_number}:\n"

        for i, panel in enumerate(panels):
            bbox = panel["bbox"]
            context_string += (f"Panel {i + 1}: X = {bbox[0]}, Y = {bbox[1]}, "
                               f"Width = {bbox[2]}, Height = {bbox[3]} \n")

        prompt = (scene_segmentation_prompt +
                  f"Previous Arcs: {previous_output}" +
                  "\n" + "Current page data:" + context_string)

        response = model_gemini.generate_content(
            [image, prompt]
        )
        summary_output = response.text
        previous_output = summary_output

        print(f"Page {page_number}: \n {summary_output} \n\n")

        page_data = {
            "page_number": page_number,
            "file_name": page["file_name"],
            "panels": panels,
            "summary": summary_output
        }

        comic_data["pages"].append(page_data)

        page_summaries.append({
            "page_number": page_number,
            "summary": summary_output
        })
        #Timeout to not exceed the free api limit of Gemini
        time.sleep(5)

    with open(rf"Data\{output_name}\{output_name}_data.json", 'w', encoding='utf-8') as json_file:
        json.dump({"comic_data": comic_data, "page_summaries": page_summaries}, json_file, ensure_ascii=False, indent=4)


def segment_scenes(name: str):
    output_name = name
    with open(rf"Data\{output_name}\{output_name}_data.json", "r", encoding="utf-8") as f:
        comic_data = json.load(f)

    for page in comic_data["comic_data"]["pages"]:

        summary_text = page["summary"].replace("```json", "").replace("```", "").strip()

        pattern = r'"coordinates_of_starting_panel":\s*"\(([\d.,\s]+)\)"'

        matches = re.findall(pattern, summary_text)

        coordinates = [list(map(float, match.split(","))) for match in matches]
        print(page["panels"])

        for annotation in page["panels"]:
            annotation["starting_tag"] = False
        for coord in coordinates:
            scene_start = find_panel_euclidane_distance(coord,page)
            scene_start["starting_tag"] = True


    with open(rf"Data\{output_name}\{output_name}_annotated_scenes.json", "w", encoding="utf-8") as f:
        json.dump(comic_data, f, ensure_ascii=False, indent=4)

