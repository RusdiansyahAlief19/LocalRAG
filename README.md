# 🏝️ Local RAG Travel AI Agent

Aplikasi **Travel AI Agent** berbasis **Local RAG (Retrieval-Augmented Generation)** yang dirancang untuk menjadi asisten cerdas (Customer Service) untuk agen perjalanan wisata (seperti SAB Tour & Travel). AI ini mampu membaca katalog PDF/TXT Anda dan menjawab pertanyaan pelanggan secara spesifik mengenai harga, paket wisata, rute, dan ketersediaan armada.

Seluruh data dan model diproses secara **Lokal** menggunakan Docker, memastikan privasi data perusahaan tetap aman 100% tanpa bergantung pada API eksternal yang berbayar.

---

## 🏗️ Arsitektur Sistem (Tech Stack)

Sistem ini dibagi menjadi dua layer utama yang berjalan harmoni menggunakan **Docker Compose**:

1. **Frontend & Core System (PHP/Laravel)**
   - **Framework:** Laravel 11 (via Laravel Sail)
   - **UI/UX:** Tailwind CSS & Alpine.js (Antarmuka SPA yang *clean* dengan efek *lazy loading* / *fade-in* ala ChatGPT).
   - **Fungsi:** Menyediakan antarmuka chat, mengatur sesi pengguna, dan meneruskan dokumen (PDF/TXT) ke RAG Service.

2. **RAG & LLM Engine (Golang)**
   - **Service:** Golang RAG Service (`langchaingo`)
   - **Vector Database:** ChromaDB (`chromadb/chroma:0.4.24`)
   - **Local LLM:** Ollama (`qwen2.5:3b` digunakan untuk *Text Embedding* dan *Text Generation*).
   - **Fungsi:** Memecah dokumen PDF/TXT menjadi *chunks*, menyimpannya ke *vector database*, dan mengekstrak jawaban akurat berdasarkan *cosine similarity search* dari *prompt* pengguna.

---

## 🚀 Fitur Utama

- **Offline & Private:** Semua pemrosesan data, embedding, dan inferensi LLM dilakukan di server lokal menggunakan Ollama.
- **Dynamic Knowledge Base:** Anda bisa mengunggah file Katalog Tour & Travel (`.txt` atau `.pdf`) kapan saja dari antarmuka Web. AI akan langsung memperbarui ingatannya.
- **Precision Pricing:** *System Prompt* didesain khusus agar AI tidak berhalusinasi. Jika ditanya harga untuk banyak orang, AI akan otomatis mengkalkulasi totalnya (contoh: *Rp 350.000 x 4 = Rp 1.400.000*).
- **SPA Chat Interface:** Menggunakan Alpine.js untuk memanipulasi DOM sehingga pengalaman berbalas pesan terasa sangat mulus tanpa *page refresh*.

---

## ⚙️ Cara Instalasi & Menjalankan (Local Development)

### Prasyarat
- **Docker & Docker Compose** (Wajib)
- **Ollama** (Wajib terinstal di *host machine* dan memiliki model `qwen2.5:3b` yang sudah di-pull)
  ```bash
  ollama run qwen2.5:3b
  ```

### Langkah-langkah Menjalankan Sistem

1. **Clone repositori ini:**
   ```bash
   git clone https://github.com/RusdiansyahAlief19/LocalRAG.git
   cd LocalRAG
   ```

2. **Masuk ke direktori Laravel dan jalankan Docker:**
   ```bash
   cd travel-chat-app
   docker compose up -d --build
   ```
   *Perintah ini akan menjalankan container untuk: Laravel Sail, MySQL, ChromaDB, dan Golang RAG Service.*

3. **Jalankan Vite Server (untuk Tailwind/Frontend):**
   Buka terminal baru di folder `travel-chat-app`, lalu jalankan:
   ```bash
   npm install
   npm run dev
   ```

4. **Akses Aplikasi:**
   Buka browser Anda dan kunjungi:
   👉 **http://localhost**

---

## 🧪 Cara Penggunaan (Testing)

1. Buka aplikasi di `http://localhost`.
2. Di sidebar sebelah kiri, klik **"Choose File"**.
3. Pilih file dataset contoh yang sudah disediakan di folder `dataset/` (misal: `katalog_sab_dataset.txt`).
4. Klik **"Proses Katalog"**. (Sistem akan memecah file Anda dan menginjeksikannya ke dalam ChromaDB).
5. Setelah muncul notifikasi sukses, cobalah mengobrol dengan AI:
   - *"Berapa harga paket Bromo untuk 3 orang?"*
   - *"Saya mau sewa Hiace Premio, harganya berapa dan kapasitasnya?"*
   - *"Ada paket ke Bali nggak?"*

---

## 📁 Struktur Direktori Utama

```text
LocalRAG/
├── dataset/                    # Kumpulan data PDF/TXT untuk testing
├── rag-service/                # (Golang) Mesin RAG dan konektor ChromaDB
│   ├── main.go                 # Kode utama RAG Engine
│   ├── go.mod                  # Dependensi Golang (langchaingo, dll)
│   └── Dockerfile              # Konfigurasi container Golang
└── travel-chat-app/            # (Laravel) Aplikasi Utama & UI
    ├── app/Http/Controllers/   # Logic pengiriman chat & upload dokumen ke Golang
    ├── resources/views/        # Tampilan frontend (chat.blade.php)
    └── compose.yaml            # Docker compose menaungi Laravel, MySQL, ChromaDB, RAG
```

---

*Project by Rusdiansyah Alief. Dibuat untuk eksplorasi Local Retrieval-Augmented Generation pada kasus bisnis Travel & Tour.*
