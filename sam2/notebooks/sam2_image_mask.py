import torch
from sam2.build_sam import build_sam2
from sam2.sam2_image_predictor import SAM2ImagePredictor
from PIL import Image
import numpy as np

checkpoint = "../checkpoints/sam2.1_hiera_large.pt"
model_cfg = "../sam2/configs/sam2.1/sam2.1_hiera_l.yaml"
predictor = SAM2ImagePredictor(build_sam2(model_cfg, checkpoint))

image = Image.open("images/cars.jpg")
image = np.array(image.convert("RGB"))

point_coords = 100  # Example coordinates
point_labels = [1]  # Example label (foreground)

with torch.inference_mode(), torch.autocast("cuda", dtype=torch.bfloat16):
    predictor.set_image(image)
    masks, _, _ = predictor.predict(
        "mask the red colour car",
        point_coords=point_coords,
        point_labels=point_labels,
    )
