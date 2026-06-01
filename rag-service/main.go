package main

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"strings"
	"time"

	"github.com/ledongthuc/pdf"
	"github.com/tmc/langchaingo/embeddings"
	"github.com/tmc/langchaingo/llms"
	"github.com/tmc/langchaingo/llms/ollama"
	"github.com/tmc/langchaingo/schema"
	"github.com/tmc/langchaingo/vectorstores"
	"github.com/tmc/langchaingo/vectorstores/chroma"
)

type AskRequest struct {
	Query string `json:"query"`
}

type AskResponse struct {
	Answer string `json:"answer"`
}

// Gunakan nomic-embed-text karena ringan dan support multilingual/Indonesia cukup baik, atau model default Ollama.
const ollamaModel = "qwen2.5:3b"
const ollamaEmbedModel = "qwen2.5:3b" 
const ollamaURL = "http://host.docker.internal:11434"
const chromaURL = "http://chromadb:8000"

var store vectorstores.VectorStore

func initChroma() {
	// Buat Ollama Client untuk Embedding
	llm, err := ollama.New(
		ollama.WithModel(ollamaEmbedModel),
		ollama.WithServerURL(ollamaURL),
	)
	if err != nil {
		log.Fatalf("Gagal inisialisasi Ollama Embedding: %v", err)
	}

	embedder, err := embeddings.NewEmbedder(llm)
	if err != nil {
		log.Fatalf("Gagal inisialisasi Embedder: %v", err)
	}

	// Koneksi ke ChromaDB dengan retry
	for i := 0; i < 15; i++ {
		s, err := chroma.New(
			chroma.WithChromaURL(chromaURL),
			chroma.WithEmbedder(embedder),
			chroma.WithDistanceFunction("cosine"),
			chroma.WithNameSpace("travel_catalog"),
		)
		if err == nil {
			store = s
			log.Println("Berhasil terhubung ke ChromaDB")
			return
		}
		log.Printf("Warning: Gagal koneksi ke ChromaDB, mencoba lagi dalam 5 detik... (%v)", err)
		time.Sleep(5 * time.Second)
	}
	
	log.Printf("Gagal koneksi ke ChromaDB setelah beberapa percobaan. Store akan nil.")
	store = nil
}

func askHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	var req AskRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid request", http.StatusBadRequest)
		return
	}

	ctx := context.Background()

	// 1. Cari Dokumen Relevan di ChromaDB
	var contextText string
	if store != nil {
		docs, err := store.SimilaritySearch(ctx, req.Query, 8) // Tingkatkan menjadi 8 chunk
		if err == nil && len(docs) > 0 {
			var sb strings.Builder
			for _, doc := range docs {
				sb.WriteString(doc.PageContent)
				sb.WriteString("\n---\n")
			}
			contextText = sb.String()
		} else {
			log.Printf("Similarity search error or no docs: %v", err)
		}
	}

	// 2. Siapkan Ollama LLM
	llm, err := ollama.New(
		ollama.WithModel(ollamaModel),
		ollama.WithServerURL(ollamaURL),
	)
	if err != nil {
		http.Error(w, fmt.Sprintf("Failed to initialize Ollama: %v", err), http.StatusInternalServerError)
		return
	}

	// 3. Susun Prompt dengan Konteks RAG
	prompt := fmt.Sprintf(`Anda adalah Customer Service (Travel AI Agent) yang ramah dan solutif dari SAB Tour & Travel.
Tugas Anda adalah menjawab pertanyaan pengguna BERDASARKAN informasi katalog di bawah ini.
Aturan penting:
1. Jika pengguna menanyakan harga atau destinasi (misal Bromo, Surabaya), cari paket yang relevan di katalog dan sebutkan harganya secara detail.
2. Jika ditanya harga untuk beberapa orang dan harga di katalog adalah "per orang", maka hitunglah total biayanya (misal: Rp 350.000 x 4 orang = Rp 1.400.000).
3. Jika informasi benar-benar tidak ada di katalog, katakan 'Maaf, rute/paket tersebut tidak tersedia di katalog kami.' Jangan mengarang.

Katalog:
%s

Pertanyaan pengguna: %s
Jawaban (Gunakan bahasa Indonesia yang ramah, santai, dan berikan harga yang spesifik): `, contextText, req.Query)

	completion, err := llms.GenerateFromSinglePrompt(ctx, llm, prompt, llms.WithTemperature(0.1))
	if err != nil {
		http.Error(w, fmt.Sprintf("Failed to generate response: %v", err), http.StatusInternalServerError)
		return
	}

	res := AskResponse{Answer: completion}
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(res)
}

func main() {
	// Inisialisasi ChromaDB saat server nyala
	initChroma()

	http.HandleFunc("/api/ask", askHandler)

	http.HandleFunc("/api/process-document", func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodPost {
			http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
			return
		}

		err := r.ParseMultipartForm(10 << 20) // 10 MB limit
		if err != nil {
			http.Error(w, "Error parsing form", http.StatusBadRequest)
			return
		}

		file, header, err := r.FormFile("document")
		if err != nil {
			http.Error(w, "Document not found", http.StatusBadRequest)
			return
		}
		defer file.Close()

		var textContent string

		if strings.HasSuffix(strings.ToLower(header.Filename), ".pdf") {
			// Read PDF
			fileBytes, err := io.ReadAll(file)
			if err != nil {
				http.Error(w, "Failed to read pdf", http.StatusInternalServerError)
				return
			}
			
			reader, err := pdf.NewReader(bytes.NewReader(fileBytes), int64(len(fileBytes)))
			if err != nil {
				http.Error(w, "Failed to parse pdf", http.StatusInternalServerError)
				return
			}
			
			var sb strings.Builder
			for i := 1; i <= reader.NumPage(); i++ {
				page := reader.Page(i)
				if page.V.IsNull() {
					continue
				}
				content, _ := page.GetPlainText(nil)
				sb.WriteString(content)
			}
			textContent = sb.String()
		} else {
			// Assume TXT
			fileBytes, _ := io.ReadAll(file)
			textContent = string(fileBytes)
		}

		// Split by newline and insert to ChromaDB
		chunks := strings.Split(textContent, "\n\n")
		var docs []schema.Document
		for _, chunk := range chunks {
			trimmed := strings.TrimSpace(chunk)
			if len(trimmed) > 10 {
				docs = append(docs, schema.Document{
					PageContent: trimmed,
					Metadata:    map[string]any{"source": header.Filename},
				})
			}
		}

		if store != nil && len(docs) > 0 {
			_, err := store.AddDocuments(context.Background(), docs)
			if err != nil {
				http.Error(w, "Failed to insert to ChromaDB: "+err.Error(), http.StatusInternalServerError)
				return
			}
		}

		w.Header().Set("Content-Type", "application/json")
		w.Write([]byte(`{"status": "success", "message": "Document parsed and injected to ChromaDB!"}`))
	})

	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}

	log.Printf("Golang RAG Service is running on port %s...", port)
	if err := http.ListenAndServe(":"+port, nil); err != nil {
		log.Fatalf("Server failed: %v", err)
	}
}
