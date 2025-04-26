import torch
import re
import spacy

# Load SpaCy English model once
nlp = spacy.load("en_core_web_sm")

# Load Contextual Model
def load_contextual_model():
    model = torch.load("backend/model/contextual_pii_model.pth", map_location=torch.device('cpu'))
    model.eval()
    return model

# Preprocessing for model input (simulate for now)
def preprocess(text):
    # Real implementation should tokenize properly
    tensor = torch.rand(1, 768)  # Fake tensor example
    return tensor

# Contextual PII prediction
def contextual_pii_predict(model, text):
    sentences = text.split(".")
    results = []
    
    for idx, sentence in enumerate(sentences):
        sentence = sentence.strip()
        if not sentence:
            continue
        
        input_tensor = preprocess(sentence)
        
        with torch.no_grad():
            output = model(input_tensor)
            prediction = torch.argmax(output, dim=1).item()  # 0 or 1

        results.append({
            "index": idx,
            "content": sentence,
            "contextual_pii": prediction
        })

    return results

# Classical (Traditional) PII detection
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

    return list(set(detected_pii))  # Remove duplicates

# Final detection flow
def detect_pii(contextual_model, text):
    contextual_results = contextual_pii_predict(contextual_model, text)
    classical_results = classical_pii_detect(text)

    for item in contextual_results:
        item["other_fields"] = classical_results if item["contextual_pii"] == 1 else []

    return contextual_results