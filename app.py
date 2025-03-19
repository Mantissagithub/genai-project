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

from image import image_generation

load_dotenv()

app = FastAPI()


@app.get("/")
def home():
    return {"Message":"Welcome to Clothing"}

@app.post("/image-generation")
async def refine_prompt_with_gemini(request: Request):
    data = await request.json()
    prompt = data.get("prompt", None)

    if not prompt:
        return {"Message":"Failed to get prompt "}    
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
    print("Gemini Response : ", json_response["prompt"])
    
    image_generation(prompt)
    return response.text


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)

# refine_prompt_with_gemini("Create a prompt to generate a skeletal structure of a sofaset.")

