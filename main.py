from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from uuid import uuid4
from typing import List
from pdf2image import convert_from_bytes
from PIL import Image, ImageEnhance
import base64
import io
import os

app = FastAPI()


def enhance_image(image: Image.Image) -> Image.Image:
    # Aumenta o contraste e nitidez
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2.0)  # Ajuste conforme necessário

    enhancer = ImageEnhance.Sharpness(image)
    image = enhancer.enhance(1.5)

    return image


def image_to_base64(image: Image.Image) -> str:
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")


@app.post("/convert-pdf")
async def convert_pdf(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        return JSONResponse(status_code=400, content={"error": "O arquivo deve ser um PDF."})

    contents = await file.read()
    uuid_code = str(uuid4())
    try:
        images = convert_from_bytes(contents, dpi=300)  # Alta resolução

        base64_images: List[str] = []
        for img in images:
            enhanced = enhance_image(img)
            base64_img = image_to_base64(enhanced)
            base64_images.append(base64_img)

        return {
            "uuid": uuid_code,
            "filename": file.filename,
            "images_base64": base64_images
        }

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
