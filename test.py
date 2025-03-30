# from huggingface_hub import InferenceClient
# import cv2 as cv
# import os
# from dotenv import load_dotenv
# import numpy as np
# load_dotenv()


# base_image_path = "data/img.jpg"
# combined_prompt = "Apply a sepia tone filter to the image, shifting the overall color balance towards shades of brown. Increase the warmth of the image by boosting yellow and red hues. Add a subtle vignette effect with darkened brown edges to focus attention on the center. Ensure that the original composition and subject remain clearly visible and recognizable, with the core details and structure unchanged; only alter the color palette."

# client = InferenceClient(
#         provider="hf-inference",
#         api_key=os.getenv("HF_API_KEY"),
#     )

# with open(base_image_path, "rb") as f:
#     image_data = f.read()

# image = client.image_to_image(
#     image=image_data,
#     prompt=combined_prompt,
#     model="stabilityai/stable-diffusion-xl-refiner-1.0",
#     negative_prompt="blurry, distorted, low quality",
#     guidance_scale=7.5,
#     strength=0.6,
# )

# image_cv = cv.cvtColor(np.array(image), cv.COLOR_RGB2BGR)
# cv.imwrite("data/test.jpg", image_cv)


import torch

print(torch.cuda.is_available())
