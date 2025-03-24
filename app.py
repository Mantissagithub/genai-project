from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
# import openai
from transformers import pipeline
import uvicorn
import json
from jinja2 import Template
import logging
from google.genai import types # type: ignore
from google import genai
from dotenv import load_dotenv
import os

from image import image_generation,update_image
from fastapi.middleware.cors import CORSMiddleware
load_dotenv()


app = FastAPI()

# Configure CORS for the application
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "Accept"],
    expose_headers=["Content-Type"],
    max_age=600, 
)

@app.get("/")
def home():
    return {"Message":"Welcome to Clothing"}

@app.post("/image-generation-base")
async def generate_base_image(request: Request):
    data = await request.json()
    print(data)
    prompt = data.get("initialPrompt", "")

    with open("prompt.txt","w") as file:
        file.write(prompt)
    
    if not prompt:
        return {"message": "Failed to get prompt"}    
    
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    
    sys_instruct = """
    Analyze the user's prompt and extract the object they want to visualize. 
    Create a detailed prompt for generating a clean, wireframe/skeletal structure of this object. 
    Focus only on the structural elements and form of the object. Completely avoid biological elements such as bones, muscles, organs, or any human or animal anatomy under all circumstances. 

    If the user requests a base object (e.g., a shirt, a table, etc.), ensure the base is simple and distinct. The base and the object must be visually separated by contrast in color or outline to maintain clarity. 
    For example, if a shirt is requested, visualize only the shirt's structure (e.g., seams, sleeves, and neckline) without any internal or anatomical elements. 

    The visualization should:
    1. Use a clean, contrasting background (e.g., white background with dark outlines for objects).
    2. Exclude any biological, anatomical, or human-related structures entirely.
    3. Maintain a simple, minimalistic design with no textures, decorations, or additional elements unless explicitly specified.
    4. Avoid blending of the base object and background, ensuring clear visual separation.
    5. Focus on engineering-style precision and form, emphasizing only the object's essential framework.

    Return the response as a Python dictionary with a single 'prompt' key containing your generated prompt. 
    Be highly detailed, specifying all necessary features clearly and concisely, avoiding any ambiguity or assumptions. 
    Do not include any metadata, text, or unrelated elements in the prompt.

    Output format:
    {
        'prompt': 'your generated prompt'
    }
    """



    response = client.models.generate_content(
        model="gemini-2.0-flash",
        config=types.GenerateContentConfig(
            system_instruction=sys_instruct, response_mime_type='application/json'),
        contents=prompt
    )
    
    json_response = json.loads(response.text)
    refined_prompt = json_response["prompt"]

    print("Gemini Response : ", refined_prompt)
    
    image_path = image_generation(refined_prompt)
    
    return {
        "message": "Image generated successfully",
        "original_prompt": prompt,
        "refined_prompt": refined_prompt,
        "imageUrl": image_path
    }


@app.post("/image-generation-update")
async def update_existing_image(request: Request):
    data = await request.json()
    prompt = data.get("customizingPrompt", None)
    base_image_path = "data/img.png"  


    if not prompt:
        return {"message": "Failed to get prompt"}
    
    previous_prompt = ""
    
    with open("prompt.txt","r") as file:
        previous_prompt = file.read()

    if not os.path.exists(base_image_path):
        return {"message": f"Base image not found at {base_image_path}"}
    
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    sys_instruct = """
    Analyze both the original prompt and the new update request to create a detailed instruction for transforming an existing image.

    ORIGINAL PROMPT: """ + previous_prompt + """
    UPDATE REQUEST: """ + prompt + """

    Create a detailed prompt that instructs the image generation model to modify the existing image according to the update request, while maintaining the essential structure and context established by the original prompt.

    Ensure the following conditions are met:
    1. Preserve the overall structural integrity and key elements specified in the original prompt unless explicitly instructed to alter them.
    2. Avoid introducing biological elements (e.g., muscles, bones, or anatomy) under any circumstances unless explicitly mentioned in the update request.
    3. Ensure clear visibility by maintaining a contrasting background and object colors (e.g., white background with dark outlines or vice versa).
    4. Exclude textures, decorations, or additional elements unless explicitly requested.
    5. Ensure any textures generated are displayed on a plain background, and the object must appear as if floating in the air with no additional environmental context.
    6. Avoid ambiguity in describing modifications; be highly specific and clearly explain the required changes.
    7. If the update request involves adding or changing a base object (e.g., a shirt or a table), ensure it is simple, distinct, and visually separated from the main object.
    8. Avoid blending of the base object, background, or any new additions, ensuring all elements are clearly distinguishable.
    9. Focus on clean, minimalistic, and engineering-style design principles.

    Return the response as a Python dictionary with a single 'prompt' key containing your generated prompt. Be explicit and precise in detailing the modifications, avoiding assumptions or unnecessary complexity.

    Output format:
    {
        'prompt': 'your generated prompt'
    }
    """



    response = client.models.generate_content(
        model="gemini-2.0-flash",
        config=types.GenerateContentConfig(
            system_instruction=sys_instruct, response_mime_type='application/json'),
        contents=prompt
    )
    
    json_response = json.loads(response.text)
    refined_prompt = json_response["prompt"]
    print("Gemini Response for update: ", refined_prompt)
    
    updated_image_path = update_image(refined_prompt)
    
    return {
        "message": "Image updated successfully",
        "original_prompt": prompt,
        "refined_prompt": refined_prompt,
        "base_image_path": base_image_path,
        "imageUrl": updated_image_path
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)