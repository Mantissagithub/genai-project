from huggingface_hub import InferenceClient
import numpy as np
import os
from dotenv import load_dotenv
from PIL import Image
from io import BytesIO
import base64
from google import genai
from google.genai import types
import PIL.Image

from firebase import upload_file_to_firebase
import time

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def image_generation(prompt):
    response = client.models.generate_content(
        model="gemini-2.0-flash-exp-image-generation",
        contents=prompt,
        config=types.GenerateContentConfig(response_modalities=["Text", "Image"]),
    )

    for part in response.candidates[0].content.parts:
        if part.text is not None:
            print(part.text)
        elif part.inline_data is not None:
            image = Image.open(BytesIO((part.inline_data.data)))
            image.save("Website/public/update_img.png")
            image.save("Website/public/img.png")
            timestamp = int(time.time())
            file_url = upload_file_to_firebase(f"Website/public/img.png")

    return file_url


def update_image(update_prompt):
    image = PIL.Image.open("Website/public/update_img.png")

    response = client.models.generate_content(
        model="gemini-2.0-flash-exp-image-generation",
        contents=[update_prompt, image],
        config=types.GenerateContentConfig(response_modalities=["Text", "Image"]),
    )

    for part in response.candidates[0].content.parts:
        if part.text is not None:
            print(part.text)
        elif part.inline_data is not None:
            image = Image.open(BytesIO(part.inline_data.data))
            image.save("Website/public/update_img.png")
            timestamp = int(time.time())
            file_url = upload_file_to_firebase(f"Website/public/update_img.png")
    return file_url
