from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import spacy
import sys
import subprocess

# Load or Download SpaCy model
try:
    nlp = spacy.load("en_core_web_trf")
except OSError:
    print("en_core_web_trf model not found. Downloading...")
    subprocess.run(["python", "-m", "spacy", "download", "en_core_web_trf"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    nlp = spacy.load("en_core_web_trf")

# Import custom model and utils
try:
    from model.utils import load_contextual_model, detect_pii
except Exception as e:
    print("Error importing model or utils:", e)
    sys.exit(1)

# Initialize FastAPI app
app = FastAPI()

# Load contextual model
try:
    contextual_model = load_contextual_model()
except Exception as e:
    print("Error loading contextual model:", e)
    sys.exit(1)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Key
API_KEY = "your-secret-key"

# Request schema
class TextRequest(BaseModel):
    text: str

# Main route
@app.post("/api/detect-pii")
def detect(data: TextRequest, x_api_key: str = Header(default=None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")
    
    result = detect_pii(contextual_model, data.text)
    return {"results": result}