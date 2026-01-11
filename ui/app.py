"""
Voice Agent - Premium PyWebView UI
A sleek, modern voice recording interface with glassmorphism design.
"""

import webview
import keyboard
import pyperclip
from threading import Thread

from config import get_config
from core import AudioRecorder, Transcriber, TextProcessor


# ═══════════════════════════════════════════════════════════════════════════════
# HTML/CSS/JS UI
# ═══════════════════════════════════════════════════════════════════════════════

HTML_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Voice Agent</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        *, *::before, *::after {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        :root {
            --bg-base: #08080c;
            --bg-elevated: rgba(255, 255, 255, 0.02);
            --bg-glass: rgba(255, 255, 255, 0.04);
            --bg-glass-hover: rgba(255, 255, 255, 0.06);
            --border-subtle: rgba(255, 255, 255, 0.06);
            --border-medium: rgba(255, 255, 255, 0.1);

            --text-primary: rgba(255, 255, 255, 0.95);
            --text-secondary: rgba(255, 255, 255, 0.55);
            --text-tertiary: rgba(255, 255, 255, 0.32);

            --accent-teal: #00e5bf;
            --accent-teal-dim: rgba(0, 229, 191, 0.15);
            --accent-red: #ff4757;
            --accent-red-dim: rgba(255, 71, 87, 0.15);
            --accent-amber: #ffc107;
            --accent-amber-dim: rgba(255, 193, 7, 0.15);

            --success: #00d26a;
            --error: #ff4757;

            --ease-out-expo: cubic-bezier(0.16, 1, 0.3, 1);
            --ease-out-back: cubic-bezier(0.34, 1.56, 0.64, 1);
        }

        /* Custom Scrollbar */
        ::-webkit-scrollbar {
            width: 4px;
        }
        ::-webkit-scrollbar-track {
            background: transparent;
        }
        ::-webkit-scrollbar-thumb {
            background: rgba(255, 255, 255, 0.15);
            border-radius: 4px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: rgba(255, 255, 255, 0.25);
        }

        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        @keyframes pulseRing {
            0%, 100% {
                transform: translate(-50%, -50%) scale(1);
                opacity: 0.6;
            }
            50% {
                transform: translate(-50%, -50%) scale(1.08);
                opacity: 0.3;
            }
        }

        @keyframes breathe {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.02); }
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        @keyframes shimmer {
            0% { background-position: -200% center; }
            100% { background-position: 200% center; }
        }

        html, body {
            height: 100%;
            overflow: hidden;
        }

        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: var(--bg-base);
            color: var(--text-primary);
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
            user-select: none;
            cursor: default;
        }

        /* Subtle gradient overlay */
        body::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background:
                radial-gradient(ellipse at 50% 0%, rgba(0, 229, 191, 0.03) 0%, transparent 50%),
                radial-gradient(ellipse at 50% 100%, rgba(255, 71, 87, 0.02) 0%, transparent 50%);
            pointer-events: none;
            z-index: 0;
        }

        .app {
            position: relative;
            z-index: 1;
            display: flex;
            flex-direction: column;
            align-items: center;
            height: 100vh;
            padding: 24px 28px 56px;
            overflow: hidden;
        }

        /* Header */
        .header {
            width: 100%;
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 24px;
            animation: fadeInUp 0.6s var(--ease-out-expo) both;
        }

        .header-left {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .logo {
            font-size: 11px;
            font-weight: 600;
            letter-spacing: 2.5px;
            text-transform: uppercase;
            color: var(--text-tertiary);
        }

        .status-indicator {
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background: var(--accent-teal);
            box-shadow: 0 0 12px var(--accent-teal);
            transition: all 0.4s var(--ease-out-expo);
        }

        .status-indicator.recording {
            background: var(--accent-red);
            box-shadow: 0 0 12px var(--accent-red), 0 0 24px var(--accent-red-dim);
            animation: breathe 1.2s ease-in-out infinite;
        }

        .status-indicator.processing {
            background: var(--accent-amber);
            box-shadow: 0 0 12px var(--accent-amber);
        }

        /* Language Dropdown */
        .lang-dropdown {
            position: relative;
        }

        .lang-toggle {
            display: flex;
            align-items: center;
            gap: 6px;
            padding: 5px 10px;
            border: none;
            border-radius: 6px;
            background: rgba(0, 0, 0, 0.3);
            font-family: inherit;
            font-size: 10px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
            color: var(--text-secondary);
        }

        .lang-toggle:hover {
            background: rgba(0, 0, 0, 0.4);
            color: var(--text-primary);
        }

        .lang-toggle svg {
            width: 10px;
            height: 10px;
            transition: transform 0.2s ease;
        }

        .lang-dropdown.open .lang-toggle svg {
            transform: rotate(180deg);
        }

        .lang-menu {
            position: absolute;
            top: calc(100% + 6px);
            right: 0;
            background: rgba(20, 20, 25, 0.95);
            border: 1px solid var(--border-medium);
            border-radius: 8px;
            padding: 4px;
            opacity: 0;
            visibility: hidden;
            transform: translateY(-8px);
            transition: all 0.2s ease;
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            z-index: 100;
        }

        .lang-dropdown.open .lang-menu {
            opacity: 1;
            visibility: visible;
            transform: translateY(0);
        }

        .lang-option {
            display: block;
            width: 100%;
            padding: 8px 16px;
            border: none;
            border-radius: 4px;
            background: transparent;
            font-family: inherit;
            font-size: 11px;
            font-weight: 500;
            text-align: left;
            cursor: pointer;
            color: var(--text-secondary);
            transition: all 0.15s ease;
        }

        .lang-option:hover {
            background: rgba(255, 255, 255, 0.06);
            color: var(--text-primary);
        }

        .lang-option.active {
            color: var(--accent-teal);
        }

        /* Record Button */
        .rec-wrapper {
            position: relative;
            margin-bottom: 20px;
            animation: fadeInUp 0.6s var(--ease-out-expo) 0.1s both;
        }

        .rec-ring {
            position: absolute;
            top: 50%;
            left: 50%;
            width: 164px;
            height: 164px;
            border-radius: 50%;
            border: 1px solid var(--accent-teal-dim);
            transform: translate(-50%, -50%);
            transition: all 0.5s var(--ease-out-expo);
            pointer-events: none;
        }

        .rec-ring.recording {
            border-color: var(--accent-red);
            animation: pulseRing 2s ease-in-out infinite;
        }

        .rec-ring.processing {
            border-color: var(--accent-amber-dim);
        }

        .rec-btn {
            position: relative;
            width: 132px;
            height: 132px;
            border-radius: 50%;
            border: 2px solid var(--accent-teal);
            background: linear-gradient(
                165deg,
                rgba(255, 255, 255, 0.06) 0%,
                rgba(255, 255, 255, 0.02) 50%,
                rgba(0, 0, 0, 0.1) 100%
            );
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.4s var(--ease-out-expo);
            box-shadow:
                0 4px 24px rgba(0, 0, 0, 0.3),
                inset 0 1px 0 rgba(255, 255, 255, 0.05);
        }

        .rec-btn:hover {
            transform: scale(1.03);
            border-color: var(--accent-teal);
            box-shadow:
                0 8px 40px rgba(0, 229, 191, 0.2),
                0 4px 24px rgba(0, 0, 0, 0.3),
                inset 0 1px 0 rgba(255, 255, 255, 0.05);
        }

        .rec-btn:active {
            transform: scale(0.97);
        }

        .rec-btn.recording {
            border-color: var(--accent-red);
            box-shadow:
                0 8px 40px rgba(255, 71, 87, 0.25),
                0 4px 24px rgba(0, 0, 0, 0.3),
                inset 0 1px 0 rgba(255, 255, 255, 0.05);
        }

        .rec-btn.processing {
            border-color: var(--accent-amber);
            cursor: wait;
        }

        .rec-text {
            font-size: 16px;
            font-weight: 700;
            letter-spacing: 4px;
            color: var(--accent-teal);
            transition: color 0.3s ease;
        }

        .rec-btn.recording .rec-text {
            color: var(--accent-red);
        }

        .rec-btn.processing .rec-text {
            display: none;
        }

        .rec-spinner {
            display: none;
            width: 28px;
            height: 28px;
            border: 2px solid var(--accent-amber-dim);
            border-top-color: var(--accent-amber);
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
        }

        .rec-btn.processing .rec-spinner {
            display: block;
        }

        /* Status Text */
        .status-section {
            text-align: center;
            margin-top: 8px;
            margin-bottom: 16px;
            animation: fadeInUp 0.6s var(--ease-out-expo) 0.15s both;
        }

        .status-title {
            font-size: 16px;
            font-weight: 600;
            color: var(--text-primary);
            margin-bottom: 4px;
            letter-spacing: -0.2px;
        }

        .status-subtitle {
            font-size: 12px;
            color: var(--text-tertiary);
            letter-spacing: 0.1px;
        }

        /* Transcription Card */
        .transcript-card {
            flex: 1;
            width: 100%;
            max-width: 320px;
            display: flex;
            flex-direction: column;
            background: var(--bg-glass);
            border: 1px solid var(--border-subtle);
            border-radius: 14px;
            padding: 14px 16px;
            cursor: pointer;
            transition: all 0.3s ease;
            animation: fadeInUp 0.6s var(--ease-out-expo) 0.2s both;
            min-height: 0;
        }

        .transcript-card:hover {
            background: var(--bg-glass-hover);
            border-color: var(--border-medium);
        }

        .transcript-card:active {
            transform: scale(0.99);
        }

        .transcript-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 10px;
            flex-shrink: 0;
        }

        .transcript-label {
            font-size: 10px;
            font-weight: 600;
            letter-spacing: 1.2px;
            text-transform: uppercase;
            color: var(--text-tertiary);
        }

        .copy-badge {
            font-size: 10px;
            font-weight: 600;
            color: var(--success);
            opacity: 0;
            transform: translateY(-4px);
            transition: all 0.3s var(--ease-out-expo);
        }

        .copy-badge.show {
            opacity: 1;
            transform: translateY(0);
        }

        .transcript-content {
            flex: 1;
            overflow-y: auto;
            padding-right: 4px;
            min-height: 0;
        }

        .transcript-text {
            font-size: 13px;
            line-height: 1.6;
            color: var(--text-tertiary);
            font-style: italic;
        }

        .transcript-text.filled {
            color: var(--text-secondary);
            font-style: normal;
        }

        .transcript-text.error {
            color: var(--error);
            font-style: normal;
        }

        /* History Navigation */
        .transcript-footer {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-top: 10px;
            padding-top: 10px;
            border-top: 1px solid var(--border-subtle);
            flex-shrink: 0;
            opacity: 0;
            transition: opacity 0.2s ease;
        }

        .transcript-card.has-text .transcript-footer {
            opacity: 1;
        }

        .history-nav {
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .nav-btn {
            display: flex;
            align-items: center;
            justify-content: center;
            width: 24px;
            height: 24px;
            border: none;
            border-radius: 6px;
            background: rgba(255, 255, 255, 0.05);
            color: var(--text-secondary);
            cursor: pointer;
            transition: all 0.2s ease;
        }

        .nav-btn:hover:not(:disabled) {
            background: rgba(255, 255, 255, 0.1);
            color: var(--text-primary);
        }

        .nav-btn:disabled {
            opacity: 0.3;
            cursor: default;
        }

        .nav-btn svg {
            width: 12px;
            height: 12px;
        }

        .history-indicator {
            font-size: 10px;
            font-weight: 500;
            color: var(--text-tertiary);
            min-width: 36px;
            text-align: center;
        }

        .click-hint {
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: 10px;
            color: var(--text-tertiary);
        }

        .click-hint svg {
            width: 12px;
            height: 12px;
            opacity: 0.6;
        }

        /* Footer */
        .footer {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            padding: 14px 0;
            display: flex;
            justify-content: center;
            background: linear-gradient(to top, var(--bg-base) 60%, transparent);
            animation: fadeInUp 0.6s var(--ease-out-expo) 0.25s both;
        }

        .hotkey-row {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 11px;
            color: var(--text-tertiary);
        }

        .kbd {
            display: inline-flex;
            align-items: center;
            padding: 4px 8px;
            background: rgba(255, 255, 255, 0.04);
            border: 1px solid var(--border-subtle);
            border-radius: 5px;
            font-family: 'SF Mono', 'Fira Code', 'Consolas', monospace;
            font-size: 10px;
            font-weight: 500;
            letter-spacing: 0.5px;
            color: var(--text-secondary);
        }
    </style>
</head>
<body>
    <div class="app">
        <header class="header">
            <div class="header-left">
                <span class="logo">STT -0</span>
                <div class="status-indicator" id="statusIndicator"></div>
            </div>
            <div class="lang-dropdown" id="langDropdown">
                <button class="lang-toggle" onclick="toggleLangMenu()">
                    <span id="currentLang">EN</span>
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <polyline points="6 9 12 15 18 9"></polyline>
                    </svg>
                </button>
                <div class="lang-menu">
                    <button class="lang-option" data-lang="it" onclick="selectLang('it')">Italiano</button>
                    <button class="lang-option active" data-lang="en" onclick="selectLang('en')">English</button>
                    <button class="lang-option" data-lang="es" onclick="selectLang('es')">Español</button>
                    <button class="lang-option" data-lang="fr" onclick="selectLang('fr')">Français</button>
                    <button class="lang-option" data-lang="de" onclick="selectLang('de')">Deutsch</button>
                </div>
            </div>
        </header>

        <div class="rec-wrapper">
            <div class="rec-ring" id="recRing"></div>
            <button class="rec-btn" id="recBtn" onclick="handleRecord()">
                <span class="rec-text" id="recText">REC</span>
                <div class="rec-spinner"></div>
            </button>
        </div>

        <section class="status-section">
            <h2 class="status-title" id="statusTitle">Ready</h2>
            <p class="status-subtitle" id="statusSubtitle">Tap to start recording</p>
        </section>

        <div class="transcript-card" id="transcriptCard">
            <div class="transcript-header">
                <span class="transcript-label">Transcription</span>
                <span class="copy-badge" id="copyBadge">Copied!</span>
            </div>
            <div class="transcript-content" onclick="copyTranscription()">
                <p class="transcript-text" id="transcriptText">Your transcription will appear here...</p>
            </div>
            <div class="transcript-footer">
                <div class="history-nav">
                    <button class="nav-btn" id="btnPrev" onclick="navigateHistory(1)" disabled>
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <polyline points="15 18 9 12 15 6"></polyline>
                        </svg>
                    </button>
                    <span class="history-indicator" id="historyIndicator">0 / 0</span>
                    <button class="nav-btn" id="btnNext" onclick="navigateHistory(-1)" disabled>
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <polyline points="9 18 15 12 9 6"></polyline>
                        </svg>
                    </button>
                </div>
                <div class="click-hint" onclick="copyTranscription()">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                        <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                    </svg>
                    <span>Click to copy</span>
                </div>
            </div>
        </div>

        <footer class="footer">
            <div class="hotkey-row">
                <span>Hotkey</span>
                <kbd class="kbd" id="hotkeyDisplay">ctrl+shift+v</kbd>
            </div>
        </footer>
    </div>

    <script>
        let state = 'idle';
        let history = [];
        let historyIndex = -1;
        const MAX_HISTORY = 20;

        function handleRecord() {
            if (state === 'processing') return;
            pywebview.api.toggle_recording();
        }

        function toggleLangMenu() {
            document.getElementById('langDropdown').classList.toggle('open');
        }

        function selectLang(lang) {
            pywebview.api.set_language(lang);
            document.getElementById('currentLang').textContent = lang.toUpperCase();

            document.querySelectorAll('.lang-option').forEach(opt => {
                opt.classList.toggle('active', opt.dataset.lang === lang);
            });

            document.getElementById('langDropdown').classList.remove('open');
        }

        // Close dropdown when clicking outside
        document.addEventListener('click', function(e) {
            const dropdown = document.getElementById('langDropdown');
            if (!dropdown.contains(e.target)) {
                dropdown.classList.remove('open');
            }
        });

        function copyTranscription() {
            if (history.length === 0 || historyIndex < 0) return;
            pywebview.api.copy_text(history[historyIndex]);
            const badge = document.getElementById('copyBadge');
            badge.classList.add('show');
            setTimeout(() => badge.classList.remove('show'), 2000);
        }

        function navigateHistory(dir) {
            const newIndex = historyIndex + dir;
            if (newIndex < 0 || newIndex >= history.length) return;
            historyIndex = newIndex;
            displayCurrentTranscription();
            updateHistoryUI();
        }

        function displayCurrentTranscription() {
            const el = document.getElementById('transcriptText');
            if (historyIndex >= 0 && historyIndex < history.length) {
                el.textContent = history[historyIndex];
                el.className = 'transcript-text filled';
            }
        }

        function updateHistoryUI() {
            const btnPrev = document.getElementById('btnPrev');
            const btnNext = document.getElementById('btnNext');
            const indicator = document.getElementById('historyIndicator');

            if (history.length === 0) {
                indicator.textContent = '0 / 0';
                btnPrev.disabled = true;
                btnNext.disabled = true;
            } else {
                indicator.textContent = `${historyIndex + 1} / ${history.length}`;
                btnPrev.disabled = historyIndex >= history.length - 1;
                btnNext.disabled = historyIndex <= 0;
            }
        }

        function updateStatus(newState) {
            state = newState;

            const indicator = document.getElementById('statusIndicator');
            const ring = document.getElementById('recRing');
            const btn = document.getElementById('recBtn');
            const text = document.getElementById('recText');
            const title = document.getElementById('statusTitle');
            const subtitle = document.getElementById('statusSubtitle');

            indicator.className = 'status-indicator ' + newState;
            ring.className = 'rec-ring ' + newState;
            btn.className = 'rec-btn ' + newState;

            switch(newState) {
                case 'idle':
                    text.textContent = 'REC';
                    title.textContent = 'Ready';
                    subtitle.textContent = 'Tap to start recording';
                    break;
                case 'recording':
                    text.textContent = 'STOP';
                    title.textContent = 'Recording';
                    subtitle.textContent = 'Tap again to finish';
                    break;
                case 'processing':
                    text.textContent = '';
                    title.textContent = 'Processing';
                    subtitle.textContent = 'Transcribing audio...';
                    break;
            }
        }

        function showTranscription(text, isError = false) {
            const el = document.getElementById('transcriptText');
            const badge = document.getElementById('copyBadge');
            const card = document.getElementById('transcriptCard');

            if (!isError) {
                // Add to history
                history.unshift(text);
                if (history.length > MAX_HISTORY) {
                    history.pop();
                }
                historyIndex = 0;

                el.textContent = text;
                el.className = 'transcript-text filled';
                card.classList.add('has-text');
                updateHistoryUI();

                badge.classList.add('show');
                setTimeout(() => badge.classList.remove('show'), 2500);
            } else {
                el.textContent = text;
                el.className = 'transcript-text error';
            }
        }

        function setHotkey(key) {
            document.getElementById('hotkeyDisplay').textContent = key;
        }

        function setInitialLanguage(lang) {
            document.getElementById('currentLang').textContent = lang.toUpperCase();
            document.querySelectorAll('.lang-option').forEach(opt => {
                opt.classList.toggle('active', opt.dataset.lang === lang);
            });
        }
    </script>
</body>
</html>
"""


# ═══════════════════════════════════════════════════════════════════════════════
# PYTHON API
# ═══════════════════════════════════════════════════════════════════════════════

class Api:
    """Python API exposed to JavaScript."""

    def __init__(self):
        self.config = get_config()
        self._validate_config()

        self._status = "idle"
        self._window = None

        # Initialize components
        self.recorder = AudioRecorder(
            sample_rate=self.config.audio.sample_rate,
            channels=self.config.audio.channels,
        )

        self.transcriber = Transcriber(
            api_key=self.config.groq_api_key,
            language=self.config.language,
        )

        self.processor = TextProcessor(
            corrections=self.config.text_corrections,
        )

    def _validate_config(self):
        if not self.config.groq_api_key:
            raise ValueError(
                "GROQ_API_KEY not set!\n"
                "Please add it to your .env file.\n"
                "Get your free API key at: https://console.groq.com"
            )

    def set_window(self, window):
        self._window = window

    def toggle_recording(self):
        """Toggle recording state."""
        if self._status == "processing":
            return

        if not self.recorder.is_recording:
            self._set_status("recording")
            self.recorder.start()
        else:
            audio_data = self.recorder.stop()
            self._set_status("processing")
            Thread(target=self._process_audio, args=(audio_data,), daemon=True).start()

    def set_language(self, lang):
        """Set transcription language and save preference."""
        self.config.set_language(lang)
        self.transcriber.set_language(lang)

    def copy_text(self, text):
        """Copy text to clipboard."""
        pyperclip.copy(text)

    def _set_status(self, status):
        """Update status and notify UI."""
        self._status = status
        if self._window:
            self._window.evaluate_js(f"updateStatus('{status}')")

    def _process_audio(self, audio_data):
        """Process recorded audio."""
        if not audio_data:
            self._show_error("No audio recorded")
            self._set_status("idle")
            return

        text = self.transcriber.transcribe(audio_data)

        if not text:
            self._show_error("Transcription failed")
            self._set_status("idle")
            return

        text = self.processor.process(text)
        text = self.processor.format_for_terminal(text)

        if not text:
            self._show_error("Empty result")
            self._set_status("idle")
            return

        # Copy to clipboard
        pyperclip.copy(text)

        # Update UI with full text (JS will handle display)
        escaped = text.replace("\\", "\\\\").replace("'", "\\'").replace("\n", " ")
        if self._window:
            self._window.evaluate_js(f"showTranscription('{escaped}')")

        self._set_status("idle")

    def _show_error(self, message):
        """Show error in UI."""
        if self._window:
            self._window.evaluate_js(f"showTranscription('Error: {message}', true)")


# ═══════════════════════════════════════════════════════════════════════════════
# APPLICATION
# ═══════════════════════════════════════════════════════════════════════════════

class VoiceAgentApp:
    """Premium Voice Agent with PyWebView."""

    def __init__(self):
        self.api = Api()

    def run(self):
        """Run the application."""
        # Create window
        window = webview.create_window(
            title="Voice Agent",
            html=HTML_CONTENT,
            width=360,
            height=580,
            resizable=False,
            on_top=True,
            js_api=self.api,
            background_color="#0a0a0f"
        )

        self.api.set_window(window)

        def on_loaded():
            # Set initial values
            window.evaluate_js(f"setHotkey('{self.api.config.hotkey}')")
            window.evaluate_js(f"setInitialLanguage('{self.api.config.language}')")

            # Register hotkey
            keyboard.add_hotkey(
                self.api.config.hotkey,
                self.api.toggle_recording,
                suppress=False
            )

        window.events.loaded += on_loaded

        # Start webview
        webview.start()

        # Cleanup
        keyboard.unhook_all()
        if self.api.recorder.is_recording:
            self.api.recorder.stop()


# ═══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    """Entry point."""
    app = VoiceAgentApp()
    app.run()


if __name__ == "__main__":
    main()
