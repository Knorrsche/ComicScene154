import json
import os
import cv2


str_name = "Treasure_Comics"
with open(f"Data/{str_name}/_annotations.coco.json", "r") as file:
    data = json.load(file)

output_dir = f"Data/{str_name}/split_json_absolute"
os.makedirs(output_dir, exist_ok=True)
annotations_by_image = {}
for annotation in data["annotations"]:
    image_id = annotation["image_id"]

    x, y, w, h = annotation["bbox"]
    annotation["bbox"] = [x, y, x + w, y + h]

    if image_id not in annotations_by_image:
        annotations_by_image[image_id] = []
    annotations_by_image[image_id].append(annotation)

for image in data["images"]:
    image_id = image["id"]
    image_filename = image["file_name"]

    image_path = os.path.join(rf"Data/{str_name}/output_images", image_filename)
    page_image = cv2.imread(image_path)

    if page_image is None:
        print(f"Warning: Could not load image {image_filename}")
        continue

    new_annotations = []
    for idx, annotation in enumerate(annotations_by_image.get(image_id, []), start=1):
        annotation["id"] = idx
        new_annotations.append(annotation)

    new_json = {
        "file_name": image_filename,
        "annotations": new_annotations
    }

    output_filename = os.path.join(output_dir, f"{image_filename}.json")
    with open(output_filename, "w") as out_file:
        json.dump(new_json, out_file, indent=4)

print("JSON files created with absolute bounding box coordinates and annotation IDs starting at 1!")
