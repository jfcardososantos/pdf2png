import io
import base64
import uuid
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from PIL import Image
import pytesseract
import numpy as np
import cv2

app = FastAPI()

def pdf_to_images(pdf_file_bytes) -> list:
    from pdf2image import convert_from_bytes
    return convert_from_bytes(pdf_file_bytes, dpi=300)

def pil_to_cv2(image: Image.Image) -> np.ndarray:
    return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

def crop_content_region(cv_image: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 245, 255, cv2.THRESH_BINARY_INV)
    coords = cv2.findNonZero(thresh)
    x, y, w, h = cv2.boundingRect(coords)
    cropped = cv_image[y:y+h, x:x+w]
    return cropped

def find_vantagens_region(cv_image: np.ndarray) -> np.ndarray:
    ocr_data = pytesseract.image_to_data(cv_image, output_type=pytesseract.Output.DICT, lang='por')
    vantagens_y = None
    for i, text in enumerate(ocr_data['text']):
        if 'VANTAGEN' in text.upper():
            vantagens_y = ocr_data['top'][i]
            break
    if vantagens_y is None:
        return None

    # assume que a tabela vai da posição encontrada até o final da imagem
    height = cv_image.shape[0]
    return cv_image[vantagens_y:height, :]

def extract_personal_data(image: Image.Image) -> dict:
    text = pytesseract.image_to_string(image, lang='por')
    lines = text.splitlines()
    result = {
        "nome": None,
        "matricula": None,
        "mes": None,
        "classe": None
    }
    for line in lines:
        if 'Nome' in line:
            result['nome'] = line.split(':')[-1].strip()
        if 'Matr' in line or 'Matrícula' in line:
            result['matricula'] = line.split(':')[-1].strip()
        if 'Classe' in line:
            result['classe'] = line.split(':')[-1].strip()
        if 'Mês' in line:
            result['mes'] = line.split(':')[-1].strip()
    return result

def image_to_base64(image: np.ndarray) -> str:
    img_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    buffer = io.BytesIO()
    img_pil.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode()

@app.post("/infer")
async def process_pdf(file: UploadFile = File(...)):
    uuid_code = str(uuid.uuid4())
    images = pdf_to_images(await file.read())

    results = []
    for img in images:
        cv_img = pil_to_cv2(img)
        cropped_full = crop_content_region(cv_img)

        # divide a imagem em 2 partes: cabeçalho (dados pessoais) e tabela (vantagens)
        vantagens_img = find_vantagens_region(cropped_full)
        if vantagens_img is None:
            continue  # ignora página sem tabela

        top_half = cropped_full[0:vantagens_img.shape[0], :]

        dados_pessoais = extract_personal_data(Image.fromarray(top_half))
        vantagens_base64 = image_to_base64(vantagens_img)

        results.append({
            "uuid": uuid_code,
            "filename": file.filename,
            "dados_pessoais": dados_pessoais,
            "imagem_vantagens_base64": vantagens_base64
        })

    return JSONResponse(content=results)
