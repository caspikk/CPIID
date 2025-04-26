from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys

try:
    from model.utils import load_contextual_model, detect_pii
except Exception as e:
    print("Error importing model or utils:", e)
    sys.exit(1)

app = FastAPI()

try:
    contextual_model = load_contextual_model()
except Exception as e:
    print("Error loading contextual model:", e)
    sys.exit(1)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

API_KEY = "your-secret-key"

class TextRequest(BaseModel):
    text: str

@app.post("/api/detect-pii")
def detect(data: TextRequest, x_api_key: str = Header(default=None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")
    
    result = detect_pii(contextual_model, data.text)
    return { "results": result }