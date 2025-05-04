from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, FileResponse
import os
import shutil
from mcp_app.convert_pdf_to_docx_ocr import convert_pdf_to_docx

app = FastAPI()

# MCP가 요구하는 /tools/list 엔드포인트
@app.post("/tools/list")
async def list_tools():
    return {
        "tools": [
            {
                "name": "convert-pdf",
                "description": "Convert a PDF to a DOCX file using optional OCR",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ocr": {
                            "type": "boolean",
                            "default": True
                        },
                        "filename": {
                            "type": "string",
                            "description": "Filename of uploaded PDF"
                        },
                        "file_content": {
                            "type": "string",
                            "description": "Base64 encoded file content"
                        }
                    },
                    "required": ["filename", "file_content"]
                }
            }
        ]
    }

# MCP가 요구하는 JSON-RPC 2.0 형태의 호출 처리
@app.post("/tools/call")
async def call_tool(request: Request):
    body = await request.json()
    method = body.get("method")
    params = body.get("params", {})
    request_id = body.get("id")

    if method == "convert-pdf":
        try:
            import base64
            filename = params["filename"]
            file_content = base64.b64decode(params["file_content"])
            ocr = params.get("ocr", True)

            # 파일 저장
            os.makedirs("temp", exist_ok=True)
            input_path = f"temp/{filename}"
            output_path = input_path.replace(".pdf", ".docx")

            with open(input_path, "wb") as f:
                f.write(file_content)

            # 변환 수행
            convert_pdf_to_docx(input_path, output_path, ocr=ocr)

            # 결과 파일을 base64로 반환
            with open(output_path, "rb") as f:
                converted_data = base64.b64encode(f.read()).decode("utf-8")

            result = {
                "filename": os.path.basename(output_path),
                "docx_base64": converted_data
            }

        except Exception as e:
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32000,
                    "message": str(e)
                }
            })

        return JSONResponse({
            "jsonrpc": "2.0",
            "id": request_id,
            "result": result
        })

    else:
        return JSONResponse({
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": -32601,
                "message": "Method not found"
            }
        })

# 기본 루트 테스트용
@app.get("/")
def read_root():
    return {"message": "MCP-compliant PDF to DOCX OCR server"}
