from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def serve_frontend():
    return """
<!DOCTYPE html>
<html lang="en" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Neural Nexus AI</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.js"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <script>
        tailwind.config = {
            darkMode: 'class',
            theme: {
                extend: {
                    colors: {
                        dark: { 900: '#0b0f19', 800: '#111827', 700: '#1f2937', 600: '#374151' }
                    }
                }
            }
        }
    </script>
</head>
<body class="bg-dark-900 text-gray-100 font-sans h-screen flex overflow-hidden">

    <!-- Sidebar -->
    <aside class="w-72 bg-dark-800 border-r border-gray-800 flex flex-col justify-between hidden md:flex">
        <div class="p-4">
            <div class="flex items-center gap-3 mb-6 px-2">
                <div class="w-8 h-8 rounded-lg bg-gradient-to-tr from-blue-600 to-indigo-500 flex items-center justify-center shadow-lg shadow-blue-500/30">
                    <i class="fa-solid fa-brain text-white text-sm"></i>
                </div>
                <h1 class="font-bold text-lg tracking-wide bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent">Neural Nexus</h1>
            </div>
            
            <button onclick="newChat()" class="w-full bg-blue-600 hover:bg-blue-500 text-white font-medium py-2.5 px-4 rounded-xl flex items-center gap-2 transition shadow-lg shadow-blue-600/20 mb-6">
                <i class="fa-solid fa-plus text-xs"></i> New Chat
            </button>

            <div class="text-xs font-semibold text-gray-500 uppercase tracking-wider px-2 mb-2">System Metrics</div>
            <div class="space-y-2 px-2 text-sm text-gray-400">
                <div class="flex justify-between bg-dark-700/50 p-2 rounded-lg border border-gray-800">
                    <span>Tier</span>
                    <span id="badge-tier" class="text-blue-400 font-mono">Pro</span>
                </div>
                <div class="flex justify-between bg-dark-700/50 p-2 rounded-lg border border-gray-800">
                    <span>Requests Left</span>
                    <span id="badge-quota" class="text-emerald-400 font-mono">1000</span>
                </div>
                <div class="flex justify-between bg-dark-700/50 p-2 rounded-lg border border-gray-800">
                    <span>Evolution Gen</span>
                    <span id="badge-gen" class="text-purple-400 font-mono">Gen-1</span>
                </div>
            </div>
        </div>

        <div class="p-4 border-t border-gray-800 text-xs text-gray-500 flex items-center justify-between">
            <span>Engine: Llama + Qwen</span>
            <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
        </div>
    </aside>

    <!-- Main Chat Area -->
    <main class="flex-1 flex flex-col h-full bg-dark-900 relative">
        <!-- Top Navbar -->
        <header class="h-14 border-b border-gray-800 flex items-center justify-between px-6 bg-dark-900/80 backdrop-blur z-10">
            <div class="flex items-center gap-3">
                <span class="text-sm font-medium text-gray-400">Model:</span>
                <span class="text-xs bg-dark-700 text-blue-400 border border-blue-500/30 px-2.5 py-1 rounded-full font-mono">Multi-Engine Reflexion v2.0</span>
            </div>
            <div class="flex items-center gap-4 text-sm text-gray-400">
                <input type="password" id="api-key-input" placeholder="API Key (default: free_user_key)" value="pro_user_key" 
                    class="bg-dark-800 border border-gray-700 rounded-lg px-3 py-1 text-xs text-gray-200 focus:outline-none focus:border-blue-500 w-48">
            </div>
        </header>

        <!-- Chat Stream Box -->
        <div id="chat-container" class="flex-1 overflow-y-auto p-4 md:p-6 space-y-6 max-w-4xl w-full mx-auto pb-32">
            <!-- Welcome Message -->
            <div class="flex gap-4 items-start">
                <div class="w-8 h-8 rounded-full bg-gradient-to-tr from-blue-600 to-indigo-600 flex items-center justify-center shrink-0 shadow-md">
                    <i class="fa-solid fa-robot text-white text-xs"></i>
                </div>
                <div class="bg-dark-800 border border-gray-800 rounded-2xl p-4 text-gray-200 shadow-sm max-w-[85%] leading-relaxed">
                    <p class="font-semibold text-white mb-1">Neural Nexus Online</p>
                    <p class="text-sm text-gray-300">Self-evolving multi-engine backend active. Ready for analytical workflows, code generation, and multi-step reflexions.</p>
                </div>
            </div>
        </div>

        <!-- Input Bar -->
        <div class="absolute bottom-0 left-0 right-0 p-4 bg-gradient-to-t from-dark-900 via-dark-900/90 to-transparent">
            <div class="max-w-4xl mx-auto">
                <form id="chat-form" onsubmit="handleSend(event)" class="relative bg-dark-800 border border-gray-700/80 rounded-2xl shadow-2xl focus-within:border-blue-500 transition">
                    <textarea id="user-input" rows="1" placeholder="Message Neural Nexus..." 
                        class="w-full bg-transparent text-gray-100 placeholder-gray-500 text-sm px-4 py-3.5 pr-12 focus:outline-none resize-none max-h-32"
                        onkeydown="if(event.key === 'Enter' && !event.shiftKey) { event.preventDefault(); handleSend(event); }"></textarea>
                    <button type="submit" id="send-btn" class="absolute right-3 bottom-3 w-8 h-8 bg-blue-600 hover:bg-blue-500 text-white rounded-xl flex items-center justify-center transition shadow-md">
                        <i class="fa-solid fa-arrow-up text-xs"></i>
                    </button>
                </form>
                <div class="text-center text-[11px] text-gray-500 mt-2">
                    Secured with automated rate metering and local LLM execution.
                </div>
            </div>
        </div>
    </main>

    <script>
        const chatContainer = document.getElementById('chat-container');
        const userInput = document.getElementById('user-input');
        let chatHistory = [];

        function newChat() {
            chatHistory = [];
            chatContainer.innerHTML = `
                <div class="flex gap-4 items-start">
                    <div class="w-8 h-8 rounded-full bg-gradient-to-tr from-blue-600 to-indigo-600 flex items-center justify-center shrink-0 shadow-md">
                        <i class="fa-solid fa-robot text-white text-xs"></i>
                    </div>
                    <div class="bg-dark-800 border border-gray-800 rounded-2xl p-4 text-gray-200 shadow-sm max-w-[85%] leading-relaxed">
                        <p class="font-semibold text-white mb-1">New Session Started</p>
                        <p class="text-sm text-gray-300">Context wiped. How can I assist you today?</p>
                    </div>
                </div>`;
        }

        async function handleSend(e) {
            e.preventDefault();
            const prompt = userInput.value.trim();
            if (!prompt) return;

            const apiKey = document.getElementById('api-key-input').value.trim() || 'free_user_key';

            // Append User Bubble
            chatContainer.innerHTML += `
                <div class="flex gap-4 items-start justify-end">
                    <div class="bg-blue-600 text-white rounded-2xl p-4 shadow-sm max-w-[85%] text-sm leading-relaxed">
                        ${escapeHtml(prompt)}
                    </div>
                </div>`;
            
            userInput.value = '';
            chatContainer.scrollTop = chatContainer.scrollHeight;

            // Loading state placeholder
            const loadingId = 'loading-' + Date.now();
            chatContainer.innerHTML += `
                <div id="${loadingId}" class="flex gap-4 items-start">
                    <div class="w-8 h-8 rounded-full bg-gradient-to-tr from-blue-600 to-indigo-600 flex items-center justify-center shrink-0 shadow-md animate-pulse">
                        <i class="fa-solid fa-robot text-white text-xs"></i>
                    </div>
                    <div class="bg-dark-800 border border-gray-800 rounded-2xl p-4 text-gray-400 text-sm flex items-center gap-2">
                        <i class="fa-solid fa-circle-notch fa-spin text-blue-500"><span>Executing multi-engine workflow...</span></i>
                    </div>
                </div>`;
            chatContainer.scrollTop = chatContainer.scrollHeight;

            try {
                const res = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-API-Key': apiKey
                    },
                    body: JSON.stringify({ prompt: prompt, history: chatHistory })
                });

                const data = await res.json();
                document.getElementById(loadingId).remove();

                if (!res.ok) {
                    throw new Error(data.detail || 'Server error occurred');
                }

                // Update headers / badges from response headers if available
                const remaining = res.headers.get('X-Requests-Remaining');
                const tier = res.headers.get('X-Tier');
                if (remaining) document.getElementById('badge-quota').innerText = remaining;
                if (tier) document.getElementById('badge-tier').innerText = tier;

                // Append Assistant Bubble with Markdown rendering
                const formattedResponse = marked.parse(data.response);
                chatContainer.innerHTML += `
                    <div class="flex gap-4 items-start">
                        <div class="w-8 h-8 rounded-full bg-gradient-to-tr from-blue-600 to-indigo-600 flex items-center justify-center shrink-0 shadow-md">
                            <i class="fa-solid fa-robot text-white text-xs"></i>
                        </div>
                        <div class="bg-dark-800 border border-gray-800 rounded-2xl p-4 text-gray-200 shadow-sm max-w-[85%] leading-relaxed prose prose-invert text-sm">
                            ${formattedResponse}
                        </div>
                    </div>`;

                // Update history
                chatHistory.push({ role: 'user', content: prompt });
                chatHistory.push({ role: 'assistant', content: data.response });

            } catch (err) {
                document.getElementById(loadingId).remove();
                chatContainer.innerHTML += `
                    <div class="flex gap-4 items-start">
                        <div class="w-8 h-8 rounded-full bg-red-600 flex items-center justify-center shrink-0 shadow-md">
                            <i class="fa-solid fa-triangle-exclamation text-white text-xs"></i>
                        </div>
                        <div class="bg-red-950/50 border border-red-800/50 rounded-2xl p-4 text-red-200 text-sm">
                            Error: ${escapeHtml(err.message)}
                        </div>
                    </div>`;
            }
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }

        function escapeHtml(text) {
            return text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
        }
    </script>
</body>
</html>
    """
