import SceneSegmentation
import SceneRefiner
import google.generativeai as genai

model_name: str = "gemini-2.0-flash-thinking-exp"
model_gemini = genai.GenerativeModel(model_name=model_name)
#Enter API Key for Gemini
genai.configure(api_key="")


if __name__ == '__main__':
    name = "Alley_Oop"

    #Multi-modal Iteration
    #Generate JSON with scene data
    SceneSegmentation.predict_scene_data(name,model_gemini)
    #Segment the JSON into scenes
    SceneSegmentation.segment_scenes(name)

    #LLM-Refined Iteration
    #Generate refined JSON data
    #Note: If the JSON is in incorrect format, a TXT of the faulty JSON will be saved
    SceneRefiner.refine_data(name,model_gemini)
    #Segment the refined JSON into scenes
    SceneRefiner.segment_scenes(name)