import pandas as pd
import json
import itertools


def pk_score(your_data, evaluator_data, k):
    N = len(your_data)
    mismatches = 0
    total_windows = N - k

    for i in range(total_windows):
        if (your_data[i] == your_data[i + k]) != (evaluator_data[i] == evaluator_data[i + k]):
            mismatches += 1

    pk = mismatches / total_windows
    return pk


# List of your JSON files (annotated scenes 1 to 10)
files = [f"annotated_scenes_{i}.json" for i in range(1, 11)]

# Load the data from all files
data = []
for file in files:
    with open(file, "r", encoding="utf-8") as f:
        data.append(json.load(f))

# Load the updated comic metadata
with open("Data/Alley_Oop/updated_comic_metadata.json", "r", encoding="utf-8") as f:
    updated_comic_data = json.load(f)


# Function to compare two datasets and return pk score, ignored and additional tags
def compare_annotations(data_1, data_2):
    original_data = data_1["comic_data"]["pages"]
    person_data = data_2["comic_data"]["pages"]

    orig_annotations_all = []
    person_annotations_all = []
    ignored_tags = 0
    additional_tags = 0

    for orig_page, person_page in zip(original_data, person_data):
        if orig_page["page_number"] != person_page["page_number"]:
            print(f"Warning: Mismatch in page numbers - {orig_page['page_number']} vs {person_page['page_number']}")
            continue

        try:
            orig_annotations = [annotation["starting_tag"] for annotation in orig_page["annotations"]]
            person_annotations = [annotation["starting_tag"] for annotation in person_page["annotations"]]
        except KeyError as e:
            print(f"Missing key {e} in annotations for page {orig_page['page_number']}")
            continue

        orig_annotations_all.extend(orig_annotations)
        person_annotations_all.extend(person_annotations)

        # Count ignored tags: any tag in original (updated_comic_metadata) not present in person annotations
        for tag in orig_annotations:
            if tag not in person_annotations:
                ignored_tags += 1

        # Count additional tags: any tag in person annotations not present in original (updated_comic_metadata)
        for tag in person_annotations:
            if tag not in orig_annotations:
                additional_tags += 1

    # Calculate PK score for the existing annotations (optional)
    k = 5
    score = pk_score(person_annotations_all, orig_annotations_all, k)

    # Calculate percentages
    ignored_percentage = (ignored_tags / len(orig_annotations_all)) * 100 if len(orig_annotations_all) > 0 else 0
    additional_percentage = (additional_tags / len(person_annotations_all)) * 100 if len(
        person_annotations_all) > 0 else 0

    return score, ignored_tags, additional_tags, ignored_percentage, additional_percentage


# Compare each annotated scene to the "updated_comic_metadata.json"
results = []

# Compare every scene (annotated_scenes_1 to annotated_scenes_10) with the updated_comic_metadata
for i, scene in enumerate(data):
    score, ignored_tags, additional_tags, ignored_percentage, additional_percentage = compare_annotations(
        updated_comic_data, scene)
    results.append({
        'scene': f"annotated_scenes_{i + 1}.json",
        'compared_to': "updated_comic_metadata.json",
        'pk_score': score,
        'ignored_tags': ignored_tags,
        'additional_tags': additional_tags
    })

# Convert results to DataFrame for better visualization
pk_scores_df = pd.DataFrame(results)

# Print the DataFrame with pk scores, ignored and additional tags
print(pk_scores_df)

# Optionally, calculate the average pk score across all scenes
average_pk = pk_scores_df['pk_score'].mean()
print(f"Average Pk Score across all scenes compared to updated_comic_metadata.json: {average_pk}")
