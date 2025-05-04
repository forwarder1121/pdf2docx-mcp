from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
import shutil
from convert_pdf_to_docx_ocr import convert_pdf_to_docx

app = FastAPI()

# 📁 파일 업로드 기반 변환 (사용자 UI 전용)
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


# 🌐 MCP용 핸들러: tools/list
@app.post("/tools/list")
def list_tools():
    return {
        "tools": [
            {
                "name": "convert-pdf",
                "description": "Convert a PDF to DOCX using OCR"
            }
        ]
    }

# 📤 MCP용 핸들러: tools/call
@app.post("/tools/call")
def call_tool(payload: dict):
    if payload.get("name") != "convert-pdf":
        return {"error": f"Unknown tool: {payload.get('name')}"}

    args = payload.get("arguments", {})
    input_path = args.get("input_path")
    output_path = args.get("output_path")
    use_ocr = args.get("use_ocr", True)

    if not input_path or not output_path:
        return {"error": "Missing required parameters: input_path or output_path"}

    try:
        convert_pdf_to_docx(input_path, output_path, ocr=use_ocr)
        return {"status": "success", "output_path": output_path}
    except Exception as e:
        return {"status": "failed", "error": str(e)}
