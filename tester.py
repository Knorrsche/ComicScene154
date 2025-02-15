import google.generativeai as genai
import os
import json
import math
import re
from PIL import Image

comic_scene_prompt = """
You are given narrative data from a comic. Your task is to construct a hierarchical scene breakdown based on this data.

### Hierarchy Structure:
1. **Major Arcs** (Broad thematic or structural divisions)
2. **Sub-Scenes** (Clusters of related narrative arcs contributing to a specific event or sequence)
3. **Narrative Arcs** (Individual moments within a sub-scene, following narrative grammar)

### Instructions:
- **Identify Narrative Arcs**:
  - A narrative arc should capture a complete small event (e.g., a conversation, action sequence, or transition).
  - Each arc should include:
    - Title
    - Description
    - Starting panel & page
    - Occurring characters
    - Coordinates of starting panel
    - Breakdown using narrative grammar (Establisher, Initial, Peak, Release)

- **Group Narrative Arcs into Sub-Scenes**:
  - A sub-scene consists of multiple related narrative arcs that together form a meaningful event or section.
  - Provide a title, summary, and justification for grouping these arcs together.

- **Form Major Arcs from Sub-Scenes**:
  - A major arc is a broader thematic structure formed by multiple sub-scenes.
  - It should have a title, description, and key themes tying the sub-scenes together.

### Scene Structuring & Panel Placement:
Each scene must specify its starting page and panel number  
A scene does not have to start at the first panel of a page (e.g., it can begin at Page 3, Panel 4 if narratively justified).  
Consider narrative connections across pages rather than forcing boundaries based on page breaks.  

### Use of Narrative Grammar (Cohn):
- **Establisher**: Introduces setting and context
- **Initial**: Initiates an action or event
- **Peak**: The climax or high point of the event
- **Release**: The resolution or transition out of the arc

### Example Output Format:

{
    "Major_Arcs": [
        {
            "arc_id": "M1",
            "title": "The Mystery of Ghost Town",
            "description": "This major arc explores the legend of Ghost Town, skepticism surrounding it, and the conflicts arising from its potential destruction.",
            "sub_scenes": [
                {
                    "sub_scene_id": "S1",
                    "title": "Introduction to the Myth",
                    "starting_page": "1",
                    "panel_index_of_start": "3",
                    "coordinates_of_starting_panel": "(x1, y1, x2, y2)",
                    "description": "The scene establishes the legend of Ghost Town, introducing conflicting beliefs between characters.",
                    "narrative_arcs": [
                        {
                            "arc_id": "1",
                            "title": "Ghost Town Skepticism",
                            "starting_page": "1",
                            "panel_index_of_start": "3",
                            "description": "A man wearing a blue hat argues with a blonde woman about the existence of Ghost Town. He insists on its reality, while she remains skeptical.",
                        },
                        {
                            "arc_id": "2",
                            "title": "Flashback to Ghost Town's Arrival",
                            "starting_page": "2",
                            "panel_index_of_start": "2",
                            "description": "A woman on horseback narrates her past journey to Ghost Town, setting an ominous or nostalgic tone.",

                        }
                    ]
                },
                {
                    "sub_scene_id": "S2",
                    "title": "Modern Day Conflict",
                    "starting_page": "2",
                    "panel_index_of_start": "3",
                    "coordinates_of_starting_panel": "(x1, y1, x2, y2)",
                    "description": "The debate shifts to the present day, where characters discuss plans to destroy Ghost Town for an airport.",
                    "narrative_arcs": [
                        {
                            "arc_id": "3",
                            "title": "Airport Plans for Ghost Town",
                            "starting_page": "2",
                            "panel_index_of_start": "3",
                            "description": "A man in a hat explains that Ghost Town will be replaced by an airport, sparking outrage.",
                        }
                    ]
                }
            ]
        }
    ]
}

### Final Notes:
Each major arc should feel like a cohesive overarching event, while sub-scenes focus on smaller narrative sequences within it.  
The arcs have to be continous - so start with arc 1 page 1 panel 1 until end, do not mix the order.
Narrative arcs should be small, self-contained interactions but connected by sub-scenes and major arcs.  
Avoid strict page-based divisions—let narrative flow dictate structure.
Only output the arc_id, title, starting_page and panel_index_of_start for the narrative arcs in the output.
Ensure that the output is valid json.
"""


model_name: str = "gemini-2.0-flash-thinking-exp"
model_gemini = genai.GenerativeModel(model_name=model_name)
genai.configure(api_key="")

output_name = "Treasure_Comics"
outer_iteration = 0
for x in range(10):
    outer_iteration += 1
    dir_json = f"Data/{output_name}/annotated_scenes/{output_name}_annotated_scenes_{outer_iteration}.json"

    with open(dir_json, "r", encoding="utf-8") as f:
        json_data = json.load(f)
    narrative_data = json_data["page_summaries"]
    prompt = str(narrative_data) + comic_scene_prompt

    iteration = 0
    for x in range(10):
        iteration += 1

        response = model_gemini.generate_content(
            prompt
        )

        output = response.text.strip()
        output = output.replace("```json", "").replace("```", "")
        print(output)
        try:
            output_json = json.loads(output)
            output_file = f"{output_name}_{outer_iteration}_refined_output_{iteration}.json"
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(output_json, f, indent=4)
        except json.JSONDecodeError:
            print("Error: Could not parse response as JSON. Saving raw output as text.")
            error_output_file = f"{output_name}_{outer_iteration}_refined_output_{iteration}.txt"
            with open(error_output_file, "w", encoding="utf-8") as f:
                f.write(output)