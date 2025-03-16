import requests
import os
import csv
import zipfile
import json
from fpdf import FPDF
from docx import Document
from flask import Flask, request, jsonify, send_file

app = Flask(__name__)

# Remplace par ta clé API d'Anthropic
API_KEY = "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"

# URL de l'API Claude AI
API_URL = "https://api.anthropic.com/v1/complete"

# Headers pour la requête API
HEADERS = {
    "x-api-key": API_KEY,
    "Content-Type": "application/json",
    "anthropic-version": "2023-06-01"
}

# Dossier pour stocker les fichiers générés
UPLOAD_FOLDER = "generated_files"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Fonction pour interroger Claude AI
def interroger_claude(prompt, max_tokens=500):
    data = {
        "model": "claude-2",
        "prompt": f"\n\nHuman: {prompt}\n\nAssistant:",
        "max_tokens_to_sample": max_tokens,
        "temperature": 0.7
    }
    
    response = requests.post(API_URL, headers=HEADERS, json=data)
    
    if response.status_code == 200:
        return response.json().get("completion", "Pas de réponse reçue.")
    else:
        return f"Erreur : {response.status_code} - {response.text}"

# Fonction pour enregistrer en fichier TXT
def save_as_txt(text, filename):
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(text)
    return file_path

# Fonction pour enregistrer en fichier PDF
def save_as_pdf(text, filename):
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(190, 10, text)
    pdf.output(file_path)
    return file_path

# Fonction pour enregistrer en fichier DOCX (Word)
def save_as_docx(text, filename):
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    doc = Document()
    doc.add_paragraph(text)
    doc.save(file_path)
    return file_path

# Fonction pour enregistrer en fichier CSV
def save_as_csv(text, filename):
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    with open(file_path, mode='w', newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Réponse de Claude AI"])
        writer.writerow([text])
    return file_path

# Fonction pour enregistrer en fichier JSON
def save_as_json(text, filename):
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump({"response": text}, f, ensure_ascii=False, indent=4)
    return file_path

# Fonction pour enregistrer en fichier JavaScript (.js)
def save_as_js(text, filename):
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(f"// Réponse de Claude AI\nconst response = `{text}`;\nconsole.log(response);")
    return file_path

# Fonction pour enregistrer en fichier Java (.java)
def save_as_java(text, filename):
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(f"// Réponse de Claude AI\npublic class Response {{\n    public static void main(String[] args) {{\n        System.out.println(\"{text}\");\n    }}\n}}")
    return file_path

# Fonction pour créer un fichier ZIP contenant plusieurs fichiers
def create_zip(files, zip_filename):
    zip_path = os.path.join(UPLOAD_FOLDER, zip_filename)
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for file in files:
            zipf.write(file, os.path.basename(file))
    return zip_path

# Endpoint Flask pour générer un ZIP contenant plusieurs fichiers
@app.route('/ask_claude_zip', methods=['POST'])
def ask_claude_zip():
    data = request.json
    question = data.get("question", "")

    if not question:
        return jsonify({"error": "Aucune question fournie"}), 400

    response = interroger_claude(question)

    # Générer plusieurs formats de fichiers
    files = []
    files.append(save_as_txt(response, "response.txt"))
    files.append(save_as_pdf(response, "response.pdf"))
    files.append(save_as_docx(response, "response.docx"))
    files.append(save_as_csv(response, "response.csv"))
    files.append(save_as_json(response, "response.json"))
    files.append(save_as_js(response, "response.js"))
    files.append(save_as_java(response, "response.java"))

    # Créer un ZIP avec tous les fichiers générés
    zip_filename = "responses.zip"
    zip_path = create_zip(files, zip_filename)

    return jsonify({"message": "Fichier ZIP généré", "download_url": f"/download?filename={zip_filename}"})

# Endpoint pour télécharger un fichier (y compris ZIP)
@app.route('/download', methods=['GET'])
def download_file():
    filename = request.args.get("filename")
    if not filename:
        return jsonify({"error": "Aucun fichier spécifié"}), 400

    file_path = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return jsonify({"error": "Fichier non trouvé"}), 404

# Lancer le serveur Flask
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
