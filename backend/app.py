from flask import Flask, request, jsonify
from google.cloud import vision
import os
import spacy
import re
from flask_cors import CORS

# After creating the Flask app, enable CORS
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize Google Vision Client
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\Users\Daniel\Desktop\Handwritten Text\backend\handwritten-medical-entites-89babde8ba7b.json"
client = vision.ImageAnnotatorClient()

nlp = spacy.load("en_ner_bc5cdr_md")

# Load the disease dataset from a text file
def load_disease_dataset(file_path="diseases.txt"):
    with open(file_path, "r") as f:
        return set(line.strip().lower() for line in f.readlines())

disease_set = load_disease_dataset("diseases.txt")

# Function to extract the name from the extracted text
def extract_name(text):
    # Updated regex pattern to capture only the name part before "Age"
    match = re.search(r"Name:\s*([A-Za-z\s]+)(?=\s+Age)", text)
    if match:
        return match.group(1).strip()
    return None

@app.route("/upload", methods=["POST"])
def process_image():
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    image = request.files["image"]
    print(f"Received image: {image.filename}")
    content = image.read()
    image = vision.Image(content=content)

    # Extract text using Google Vision
    response = client.text_detection(image=image)
    texts = response.text_annotations

    if not texts:
        print("No text detected")
        return jsonify({"error": "No text detected"}), 400

    extracted_text = texts[0].description
    cleaned_text = " ".join(extracted_text.split())
    print(f"Extracted text: {cleaned_text}")

    # Extract the patient's name from the extracted text
    name = extract_name(cleaned_text)
    print(f"Extracted name: {name}")
    
    if not name:
        return jsonify({"error": "Name not found in the text."}), 400

    # Process the extracted text with the NER model
    doc = nlp(cleaned_text)  # Pass cleaned_text for processing
    entities = []

    for ent in doc.ents:
        # Rename CHEMICAL label to MEDICATION
        if ent.label_ == "CHEMICAL":
            ent.label_ = "MEDICATION"
        
        # Check if the entity is labeled as DISEASE
        if ent.label_ == "DISEASE":
            entity_text = ent.text.strip().lower()  # Normalize to lower case for comparison
            # If it's found in the disease dataset, keep the label as DISEASE
            if entity_text in disease_set:
                label = "DISEASE"
            else:
                # If not found in the dataset, mark it as SYMPTOM
                label = "SYMPTOM"
        else:
            # Keep the original label for other entities (like MEDICATION)
            label = ent.label_

        # Add the entity to the list
        entities.append({"text": ent.text, "label": label})

    # Return the output as JSON
    return jsonify({
        "name": name,  # Include the extracted name in the response
        "extracted_text": cleaned_text,
        "entities": entities
    })

if __name__ == "__main__":
    app.run(port=5000, debug=True)