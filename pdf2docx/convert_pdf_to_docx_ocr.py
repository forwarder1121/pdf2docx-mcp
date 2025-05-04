import os
import pytesseract
from pdf2image import convert_from_path
from docx import Document
from pdf2docx import Converter

def convert_pdf_to_docx(pdf_path, output_path, ocr=True):
    if not ocr:
        # 단순 변환 (텍스트 기반 PDF)
        cv = Converter(pdf_path)
        cv.convert(output_path, start=0, end=None)
        cv.close()
        return

    # OCR 기반 변환
    images = convert_from_path(pdf_path)
    doc = Document()

    for i, img in enumerate(images):
        text = pytesseract.image_to_string(img, lang='eng+kor')  # 한글/영어 인식
        doc.add_paragraph(text)
        doc.add_page_break()

    doc.save(output_path)
