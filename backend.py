import cv2
import numpy as np
from diffusers import AutoPipelineForInpainting, DEISMultistepScheduler
import torch
from PIL import Image, ImageFilter
from dotenv import load_dotenv, find_dotenv
import os

print(load_dotenv(find_dotenv(".env")))
CACHE_DIR = os.getenv("CACHE_DIR")


def inpaint_cv2(image, mask, method="telea", radius=3):

    flags = cv2.INPAINT_NS
    if method == "telea":
        flags = cv2.INPAINT_TELEA
    print(method)
    mask = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
    # perform inpainting using OpenCV
    output = cv2.inpaint(image, mask, radius, flags=flags)
    return output

def dream8(image, mask, prompt="", ratio=1, merge=False):


    init_image = Image.fromarray(image).convert("RGB")
    init_mask = Image.fromarray(mask).convert("RGBA")
    height_size = int(round(init_image.size[1]*ratio))
    width_size = int(round(init_image.size[0]*ratio))
    height_size -= height_size % 8
    width_size -= width_size % 8

    pipe = AutoPipelineForInpainting.from_pretrained('Lykon/dreamshaper-8-inpainting', torch_dtype=torch.float16, variant="fp16", cache_dir=CACHE_DIR)
    pipe.scheduler = DEISMultistepScheduler.from_config(pipe.scheduler.config)
    pipe = pipe.to("cuda")

    real_prompt = "photorealistic, 8k, " + prompt
    negative_prompt = "unrealistic, text, human, artefact, furniture, chairs, couch, sofa, table, objects, clutter, shadows"

    inpainted = pipe(prompt=real_prompt, image=init_image, mask_image=init_mask, num_inference_steps=25,
                     height=height_size, width=width_size, negative_prompt=negative_prompt).images[0] 
    
    if merge:
        inpainted = combine_output_blend(init_image, inpainted, init_mask, blur_radius=6)

    
    inpainted_ndarray = np.array(inpainted)
    return inpainted_ndarray


def extract_mask(image, mask_image):

    image_np = np.array(image)
    mask_image_np = np.array(mask_image)

    mask = mask_image_np[:, :, 2] != 0
    output_image = np.zeros_like(image_np)
    output_image[mask] = image_np[mask]
    final_image = Image.fromarray(output_image)

    return final_image

def convert_to_transparent(image):
    image = image.convert("RGBA")
    image_np = np.array(image)
    image_np[image_np[:, :, 0] == 0] = [0, 0, 0, 0]
    image_np = Image.fromarray(image_np, mode="RGBA")
    return image_np




def combine_init_generated(init_image, generated_image, mask):
    resized_output = generated_image.resize(init_image.size)
    resized_mask = mask.resize(init_image.size)
    extracted_mask = extract_mask(resized_output, resized_mask)

    extracted_mask_transparent = convert_to_transparent(extracted_mask)

    combined_image = Image.new("RGB", init_image.size)
    combined_image.paste(init_image, (0, 0), mask=resized_mask)
    combined_image.paste(extracted_mask_transparent, (0, 0), mask=extracted_mask_transparent)

    return combined_image
        

def combine_output_blend(init_image, output_image, mask_image, blur_radius=6):
    # Resize output to original size
    resized_output = output_image.resize(init_image.size, Image.LANCZOS)
    mask_resized = mask_image.resize(init_image.size)

    # Convert all to numpy
    img_init = np.array(init_image).astype(np.float32)
    img_output = np.array(resized_output).astype(np.float32)
    mask_np = np.array(mask_resized.convert("L")).astype(np.float32) / 255.0

    # Flouter le masque pour blending progressif
    mask_blurred = Image.fromarray((mask_np * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(radius=blur_radius))
    mask_blurred_np = np.array(mask_blurred).astype(np.float32) / 255.0

    # Alpha blending
    blended = (1 - mask_blurred_np[..., None]) * img_init + mask_blurred_np[..., None] * img_output
    blended = blended.clip(0, 255).astype(np.uint8)

    return Image.fromarray(blended)


def inpaint_deepfill(image, mask):
    # call your custom algorithm for inpainting here 
    # and pass your image and mask to your algorithm
    # return your output image with format numpy ndarray
    # for now just returning the input image
    print("deepfill - not implemented yet")
    return image    


def enhance_image(image: np.ndarray, params=None) -> np.ndarray:
    """
    Placeholder pour l'algorithme d'enhancement.
    Vous implémenterez ici la logique.
    """
    # TODO: implement enhancement algorithm
    return image


def change_style(image: np.ndarray, style_params=None) -> np.ndarray:
    """
    Placeholder pour l'algorithme de changement de style (depth image generation).
    """
    # TODO: implement style change algorithm
    return image