import streamlit as st
import ollama
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader
import tempfile
import os

# Memaksa Ollama menggunakan CPU agar tidak bentrok dengan CUDA
os.environ["OLLAMA_NUM_GPU"] = "0" 

st.set_page_config(page_title="SAB Tour & Travel AI", layout="wide")
st.title("🚐 SAB Tour & Travel - AI Assistant")
st.markdown("---")

with st.sidebar:
    st.header("Konfigurasi Data")
    uploaded_file = st.file_uploader("Upload Katalog (TXT/PDF)", type=["txt", "pdf"])
    
    if st.button("Hapus Database"):
        if os.path.exists("./chroma_db"):
            import shutil
            shutil.rmtree("./chroma_db")
            if "vector_db" in st.session_state:
                del st.session_state.vector_db
            st.warning("Database dihapus. Silakan upload ulang.")

def proses_dokumen(file):
    with st.spinner("Sedang membaca dan mengonversi dokumen..."):
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.name)[1]) as tmp:
            tmp.write(file.getvalue())
            tmp_path = tmp.name

        if file.name.endswith(".pdf"):
            loader = PyPDFLoader(tmp_path)
            docs = loader.load()
        else:
            loader = TextLoader(tmp_path, encoding="utf-8")
            docs = loader.load()
            
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=700, chunk_overlap=100)
        chunks = text_splitter.split_documents(docs)
        
        # --- PERBAIKAN ARSITEKTUR 1: Multilingual Embedding ---
        embeddings = HuggingFaceEmbeddings(model_name="paraphrase-multilingual-MiniLM-L12-v2")
        
        vector_db = Chroma.from_documents(
            documents=chunks, 
            embedding=embeddings, 
            persist_directory="./chroma_db"
        )
        
        os.remove(tmp_path)
        return vector_db

if uploaded_file is not None:
    if "vector_db" not in st.session_state:
        st.session_state.vector_db = proses_dokumen(uploaded_file)
        st.success("✅ Katalog Berhasil Dimuat dengan Multilingual Embedding!")
    
    db = st.session_state.vector_db

    # --- MEMORI CHAT (Week 4) ---
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Render ulang riwayat pesan setiap kali ada interaksi
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_query = st.chat_input("Tanyakan paket atau harga armada...")

    if user_query:
        # Simpan pesan user ke memori
        st.session_state.messages.append({"role": "user", "content": user_query})
        
        with st.chat_message("user"):
            st.markdown(user_query)

        # 1. Tarik data relevan HANYA menggunakan query terbaru (k=4)
        results = db.similarity_search(user_query, k=4)
        konteks = "\n".join([res.page_content for res in results])

        # 2. FITUR DEBUG: Kacamata X-Ray untuk melihat otak RAG
        with st.expander("🔍 Intip Konteks yang Ditarik dari Database (Hanya untuk Developer)"):
            st.text(konteks)

        with st.chat_message("assistant"):
            with st.spinner("Menganalisis katalog..."):
                # 3. System Prompt dengan aturan baru (termasuk output terstruktur)
                system_prompt = f"""Sebagai Customer Service SAB Tour & Travel, jawab HANYA berdasarkan KATALOG.

                KATALOG:
                {konteks}

                ATURAN MUTLAK:
                1. Jika rute/tujuan TIDAK ADA di teks KATALOG, Anda WAJIB langsung menjawab: "Mohon maaf, rute tersebut belum tersedia. Layanan kami saat ini hanya untuk Malang, Batu, Bromo, dan Bali." (TIDAK BOLEH MENAMBAHKAN KALIMAT LAIN).
                2. Jika kota ADA di KATALOG, sebutkan harga dan fasilitasnya. Kalikan harga jika jumlah orang/hari bertambah.
                3. JANGAN PERNAH menawarkan paket kota lain jika kota yang diminta tidak ada.
                4. Tampilkan rincian harga dan fasilitas dalam bentuk daftar poin (bullet points) atau tabel Markdown agar rapi dan mudah dibaca.
                """
                
                # Susun pesan untuk AI (System Prompt + Riwayat Percakapan)
                messages_for_ai = [{"role": "system", "content": system_prompt}]
                for msg in st.session_state.messages:
                    messages_for_ai.append({"role": msg["role"], "content": msg["content"]})
                
                # Gunakan ollama.chat bukan generate agar AI membaca seluruh riwayat
                response = ollama.chat(
                    model="qwen2.5:3b", 
                    messages=messages_for_ai,
                    options={
                        "temperature": 0.0,
                        "num_gpu": 0
                    }
                )
                
                ai_response = response['message']['content']
                st.markdown(ai_response)
                
                # Simpan jawaban AI ke memori
                st.session_state.messages.append({"role": "assistant", "content": ai_response})
else:
    st.info("👋 Silakan upload file `katalog_sab.txt` atau `data.pdf` di sidebar untuk mulai.")