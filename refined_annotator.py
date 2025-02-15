import json
import math
import re
def find_panel_euclidane_distance(arc_coordinates, page_data):
    arc_x1, arc_y1, arc_x2, arc_y2 = arc_coordinates  # Unpack safely

    closest_panel = None
    min_distance = float("inf")

    for panel_data in page_data["annotations"]:
        panel_x1, panel_y1, panel_x2, panel_y2 = panel_data["bbox"]

        distance = math.sqrt((arc_x1 - panel_x1) ** 2 + (arc_y1 - panel_y1) ** 2)

        if distance < min_distance:
            min_distance = distance
            closest_panel = panel_data

    return closest_panel

name = "Alley_Oop"
scenes = []
folder_iter = 0
for y in range(10):
    folder_iter += 1
    dir = rf"Data\{name}\refined_scenes\{folder_iter}\{name}_{folder_iter}"
    iteration = 0
    for x in range(10):
        iteration = iteration + 1
        try:
            with open(dir + f"_refined_output_{iteration}.json", 'r') as f:
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

            with open(name + "_data_1.json", 'r', encoding="utf-8") as f:
                data = json.load(f)

            for page in data["comic_data"]["pages"]:
                print(page)
                page_number = page["page_number"]

                coordinates = scene_starting_panel.get(str(page_number), [])
                print(coordinates)

                for annotation in page["annotations"]:
                    annotation["starting_tag"] = False

                for coord in coordinates:
                    coord = tuple(map(float, re.findall(r"[-+]?\d*\.\d+|\d+", coord)))

                    if len(coord) == 4:
                        scene_start = find_panel_euclidane_distance(coord, page)
                        if scene_start:
                            scene_start["starting_tag"] = True
                    else:
                        print(f"Skipping invalid coordinate: {coord}")

            with open(dir + f"_refined_scenes_{iteration}.json", "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except:
            continue