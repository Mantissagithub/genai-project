from google.genai import types
from google import genai
from PIL import Image
from io import BytesIO
import PIL.Image
from dotenv import load_dotenv
import os
load_dotenv()


image = PIL.Image.open('data/img.jpg')

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

text_input = ('Hi, This is a picture of tshort'
            'Can you make it black and add white stripes',)

response = client.models.generate_content(
    model="gemini-2.0-flash-exp-image-generation",
    contents=[text_input, image],
    config=types.GenerateContentConfig(
      response_modalities=['Text', 'Image']
    )
)

for part in response.candidates[0].content.parts:
  if part.text is not None:
    print(part.text)
  elif part.inline_data is not None:
    image = Image.open(BytesIO(part.inline_data.data))
    image.show()