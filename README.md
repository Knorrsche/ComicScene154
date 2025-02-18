# ComicScene154: A Scene Dataset for Comic Analysis

## Overview
ComicScene154 is a dataset designed for the analysis of comic book scenes, enabling research in scene segmentation, multimodal learning, and captioning. The dataset includes multiple comic titles, each with annotated ground truth data, images, and benchmarked scene segmentations.

## Project Structure

```
docs/
├── README.md                   # Project overview, installation, quick start
├── Data/                       # Dataset documentation
    ├── Alley_Oop               # Comic 1
    │   ├── Alley_Oop.json      # Ground Truth data (Scene+Panels)
    │   ├── images              # Images of the comic
    │   ├── benchmarked_scenes  # Benchmark for the multi-modal-only scenes
    │   └── benchmarked_refined_scenes  # Refined benchmarks used in the paper
    ├── Champ                   # Comic 2
    │   ├── Champ.json          # Ground Truth data (Scene+Panels)
    │   ├── images              # Images of the comic
    │   ├── benchmarked_scenes  # Benchmark for the multi-modal-only scenes
    │   └── benchmarked_refined_scenes  # Refined benchmarks used in the paper
    ├── Treasure_Comics         # Comic 3
    │   ├── Treasure_Comics.json # Ground Truth data (Scene+Panels)
    │   ├── images              # Images of the comic
    │   ├── benchmarked_scenes  # Benchmark for the multi-modal-only scenes
    │   └── benchmarked_refined_scenes  # Refined benchmarks used in the paper
    ├── Western_Love            # Comic 4
    │   ├── Western_Love.json   # Ground Truth data (Scene+Panels)
    │   ├── images              # Images of the comic
    │   ├── benchmarked_scenes  # Benchmark for the multi-modal-only scenes
    │   └── benchmarked_refined_scenes  # Refined benchmarks used in the paper
├── Prompts/                    # Prompts used for the scene segmentation
    ├── ScenePrompt.txt         # Prompt for the scene segmentation
    └── SceneRefinerPrompt.txt  # Prompt for the refined scene segmentation
├── __main__.py                 # Main function for scene segmentation
├── SceneSegmentation.py        # Functions for scene segmentation
├── SceneRefiner.py             # Functions for the refined scene segmentation
├── SceneUtils.py               # Utility functions
├── requirements.txt            # Requirements for building
└── benchmark.ipynb             # Benchmark of the scene segmentation
```

## Installation
To set up the environment and install dependencies, run:
```bash
pip install -r requirements.txt
```

## Usage
### Running Scene Segmentation
To perform scene segmentation on the dataset, use:
```bash
python __main__.py
```

### Evaluating Benchmarks
The dataset includes benchmarked scenes for evaluation. Open the Jupyter Notebook for benchmarking:
```bash
jupyter notebook benchmark.ipynb
```

## Dataset Details
Each comic title includes:
- **Ground Truth Data** (`.json` files) containing scene and panel annotations.
- **Images** of the comic pages.
- **Benchmarked Scenes** used in multi-modal scene analysis.
- **Refined Benchmarks** that improve upon initial segmentation.

## Contribution
We welcome contributions! If you'd like to add improvements or additional features, feel free to submit a pull request.

## License


## Contact
For any questions or issues, please open an issue on GitHub or contact the maintainers.
