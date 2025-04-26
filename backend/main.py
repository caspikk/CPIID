from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from model.utils import load_contextual_model, detect_pii

app = FastAPI()
contextual_model = load_contextual_model()

# CORS for Frontend Access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for now (public API)
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Key for security
API_KEY = "your-secret-key"

# Request body format
class TextRequest(BaseModel):
    text: str

# PII Detection endpoint
@app.post("/api/detect-pii")
def detect(data: TextRequest, x_api_key: str = Header(default=None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")
    
    results = detect_pii(contextual_model, data.text)
    return { "results": results }