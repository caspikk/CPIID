import os
import re
import torch
import spacy
import subprocess
from transformers import DebertaV2Tokenizer, DebertaV2ForSequenceClassification

# Load SpaCy small English model
# Load lightweight small spaCy model
def load_spacy_model():
    try:
        nlp = spacy.load("en_core_web_sm")
    except OSError:
        from spacy.cli import download
        download("en_core_web_sm")
        nlp = spacy.load("en_core_web_sm")
    return nlp
nlp = load_spacy_model()

# Load DeBERTa tokenizer once
tokenizer = DebertaV2Tokenizer.from_pretrained("microsoft/deberta-v3-base")

def load_contextual_model():
    """
    Loads the DeBERTa V3 model and your saved contextual_pii_model.pth weights.
    If weights are missing, downloads from Google Drive.
    """
    model_path = os.path.join(os.path.dirname(__file__), 'contextual_pii_model.pth')

    # If model file does not exist, download it
    if not os.path.exists(model_path):
        print("🔽 Model file not found. Downloading from Google Drive...")

        # Install gdown if not installed
        try:
            import gdown
        except ImportError:
            subprocess.check_call(["pip", "install", "gdown"])
            import gdown

        # Google Drive file ID
        file_id = "1bCDJnaBdJKDzIhe2jadPGYm0B7XRuFtC"
        output_path = model_path
        gdown.download(id=file_id, output=output_path, quiet=False)

        print("Model downloaded successfully!")

    # Load DeBERTa model structure
    model = DebertaV2ForSequenceClassification.from_pretrained(
        "microsoft/deberta-v3-base",
        num_labels=2
    )

    # Load custom trained weights
    state_dict = torch.load(model_path, map_location=torch.device('cpu'))
    model.load_state_dict(state_dict, strict=False)

    model.eval()
    return model

def preprocess(text):
    """
    Tokenizes input text using DeBERTa tokenizer.
    """
    inputs = tokenizer(
        text,
        truncation=True,
        padding="max_length",
        max_length=128,
        return_tensors="pt"
    )
    return inputs

def contextual_pii_predict(model, text):
    """
    Predicts contextual PII presence (0 or 1) for the WHOLE text (no splitting).
    """
    results = []

    # Preprocess the whole input text
    inputs = preprocess(text)
    input_ids = inputs['input_ids']
    attention_mask = inputs['attention_mask']

    with torch.no_grad():
        outputs = model(input_ids=input_ids, attention_mask=attention_mask)
        logits = outputs.logits
        prediction = torch.argmax(logits, dim=1).item()

    results.append({
        "index": 0,
        "content": text.strip(),
        "contextual_pii": prediction
    })

    return results

def classical_pii_detect(text):
    detected_pii = []

    if re.search(r'\S+@\S+', text):
        detected_pii.append("EMAIL")
    if re.search(r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b', text) or re.search(r'\(\d{3}\)\s?\d{3}-\d{4}', text):
        detected_pii.append("PHONE_NUMBER")

    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            detected_pii.append("NAME")
        elif ent.label_ in ["GPE", "LOC"]:
            detected_pii.append("LOCATION")
        elif ent.label_ == "DATE":
            detected_pii.append("DATE")
        elif ent.label_ == "ORG":
            detected_pii.append("ORGANIZATION")

    return list(set(detected_pii))

def detect_pii(contextual_model, text):
    """
    Combines contextual model prediction and classical detection.
    """
    contextual_results = contextual_pii_predict(contextual_model, text)
    classical_results = classical_pii_detect(text)

    for item in contextual_results:
        item["other_fields"] = classical_results

    return contextual_results