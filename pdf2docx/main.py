from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse
import os
import shutil
from convert_pdf_to_docx_ocr import convert_pdf_to_docx

app = FastAPI()

@app.post("/convert")
async def convert_pdf(
    file: UploadFile = File(...),
    ocr: bool = Form(True)
):
    input_path = f"temp/{file.filename}"
    output_path = input_path.replace(".pdf", ".docx")

    os.makedirs("temp", exist_ok=True)

    with open(input_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    convert_pdf_to_docx(input_path, output_path, ocr=ocr)

    return FileResponse(output_path, filename=os.path.basename(output_path))

@app.get("/")
def read_root():
    return {"message": "PDF to DOCX with OCR MCP server"}
