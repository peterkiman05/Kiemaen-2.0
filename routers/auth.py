from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import hashlib

router = APIRouter()

USER_DATABASE = {
    "admin": {
        "password_hash": hashlib.sha256("admin2026_secure".encode()).hexdigest(),
        "api_key": "pro_user_key",
    },
    "student": {
        "password_hash": hashlib.sha256("student2026_secure".encode()).hexdigest(),
        "api_key": "free_user_key",
    },
}


class LoginRequest(BaseModel):
    username: str
    password: str


@router.get("/login", response_class=HTMLResponse)
async def serve_login_page():
    return """
<!DOCTYPE html>
<html lang="en" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Neural Nexus - Gateway</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <script>
        tailwind.config = {
            darkMode: 'class',
            theme: {
                extend: {
                    colors: { dark: { 900: '#070a13', 800: '#0f172a', 700: '#1e293b' } },
                    animation: {
                        'pulse-slow': 'pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite',
                        'float': 'float 6s ease-in-out infinite',
                        'spin-slow': 'spin 12s linear infinite',
                    },
                    keyframes: {
                        float: {
                            '0%, 100%': { transform: 'translateY(0px)' },
                            '50%': { transform: 'translateY(-10px)' },
                        }
                    }
                }
            }
        }
    </script>
</head>
<body class="bg-dark-900 text-gray-100 font-sans min-h-screen flex items-center justify-center overflow-hidden relative selection:bg-blue-500 selection:text-white">

    <!-- Atmospheric Background Glows -->
    <div class="absolute -top-40 -left-40 w-96 h-96 bg-blue-600/20 rounded-full blur-[120px] pointer-events-none animate-pulse-slow"></div>
    <div class="absolute -bottom-40 -right-40 w-96 h-96 bg-indigo-600/20 rounded-full blur-[120px] pointer-events-none animate-pulse-slow" style="animation-delay: 2s;"></div>

    <!-- Main Container -->
    <div class="relative z-10 w-full max-w-md p-6">
        
        <!-- Kinetic Neural Emblem & Telemetry -->
        <div class="text-center mb-8 flex flex-col items-center">
            <div class="relative w-20 h-20 mb-4 flex items-center justify-center">
                <!-- Outer Ring -->
                <div class="absolute inset-0 rounded-2xl border border-blue-500/30 animate-spin-slow"></div>
                <!-- Inner Glow Ring -->
                <div class="absolute inset-1 rounded-xl border border-indigo-500/40 animate-spin-slow" style="animation-direction: reverse; animation-duration: 8s;"></div>
                <!-- Core Icon -->
                <div class="w-12 h-12 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-600 flex items-center justify-center shadow-lg shadow-blue-500/40 animate-float">
                    <i class="fa-solid fa-brain text-white text-lg"></i>
                </div>
            </div>
            
            <h1 class="font-extrabold text-2xl tracking-tight bg-gradient-to-r from-white via-gray-200 to-gray-400 bg-clip-text text-transparent">Neural Nexus</h1>
            
            <!-- Live Telemetry Badge -->
            <div class="mt-2 inline-flex items-center gap-2 px-3 py-1 rounded-full bg-dark-800/80 border border-gray-800 text-[11px] font-mono text-gray-400 backdrop-blur-md shadow-inner">
                <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                <span>Cluster v4.2 // Latency 14ms</span>
            </div>
        </div>

        <!-- Glassmorphic Authentication Card -->
        <div class="bg-dark-800/60 backdrop-blur-xl border border-gray-700/60 p-8 rounded-3xl shadow-2xl shadow-black/50 relative">
            
            <form id="login-form" onsubmit="handleLogin(event)" class="space-y-5">
                <div>
                    <label class="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Neural Identity</label>
                    <div class="relative">
                        <span class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-gray-500">
                            <i class="fa-solid fa-user text-xs"></i>
                        </span>
                        <input type="text" id="username" required placeholder="admin or student" 
                            class="w-full bg-dark-900/80 border border-gray-700/80 rounded-xl pl-11 pr-4 py-3.5 text-sm text-gray-200 focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition">
                    </div>
                </div>

                <div>
                    <label class="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Security Key</label>
                    <div class="relative">
                        <span class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-gray-500">
                            <i class="fa-solid fa-lock text-xs"></i>
                        </span>
                        <input type="password" id="password" required placeholder="••••••••••••" 
                            class="w-full bg-dark-900/80 border border-gray-700/80 rounded-xl pl-11 pr-4 py-3.5 text-sm text-gray-200 focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition">
                    </div>
                </div>

                <div id="error-msg" class="text-red-400 text-xs text-center font-medium bg-red-950/40 border border-red-800/40 py-2 rounded-lg hidden animate-bounce"></div>

                <button type="submit" id="submit-btn" class="w-full bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-semibold py-3.5 px-4 rounded-xl transition duration-200 shadow-lg shadow-blue-600/30 flex items-center justify-center gap-2 group">
                    <span>Initialize Session</span>
                    <i class="fa-solid fa-arrow-right text-xs group-hover:translate-x-1 transition-transform"></i>
                </button>
            </form>

            <!-- Divider -->
            <div class="relative my-6">
                <div class="absolute inset-0 flex items-center"><div class="w-full border-t border-gray-700/60"></div></div>
                <div class="relative flex justify-center text-xs uppercase"><span class="bg-dark-800 px-3 text-gray-500 font-mono">or connect via</span></div>
            </div>

            <!-- OAuth / Quick Connect Buttons -->
            <div class="grid grid-cols-2 gap-3">
                <button type="button" onclick="quickFill('admin', 'admin2026_secure')" class="bg-dark-900/60 hover:bg-dark-700 border border-gray-700/60 text-gray-300 text-xs font-medium py-2.5 rounded-xl transition flex items-center justify-center gap-2">
                    <i class="fa-solid fa-shield-halved text-blue-400"></i> Admin Access
                </button>
                <button type="button" onclick="quickFill('student', 'student2026_secure')" class="bg-dark-900/60 hover:bg-dark-700 border border-gray-700/60 text-gray-300 text-xs font-medium py-2.5 rounded-xl transition flex items-center justify-center gap-2">
                    <i class="fa-solid fa-graduation-cap text-emerald-400"></i> Student Pass
                </button>
            </div>
        </div>

        <!-- Enterprise Trust Footer -->
        <div class="mt-8 text-center flex items-center justify-center gap-4 text-[11px] text-gray-500">
            <span class="flex items-center gap-1"><i class="fa-solid fa-shield text-emerald-500 text-[10px]"></i> SOC-2 Verified</span>
            <span>•</span>
            <span>SHA-256 Encrypted Node</span>
        </div>

    </div>

    <script>
        function quickFill(user, pass) {
            document.getElementById('username').value = user;
            document.getElementById('password').value = pass;
        }

        async function handleLogin(e) {
            e.preventDefault();
            const username = document.getElementById('username').value.trim();
            const password = document.getElementById('password').value.trim();
            const errorDiv = document.getElementById('error-msg');
            const submitBtn = document.getElementById('submit-btn');
            
            errorDiv.classList.add('hidden');
            submitBtn.innerHTML = `<i class="fa-solid fa-circle-notch fa-spin"></i><span>Authenticating Node...</span>`;
            submitBtn.disabled = true;

            try {
                const res = await fetch('/api/auth/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, password })
                });
                const data = await res.json();
                if (!res.ok) throw new Error(data.detail || 'Authentication failed');

                localStorage.setItem('neural_api_key', data.api_key);
                
                // Success state transition
                submitBtn.innerHTML = `<i class="fa-solid fa-check text-emerald-400"></i><span>Access Granted</span>`;
                setTimeout(() => {
                    window.location.href = '/';
                }, 600);

            } catch (err) {
                errorDiv.innerText = err.message;
                errorDiv.classList.remove('hidden');
                submitBtn.innerHTML = `<span>Initialize Session</span><i class="fa-solid fa-arrow-right text-xs"></i>`;
                submitBtn.disabled = false;
            }
        }
    </script>
</body>
</html>
    """


@router.post("/api/auth/login")
async def login_user(payload: LoginRequest):
    user_record = USER_DATABASE.get(payload.username)
    if not user_record:
        raise HTTPException(
            status_code=401, detail="Invalid credentials or unknown neural entity."
        )

    hashed_input_pwd = hashlib.sha256(payload.password.encode()).hexdigest()
    if hashed_input_pwd != user_record["password_hash"]:
        raise HTTPException(
            status_code=401, detail="Invalid password verification hash."
        )

    return {
        "status": "success",
        "username": payload.username,
        "api_key": user_record["api_key"],
    }
