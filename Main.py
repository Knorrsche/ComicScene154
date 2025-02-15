import google.generativeai as genai
import os
import json
import math
import re
from PIL import Image

comic_summarization_prompt = """
{
    "General_Instructions": "You are an expert in analyzing comic pages and structuring them into continuous narrative arcs based on provided image data. Your goal is to break down the comic page into coherent story segments, ensuring a smooth chronological flow without gaps, overlaps, or disjointed descriptions. Each narrative arc should integrate seamlessly into the previous one, forming a single, unified storyline. Where possible, combine arcs that are close in sequence or thematic focus into larger, cohesive major plots.",
    
    "Key_Guidelines": {
        "1": {
            "Narrative_Arc_Construction": "- Define narrative arcs based on how the comic panels contribute to distinct story developments.\n- Each arc must be self-contained but sequentially linked to the next.\n- Arcs should not overlap or split mid-scene—once an arc begins, it must be fully developed before transitioning.\n- When a new scene, conflict, or significant character interaction begins, start a new arc.\n- Combine arcs that are geographically close or thematically related into larger, overarching plots if it makes sense for the flow of the story."
        },

        "2": {
            "Chronological_Flow_and_Panel_Integration": "- Panels must be grouped logically into arcs, ensuring that events progress smoothly.\n- Transitions should be natural—if a new panel extends a previous arc, integrate it instead of forcing a break.\n- Each arc should start immediately after the previous arc ends."
        },

        "3": {
            "Inferring_Meaning_Without_Quoting": "- Use dialogue and character expressions to infer plot developments but avoid direct quotes.\n- Describe actions, emotions, and intentions rather than textual content."
        },

        "4": {
            "Narrative_Role_Assignment_Cohn": "Each arc must be analyzed using the Cohn Visual Narrative Grammar framework:\n- Establisher: What introduces the arc’s setting, characters, or situation?\n- Initial: What action or event begins the core of the arc?\n- Peak: What is the emotional or narrative climax of the arc?\n- Release: What resolves the tension and sets up the next arc?\n\nYou do NOT need to assign specific panels to these roles—just describe the narrative progression within each arc."
        },

        "5": {
            "Updating_and_Refining_Summaries": "- If new panels clarify or expand a previous arc, update the summary accordingly.\n- The final structure should reflect a single, uninterrupted timeline with no gaps or missing context."
        }
    },

    "Output_Format": {
        "Narrative_Arcs": [
            {
                "arc_id": "1",
                "title": "Title of Arc",
                "starting_page": "1",
                "description": "Comprehensive summary of the arc, describing key actions, emotions, and plot points.",
                "occurring_characters": ["Character A", "Character B"],
                "coordinates_of_starting_panel": "(x1, y1, x2, y2)",
                "panel_index_of_start": "1",
                "reasoning_for_new_arc": "Why this arc is distinct from the previous one.",
                "establisher": "What sets up the arc? (Cohn Visual Narrative Grammar)",
                "initial": "What triggers the main action? (Cohn Visual Narrative Grammar)",
                "peak": "What is the climax of the arc? (Cohn Visual Narrative Grammar)",
                "release": "How is tension resolved? (Cohn Visual Narrative Grammar)",
                "confidence": "A score (1-100) indicating how confident we are that this arc is independent."
            }
        ]
    },

    "Additional_Considerations": {
        "Confidence_Score": "Rate how certain you are that an arc stands alone (higher score means greater confidence in its independence).",
        "Character_Identification": "If a name is unknown, describe the character (e.g., 'Officer,' 'James’ Mother').",
        "Panel_Bounding_Boxes": "Extract coordinates from panel data to mark where each arc starts."
    }
}
Only output the data of the current page and not of the previous page.
"""

def find_panel_euclidane_distance(arc_coordinates, page_data):
    arc_x1, arc_y1, arc_x2, arc_y2 = arc_coordinates

    closest_panel = None
    min_distance = float("inf")

    for panel_data in page_data["annotations"]:
        panel_x1, panel_y1, panel_x2, panel_y2 = panel_data["bbox"]

        distance = math.sqrt((arc_x1 - panel_x1) ** 2 + (arc_y1 - panel_y1) ** 2)

        if distance < min_distance:
            min_distance = distance
            closest_panel = panel_data

    return closest_panel


model_name: str = "gemini-2.0-flash-thinking-exp"
model_gemini = genai.GenerativeModel(model_name=model_name)
genai.configure(api_key="")

output_name = "Treasure_Comics"
dir_json = f"Data/{output_name}/split_json_absolute"
dir_image = f"Data/{output_name}/output_images"

iteration = 0
for x in range(10):
    iteration = iteration + 1
    page_counter = 1
    previous_output = ""
    comic_data = {"pages": []}
    page_summaries = []

    for dirpath, dirnames, filenames in os.walk(dir_json):
        for filename in sorted(filenames):
            file_path = os.path.join(dirpath, filename)

            with open(file_path, "r", encoding="utf-8") as json_file:
                data = json.load(json_file)

                image_path = os.path.join(dir_image, data["file_name"])
                image = Image.open(image_path)

                panels = [
                    {
                        "id": idx + 1,
                        "bbox": panel["bbox"]
                    }
                    for idx, panel in enumerate(data["annotations"])
                ]

                context_string = f"Page {page_counter}:\n"
                for i, panel in enumerate(panels):
                    bbox = panel["bbox"]
                    context_string += (f"Panel {i + 1}: X = {bbox[0]}, Y = {bbox[1]}, "
                                       f"Width = {bbox[2]}, Height = {bbox[3]} \n")

                prompt = (comic_summarization_prompt +
                          f"Previous Arcs: {previous_output} \n \n \n" +
                          "\n" + "Current page data:" + context_string)

                response = model_gemini.generate_content(
                    [image, prompt]
                )
                summary_output = response.text
                previous_output = summary_output

                print(f"Page {page_counter}: \n{summary_output}\n\n")

                page_data = {
                    "page_number": page_counter,
                    "file_name": data["file_name"],
                    "annotations": panels,
                    "summary": summary_output
                }
                comic_data["pages"].append(page_data)

                page_summaries.append({
                    "page_number": page_counter,
                    "summary": summary_output
                })

            page_counter += 1

    comic_data["Output"] = previous_output

    with open(output_name + f"_data_{iteration}.json", 'w', encoding='utf-8') as json_file:
        json.dump({"comic_data": comic_data, "page_summaries": page_summaries}, json_file, ensure_ascii=False, indent=4)


    with open(output_name + f"_data_{iteration}.json", "r", encoding="utf-8") as f:
        comic_data = json.load(f)

    extracted_coordinates = {}

    for page in comic_data["comic_data"]["pages"]:
        page_number = page["page_number"]

        summary_text = page["summary"].replace("```json", "").replace("```", "").strip()

        pattern = r'"coordinates_of_starting_panel":\s*"\(([\d.,\s]+)\)"'

        matches = re.findall(pattern, summary_text)

        coordinates = [list(map(float, match.split(","))) for match in matches]
        print(page["annotations"])

        for annotation in page["annotations"]:
            annotation["starting_tag"] = False
        for coord in coordinates:
            scene_start = find_panel_euclidane_distance(coord,page)
            scene_start["starting_tag"] = True


    with open(output_name + f"_annotated_scenes_{iteration}.json", "w", encoding="utf-8") as f:
        json.dump(comic_data, f, ensure_ascii=False, indent=4)




