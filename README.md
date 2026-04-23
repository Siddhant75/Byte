# 🐰 Byte: Your FOSS AI Co-working Companion

Byte is a stateful, memory-aware AI companion designed to live on your desktop and help you stay focused. Built entirely with **Free and Open-Source Software (FOSS)**, Byte combines a Tamagotchi-style pet with a high-performance productivity tool.

![Byte Preview](https://img.shields.io/badge/Status-Beta-orange?style=for-the-badge)
![Tech Stack](https://img.shields.io/badge/Stack-Python_%7C_FastAPI_%7C_Electron_%7C_SQLite-blue?style=for-the-badge)

---

## ✨ Core Features

*   **🧠 Deep Memory (RAG):** Byte uses a local vector database (ChromaDB) to remember your past interactions, preferences, and work habits.
*   **⏲️ Focus-Driven Gameplay:** Earn experience and level up Byte by completing focus sessions. The Pomodoro timer is integrated directly into Byte's state machine.
*   **🐾 Stateful Needs:** Byte has real biological-style needs. Hunger, Energy, and Happiness decay over time, requiring you to interact and "care" for your companion.
*   **🤖 Local Intelligence:** Powered by **Ollama** and **Dolphin-Llama3**, ensuring your data never leaves your machine.
*   **✨ Premium Aesthetics:** A cozy, glassmorphism-inspired UI with layered SVG animations that reflect Byte's current mood and activity.

---

## 🛠️ Technology Stack

| Layer | Technology |
| :--- | :--- |
| **Brain** | Ollama (Dolphin-Llama3:8b) |
| **Memory** | ChromaDB (Local Vector Store) |
| **Backend** | Python 3.10+, FastAPI, SQLite |
| **Frontend** | Electron, Vanilla JS, CSS3, SVGs |
| **Scheduler** | APScheduler (Background Stat Decay) |

---

## 🚀 Getting Started

### 1. Prerequisites
*   [Python 3.10+](https://www.python.org/)
*   [Node.js & npm](https://nodejs.org/)
*   [Ollama](https://ollama.com/) (Run `ollama pull dolphin-llama3:8b` after installation)

### 2. Backend Setup
```powershell
# Navigate to backend directory
cd backend

# Install dependencies
pip install -r requirements.txt

# Start the FastAPI server
python main.py
```

### 3. Frontend Setup
```powershell
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Launch Byte
npm start
```

---

## ⌨️ Shortcuts & Interaction

*   **`Ctrl + Space`**: Toggle the chat window visibility.
*   **`Click Byte`**: Trigger a quick interaction or greeting when the chat is closed.
*   **Focus Timer**: Set your desired minutes and hit **Start Focus**. Byte will cheer you on!
*   **Stats**: Byte's hunger and energy decay every 5 minutes. Use the chat to "feed" or "play" with him (Autonomous action parsing is built-in).

---

## 🏗️ Architecture
For a deep dive into the design philosophy, state machine logic, and SVG animation layers, please refer to the [Workflow Specification](ai_companion_workflow.md).

---

## 🗺️ Roadmap
- [x] Background Stat Decay system.
- [x] Autonomous Action Parsing (LLM triggers state changes).
- [ ] Voice Interface (STT/TTS integration).
- [ ] Advanced SVG path-morphing animations for Byte.
- [ ] Multi-device sync via local network.

---

## ⚖️ License
This project is open-source and intended for educational and personal productivity use. See the individual components for specific FOSS licenses (MIT/Apache 2.0).
