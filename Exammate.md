# ExamMate — School Examination & Assessment Platform

## What is included
- School dashboard and setup screen
- Upload PDF, DOCX, TXT and image files
- AI workflow for suggested answers, marking, marking guides and question extraction
- AI paper generator by subject, level, topic, difficulty and question count
- Working sample Biology objective quiz with instant marking, explanations and local result history

## Run locally
1. Install Python 3.10 or newer.
2. Open a terminal in this folder.
3. Install dependencies: `pip install -r requirements.txt`
4. Set your API key on the server:
   - Windows PowerShell: `$env:OPENAI_API_KEY="your-key"`
   - macOS/Linux: `export OPENAI_API_KEY="your-key"`
5. Start: `python app.py`
6. Open `http://127.0.0.1:5000` in Chrome.

The AI features require an OpenAI API key and internet access. Keep the key on the server. Never put it in index.html or share it with learners.

## Image OCR
Image OCR requires Tesseract OCR installed on the server in addition to the Python packages. Scanned PDF OCR is not included in this starter build; PDFs with selectable text are supported.

## Before real school deployment
This is a starter prototype, not yet a production multi-school service. Add secure sign-in, school/teacher/student roles, a hosted database, private file storage, backups, rate limits, audit logs, HTTPS, privacy/consent processes and school-level data separation. Have teachers verify AI-generated answer keys and subjective marks before official use.
