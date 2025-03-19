from huggingface_hub import InferenceClient
import cv2 as cv
import numpy as np
import os
from dotenv import load_dotenv

load_dotenv()

def image_generation(prompt):
    client = InferenceClient(
        provider="hf-inference",
        api_key=os.getenv("HF_API_KEY"),
    )

    image = client.text_to_image(
        prompt,
        model="black-forest-labs/FLUX.1-schnell",
    )

    image = cv.cvtColor(np.array(image), cv.COLOR_RGB2BGR)

    cv.imwrite("data/img.jpg", image)
    cv.waitKey(0)

    return