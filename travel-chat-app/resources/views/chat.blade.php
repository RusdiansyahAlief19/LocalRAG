<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Travel Agent</title>
    <!-- Tailwind CSS -->
    @vite('resources/css/app.css')
    
    <!-- Alpine.js & Intersect Plugin -->
    <script defer src="https://cdn.jsdelivr.net/npm/@alpinejs/intersect@3.x.x/dist/cdn.min.js"></script>
    <script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>

    <!-- Font -->
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Inter', sans-serif; }
        .scrollbar-hide::-webkit-scrollbar { display: none; }
        .scrollbar-hide { -ms-overflow-style: none; scrollbar-width: none; }
    </style>
</head>
<body class="bg-gray-900 text-gray-100 flex h-screen overflow-hidden" x-data="chatApp()">

    <!-- Sidebar -->
    <aside class="w-64 bg-gray-950 flex flex-col transition-all duration-300" :class="sidebarOpen ? 'translate-x-0' : '-translate-x-full fixed'">
        <div class="p-4 flex items-center justify-between border-b border-gray-800">
            <h1 class="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-teal-400 to-blue-500">Travel AI</h1>
            <button @click="sidebarOpen = false" class="text-gray-400 hover:text-white md:hidden">
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
            </button>
        </div>
        
        <div class="p-4">
            <button class="w-full flex items-center justify-center gap-2 py-2.5 px-4 bg-gray-800 hover:bg-gray-700 text-sm font-medium rounded-lg transition-colors border border-gray-700">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path></svg>
                New Chat
            </button>
        </div>

        <div class="flex-1 overflow-y-auto scrollbar-hide px-3 py-2 space-y-2">
            <h3 class="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3 px-2">Katalog & Workspace</h3>
            
            <!-- Dokumen Upload Area -->
            <div class="bg-gray-800/50 rounded-lg p-3 border border-gray-700/50">
                <p class="text-xs text-gray-400 mb-2">Upload PDF Katalog Trip</p>
                <form @submit.prevent="uploadDocument" class="flex flex-col gap-2">
                    <input type="file" id="pdfUpload" accept=".pdf,.txt" class="text-xs text-gray-300 file:mr-2 file:py-1 file:px-2 file:rounded-md file:border-0 file:text-xs file:font-semibold file:bg-teal-500/20 file:text-teal-400 hover:file:bg-teal-500/30 cursor-pointer">
                    <button type="submit" class="w-full bg-teal-600 hover:bg-teal-500 text-white text-xs py-1.5 rounded-md transition-colors font-medium flex items-center justify-center gap-1" :disabled="uploading">
                        <span x-show="!uploading">Proses Katalog</span>
                        <span x-show="uploading">Loading...</span>
                    </button>
                </form>
            </div>
            
            <!-- Simulasi Lazy Loading History Chat -->
            <div class="mt-6">
                <h3 class="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3 px-2">History</h3>
                <div class="space-y-1">
                    <button class="w-full text-left px-3 py-2 text-sm text-gray-300 hover:bg-gray-800 rounded-md truncate">Paket Bromo 3 Orang</button>
                    <button class="w-full text-left px-3 py-2 text-sm text-gray-300 hover:bg-gray-800 rounded-md truncate">Info Trip Jogja</button>
                </div>
            </div>
        </div>
    </aside>

    <!-- Main Chat Area -->
    <main class="flex-1 flex flex-col bg-gray-900 relative">
        <!-- Mobile Header -->
        <header class="md:hidden flex items-center p-4 border-b border-gray-800">
            <button @click="sidebarOpen = true" class="text-gray-400 hover:text-white mr-3">
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path></svg>
            </button>
            <h1 class="text-lg font-bold">Travel AI</h1>
        </header>

        <!-- Chat Container -->
        <div id="chat-container" class="flex-1 overflow-y-auto px-4 py-6 sm:px-6 lg:px-8 space-y-6 scrollbar-hide">
            
            <!-- Pesan Pembuka -->
            <div class="flex items-start gap-4">
                <div class="w-8 h-8 rounded-full bg-teal-600 flex items-center justify-center flex-shrink-0 shadow-lg">
                    <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path></svg>
                </div>
                <div class="bg-gray-800 px-5 py-3.5 rounded-2xl rounded-tl-sm max-w-[85%] sm:max-w-[75%] border border-gray-700/50 shadow-md">
                    <p class="text-sm sm:text-base leading-relaxed">Halo! Saya adalah Travel AI Agent Anda. Silakan *upload* katalog paket wisata Anda (PDF) di menu samping, lalu tanyakan harganya di sini!</p>
                </div>
            </div>

            <!-- Pesan Dinamis di-render oleh Alpine -->
            <template x-for="(message, index) in messages" :key="index">
                <div class="flex items-start gap-4" :class="message.role === 'user' ? 'flex-row-reverse' : ''" 
                     x-intersect.once="$el.classList.add('animate-fade-in-up')">
                    
                    <!-- Avatar -->
                    <div class="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 shadow-lg"
                         :class="message.role === 'user' ? 'bg-blue-600' : 'bg-teal-600'">
                        <template x-if="message.role === 'user'">
                            <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path></svg>
                        </template>
                        <template x-if="message.role === 'assistant'">
                            <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path></svg>
                        </template>
                    </div>

                    <!-- Chat Bubble -->
                    <div class="px-5 py-3.5 rounded-2xl max-w-[85%] sm:max-w-[75%] shadow-md whitespace-pre-wrap"
                         :class="message.role === 'user' ? 'bg-blue-600 text-white rounded-tr-sm' : 'bg-gray-800 border border-gray-700/50 rounded-tl-sm'">
                        <p class="text-sm sm:text-base leading-relaxed" x-text="message.content"></p>
                    </div>
                </div>
            </template>
            
            <!-- Loading Indicator -->
            <div x-show="isTyping" class="flex items-start gap-4">
                <div class="w-8 h-8 rounded-full bg-teal-600 flex items-center justify-center flex-shrink-0">
                    <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path></svg>
                </div>
                <div class="bg-gray-800 px-5 py-3.5 rounded-2xl rounded-tl-sm border border-gray-700/50 flex items-center gap-2">
                    <div class="w-2 h-2 bg-gray-500 rounded-full animate-bounce"></div>
                    <div class="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
                    <div class="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style="animation-delay: 0.4s"></div>
                </div>
            </div>

            <!-- Anchor untuk scroll bawah otomatis -->
            <div id="scroll-anchor"></div>
        </div>

        <!-- Input Area -->
        <div class="p-4 sm:p-6 bg-gradient-to-t from-gray-900 via-gray-900 to-transparent">
            <form @submit.prevent="sendMessage" class="max-w-4xl mx-auto relative flex items-center">
                <input x-model="userInput" type="text" placeholder="Tanyakan harga untuk paket Bromo 4 orang..." 
                       class="w-full bg-gray-800 border border-gray-700 text-gray-100 rounded-xl px-5 py-4 pr-14 focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent transition-all shadow-lg"
                       :disabled="isTyping">
                <button type="submit" 
                        class="absolute right-3 p-2 bg-teal-600 hover:bg-teal-500 rounded-lg text-white transition-colors disabled:opacity-50"
                        :disabled="!userInput.trim() || isTyping">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"></path></svg>
                </button>
            </form>
            <p class="text-center text-xs text-gray-500 mt-3">Travel AI Agent dapat membuat kesalahan. Harap verifikasi info penting.</p>
        </div>
    </main>

    <style>
        .animate-fade-in-up {
            animation: fadeInUp 0.4s cubic-bezier(0.16, 1, 0.3, 1) forwards;
            opacity: 0;
            transform: translateY(10px);
        }
        @keyframes fadeInUp {
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
    </style>

    <script>
        function chatApp() {
            return {
                sidebarOpen: window.innerWidth > 768,
                userInput: '',
                isTyping: false,
                uploading: false,
                messages: [],

                init() {
                    window.addEventListener('resize', () => {
                        this.sidebarOpen = window.innerWidth > 768;
                    });
                },

                scrollToBottom() {
                    setTimeout(() => {
                        const container = document.getElementById('chat-container');
                        container.scrollTop = container.scrollHeight;
                    }, 50);
                },

                async sendMessage() {
                    if (!this.userInput.trim()) return;

                    const query = this.userInput;
                    this.messages.push({ role: 'user', content: query });
                    this.userInput = '';
                    this.isTyping = true;
                    this.scrollToBottom();

                    try {
                        const csrfToken = '{{ csrf_token() }}'; // Laravel CSRF
                        const res = await fetch('/chat', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                                'X-CSRF-TOKEN': csrfToken
                            },
                            body: JSON.stringify({ query: query })
                        });

                        const data = await res.json();
                        
                        if (!res.ok) throw new Error(data.error || 'Terjadi kesalahan');

                        this.messages.push({ role: 'assistant', content: data.answer });
                    } catch (error) {
                        this.messages.push({ role: 'assistant', content: "Maaf, mesin RAG sedang sibuk atau offline. " + error.message });
                    } finally {
                        this.isTyping = false;
                        this.scrollToBottom();
                    }
                },

                async uploadDocument(e) {
                    const fileInput = document.getElementById('pdfUpload');
                    if (!fileInput.files.length) return alert('Pilih file PDF/TXT dulu!');

                    this.uploading = true;
                    
                    const formData = new FormData();
                    formData.append('document', fileInput.files[0]);

                    try {
                        const csrfToken = '{{ csrf_token() }}';
                        const res = await fetch('/upload', {
                            method: 'POST',
                            headers: {
                                'X-CSRF-TOKEN': csrfToken
                            },
                            body: formData
                        });

                        const data = await res.json();
                        if (!res.ok) throw new Error(data.error || 'Terjadi kesalahan saat upload');
                        
                        alert('Sukses: Dokumen telah di-inject ke memori AI!');
                        fileInput.value = '';
                    } catch (error) {
                        alert('Error: ' + error.message);
                    } finally {
                        this.uploading = false;
                    }
                }
            }
        }
    </script>
</body>
</html>
