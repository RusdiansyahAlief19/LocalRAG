import requests
import json
from pypdf import PdfReader

# 1. Fungsi untuk mengekstrak teks dari PDF
def baca_dokumen(file_path):
    print(f"--- Membaca file: {file_path} ---")
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

# 2. Fungsi kirim ke AI dengan Konteks
def tanya_ai_dengan_konteks(konteks, pertanyaan):
    url = "http://localhost:11434/api/generate"
    
    # Kita gabungkan teks dari PDF (konteks) dengan pertanyaanmu
    prompt_lengkap = f"""
    Gunakan data berikut untuk menjawab pertanyaan:
    ---
    DATA: {konteks}
    ---
    PERTANYAAN: {pertanyaan}
    """
    
    data = {
        "model": "phi3",
        "prompt": prompt_lengkap,
        "stream": False,
        "options": {"num_gpu": 0}
    }

    print("--- AI sedang membaca data dan berpikir... ---")
    response = requests.post(url, json=data)
    return response.json().get('response')

# --- EKSEKUSI ---
teks_pdf = baca_dokumen("data.pdf")
jawaban = tanya_ai_dengan_konteks(teks_pdf, "Tolong buatkan ringkasan 3 poin dari dokumen ini.")

print("\nJawaban dari Dokumenmu:")
print(jawaban)