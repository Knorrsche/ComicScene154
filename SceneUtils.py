import math

def find_panel_euclidane_distance(arc_coordinates, page_data):
    arc_x1, arc_y1, arc_x2, arc_y2 = arc_coordinates

    closest_panel = None
    min_distance = float("inf")

    for panel_data in page_data["panels"]:
        panel_x1, panel_y1, panel_x2, panel_y2 = panel_data["bbox"]

        distance = math.sqrt((arc_x1 - panel_x1) ** 2 + (arc_y1 - panel_y1) ** 2)

        if distance < min_distance:
            min_distance = distance
            closest_panel = panel_data

    return closest_panel