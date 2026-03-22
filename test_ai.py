import requests
import json

def tanya_ai(prompt):
    url = "http://localhost:11434/api/generate"
    data = {
        "model": "phi3",
        "prompt": prompt,
        "stream": False,
        "options": {
            "num_gpu": 0  # INI KUNCINYA: Memaksa Ollama pakai CPU (0 GPU)
        }
    }

    print("--- Mengirim pesan ke AI (Mode CPU)... ---")
    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            jawaban = response.json().get('response')
            print("\nJawaban AI:")
            print(jawaban)
        else:
            print(f"Gagal konek. Kode status: {response.status_code}")
    except Exception as e:
        print(f"Terjadi kesalahan: {e}")

# Jalankan tes
tanya_ai("Halo Phi-3! Ini Rusdiansyah. Katakan 'Sistem Berhasil' jika kamu dengar saya.")