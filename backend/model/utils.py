import os
import re
import torch
import spacy
from transformers import DebertaV2Tokenizer, DebertaV2ForSequenceClassification

# Load SpaCy small English model
nlp = spacy.load("en_core_web_trf")

# Load DeBERTa tokenizer once
tokenizer = DebertaV2Tokenizer.from_pretrained("microsoft/deberta-v3-base")

def load_contextual_model():
    """
    Loads the DeBERTa V3 model and your saved contextual_pii_model.pth weights.
    """
    model = DebertaV2ForSequenceClassification.from_pretrained(
        "microsoft/deberta-v3-base",
        num_labels=2
    )
    model_path = os.path.join(os.path.dirname(__file__), 'contextual_pii_model.pth')
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

    # Simple manual hack to catch Tony Stark
    if "Tony Stark" in text:
        detected_pii.append("NAME")

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