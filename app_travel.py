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
    user_query = st.chat_input("Tanyakan paket atau harga armada...")

    if user_query:
        with st.chat_message("user"):
            st.markdown(user_query)

        # 1. Kita perbanyak tarikan datanya (k=4) agar tidak ada yang terlewat
        results = db.similarity_search(user_query, k=4)
        konteks = "\n".join([res.page_content for res in results])

        # 2. FITUR DEBUG: Kacamata X-Ray untuk melihat otak RAG
        with st.expander("🔍 Intip Konteks yang Ditarik dari Database (Hanya untuk Developer)"):
            st.text(konteks)

        with st.chat_message("assistant"):
            with st.spinner("Menganalisis katalog..."):
                # 3. Prompt yang lebih luwes tapi tetap aman
                prompt = f"""
                Anda adalah Agen Customer Service SAB Tour & Travel yang ramah, cerdas, dan pintar berjualan.
                Tugas Anda adalah melayani pelanggan berdasarkan Data Katalog berikut.
                
                Data Katalog:
                {konteks}
                
                Pertanyaan Pelanggan: {user_query}
                
                ATURAN KERJA:
                1. JAWAB UTAMA: Jawab pertanyaan inti pelanggan secara lengkap dan ramah sesuai Data Katalog.
                2. KALKULASI CERDAS: Jika pelanggan meminta durasi/jumlah yang lebih besar dari standar di katalog (misal: sewa 2 hari padahal di katalog harga 1 hari), Anda WAJIB menghitung total estimasinya (Kalikan harga dasar dengan jumlah hari). Tambahkan kalimat "Ini adalah estimasi biaya...".
                3. REKOMENDASI (CROSS-SELLING): Di akhir jawaban, selalu tawarkan atau sebutkan 1 paket wisata/armada lain yang ada di dalam Data Katalog untuk memancing minat pelanggan.
                4. Jika informasi destinasi TIDAK ADA di Data Katalog, tolak dengan sopan dan tawarkan destinasi yang TERSEDIA di katalog.
                5. JANGAN PERNAH mengarang harga dasar yang tidak ada di katalog.
                """
                
                response = ollama.generate(
                    model="qwen2.5:3b", 
                    prompt=prompt,
                    options={
                        "temperature": 0.0,
                        "num_gpu": 0
                    }
                )
                st.markdown(response['response'])
else:
    st.info("👋 Silakan upload file `katalog_sab.txt` di sidebar untuk mulai.")