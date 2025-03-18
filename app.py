from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
# import openai
from transformers import pipeline
import uvicorn
import json
from jinja2 import Template
import google.genai as genai
import logging
from google.genai import types
from google import genai
from dotenv import load_dotenv
import os

# app = FastAPI()
# genai.configure(api_key=api_key)

load_dotenv()

# Load the Flux Schnell model
# flux_pipeline = pipeline("text-generation", model="huggingface/flux-schnell")

# Function to refine prompt using Gemini
def refine_prompt_with_gemini(prompt: str):
    # response = openai.ChatCompletion.create(
    #     model="gemini", 
    #     messages=[
    #         {"role": "system", "content": "Extract only the skeletal structure from the given prompt."},
    #         {"role": "user", "content": prompt}
    #     ],
    #     api_key=api_key
    # )
    # model = genai.GenerativeModel(
    #     "models/gemini-1.5-flash",
    #     system_instruction="Create a prompt to create a skeletal structure of the thing mentioned in the promtp by the user. Take only the object and give the prompt to flux to generate the skeletal structure.",
    #     # generation_config={"response_mime_type": "application/json"},
    # )
    # try:
    #     resp = model.generate_content(prompt)
    #     print(resp)
    # except Exception as e:
    #     logging.error(f"Error generating content from Gemini: {e}")
    #     return {"error": "Failed to generate content from Gemini."}
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    sys_instruct = "Create a prompt to create a skeletal structure of the thing mentioned in the prompt by the user. Take only the object and give the prompt to flux to generate the skeletal structure."

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        config=types.GenerateContentConfig(
            system_instruction=sys_instruct,response_mime_type='application/json'),
        contents=prompt
    )
    print(response.text)
    json_response = json.loads(response.text)
    # refined_prompt = json_response["content"]
    print(json_response["prompt"])

    # print(response)
    return response.text


# @app.get("/", response_class=HTMLResponse)
# async def index():
#     html_template = Template("""
#     <!DOCTYPE html>
#     <html>
#     <head>
#         <title>Flux Schnell AI</title>
#     </head>
#     <body>
#         <h1>Enter Prompt</h1>
#         <form action="/generate" method="post">
#             <textarea name="prompt" rows="4" cols="50"></textarea><br>
#             <button type="submit">Generate</button>
#         </form>
#     </body>
#     </html>
#     """)
#     return html_template.render()

# @app.post("/generate", response_class=HTMLResponse)
# async def generate(request: Request, prompt: str = Form(...)):
#     refined_prompt = refine_prompt_with_gemini(prompt)
#     flux_result = flux_pipeline(refined_prompt, max_length=200)[0]["generated_text"]
    
#     html_template = Template("""
#     <!DOCTYPE html>
#     <html>
#     <head>
#         <title>Flux Schnell AI</title>
#     </head>
#     <body>
#         <h1>Generated Response</h1>
#         <p><strong>Refined Prompt:</strong> {{ refined_prompt }}</p>
#         <p><strong>Flux Output:</strong> {{ flux_result }}</p>
#         <a href="/">Go Back</a>
#     </body>
#     </html>
#     """)
#     return html_template.render(refined_prompt=refined_prompt, flux_result=flux_result)

# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8000)

refine_prompt_with_gemini("Create a prompt to generate a skeletal structure of a sofaset.")

