# AI Email Assistant with PDF Knowledge Base

Python Based MCP Agent to Automate mail reponses (RAG)

## Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Setup Gmail API
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable **Gmail API**
4. Go to **Credentials** → **Create Credentials** → **OAuth 2.0 Client ID**
5. Choose **Desktop Application**
6. Download the JSON file and rename it to `credentials.json`
7. Put `credentials.json` in the project folder

### 3. Install Ollama (AI Model)
1. Download [Ollama](https://ollama.ai/)
2. Install and start it
3. Pull the Mistral model (or any model you want):
```bash
ollama pull mistral:7b
```

### 4. Add Your PDF
- add your own PDF file to the project
- Update the filename in `pdf_ingest.py` (line 8):
```python
PDF_PATH = Path("pdf_name.pdf")
```

##  How to Run it

### Step 1: Process Your PDF
```bash
python pdf_ingest.py
```
*This creates embeddings from your PDF (only run unless you change the pdf)*

### Step 2: Start Email Monitoring
```bash
python main.py
```
*This checks your latest unread email and creates a draft reply*

## How does it work?

1. **Checks** your latest unread Gmail
2. **Determines** if the question needs your PDF knowledge
3. **Generates** a smart reply using AI + your PDF content
4. **Saves** the reply as a draft (you review before sending)
5. **Marks** the email as read

## First Run
- First time will open browser to authorize Gmail access
- Choose your Gmail account and allow permissions
- `token.json` will be created automatically

## 📁 Files You Need
- `credentials.json` (from Google)
- Your PDF file
- Everything else is included!

## ⚙️ Settings
- **PDF filename**: Change in `pdf_ingest.py`
- **LLM**: Change `MODEL` in `llm.py` 

---
**That's it!** Your AI email assistant is ready to help with PDF-based email reponse automation

- **Note:** The Generated mail will be saved in Draft
