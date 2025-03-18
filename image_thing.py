from huggingface_hub import InferenceClient
import cv2 as cv
import numpy as np
import os
from dotenv import load_dotenv

load_dotenv()

client = InferenceClient(
    provider="hf-inference",
    api_key=os.getenv("HF_API"),
)

# output is a PIL.Image object
image = client.text_to_image(
	"Generate a skeletal structure of a sofa set. Focus on the underlying frame and support system, highlighting the connections and joints. Omit any upholstery or cushioning. Use simple lines and shapes to clearly define the form.",
	model="black-forest-labs/FLUX.1-schnell",
)

# Convert PIL.Image to OpenCV image
image = cv.cvtColor(np.array(image), cv.COLOR_RGB2BGR)

cv.imshow("image", image)
cv.waitKey(0)