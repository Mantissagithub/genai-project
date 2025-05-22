from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse

# import openai
from transformers import pipeline
import uvicorn
import json
from jinja2 import Template
import logging
from google.genai import types  # type: ignore
from google import genai
from dotenv import load_dotenv
import os

from image import image_generation, update_image
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
    return {"Message": "Welcome to Clothing"}


@app.post("/image-generation-base")
async def generate_base_image(request: Request):
    data = await request.json()
    print(data)
    prompt = data.get("initialPrompt", "")

    with open("prompt.txt", "w") as file:
        file.write(prompt)

    if not prompt:
        return {"message": "Failed to get prompt"}

    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"),)

    sys_instruct = """
Analyze the user's prompt to identify the fashion-related object they want to visualize, ensuring accurate extraction of the item's structure, form, and details. Maintain a sharp focus on external design elements while applying the specified color to the garment's surface.  

Key Considerations:  
1. Color Consistency: Apply the specified color uniformly to the item's surface, including fabric, material, and design elements. Avoid inconsistencies in shade or tone.  
2. Strictly External Features: Exclude any internal anatomical elements or references. The output should strictly represent the garment’s external structure, including seams, sleeves, collars, patterns, and textures.  
3. Structural Emphasis: Highlight critical fashion design elements such as stitching, edges, folds, fabric textures, pleats, buttons, zippers, or other relevant details that contribute to the item's visual identity.  
4. Clean White Background: Ensure a pure white background for optimal contrast and visibility, making the item’s shape and details stand out.  
5. Clear & Sharp Design: Maintain high visual distinction between the garment’s color, wireframe elements (if any), and the background. Avoid any blending or loss of detail.  
6. Default View: If the prompt does not specify multiple perspectives, default to a clear front view of the fashion item. If both front and back views are required, explicitly generate them.  
7. Return Format: The response must be structured as a Python dictionary containing a single key, 'prompt', with the optimized visualization prompt as its value.  

Output Format:  
python
{
    'prompt': 'your optimized fashion visualization prompt'
}
"""


    response = client.models.generate_content(
        model="gemini-2.0-flash",
        config=types.GenerateContentConfig(
            system_instruction=sys_instruct, response_mime_type="application/json",temperature=0.8
        ),
        contents=prompt,
    )

    json_response = json.loads(response.text)
    refined_prompt = json_response["prompt"]

    print("Gemini Response : ", refined_prompt)

    image_path = image_generation(refined_prompt)

    return {
        "message": "Image generated successfully",
        "original_prompt": prompt,
        "refined_prompt": refined_prompt,
        "imageUrl": image_path,
    }


@app.post("/image-generation-update")
async def update_existing_image(request: Request):
    data = await request.json()
    prompt = data.get("customizingPrompt", None)
    base_image_path = "Website/public/img.png"

    if not prompt:
        return {"message": "Failed to get prompt"}

    previous_prompt = ""

    with open("prompt.txt", "r") as file:
        previous_prompt = file.read()

    if not os.path.exists(base_image_path):
        return {"message": f"Base image not found at {base_image_path}"}

    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    sys_instruct = """
Analyze the provided image and the user’s modification request to identify and mask only the exact region that requires changes. Apply inpainting exclusively to the masked area, ensuring a precise, seamless blend with the rest of the image while maintaining the original style, lighting, texture, and context.

 Key Considerations  

 1. Strictly Targeted Modifications  
- Modify only the area explicitly described in the prompt.  
- If the request is for a specific part (e.g., left sleeve, right collar, bottom hem), ensure no modifications extend beyond the specified section.  
- Prevent unintended changes to surrounding regions, including symmetrical or connected areas unless explicitly requested.  

 2. Absolute Preservation of Structure  
- Maintain the original proportions, shape, and alignment unless the request explicitly requires structural modifications.  
- Ensure no distortion, stretching, or unintended design alterations occur in unmodified areas.  
- The modified section must blend naturally with the unaltered parts of the image.  

 3. No Unintended Symmetry Adjustments  
- If a change is requested for one side (e.g., left sleeve, right pocket), ensure that only that side is modified.  
- Do not automatically mirror or extend changes to the other side unless explicitly mentioned.  
- Changes to elements near symmetrical regions (e.g., collars, cuffs) must be precisely localized without affecting their mirrored counterpart.  

 4. Exclusion of Biological Features  
- Avoid introducing or modifying anatomical elements (e.g., muscles, bones, body shape) unless explicitly requested.  
- Ensure that the focus remains on garment or object modifications, not the underlying human structure.  

 5. Clear Boundaries & No Background Spillover  
- Use precise edge detection and masking to ensure changes are confined to the intended region.  
- Do not modify the background or introduce color bleed beyond the object being edited.  
- Keep modifications sharp, clean, and clearly distinguishable from unmodified areas.  

 6. No Overlapping or Unintended Blending  
- Maintain clear separation between:  
  - The modified area and unmodified sections.  
  - The background and the object (no fading, no blending outside the specified edit region).  
- If replacing an element (e.g., changing a button or pattern), ensure that the replacement is well-integrated but does not extend into unrelated areas.  

 7. No Texture or Additional Elements Unless Specified  
- Avoid generating new textures, decorations, or patterns unless the request explicitly requires them.  
- If a texture is necessary, it must appear well-defined and contained within the modified section.  

 8. No Assumptions – Follow Explicit Instructions  
- Do not make assumptions about what the user wants beyond what is explicitly stated in the request.  
- Ensure highly specific and localized modifications without unnecessary complexity.  

 9. Engineering-Style, Minimalistic Precision  
- Maintain precision, structure, and simplicity in modifications.  
- Avoid unnecessary artistic interpretations or design embellishments that deviate from the intended edit.  

 10. Output Format  
- Return the modification request as a Python dictionary with a single key, `'prompt'`, containing a detailed and explicit instruction for the required modification.  

 Output Format Example:  
{
    'prompt': 'your optimized modification prompt'
}
"""


    response = client.models.generate_content(
        model="gemini-2.0-flash",
        config=types.GenerateContentConfig(
            system_instruction=sys_instruct, response_mime_type="application/json"
        ),
        contents=prompt,
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
        "imageUrl": updated_image_path,
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)
