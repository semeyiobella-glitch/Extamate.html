import os, tempfile
from flask import Flask, request, jsonify, send_from_directory
from openai import OpenAI
from werkzeug.utils import secure_filename

app=Flask(__name__, static_folder=".")
client = OpenAI()  # reads OPENAI_API_KEY from the server environment
ALLOWED={".pdf",".docx",".txt",".png",".jpg",".jpeg",".webp"}

def extract_text(path, ext):
    if ext==".pdf":
        from pypdf import PdfReader
        return "\n".join(p.extract_text() or "" for p in PdfReader(path).pages)
    if ext==".docx":
        from docx import Document
        return "\n".join(p.text for p in Document(path).paragraphs)
    if ext==".txt":
        return open(path,encoding="utf-8",errors="ignore").read()
    if ext in {".png",".jpg",".jpeg",".webp"}:
        try:
            from PIL import Image
            import pytesseract
            return pytesseract.image_to_string(Image.open(path))
        except Exception as e:
            raise ValueError("Image OCR needs Tesseract OCR and Pillow installed on the server.")
    raise ValueError("Unsupported file type.")

def ask_ai(prompt):
    response=client.responses.create(model=os.getenv("OPENAI_MODEL","gpt-4.1-mini"),input=prompt)
    return response.output_text

@app.get("/")
def home(): return send_from_directory(".", "index.html")

@app.post("/api/analyse")
def analyse():
    f=request.files.get("file")
    if not f: return jsonify(error="No file uploaded"),400
    ext=os.path.splitext(secure_filename(f.filename))[1].lower()
    if ext not in ALLOWED: return jsonify(error="Use PDF, DOCX, TXT, PNG or JPG."),400
    path=None
    try:
        with tempfile.NamedTemporaryFile(delete=False,suffix=ext) as tmp:
            f.save(tmp.name); path=tmp.name
        content=extract_text(path,ext)
        if not content.strip(): return jsonify(error="No readable text found. For scanned PDFs, OCR support must be enabled."),422
        content=content[:45000]
        task=request.form.get("task","solve")
        notes=request.form.get("notes","")
        instructions={
          "solve":"Extract each question, provide a correct suggested answer, explain it clearly, and show marks where possible.",
          "mark":"Identify the questions and learner responses. Mark strictly against the supplied marking guide if present. If no guide is supplied, state that marks are provisional and explain the criteria. Give score, corrections and feedback.",
          "guide":"Create a structured marking guide with expected points, acceptable alternatives and marks per point. Ensure totals add up.",
          "extract":"Extract and number all questions, preserving sub-question structure and marks. Do not invent missing text."
        }.get(task,"Analyse the document.")
        prompt=f"""You are ExamMate, an educational assessment assistant supporting schools.
Task: {instructions}
Additional teacher instructions: {notes}
Document text:
{content}
Be accurate and transparent. Do not pretend an unreadable section was read. Separate facts from assumptions. For marking, never invent a learner's answer or an official marking scheme. Flag ambiguous questions and recommend teacher review. Return clear headings."""
        return jsonify(result=ask_ai(prompt))
    except Exception as e: return jsonify(error=str(e)),500
    finally:
        if path and os.path.exists(path): os.unlink(path)

@app.post("/api/generate")
def generate():
    subject=request.form.get("subject","Biology"); level=request.form.get("level","Secondary"); topic=request.form.get("topic",""); difficulty=request.form.get("difficulty","Mixed")
    number=max(1,min(50,int(request.form.get("number","10")))); fmt=request.form.get("format","MCQ")
    prompt=f"""Create an original school practice examination for {subject}, level {level}.
Topic: {topic or 'a balanced selection of core topics'}. Difficulty: {difficulty}.
Generate exactly {number} questions. Format: {fmt}. For MCQs give four plausible options A-D and one unambiguous best answer.
Use clear curriculum-appropriate language. After the paper, provide a separate answer key and brief explanations. Give total marks and suggested time. Do not claim this is an official examination or reproduce a copyrighted paper."""
    try: return jsonify(paper=ask_ai(prompt))
    except Exception as e: return jsonify(error=str(e)),500

if __name__=="__main__":
    app.run(host="0.0.0.0",port=int(os.getenv("PORT","5000")),debug=False)
