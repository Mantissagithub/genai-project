from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
# import openai
from transformers import pipeline
import uvicorn
import json
from jinja2 import Template
import google.genai as genai # type: ignore
import logging
from google.genai import types # type: ignore
from google import genai
from dotenv import load_dotenv
import os

from image import image_generation,update_image
load_dotenv()

app = FastAPI()


@app.get("/")
def home():
    return {"Message":"Welcome to Clothing"}

@app.post("/image-generation-base")
async def generate_base_image(request: Request):
    data = await request.json()
    prompt = data.get("prompt", None)

    with open("prompt.txt","w") as file:
        file.write(prompt)
    
    if not prompt:
        return {"message": "Failed to get prompt"}    
    
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    
    sys_instruct = """Analyze the user's prompt and extract only the object they want to visualize.
    Create a detailed prompt for generating a clean, wireframe/skeletal structure of this object.
    Focus only on the structural elements and form - no textures, colors, or decorative elements.
    The output should be a minimalist, engineering-style visualization showing only the essential framework.
    Return your response as valid JSON with a single 'prompt' field containing your generated prompt.
    Do not include any metadata or text within the image itself in the prompt.
    {
        "prompt":"your generated prompt"
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
        "image_path": image_path
    }


@app.post("/image-generation-update")
async def update_existing_image(request: Request):
    data = await request.json()
    prompt = data.get("prompt", None)
    base_image_path = "data/img.jpg"  


    if not prompt:
        return {"message": "Failed to get prompt"}
    
    previous_prompt = ""
    
    with open("prompt.txt","r") as file:
        previous_prompt = file.read()

    if not os.path.exists(base_image_path):
        return {"message": f"Base image not found at {base_image_path}"}
    
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    sys_instruct = """Analyze both the original prompt and the new update request to create a detailed instruction for transforming an existing image.
    
    ORIGINAL PROMPT: {previous_prompt}
    UPDATE REQUEST: {prompt}
    
    Create a detailed prompt that instructs the image generation model to modify the existing image according to the update request,
    while maintaining the essential structure established by the original prompt.
    
    Return your response as valid JSON with a single 'prompt' field containing your generated prompt.
    {
        "prompt":"your generated prompt"
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
        "updated_image_path": updated_image_path
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)
