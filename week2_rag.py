import requests
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
import os


def baca_dokumen(file_path):
    print(f"--- 1. Membaca file: {file_path} ---")
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text


def buat_vector_db(teks):
    print("--- 2. Memotong teks (Chunking)... ---")
    
    # Memotong teks menjadi potongan 1000 huruf, dengan irisan 200 huruf agar konteks tidak hilang
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_text(teks)
    print(f"   -> Teks berhasil dipotong menjadi {len(chunks)} bagian.")

    print("--- 3. Mengubah teks jadi angka (Embedding) & Menyimpan ke ChromaDB... ---")
    
  
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    33

    vectorstore = Chroma.from_texts(
        texts=chunks, 
        embedding=embeddings,
        persist_directory="./db_dokumen"
    )
    return vectorstore
# 3. Tanya AI menggunakan Request (Anti CUDA Error)
def tanya_ai(konteks, pertanyaan):
    url = "http://localhost:11434/api/generate"
    
    # Instruksi ketat agar AI hanya menjawab berdasarkan dokumen
    prompt_lengkap = f"""
    Anda adalah sistem pengekstraksi fakta yang sangat ketat. 
    BACA data berikut ini dengan teliti. 
    TUGAS ANDA: Jawab pertanyaan HANYA menggunakan kalimat yang ada di dalam DATA. 
    JANGAN mengarang, JANGAN menulis kode, JANGAN menambahkan informasi dari luar. 
    Jika jawabannya tidak tertulis secara eksplisit di dalam DATA, jawab persis dengan kalimat: "SAYA TIDAK TAHU."

    ---
    DATA: {konteks}
    ---
    PERTANYAAN: {pertanyaan}
    """    
    data = {
        "model": "phi3",
        "prompt": prompt_lengkap,
        "stream": False,
        "options": {"num_gpu": 0} # Wajib 0 untuk CPU
    }

    print("--- 5. AI sedang menyusun jawaban... ---")
    response = requests.post(url, json=data)
    return response.json().get('response')

# ==========================================
# EKSEKUSI UTAMA
# ==========================================

# A. Masukkan data ke Database
teks_pdf = baca_dokumen("Readfile.pdf")
db = buat_vector_db(teks_pdf)

# B. Sesi Tanya Jawab
pertanyaan_user = "Menurut dokumen ini, apa fungsi dari perintah grep dan head pada Linux?"
print(f"\n--- 4. Mencari jawaban untuk: '{pertanyaan_user}' ---")

# Cari 3 potongan teks yang paling relevan dengan pertanyaan dari dalam ChromaDB
hasil_pencarian = db.similarity_search(pertanyaan_user, k=3)

# Gabungkan 3 teks tersebut untuk dikirim ke Phi-3
konteks_ditemukan = "\n".join([doc.page_content for doc in hasil_pencarian])

# Dapatkan Jawaban AI
jawaban = tanya_ai(konteks_ditemukan, pertanyaan_user)

print("\n✅ Jawaban AI:")
print(jawaban)